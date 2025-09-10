from fastapi import FastAPI

from storage.api.routers import api_router
from storage.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

app.include_router(api_router)
