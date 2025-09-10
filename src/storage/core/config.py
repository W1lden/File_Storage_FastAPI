from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Конфигурация приложения.

    Читает параметры окружения из файла `.env` и системных переменных.
    Используется для настройки:
    - Названия проекта и ключа безопасности
    - JWT (алгоритм и время жизни токена)
    - Подключения к базе данных
    - Брокера и бекенда Celery
    - Хранилища MinIO (endpoint, ключи доступа, bucket)
    """

    PROJECT_NAME: str
    DESCRIPTION: str
    VERSION: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
