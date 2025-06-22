import logging
from io import BytesIO
from urllib.parse import ParseResult, parse_qs

from .base import Storage

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.client import Config

    class S3Storage(Storage):
        @classmethod
        def accept(cls, scheme):
            return scheme == "s3"

        def __init__(self, url: ParseResult) -> None:
            super().__init__(url)
            q = parse_qs(url.query)

            key, secret = q.get("access_key", [None])[0], q.get("secret", [None])[0]

            if key and secret:
                self.client = boto3.client(
                    "s3",
                    aws_access_key_id=key,
                    aws_secret_access_key=secret,
                    config=Config(signature_version="s3v4"),
                    region_name=url.netloc,
                )
                self.bucket = url.path.lstrip("/")
            else:
                self.client = boto3.client(
                    "s3",
                    region_name=url.netloc,
                )
                self.bucket = url.path.lstrip("/")

        def exists(self, path):
            contents = self.client.list_objects(
                Bucket=self.bucket,
            ).get("Contents", [])
            return any([c["Key"] == path for c in contents])

        def read(self, path):
            buf = BytesIO()
            self.client.download_fileobj(self.bucket, path, buf)
            return buf.getvalue()

        def write(self, path, data, public=False):
            buf = BytesIO(data)
            extra_args = {}
            
            if path.startswith("profile_pictures/") or public:
                extra_args['ACL'] = 'public-read'
                
            self.client.upload_fileobj(buf, self.bucket, path, ExtraArgs=extra_args)

        def delete(self, path):
            self.client.delete_object(
                Bucket=self.bucket,
                Key=path,
            )

        def urlize(self, path, expiration=3600, public=None, **kwargs):
            if path.startswith("profile_pictures/"):
                public = True
            elif public is None:
                public = False
                
            if public:
                return f"https://{self.bucket}.s3.amazonaws.com/{path}"
            else:
                return self.client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": path},
                    ExpiresIn=expiration,
                )

except Exception as e:
    logger.error(e)
