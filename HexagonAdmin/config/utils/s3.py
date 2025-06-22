import os
import logging
from typing import Optional, List, Dict, Any, BinaryIO, Union
from datetime import datetime, timedelta
import mimetypes

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from django.conf import settings

logger = logging.getLogger(__name__)


class S3Client:
    """
    S3/MinIO client wrapper for CRUD operations with presigned URL support
    """

    def __init__(self):
        """Initialize S3 client with MinIO configuration"""
        self.endpoint_url = f"http://{getattr(settings, 'MINIO_ENDPOINT', 'minio:9000')}"
        self.access_key = getattr(settings, 'MINIO_ACCESS_KEY', '')
        self.secret_key = getattr(settings, 'MINIO_SECRET_KEY', '')
        self.bucket_name = getattr(settings, 'MINIO_BUCKET_NAME', 'hexagon-storage')
        self.use_https = getattr(settings, 'MINIO_USE_HTTPS', False)

        if self.use_https:
            self.endpoint_url = self.endpoint_url.replace('http://', 'https://')

        self.config = Config(
            region_name='us-east-1',
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            signature_version='s3v4'
        )

        try:
            self.client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=self.config
            )

            # Test connection
            self._test_connection()
            logger.info(f"S3 client initialized successfully - Endpoint: {self.endpoint_url}")

        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise

    def _test_connection(self):
        """Test S3 connection by listing buckets"""
        try:
            self.client.list_buckets()
        except Exception as e:
            logger.error(f"S3 connection test failed: {str(e)}")
            raise

    def _get_content_type(self, file_path: str) -> str:
        """Get content type based on file extension"""
        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'

    def _ensure_bucket_exists(self) -> bool:
        """Ensure bucket exists, create if not"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                    return True
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket {self.bucket_name}: {create_error}")
                    return False
            else:
                logger.error(f"Error accessing bucket {self.bucket_name}: {e}")
                return False

    def upload_file(
            self,
            file_obj: Union[BinaryIO, bytes, str],
            key: str,
            content_type: Optional[str] = None,
            metadata: Optional[Dict[str, str]] = None,
            public: bool = False
    ) -> Dict[str, Any]:
        """
        Upload file to S3/MinIO

        Args:
            file_obj: File object, bytes, or file path
            key: S3 object key (path)
            content_type: MIME type (auto-detected if None)
            metadata: Additional metadata
            public: Whether file should be publicly accessible

        Returns:
            Dictionary with upload result
        """
        try:
            if not self._ensure_bucket_exists():
                raise Exception(f"Bucket {self.bucket_name} not accessible")

            # Handle different file input types
            if isinstance(file_obj, str):
                # File path
                with open(file_obj, 'rb') as f:
                    file_data = f.read()
                if not content_type:
                    content_type = self._get_content_type(file_obj)
            elif hasattr(file_obj, 'read'):
                # File-like object
                file_data = file_obj.read()
                if hasattr(file_obj, 'name') and not content_type:
                    content_type = self._get_content_type(file_obj.name)
            else:
                # Bytes
                file_data = file_obj

            if not content_type:
                content_type = 'application/octet-stream'

            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': key,
                'Body': file_data,
                'ContentType': content_type,
            }

            if metadata:
                upload_params['Metadata'] = metadata

            if public:
                upload_params['ACL'] = 'public-read'

            self.client.put_object(**upload_params)

            public_url = None
            if public:
                public_url = f"{self.endpoint_url}/{self.bucket_name}/{key}"

            result = {
                'success': True,
                'key': key,
                'bucket': self.bucket_name,
                'size': len(file_data),
                'content_type': content_type,
                'public_url': public_url,
                'uploaded_at': datetime.now().isoformat()
            }

            logger.info(f"File uploaded successfully: {key}")
            return result

        except Exception as e:
            logger.error(f"Failed to upload file {key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'key': key
            }

    def download_file(self, key: str, local_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Download file from S3/MinIO

        Args:
            key: S3 object key
            local_path: Local file path to save (optional)

        Returns:
            Dictionary with download result
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=key)
            file_data = response['Body'].read()

            result = {
                'success': True,
                'key': key,
                'data': file_data,
                'size': len(file_data),
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified', ''),
                'metadata': response.get('Metadata', {})
            }

            if local_path:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                result['local_path'] = local_path

            logger.info(f"File downloaded successfully: {key}")
            return result

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.warning(f"File not found: {key}")
                return {
                    'success': False,
                    'error': 'File not found',
                    'key': key
                }
            else:
                logger.error(f"Failed to download file {key}: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'key': key
                }
        except Exception as e:
            logger.error(f"Failed to download file {key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'key': key
            }

    def delete_file(self, key: str) -> Dict[str, Any]:
        """
        Delete file from S3/MinIO

        Args:
            key: S3 object key

        Returns:
            Dictionary with delete result
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)

            logger.info(f"File deleted successfully: {key}")
            return {
                'success': True,
                'key': key,
                'deleted_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to delete file {key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'key': key
            }

    def list_files(
            self,
            prefix: str = '',
            limit: Optional[int] = None,
            recursive: bool = True
    ) -> Dict[str, Any]:
        """
        List files in S3/MinIO bucket

        Args:
            prefix: Key prefix to filter
            limit: Maximum number of files to return
            recursive: Include subdirectories

        Returns:
            Dictionary with list result
        """
        try:
            paginator = self.client.get_paginator('list_objects_v2')

            page_params = {
                'Bucket': self.bucket_name,
                'Prefix': prefix
            }

            if not recursive:
                page_params['Delimiter'] = '/'

            if limit:
                page_params['MaxKeys'] = limit

            files = []
            total_size = 0

            for page in paginator.paginate(**page_params):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_info = {
                            'key': obj['Key'],
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].isoformat(),
                            'etag': obj['ETag'].strip('"')
                        }
                        files.append(file_info)
                        total_size += obj['Size']

                        if limit and len(files) >= limit:
                            break

                if limit and len(files) >= limit:
                    break

            return {
                'success': True,
                'files': files,
                'count': len(files),
                'total_size': total_size,
                'prefix': prefix
            }

        except Exception as e:
            logger.error(f"Failed to list files with prefix {prefix}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prefix': prefix
            }

    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in S3/MinIO

        Args:
            key: S3 object key

        Returns:
            Boolean indicating file existence
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking file existence {key}: {str(e)}")
                return False

    def get_file_info(self, key: str) -> Dict[str, Any]:
        """
        Get file metadata without downloading content

        Args:
            key: S3 object key

        Returns:
            Dictionary with file info
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=key)

            return {
                'success': True,
                'key': key,
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {})
            }

        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {
                    'success': False,
                    'error': 'File not found',
                    'key': key
                }
            else:
                logger.error(f"Failed to get file info {key}: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'key': key
                }

    def generate_presigned_url(
            self,
            key: str,
            expiration: Optional[int] = 3600,
            method: str = 'GET'
    ) -> Dict[str, Any]:
        """
        Generate presigned URL for file access

        Args:
            key: S3 object key
            expiration: URL expiration in seconds (None for no expiration, 3600 = 1 hour)
            method: HTTP method (GET, PUT, DELETE)

        Returns:
            Dictionary with presigned URL result
        """
        try:
            if expiration is None:
                public_url = f"{self.endpoint_url}/{self.bucket_name}/{key}"
                return {
                    'success': True,
                    'url': public_url,
                    'key': key,
                    'expires_at': None,
                    'method': method
                }

            # Generate presigned URL with expiration
            if method.upper() == 'GET':
                operation = 'get_object'
            elif method.upper() == 'PUT':
                operation = 'put_object'
            elif method.upper() == 'DELETE':
                operation = 'delete_object'
            else:
                raise ValueError(f"Unsupported method: {method}")

            presigned_url = self.client.generate_presigned_url(
                operation,
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )

            expires_at = datetime.now() + timedelta(seconds=expiration)

            return {
                'success': True,
                'url': presigned_url,
                'key': key,
                'expires_at': expires_at.isoformat(),
                'expiration_seconds': expiration,
                'method': method
            }

        except Exception as e:
            logger.error(f"Failed to generate presigned URL for {key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'key': key
            }

    def copy_file(self, source_key: str, dest_key: str) -> Dict[str, Any]:
        """
        Copy file within the same bucket

        Args:
            source_key: Source object key
            dest_key: Destination object key

        Returns:
            Dictionary with copy result
        """
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }

            self.client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=dest_key
            )

            logger.info(f"File copied successfully: {source_key} -> {dest_key}")
            return {
                'success': True,
                'source_key': source_key,
                'dest_key': dest_key,
                'copied_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to copy file {source_key} -> {dest_key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'source_key': source_key,
                'dest_key': dest_key
            }

    def move_file(self, source_key: str, dest_key: str) -> Dict[str, Any]:
        """
        Move file (copy + delete original)

        Args:
            source_key: Source object key
            dest_key: Destination object key

        Returns:
            Dictionary with move result
        """
        try:
            copy_result = self.copy_file(source_key, dest_key)
            if not copy_result['success']:
                return copy_result

            delete_result = self.delete_file(source_key)
            if not delete_result['success']:
                self.delete_file(dest_key)
                return delete_result

            logger.info(f"File moved successfully: {source_key} -> {dest_key}")
            return {
                'success': True,
                'source_key': source_key,
                'dest_key': dest_key,
                'moved_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to move file {source_key} -> {dest_key}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'source_key': source_key,
                'dest_key': dest_key
            }

_s3_client = None


def get_s3_client() -> S3Client:
    global _s3_client
    if _s3_client is None:
        _s3_client = S3Client()
    return _s3_client


def upload_file(*args, **kwargs):
    return get_s3_client().upload_file(*args, **kwargs)


def download_file(*args, **kwargs):
    return get_s3_client().download_file(*args, **kwargs)


def delete_file(*args, **kwargs):
    return get_s3_client().delete_file(*args, **kwargs)


def list_files(*args, **kwargs):
    return get_s3_client().list_files(*args, **kwargs)


def file_exists(*args, **kwargs):
    return get_s3_client().file_exists(*args, **kwargs)


def get_file_info(*args, **kwargs):
    return get_s3_client().get_file_info(*args, **kwargs)


def generate_presigned_url(*args, **kwargs):
    return get_s3_client().generate_presigned_url(*args, **kwargs)


def copy_file(*args, **kwargs):
    return get_s3_client().copy_file(*args, **kwargs)


def move_file(*args, **kwargs):
    return get_s3_client().move_file(*args, **kwargs)