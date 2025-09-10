import secrets
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi import File as FileUpload
from fastapi import Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.background import BackgroundTask

from storage.core.config import settings
from storage.core.constants import (BYTES_IN_MB, DOWNLOADS_INCREMENT,
                                    ERR_FILE_TOO_LARGE, ERR_FORBIDDEN,
                                    ERR_NOT_FOUND, ERR_TYPE_NOT_ALLOWED,
                                    ERR_VISIBILITY_NOT_ALLOWED,
                                    OBJECT_KEY_RANDOM_BYTES,
                                    ROLE_ALLOWED_TYPES,
                                    ROLE_ALLOWED_VISIBILITY, ROLE_MAX_SIZE_MB,
                                    STREAM_CHUNK_SIZE, Role, Visibility)
from storage.core.db import get_session
from storage.core.security import get_current_user
from storage.db.models.file import File, FileVisibility
from storage.db.models.user import User
from storage.services.s3 import ensure_bucket, get_client
from storage.services.tasks import extract_metadata_task

router = APIRouter()


def _role_from_user(user: User) -> Role:
    return Role(user.role.value)


def _visibility_enum(v: Visibility) -> FileVisibility:
    return FileVisibility(v.value)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    visibility: Visibility = Form(...),
    file: UploadFile = FileUpload(...),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Загрузка файла в хранилище с учётом роли и уровня видимости.

    Принимает multipart/form-data: файл и значение видимости.
    Проверяет ограничения роли по типу и размеру, сохраняет в S3,
    создаёт запись в БД и запускает задачу извлечения метаданных.
    """
    role = _role_from_user(current_user)
    if visibility not in ROLE_ALLOWED_VISIBILITY[role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERR_VISIBILITY_NOT_ALLOWED,
        )
    if file.content_type not in ROLE_ALLOWED_TYPES[role]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=ERR_TYPE_NOT_ALLOWED,
        )
    max_bytes = ROLE_MAX_SIZE_MB[role] * BYTES_IN_MB
    chunk = await file.read()
    if len(chunk) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=ERR_FILE_TOO_LARGE,
        )
    object_key = f"{current_user.id}/{secrets.token_urlsafe(OBJECT_KEY_RANDOM_BYTES)}_{file.filename}" # noqa
    ensure_bucket()
    client = get_client()
    data_stream = BytesIO(chunk)
    client.put_object(
        bucket_name=settings.MINIO_BUCKET_NAME,
        object_name=object_key,
        data=data_stream,
        length=len(chunk),
        content_type=file.content_type,
    )
    db_file = File(
        filename=file.filename,
        object_key=object_key,
        owner_id=current_user.id,
        visibility=_visibility_enum(visibility),
        metadata_=None,
        downloads_count=0,
    )
    session.add(db_file)
    await session.commit()
    await session.refresh(db_file)
    extract_metadata_task.delay(object_key, file.content_type)
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "visibility": db_file.visibility.value,
        "object_key": db_file.object_key,
    }


@router.get("/{file_id}")
async def get_file_info(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Получение информации о файле по ID.

    Возвращает базовые сведения и извлечённые метаданные.
    Применяются проверки доступа по видимости и ролям.
    """
    q = await session.execute(
        select(File)
        .options(selectinload(File.owner))
        .where(File.id == file_id)
    )
    f = q.scalar_one_or_none()
    if not f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND
        )
    role = _role_from_user(current_user)
    if (
        f.visibility == FileVisibility.PRIVATE
        and f.owner_id != current_user.id
        and role != Role.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN
        )
    if f.visibility == FileVisibility.DEPARTMENT:
        if role == Role.USER and (
            not f.owner or f.owner.department_id != current_user.department_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN
            )
    return {
        "id": f.id,
        "filename": f.filename,
        "visibility": f.visibility.value,
        "metadata": f.metadata_,
        "downloads_count": f.downloads_count,
    }


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Скачивание файла по ID со стримингом и проверкой прав доступа.

    Увеличивает счётчик скачиваний и возвращает поток ответа
    с корректными заголовками для загрузки.
    """
    q = await session.execute(
        select(File)
        .options(selectinload(File.owner))
        .where(File.id == file_id)
    )
    f = q.scalar_one_or_none()
    if not f:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND
        )
    role = _role_from_user(current_user)
    if (
        f.visibility == FileVisibility.PRIVATE
        and f.owner_id != current_user.id
        and role != Role.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN
        )
    if f.visibility == FileVisibility.DEPARTMENT:
        if role == Role.USER and (
            not f.owner or f.owner.department_id != current_user.department_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN
            )
    client = get_client()
    obj = client.get_object(settings.MINIO_BUCKET_NAME, f.object_key)

    def _iter():
        try:
            for chunk in obj.stream(STREAM_CHUNK_SIZE):
                yield chunk
        finally:
            obj.close()
            obj.release_conn()

    f.downloads_count += DOWNLOADS_INCREMENT
    await session.commit()
    return StreamingResponse(
        _iter(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{f.filename}"'
        },
        background=BackgroundTask(lambda: None),
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Удаление файла по ID с учётом прав доступа.

    Пользователь может удалять только свои файлы.
    Менеджер может удалять файлы своего отдела.
    Администратор может удалять любые файлы.
    """
    q = await session.execute(select(File).where(File.id == file_id))
    f = q.scalar_one_or_none()
    if not f:
        return
    role = _role_from_user(current_user)
    if role == Role.USER and f.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN
        )
    if (
        role == Role.MANAGER
        and getattr(f, "owner", None)
        and getattr(f.owner, "department_id", None)
        != current_user.department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN
        )
    client = get_client()
    client.remove_object(settings.MINIO_BUCKET_NAME, f.object_key)
    await session.delete(f)
    await session.commit()
    return


@router.get("/")
async def list_files(
    department_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """
    Список доступных пользователю файлов.

    Учитывает роль и уровень видимости.
    Для MANAGER/ADMIN поддерживается фильтрация по department_id.
    """
    role = _role_from_user(current_user)
    base = (
        select(File)
        .join(User, File.owner_id == User.id)
        .options(selectinload(File.owner))
    )

    if role == Role.ADMIN:
        q = base
    elif role == Role.MANAGER:
        q = base.where(
            or_(
                File.visibility == FileVisibility.PUBLIC,
                File.visibility == FileVisibility.DEPARTMENT,
                and_(
                    File.visibility == FileVisibility.PRIVATE,
                    File.owner_id == current_user.id,
                ),
            )
        )
    else:
        q = base.where(
            or_(
                File.visibility == FileVisibility.PUBLIC,
                and_(
                    File.visibility == FileVisibility.DEPARTMENT,
                    User.department_id == current_user.department_id,
                ),
                and_(
                    File.visibility == FileVisibility.PRIVATE,
                    File.owner_id == current_user.id,
                ),
            )
        )

    if department_id is not None and role in {Role.MANAGER, Role.ADMIN}:
        q = q.where(User.department_id == department_id)

    rows = (await session.execute(q)).scalars().all()
    return [
        {"id": x.id, "filename": x.filename, "visibility": x.visibility.value}
        for x in rows
    ]
