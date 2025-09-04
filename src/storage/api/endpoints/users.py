from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from storage.api.schemas.user import UserOut
from storage.core.db import get_session
from storage.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return {"id": 1, "email": "user@example.com", "role": "USER", "department_id": 1, "is_active": True}


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return {"id": user_id, "email": "user@example.com", "role": "USER", "department_id": 1, "is_active": True}


@router.put("/{user_id}/role", response_model=UserOut)
async def update_user_role(
    user_id: int,
    new_role: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return {"id": user_id, "email": "user@example.com", "role": new_role, "department_id": 1, "is_active": True}


@router.get("/", response_model=list[UserOut])
async def list_department_users(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return [{"id": 1, "email": "user@example.com", "role": "USER", "department_id": 1, "is_active": True}]
