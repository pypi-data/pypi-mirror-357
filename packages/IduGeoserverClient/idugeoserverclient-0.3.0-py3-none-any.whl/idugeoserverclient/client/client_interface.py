from abc import ABC, abstractmethod
from datetime import datetime
from typing import BinaryIO

from idugeoserverclient.models.datastore_model import DatastoreModel
from idugeoserverclient.models.layer_model import LayerModel


class IIduGeoserverClient(ABC):
    """
    Geoserver client instance with methods for uploading
    """

    @abstractmethod
    async def upload_layer(
            self,
            workspace_name: str, 
            file: BinaryIO,
            layer_type: str,
            created_at: str | datetime,
            replace_existing: bool = True,
            style_name: str | None = None,
            *args
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

        pass

    @abstractmethod
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

        pass

    @abstractmethod
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

        pass

    @abstractmethod
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

        pass

    @abstractmethod
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

        pass
