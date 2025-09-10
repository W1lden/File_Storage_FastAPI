from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.api.schemas.user import UserOut, UserCreate, UpdateUserRole
from storage.core.db import get_session
from storage.core.security import get_current_user, get_password_hash
from storage.db.models.user import User, UserRole
from storage.core.constants import ERR_FORBIDDEN, ERR_NOT_FOUND, EMAIL_ALREADY_EXISTS


router = APIRouter()


def _is_admin(u: User) -> bool:
    """
    Проверка, является ли пользователь администратором.
    """
    return u.role == UserRole.ADMIN


def _is_manager(u: User) -> bool:
    """
    Проверка, является ли пользователь менеджером.
    """
    return u.role == UserRole.MANAGER


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """
    Создание пользователя.

    Доступно ADMIN и MANAGER.
    MANAGER может создавать только в своём отделе и не может назначать роль ADMIN.
    """
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
    q = await session.execute(select(User).where(User.email == payload.email))
    exists = q.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=EMAIL_ALREADY_EXISTS)
    role = payload.role or UserRole.USER
    department_id = payload.department_id if payload.department_id is not None else current_user.department_id
    if _is_manager(current_user):
        if role == UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
        department_id = current_user.department_id
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=role,
        department_id=department_id,
        is_active=payload.is_active,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """
    Получение пользователя по ID.

    Доступно ADMIN и MANAGER.
    MANAGER видит только пользователей своего отдела.
    """
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
    if _is_manager(current_user) and user.department_id != current_user.department_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
    return user


@router.put("/{user_id}/role", response_model=UserOut)
async def update_user_role(user_id: int, payload: UpdateUserRole, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """
    Обновление роли пользователя.

    Доступно ADMIN и MANAGER.
    MANAGER не может назначать роль ADMIN и менять роль пользователю из другого отдела.
    """
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERR_NOT_FOUND)
    if _is_manager(current_user):
        if user.department_id != current_user.department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
        if payload.role == UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
    user.role = payload.role
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/", response_model=list[UserOut])
async def list_department_users(session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    """
    Список пользователей.

    ADMIN видит всех, MANAGER — только свой отдел.
    """
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ERR_FORBIDDEN)
    if _is_admin(current_user):
        rows = (await session.execute(select(User))).scalars().all()
        return rows
    rows = (await session.execute(select(User).where(User.department_id == current_user.department_id))).scalars().all()
    return rows
