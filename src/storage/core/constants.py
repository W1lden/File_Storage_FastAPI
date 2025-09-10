from enum import Enum


# ======================
# Роли и уровни доступа
# ======================
class Role(str, Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class Visibility(str, Enum):
    PRIVATE = "PRIVATE"
    DEPARTMENT = "DEPARTMENT"
    PUBLIC = "PUBLIC"


# ======================
# Общие константы
# ======================
BYTES_IN_MB = 1024 * 1024
OBJECT_KEY_RANDOM_BYTES = 8
DOWNLOADS_INCREMENT = 1
STREAM_CHUNK_SIZE = 64 * 1024

# ======================
# Аутентификация
# ======================
API_TOKEN_URL = "/auth/token"
TOKEN_TYPE = "bearer"

# ======================
# Сообщения об ошибках
# ======================
ERR_INVALID_CREDENTIALS = "Неверные учётные данные"
ERR_FORBIDDEN = "Доступ запрещён"
ERR_NOT_FOUND = "Не найдено"
ERR_FILE_TOO_LARGE = "Файл слишком большой для данной роли"
ERR_TYPE_NOT_ALLOWED = "Тип файла не разрешён для данной роли"
ERR_VISIBILITY_NOT_ALLOWED = "Уровень видимости не разрешён для данной роли"
EMAIL_ALREADY_EXISTS = "Пользователь с таким email уже существует"

# ======================
# MIME-типы документов
# ======================
MIME_PDF = "application/pdf"
MIME_DOC = "application/msword"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document" # noqa
DOC_TYPES = {MIME_DOC, MIME_DOCX}

# ======================
# Ограничения по ролям
# ======================
ROLE_MAX_SIZE_MB = {
    Role.USER: 10,
    Role.MANAGER: 50,
    Role.ADMIN: 100,
}

ROLE_ALLOWED_TYPES = {
    Role.USER: {MIME_PDF},
    Role.MANAGER: {MIME_PDF, MIME_DOC, MIME_DOCX},
    Role.ADMIN: {MIME_PDF, MIME_DOC, MIME_DOCX},
}

ROLE_ALLOWED_VISIBILITY = {
    Role.USER: {Visibility.PRIVATE},
    Role.MANAGER: {
        Visibility.PRIVATE,
        Visibility.DEPARTMENT,
        Visibility.PUBLIC,
    },
    Role.ADMIN: {
        Visibility.PRIVATE,
        Visibility.DEPARTMENT,
        Visibility.PUBLIC,
    },
}

# ======================
# Celery
# ======================
CELERY_TASK_EXTRACT_METADATA = "extract_metadata_task"

# ======================
# Ограничения моделей
# ======================
# Файлы
FILENAME_MAX_LENGTH = 512
OBJECT_KEY_MAX_LENGTH = 1024
DEFAULT_DOWNLOADS_COUNT = 0

# Пользователи
EMAIL_MAX_LENGTH = 255
PASSWORD_HASH_MAX_LENGTH = 255
