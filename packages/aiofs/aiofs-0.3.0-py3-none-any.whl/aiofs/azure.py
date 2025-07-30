"""Implementation of FileLike with azure blobs"""
import fnmatch
from dataclasses import dataclass
from typing import Self

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobServiceClient as SyncBlobServiceClient
from azure.storage.blob.aio import BlobServiceClient

from . import FileLike, FileLikeSystem


@dataclass
class AzureContainerConfig:
    connection_string: str
    primary_key: str
    container_name: str


class BlobFileLike(FileLike):
    """Implementation of FileLike in azure blobs"""

    def __init__(self, blob: BlobServiceClient, mode: str = "r"):
        self._blob = blob
        self._lease = None
        self._content = b""
        self._mode = mode
        self._lease = None
        self._context = None

    async def __aenter__(self) -> Self:
        self._context = self._blob = await self._blob.__aenter__()
        if "w" in self._mode or "r+" in self._mode:
            try:
                self._lease = await self._blob.acquire_lease(15)
            except ResourceNotFoundError:
                ...
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._blob.__aexit__(exc_type, exc, tb)

        try:
            if self._content:
                await self._blob.upload_blob(
                    self._content, overwrite=True, lease=self._lease
                )
        except ResourceExistsError:
            raise BlockingIOError(f"")
        finally:
            if self._lease:
                await self._lease.release()

    async def read(self, size: int = -1) -> bytes:
        if not self._context:
            raise RuntimeError('Call to "read" out of context')
        if size >= 0:
            raise NotImplementedError("Not designed to donwload partially")

        try:
            stream = await self._blob.download_blob()
        except ResourceNotFoundError:
            raise FileNotFoundError(f"Not found {self._blob.blob_name}")
        return await stream.readall()

    async def write(self, b: bytes):
        if not self._context:
            raise RuntimeError('Call to "write" out of context')
        self._content += b


class BlobFileSystem(FileLikeSystem):
    """Create and manage BlobFileLike"""

    def __init__(
        self,
        config: AzureContainerConfig,
        template: str = "{}",
    ):
        connection_string = config.connection_string.format(config.primary_key)
        self._assert_container_exist(connection_string, config.container_name)
        self._service = BlobServiceClient.from_connection_string(connection_string)
        self._container = self._service.get_container_client(config.container_name)

        self._template = template

    def _assert_container_exist(self, connection_string, container_name):
        with SyncBlobServiceClient.from_connection_string(connection_string) as service:
            if not service.get_container_client(container_name).exists():
                service.create_container(container_name)

    @property
    def template(self) -> str:
        """Template to generate the full filename"""
        return self._template

    @template.setter
    def template(self, value: str):
        """Change template for locating the files"""
        self._template = value

    def open(self, filename: str, mode="r") -> BlobFileLike:
        blob_name = self._template.format(filename)
        blob = self._container.get_blob_client(blob_name)

        return BlobFileLike(blob, mode)

    async def rm(self, pattern: str):
        filenames = await self.ls(pattern)
        for fn in filenames:
            blob_name = self._template.format(fn)
            blob = self._container.get_blob_client(blob_name)
            try:
                await blob.delete_blob()
            except ResourceNotFoundError:
                pass

    async def close(self):
        if self._container:
            await self._container.close()
        await self._service.close()

    async def ls(self, pattern: str = "*"):
        """List all filenames of the system"""
        prefix, _, sufix = self._template.partition("{}")
        names = []
        prefix = prefix if prefix else None
        pre = 0 if prefix is None else len(prefix)
        suf = -len(sufix) if sufix else None
        async for blob in self._container.list_blobs(prefix):
            if blob.name.endswith(sufix):
                names.append(blob.name[pre:suf])
        return fnmatch.filter(names, pattern)
