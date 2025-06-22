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
        """
        Generate public URL for storage files
        
        Args:
            path: Storage file path
        Returns:
            Public URL for the file
        """
        from app.config import environment
        from app.resources import context as r

        storage_url = environment().settings.storage.url
        parsed_url = urlparse(storage_url)
        
        if parsed_url.scheme == "s3":
            try:
                return r.storage.urlize(path, public=True)
            except:
                bucket = parsed_url.path.lstrip("/")
                return f"https://{bucket}.s3.amazonaws.com/{path}"
                
        elif parsed_url.scheme == "minio":
            try:
                return r.storage.urlize(path)
            except:
                endpoint = parsed_url.netloc
                bucket = parsed_url.path.lstrip("/")
                protocol = "https" if parsed_url.query and "secure=true" in parsed_url.query else "http"
                return f"{protocol}://{endpoint}/{bucket}/{path}"
                
        elif parsed_url.scheme == "file":
            static = environment().settings.static
            if static:
                static_path = static.path.rstrip("/")
                return self(f"{static_path}/{path}")
            else:
                return self(f"static/{path}")
                
        else:
            try:
                return r.storage.urlize(path)
            except:
                return self(f"static/{path}")
