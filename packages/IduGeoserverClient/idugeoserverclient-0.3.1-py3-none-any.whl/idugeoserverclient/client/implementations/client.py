import asyncio
import json
from datetime import datetime
from re import match
from typing import BinaryIO

from aiohttp import ClientConnectionError, BasicAuth, ClientSession, FormData
from iduconfig import Config
from iduredis import RedisManager
from loguru import logger

from idugeoserverclient.client.client_interface import IIduGeoserverClient
from idugeoserverclient.models.datastore_model import DatastoreModel
from idugeoserverclient.models.layer_model import LayerModel


class IduGeoserverClient(IIduGeoserverClient):

    def __init__(self, config: Config):
        """
        Geoserver client instance
        """
        self._login = config.get("GEOSERVER_LOGIN")
        self._password = config.get("GEOSERVER_PASSWORD")
        self._prefix = "/geoserver/rest"
        self._caching_prefix = "/geoserver/gwc/rest"
        self._api_url = config.get('GEOSERVER_URL')
        logger.debug(f"Running configuration with {self._api_url}{self._prefix} @{self._login}:{self._password}")

        self._redis = RedisManager(config)
        self.delete_queue = []

    async def upload_layer(
            self, workspace_name: str, file: BinaryIO, layer_type: str, created_at: str | datetime,
            replace_existing: bool = True, style_name: str | None = None, *args
    ) -> None:
        """Upload .gpkg file to Geoserver workspace and publish it automatically.

        File name should be of format `YYYY-MM-DD-HH-mm-ss_{layer_type_name}_{...args}.gpkg`.
        Note that args are order sensitive.

        Please keep in mind that style with specified name should be uploaded
        before trying to set it for a layer. You won't be alerted if prompted style isn't present in current workspace
        because Geoserver API always returns 200 for any style name.

        Example of correct filename: 2024-11-24-13-33-20_ecodonut_1.gpkg

        Args:
            workspace_name (str): geoserver's workspace name.
            file (str): file stream opened in `rb` mode.
            layer_type (str): categorizing name for your layer
            (unique, contact other teams or geoserver admins to pick name).
            created_at (str or datetime): if str, date in `YYYY-MM-DD-HH-mm-ss` format.
            replace_existing (bool): if true, delete similar layer with earlier date before uploading a new one.
            style_name (str or None): if specified, set provided style as a default style for uploaded layer.
            args (Any): categorizing arguments of any type which has str() method.

        Raises:
            NameError: raised if file is not `gpkg` format file.
            RuntimeError: raised if response from upload request isn't 200 or 201.
            ConnectionError: raised if client couldn't establish connection with Geoserver.
        """

        if file.name.split(".")[-1] != "gpkg":
            raise NameError("Received not .gpkg file. Please, reformat it to gpkg")

        if replace_existing:
            filtered_layers = await self.get_layers(workspace_name, layer_type, *args)
            for layer in filtered_layers:
                await self.delete_layer(workspace_name, layer.name)
                await self.delete_datastore(workspace_name, layer.name)

        if type(created_at) is str:
            created_at = datetime.strptime(created_at, "%Y-%m-%d-%H-%M-%S")
        created_at = created_at.strftime("%Y-%m-%d-%H-%M-%S")
        layer_name = f"{created_at}_{layer_type}"
        for arg in args:
            layer_name += f"_{str(arg)}"
        async with ClientSession() as session:
            try:
                async with session.put(
                    f"{self._api_url}{self._prefix}/workspaces/{workspace_name}/datastores/{layer_name}/file.gpkg",
                    data=file,
                    headers={"Content-Type": "application/json"},
                    auth=BasicAuth(self._login, self._password)
                ) as response:
                    if response.status not in [200, 201]:
                        raise RuntimeError(
                            f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}"
                        )
                if style_name:
                    async with session.put(
                        f"{self._api_url}{self._prefix}/workspaces/{workspace_name}/layers/{layer_name}",
                        data="<layer><defaultStyle><name>{}</name></defaultStyle></layer>".format(
                            style_name
                        ),
                        headers={"Content-Type": "application/xml"},
                        auth=BasicAuth(self._login, self._password)
                    ) as response:
                        if response.status not in [200, 201]:
                            raise RuntimeError(
                                f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}"
                            )
                form_data = FormData()
                form_data.add_field("threadCount", "01")
                form_data.add_field("type", "seed")
                form_data.add_field("gridSetId", "EPSG:4326")
                form_data.add_field("tileFormat", "application/vnd.mapbox-vector-tile")
                form_data.add_field("zoomStart", "03")
                form_data.add_field("zoomStop", "10")
                if style_name:
                    form_data.add_field("parameter_STYLES", f"EcoFrames:{style_name}")
                form_data.add_field("minX", "")
                form_data.add_field("minY", "")
                form_data.add_field("maxX", "")
                form_data.add_field("maxY", "")
                form_data.add_field("tileFailureRetryCount", "-1")
                form_data.add_field("tileFailureRetryWaitTime", "100")
                form_data.add_field("tileFailuresBeforeAborting", "1000")
                async with session.post(
                    f"{self._api_url}{self._caching_prefix}/seed/{workspace_name}:{layer_name}",
                    data=form_data
                ) as response:
                    if response.status not in [200, 201]:
                        raise RuntimeError(
                            f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}"
                        )
            except ClientConnectionError as e:
                raise ConnectionError("GEOSERVER_NOT_AVAILABLE") from e
        return

    async def get_layers(self, workspace_name: str, layer_type: str | None = None, *args) -> list[LayerModel]:
        """
        Get list of layers in workspace. Can be filtered using layer_type and arguments.

        Args:
            workspace_name (str): geoserver's workspace name.
            layer_type (str): categorizing name for your layer (unique).
            args (Any): categorizing arguments of any type which has str() method.

        Returns:
            list: list of LayerModel.

        Raises:
            RuntimeError: raised if response from upload request isn't 200 or 201. Mostly raised if layer wasn't found.
            ConnectionError: raised if client couldn't establish connection with Geoserver.
        """

        async with ClientSession() as session:
            try:
                async with session.get(
                    f"{self._api_url}{self._prefix}/workspaces/{workspace_name}/layers",
                    headers={"Content-Type": "application/json"},
                    auth=BasicAuth(self._login, password=self._password)
                ) as response:
                    if response.status not in [200, 201]:
                        raise RuntimeError(f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}")
                    data = (await response.read()).decode("utf-8")
                    print(data)
            except ClientConnectionError as e:
                raise ConnectionError("GEOSERVER_NOT_AVAILABLE") from e
        deserialized_data: dict = json.loads(data)
        if deserialized_data["layers"] == "":
            return []
        data = deserialized_data.get("layers", {}).get("layer", [])
        if layer_type:
            pattern = f".*_{layer_type}"
            if len(args) != 0:
                pattern += f"{''.join([f'_{str(arg)}' for arg in args])}$"
            data = list(filter(
                lambda v: match(
                    pattern, v["name"]
                ), data))
        return [LayerModel(**layer) for layer in data]

    async def delete_layer(self, workspace_name: str, layer_name: str) -> None:
        """
        Delete layer from workspace with layer_name.
        Layer name is a string of format `YYYY-MM-DD-HH-mm-ss_{layer_type_name}_{...args}`.

        This method should be used before deleting datastore.

        Args:
            workspace_name (str): geoserver's workspace name.
            layer_name (str): a string of format `YYYY-MM-DD-HH-mm-ss_{layer_type_name}_{...args}`.

        Raises:
            RuntimeError: raised if response from upload request isn't 200 or 201. Mostly raised if layer wasn't found.
            ConnectionError: raised if client couldn't establish connection with Geoserver.
        """

        async with ClientSession() as session:
            try:
                async with session.delete(
                    f"{self._api_url}{self._prefix}/workspaces/{workspace_name}/layers/{layer_name}",
                    auth=BasicAuth(self._login, self._password)
                ) as response:
                    if response.status not in [200, 201]:
                        raise RuntimeError(f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}")
                    self.delete_queue.append(f"{workspace_name}:{layer_name}")
                    await self._delete_layer_through_redis()
                    return
            except ClientConnectionError as e:
                raise ConnectionError("GEOSERVER_NOT_AVAILABLE") from e

    async def get_datastores(
            self, workspace_name: str, datastore_type: str | None = None, *args
    ) -> list[DatastoreModel]:
        """
        Get list of datastores in workspace. Can be filtered using datastore_type and arguments.

        Args:
            workspace_name (str): geoserver's workspace name.
            datastore_type (str): categorizing name for your datastore (unique).
            args (Any): categorizing arguments of any type which has str() method.

        Returns:
            list: list of DatastoreModel.

        Raises:
            RuntimeError: raised if response from upload request isn't 200 or 201. Mostly raised if datastore wasn't found.
            ConnectionError: raised if client couldn't establish connection with Geoserver.
        """

        async with ClientSession() as session:
            try:
                async with session.get(
                    f"{self._api_url}{self._prefix}/workspaces/{workspace_name}/datastores",
                    headers={"Content-Type": "application/json"},
                    auth=BasicAuth(self._login, self._password)
                ) as response:
                    if response.status not in [200, 201]:
                        raise RuntimeError(f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}")
                    data = (await response.read()).decode("utf-8")
            except ClientConnectionError as e:
                raise ConnectionError("GEOSERVER_NOT_AVAILABLE") from e
        deserialized_data: dict = json.loads(data)
        data = deserialized_data.get("dataStores", {}).get("dataStore", [])
        if datastore_type:
            pattern = f".*_{datastore_type}"
            if len(args) != 0:
                pattern += f"{''.join([f'_{str(arg)}' for arg in args])}$"
            data = list(filter(
                lambda v: match(
                    pattern, v["name"]
                ), data))
        return [DatastoreModel(**datastore) for datastore in data]

    async def delete_datastore(self, workspace_name: str, datastore_name: str) -> None:
        """
        Delete datastore from workspace with layer_name.
        Datastore name is a string of format `YYYY-MM-DD-HH-mm-ss_{datastore_type_name}_{...args}`.

        This method should be used after deleting layer.

        Args:
            workspace_name (str): geoserver's workspace name.
            datastore_name (str): a string of format `YYYY-MM-DD-HH-mm-ss_{datastore_type_name}_{...args}`.

        Raises:
            RuntimeError: raised if response from upload request isn't 200 or 201. Mostly raised if datastore wasn't found.
            ConnectionError: raised if client couldn't establish connection with Geoserver.
        """

        async with ClientSession() as session:
            try:
                async with session.delete(
                    f"{self._api_url}{self._prefix}/workspaces/{workspace_name}/datastores/{datastore_name}?recurse=true",
                    auth=BasicAuth(self._login, self._password)
                ) as response:
                    if response.status not in [200, 201]:
                        raise RuntimeError(f"{response.status}, HTML_OF_ERROR: {(await response.read()).decode('utf-8')}")
                    return
            except ClientConnectionError as e:
                raise ConnectionError("GEOSERVER_NOT_AVAILABLE") from e

    async def _delete_layer_through_redis(self):
        max_retries = 5
        retry_delay = 5
        retries = 0
        while len(self.delete_queue) != 0:
            if retries >= max_retries:
                logger.error("Out of retries...")
                return
            while retries < max_retries:
                try:
                    await self._redis.push_to_list("clear_geoserver_layer", self.delete_queue[-1])
                    self.delete_queue.pop()
                    break
                except Exception as e:
                    logger.error(f"Retry {retries + 1}: {e}")
                    await asyncio.sleep(retry_delay)
                    retries += 1
                    continue

