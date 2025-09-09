from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from storage.api.schemas.auth import LoginInput, Token
from storage.api.schemas.user import UserOut
from storage.core.db import get_session
from storage.core.security import authenticate_user, create_access_token, get_current_user
from storage.core.constants import ERR_INVALID_CREDENTIALS

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(payload: LoginInput, session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session=session, email=payload.email, password=payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERR_INVALID_CREDENTIALS)
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)

@router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await authenticate_user(session=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERR_INVALID_CREDENTIALS)
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)

@router.get("/me", response_model=UserOut)
async def me(current_user=Depends(get_current_user)):
    return current_user
