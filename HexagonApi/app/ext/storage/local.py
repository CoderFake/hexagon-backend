import os
import os.path
from urllib.parse import urljoin, ParseResult
from .base import StorageSettings, Storage


class LocalStorage(Storage):
    """
    Storage class that represents a local file.

    Corresponds to URLs with an empty scheme or `file`.
    """
    @classmethod
    def accept(cls, scheme: str):
        return scheme == '' or scheme == 'file'

    def __init__(self, url: ParseResult) -> None:
        """Initializes from URL components."""
        super().__init__(url)
        self.root = url.path

    def _on(self, path: str) -> str:
        return os.path.join(self.root, path)

    def exists(self, path: str):
        return os.path.exists(self._on(path))

    def read(self, path: str) -> bytes:
        path = self._on(path)
        with open(path, 'rb') as f:
            return f.read()

    def write(self, path: str, data: bytes) -> int:
        path = self._on(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            return f.write(data)

    def delete(self, path: str):
        os.remove(self._on(path))

    def urlize(self, path: str, root: str, **kwargs) -> str:
        return urljoin(root, path)
