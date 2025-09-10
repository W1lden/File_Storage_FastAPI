from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.api.schemas.user import UserOut, UserCreate, UpdateUserRole
from storage.core.db import get_session
from storage.core.security import get_current_user, get_password_hash
from storage.db.models.user import User, UserRole

router = APIRouter()


def _is_admin(u: User) -> bool:
    return u.role == UserRole.ADMIN


def _is_manager(u: User) -> bool:
    return u.role == UserRole.MANAGER


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=403, detail="Forbidden")
    q = await session.execute(select(User).where(User.email == payload.email))
    exists = q.scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")
    role = payload.role or UserRole.USER
    department_id = payload.department_id if payload.department_id is not None else current_user.department_id
    if _is_manager(current_user):
        if role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Forbidden")
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
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=403, detail="Forbidden")
    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    if _is_manager(current_user) and user.department_id != current_user.department_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@router.put("/{user_id}/role", response_model=UserOut)
async def update_user_role(user_id: int, payload: UpdateUserRole, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=403, detail="Forbidden")
    q = await session.execute(select(User).where(User.id == user_id))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    if _is_manager(current_user):
        if user.department_id != current_user.department_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if payload.role == UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Forbidden")
    user.role = payload.role
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/", response_model=list[UserOut])
async def list_department_users(session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if not (_is_admin(current_user) or _is_manager(current_user)):
        raise HTTPException(status_code=403, detail="Forbidden")
    if _is_admin(current_user):
        rows = (await session.execute(select(User))).scalars().all()
        return rows
    rows = (await session.execute(select(User).where(User.department_id == current_user.department_id))).scalars().all()
    return rows
