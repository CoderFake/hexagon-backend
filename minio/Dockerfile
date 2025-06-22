FROM python:3.11-alpine

RUN pip install --no-cache-dir minio

COPY init-minio.py /init-minio.py

RUN chmod +x /init-minio.py

WORKDIR /

CMD ["python3", "/init-minio.py"]