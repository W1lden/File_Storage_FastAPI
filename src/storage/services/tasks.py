from celery import Celery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.core.config import settings
from storage.core.db import async_session_maker
from storage.db.models.file import File
from storage.core.constants import CELERY_TASK_EXTRACT_METADATA, MIME_PDF, DOC_TYPES
from storage.services.metadata import extract_pdf_meta, extract_docx_meta
from storage.services.s3 import get_client
from minio.error import S3Error

celery_app = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

@celery_app.task(name=CELERY_TASK_EXTRACT_METADATA)
def extract_metadata_task(object_key: str, content_type: str):
    client = get_client()
    try:
        response = client.get_object(settings.MINIO_BUCKET_NAME, object_key)
        data = response.read()
        response.close()
        response.release_conn()
    except S3Error:
        return
    meta = {}
    if content_type == MIME_PDF:
        meta = extract_pdf_meta(data)
    elif content_type in DOC_TYPES:
        meta = extract_docx_meta(data)
    async def _save():
        async with async_session_maker() as session:
            q = await session.execute(select(File).where(File.object_key == object_key))
            file = q.scalar_one_or_none()
            if not file:
                return
            file.metadata_ = meta
            await session.commit()
    import asyncio
    asyncio.run(_save())
