from fastapi import APIRouter

from storage.api.endpoints import auth_router, files_router, users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(files_router, prefix="/files", tags=["Files"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
