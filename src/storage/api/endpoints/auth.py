from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from storage.api.schemas.auth import LoginInput, Token
from storage.api.schemas.user import UserOut
from storage.core.constants import ERR_INVALID_CREDENTIALS
from storage.core.db import get_session
from storage.core.security import (authenticate_user, create_access_token,
                                   get_current_user)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    payload: LoginInput, session: AsyncSession = Depends(get_session)
):
    """
    Аутентификация пользователя по email и паролю.

    Принимает email и пароль в теле запроса.
    Возвращает JWT-токен при успешной проверке.
    """
    user = await authenticate_user(
        session=session, email=payload.email, password=payload.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_CREDENTIALS,
        )
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)


@router.post("/token", response_model=Token)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """
    Аутентификация пользователя по стандартной OAuth2 форме.

    Принимает form-data: username и password.
    Возвращает JWT-токен для авторизации в Swagger UI и других клиентах.
    """
    user = await authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_CREDENTIALS,
        )
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    """
    Получение информации о текущем пользователе.

    Требует действительный JWT-токен.
    Возвращает данные пользователя (id, email, роль, отдел).
    """
    return current_user
