#!/bin/bash
set -e

echo "Starting Hexagon Admin..."

# Function to wait for database
wait_for_db() {
    echo "Waiting for database..."
    while ! pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U ${DB_USER:-postgres} -d ${DB_NAME:-hexagon_db}; do
        echo "Database not ready - waiting 3 seconds..."
        sleep 3
    done
    echo "Database is ready!"
}

# Function to wait for MinIO
wait_for_minio() {
    echo "Waiting for MinIO..."
    while ! curl -f http://${MINIO_ENDPOINT:-minio:9000}/minio/health/live > /dev/null 2>&1; do
        echo "MinIO not ready - waiting 3 seconds..."
        sleep 3
    done
    echo "MinIO is ready!"
}

# Wait for services
wait_for_db
wait_for_minio

echo "Making migrations..."
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser and configuring site..."
python create_superuser_and_site.py

echo "Starting server..."
if [ "${ENV:-dev}" = "dev" ]; then
    echo "Development mode"
    python manage.py runserver 0.0.0.0:8000
else
    echo "Production mode"
    gunicorn HexagonAdmin.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 120 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --preload \
        --access-logfile - \
        --error-logfile -
fi