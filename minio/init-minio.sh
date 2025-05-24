#!/bin/sh
set -e

sleep 5

mc alias set myminio http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

if ! mc ls myminio | grep -q "$BUCKET_NAME"; then
    mc mb myminio/"$BUCKET_NAME"
    echo "Bucket $BUCKET_NAME created"
else
    echo "Bucket $BUCKET_NAME already exists"
fi

mc policy set download myminio/"$BUCKET_NAME"/public

mc mb -p myminio/"$BUCKET_NAME"/public/courses
mc mb -p myminio/"$BUCKET_NAME"/public/news
mc mb -p myminio/"$BUCKET_NAME"/public/students
mc mb -p myminio/"$BUCKET_NAME"/public/banners
mc mb -p myminio/"$BUCKET_NAME"/private/materials
mc mb -p myminio/"$BUCKET_NAME"/private/documents

echo "MinIO initialized successfully"