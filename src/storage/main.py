from fastapi import FastAPI
from storage.api.routers import api_router
from storage.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="File Storage API with metadata and roles",
    version="1.0.0"
)


app.include_router(api_router)
