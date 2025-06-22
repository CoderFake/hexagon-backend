import logging
from io import BytesIO
from urllib.parse import ParseResult, parse_qs
from datetime import timedelta

from .base import Storage

logger = logging.getLogger(__name__)

try:
    from minio import Minio
    from minio.error import S3Error

    class MinioStorage(Storage):
        @classmethod
        def accept(cls, scheme):
            return scheme == "minio"

        def __init__(self, url: ParseResult, public_url: str = None) -> None:
            super().__init__(url)
            q = parse_qs(url.query)

            self.endpoint = url.netloc
            self.bucket_name = url.path.lstrip("/")
            self.public_url = public_url 
            
            access_key = q.get("access_key", [None])[0]
            secret_key = q.get("secret_key", [None])[0]
            self.secure = q.get("secure", ["true"])[0].lower() == "true"

            if not access_key or not secret_key:
                raise ValueError("Minio storage requires access_key and secret_key in URL query parameters")

            self.client = Minio(
                endpoint=self.endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=self.secure
            )

            self._ensure_bucket_exists()

        def _ensure_bucket_exists(self):
            """Ensure the bucket exists, create if it doesn't"""
            try:
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    logger.info(f"Created Minio bucket: {self.bucket_name}")
            except S3Error as e:
                logger.error(f"Error ensuring bucket exists: {e}")
                raise

        def exists(self, path: str) -> bool:
            """Check if object exists in Minio"""
            try:
                self.client.stat_object(self.bucket_name, path)
                return True
            except S3Error:
                return False

        def read(self, path: str) -> bytes:
            """Read object from Minio"""
            try:
                response = self.client.get_object(self.bucket_name, path)
                data = response.read()
                response.close()
                response.release_conn()
                return data
            except S3Error as e:
                logger.error(f"Error reading object {path}: {e}")
                raise

        def write(self, path: str, data: bytes, content_type: str = None):
            """Write object to Minio"""
            try:
                data_stream = BytesIO(data)
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=path,
                    data=data_stream,
                    length=len(data),
                    content_type=content_type or "application/octet-stream"
                )
                logger.debug(f"Successfully uploaded object: {path}")
            except S3Error as e:
                logger.error(f"Error writing object {path}: {e}")
                raise

        def delete(self, path: str):
            """Delete object from Minio"""
            try:
                self.client.remove_object(self.bucket_name, path)
                logger.debug(f"Successfully deleted object: {path}")
            except S3Error as e:
                logger.error(f"Error deleting object {path}: {e}")
                raise

        def urlize(self, path: str, expiration: int = None, **kwargs) -> str:
            """Generate URL for object access"""
            try:
                if path.startswith("profile_pictures/"):
                    return self.get_public_url(path)
                
                if expiration is None:
                    expiration = 3600
                    
                url = self.client.presigned_get_object(
                    bucket_name=self.bucket_name,
                    object_name=path,
                    expires=timedelta(seconds=expiration)
                )
                return url
            except S3Error as e:
                logger.error(f"Error generating URL for {path}: {e}")
                raise

        def get_public_url(self, path: str) -> str:
            """Get public URL for object (if bucket is public)"""
            if self.public_url:
                return f"{self.public_url.rstrip('/')}/{self.bucket_name}/{path}"
            else:
                protocol = "https" if self.secure else "http"
                return f"{protocol}://{self.endpoint}/{self.bucket_name}/{path}"

except ImportError as e:
    logger.error(f"Minio library not available: {e}")
    logger.info("Install minio with: pip install minio")

except Exception as e:
    logger.error(f"Error initializing Minio storage: {e}") 