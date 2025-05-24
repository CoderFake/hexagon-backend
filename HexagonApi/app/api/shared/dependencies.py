from urllib.parse import urlparse

from app.ext.storage.s3 import S3Storage
from fastapi import Header, Request


class URLFor:
    """
    Dependency class for reconstructing client-facing URLs from requests.
    """

    def __init__(
        self,
        request: Request,
        x_script_name: str | None = Header(default=None, include_in_schema=False),
        x_forwarded_proto: str | None = Header(default=None, include_in_schema=False),
    ) -> None:
        self.request = request
        self.script = x_script_name
        self.proto = x_forwarded_proto

    def __call__(self, path: str) -> str:
        scheme = self.proto or self.request.url.scheme
        netloc = self.request.url.netloc
        script = f"{self.script}/" if self.script else ""

        return f"{scheme}://{netloc}/{script}/{path}"

    def storage(self, path: str) -> str:
        from app.config import environment
        from app.resources import context as r

        static = environment().settings.static
        storage_url = environment().settings.storage.url

        if storage_url.startswith("s3://"):
            s3_url = environment().settings.storage.url
            parsed_url = urlparse(s3_url)
            s3_storage = S3Storage(parsed_url)

            return s3_storage.urlize(path)
        else:
            if static:
                static_path = static.path + "/"
            else:
                static_path = "/"

            return r.storage.urlize(path, root=self(static_path))
