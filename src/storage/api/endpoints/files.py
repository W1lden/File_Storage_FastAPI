from typing import Literal, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from storage.core.db import get_session
from storage.core.security import get_current_user

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    visibility: Literal["PRIVATE", "DEPARTMENT", "PUBLIC"] = Form(...),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return {"id": 1, "filename": file.filename, "visibility": visibility}


@router.get("/{file_id}")
async def get_file_info(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return {"id": file_id, "filename": "example.pdf", "visibility": "PRIVATE", "owner_id": current_user.id}


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return {"download_url": f"/internal/download/{file_id}"}


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return


@router.get("/")
async def list_files(
    department_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return [{"id": 1, "filename": "example.pdf", "visibility": "PUBLIC"}]
