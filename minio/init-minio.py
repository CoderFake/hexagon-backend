#!/usr/bin/env python3
import os
import time
from io import BytesIO
from minio import Minio
from minio.error import S3Error
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_bucket(client, bucket_name):
    """Create bucket if not exists"""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            logger.info(f"✅ Bucket '{bucket_name}' created successfully")
        else:
            logger.info(f"ℹ️  Bucket '{bucket_name}' already exists")
        return True
    except S3Error as err:
        logger.error(f"❌ Error creating bucket '{bucket_name}': {err}")
        return False


def create_folder_structure(client, bucket_name):
    """Create folder structure by uploading .keep files"""
    folders = [
        # Public folders - accessible without login
        "public/courses",  # Course images, class images
        "public/news",  # News images and content blocks
        "public/banners",  # Website banners
        "public/about",  # About section images
        "public/roadmaps",  # Roadmap images
        "public/students",  # Student profile pics, outstanding students
        "public/materials",  # Public course materials (brochures, samples, previews)
        
        # User content - public access
        "profile_pictures",  # User profile pictures - public access for display

        # Private folders - require authentication
        "private/documents",  # Private course documents
        "private/materials",  # Premium course materials for enrolled students
        "private/student-files",  # Student submitted files, assignments
    ]

    logger.info("📁 Creating folder structure...")

    for folder in folders:
        try:
            keep_file_path = f"{folder}/.keep"
            empty_data = BytesIO(b"")

            client.put_object(
                bucket_name,
                keep_file_path,
                data=empty_data,
                length=0,
                content_type="text/plain"
            )
            logger.info(f"  ✅ Created folder: {folder}")
        except S3Error as err:
            logger.error(f"  ❌ Failed to create folder {folder}: {err}")
        except Exception as err:
            logger.error(f"  ❌ Unexpected error creating folder {folder}: {err}")


def set_bucket_policy(client, bucket_name):
    """Set bucket policy for public access to public folder and profile pictures"""
    try:
        policy = f'''{{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Effect": "Allow",
                    "Principal": {{
                        "AWS": ["*"]
                    }},
                    "Action": ["s3:GetObject"],
                    "Resource": [
                        "arn:aws:s3:::{bucket_name}/public/*",
                        "arn:aws:s3:::{bucket_name}/profile_pictures/*"
                    ]
                }}
            ]
        }}'''

        client.set_bucket_policy(bucket_name, policy)
        logger.info(f"✅ Set public access policy for {bucket_name}/public/*")
        return True
    except S3Error as err:
        logger.error(f"❌ Failed to set bucket policy: {err}")
        return False


def wait_for_minio(client, max_retries=30, delay=2):
    """Wait for MinIO to be ready"""
    logger.info("⏳ Waiting for MinIO to be ready...")

    for attempt in range(max_retries):
        try:
            client.list_buckets()
            logger.info("✅ MinIO is ready!")
            return True
        except Exception as e:
            logger.warning(f"  Attempt {attempt + 1}/{max_retries}: MinIO not ready yet ({e})")
            time.sleep(delay)

    logger.error("❌ MinIO failed to become ready after maximum retries")
    return False


def main():
    logger.info("🚀 Initializing MinIO for Hexagon Education...")

    minio_host = os.environ.get('MINIO_HOST', 'minio')
    minio_port = os.environ.get('MINIO_PORT', '9000')
    minio_access_key = os.environ.get('MINIO_ACCESS_KEY', 'hexagon')
    minio_secret_key = os.environ.get('MINIO_SECRET_KEY', 'hexagon123')
    bucket_name = os.environ.get('MINIO_BUCKET_NAME', 'hexagon-storage')

    try:
        client = Minio(
            f"{minio_host}:{minio_port}",
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )

        if not wait_for_minio(client):
            return 1

        logger.info(f"🔗 Connected successfully to MinIO Server at {minio_host}:{minio_port}")

        if not create_bucket(client, bucket_name):
            return 1

        create_folder_structure(client, bucket_name)
        set_bucket_policy(client, bucket_name)

        logger.info("\n📋 Final bucket structure:")
        try:
            objects = client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                logger.info(f"  📄 {obj.object_name}")
        except Exception as e:
            logger.info(f"  ℹ️  Cannot list objects: {e}")

        logger.info("\n🎉 MinIO initialization completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Error connecting to MinIO: {e}")
        return 1


if __name__ == "__main__":
    exit(main())