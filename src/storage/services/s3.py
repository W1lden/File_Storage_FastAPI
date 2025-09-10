from minio import Minio

from storage.core.config import settings

_client_internal = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=False,
)


def get_client() -> Minio:
    return _client_internal


def ensure_bucket() -> None:
    client = get_client()
    if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
        client.make_bucket(settings.MINIO_BUCKET_NAME)
