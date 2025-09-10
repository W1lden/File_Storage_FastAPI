from enum import Enum

class Role(str, Enum):
    USER = "USER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class Visibility(str, Enum):
    PRIVATE = "PRIVATE"
    DEPARTMENT = "DEPARTMENT"
    PUBLIC = "PUBLIC"

BYTES_IN_MB = 1024 * 1024
OBJECT_KEY_RANDOM_BYTES = 8
DOWNLOADS_INCREMENT = 1

API_TOKEN_URL = "/auth/token"
TOKEN_TYPE = "bearer"

ERR_INVALID_CREDENTIALS = "Invalid credentials"
ERR_FORBIDDEN = "Forbidden"
ERR_NOT_FOUND = "Not found"
ERR_FILE_TOO_LARGE = "File too large for role"
ERR_TYPE_NOT_ALLOWED = "File type not allowed for role"
ERR_VISIBILITY_NOT_ALLOWED = "Visibility not allowed for role"
EMAIL_ALREADY_EXISTS = "Email already exists"
MIME_PDF = "application/pdf"
MIME_DOC = "application/msword"
MIME_DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOC_TYPES = {MIME_DOC, MIME_DOCX}

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
    Role.MANAGER: {Visibility.PRIVATE, Visibility.DEPARTMENT, Visibility.PUBLIC},
    Role.ADMIN: {Visibility.PRIVATE, Visibility.DEPARTMENT, Visibility.PUBLIC},
}

CELERY_TASK_EXTRACT_METADATA = "extract_metadata_task"

STREAM_CHUNK_SIZE = 64 * 1024

# File model
FILENAME_MAX_LENGTH = 512
OBJECT_KEY_MAX_LENGTH = 1024
DEFAULT_DOWNLOADS_COUNT = 0

# User model
EMAIL_MAX_LENGTH = 255
PASSWORD_HASH_MAX_LENGTH = 255