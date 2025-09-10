import enum
from sqlalchemy import ForeignKey, Integer, JSON, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from storage.core.db import Base
from storage.core.constants import FILENAME_MAX_LENGTH, OBJECT_KEY_MAX_LENGTH, DEFAULT_DOWNLOADS_COUNT


class FileVisibility(str, enum.Enum):
    """Варианты видимости файла."""

    PRIVATE = "PRIVATE"
    DEPARTMENT = "DEPARTMENT"
    PUBLIC = "PUBLIC"


class File(Base):
    """Модель файла в системе хранения.

    Содержит информацию о загруженных файлах, их владельце,
    уровне видимости, метаданных и счётчике скачиваний.
    """

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(FILENAME_MAX_LENGTH), nullable=False)
    object_key: Mapped[str] = mapped_column(String(OBJECT_KEY_MAX_LENGTH), unique=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    visibility: Mapped[FileVisibility] = mapped_column(Enum(FileVisibility), nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    downloads_count: Mapped[int] = mapped_column(Integer, default=DEFAULT_DOWNLOADS_COUNT, nullable=False)

    owner: Mapped["User"] = relationship(backref="files")
