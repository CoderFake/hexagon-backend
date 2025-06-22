from typing import Type, Optional
from urllib.parse import urlparse, ParseResult
from pydantic import BaseModel, Field
import os


class StorageSettings(BaseModel):
    url: str = Field(default="file://./uploads", description="URL with storage access information.")


class Storage:
    """
    File storage abstract base class.
    """
    _children: set[Type] = set()

    def __init_subclass__(cls) -> None:
        Storage._children.add(cls)

    @staticmethod
    def of(url) -> Optional['Storage']:
        """
        Generates an instance of the appropriate type determined from the URL scheme.

        Args:
            url: URL containing access information.
        Returns:
            Storage access object.
        """
        parsed = urlparse(url)
        s = next(filter(lambda s: s.accept(parsed.scheme), Storage._children), None)
        return s(parsed) if s else None

    @classmethod
    def accept(cls, scheme: str) -> bool:
        """
        Checks if the specified scheme corresponds to its own type.

        Args:
            scheme: URL scheme.
        Returns:
            Whether it corresponds to its own type.
        """
        raise NotImplementedError()

    def __init__(self, url: ParseResult) -> None:
        """
        Initializes from URL components.

        Args:
            url: URL components.
        """
        pass

    def exists(self, path: str) -> bool:
        """
        Checks if a file exists at the specified path.

        Args:
            path: File path.
        Returns:
            Whether the file exists.
        """
        raise NotImplementedError()

    def read(self, path: str) -> bytes:
        """
        Reads the contents of the specified file.

        Args:
            path: File path.
        Returns:
            File data.
        """
        raise NotImplementedError()

    def write(self, path: str, data: bytes):
        """
        Writes the contents of the specified file.

        Args:
            path: File path.
            data: File data.
        """
        raise NotImplementedError()

    def delete(self, path: str):
        """
        Deletes the specified file.

        Args:
            path: File path.
        """
        raise NotImplementedError()

    def urlize(self, path: str, **kwargs) -> str:
        """
        Generates a URL that can access the specified file.

        Args:
            path: File path.
        """
        raise NotImplementedError()
