from typing import Self, Protocol


class FileLike(Protocol):
    """Interface to be implemented by storage systems like a asynchronous file"""

    async def __aenter__(self) -> Self:
        """Context manager"""
        ...

    async def __aexit__(self, exc_type, exc, tb):
        """Context manager"""
        ...

    async def read(self, size: int = -1) -> bytes:
        """Read content of file"""
        ...

    async def write(self, b: bytes):
        """Write bytes to the file"""
        ...

    # async def close(self):
    #     """Close file"""

    # async def open(self):
    #     """Open the file"""

    # async def seekable(self) -> bool:
    #     return True

    # close
    # flush
    # isatty
    # read
    # readall
    # read1
    # readinto
    # seek
    # seekable
    # tell
    # truncate
    # writable
    # write
    # writelines
    # readline
    # readlines


class FileLikeSystem(Protocol):
    def open(self, filename: str, mode: str) -> FileLike:
        """Create a FileLike ready to be used"""
        ...

    @property
    def template(self) -> str:
        """Template to generate full filenames"""
        ...

    @template.setter
    def template(self, value: str):
        """The template should be set by the client"""
        ...

    async def rm(self, pattern: str):
        """Remove file-like object"""
        ...

    async def ls(self, pattern: str = "*") -> list[str]:
        """List all filenames of system with simple pattern (* and ?)"""
        ...
