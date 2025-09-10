# 📝 PyStorage - проект файлового хранилища

Сервис для хранения файлов с метаданными и гибкой системой ролей и прав доступа.  
Поддерживает ограничение форматов, размеров, видимости, а также извлечение метаданных из PDF и DOC/DOCX документов.  

---

## 🧱 Стек технологий

- Python 3.11+
- FastAPI
- Alembic
- SQLAlchemy (async)
- PostgreSQL
- Celery
- MinIO (S3)
- Docker + Docker Compose
- PyPDF2, python-docx

---

## 🗂 Структура проекта

```
File_Storage_FastAPI/
├─ src/
│  ├─ migrations/
│  │  ├─ versions/
│  │  │  └─ 6727b10d3bf4_init.py
│  │  ├─ env.py
│  │  ├─ README
│  │  └─ script.py.mako
│  ├─ storage/
│  │  ├─ api/
│  │  │  ├─ endpoints/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ auth.py
│  │  │  │  ├─ files.py
│  │  │  │  └─ users.py
│  │  │  ├─ schemas/
│  │  │  │  ├─ __init__.py
│  │  │  │  ├─ auth.py
│  │  │  │  └─ user.py
│  │  │  ├─ __init__.py
│  │  │  └─ routers.py
│  │  ├─ core/
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py
│  │  │  ├─ config.py
│  │  │  ├─ constants.py
│  │  │  ├─ db.py
│  │  │  └─ security.py
│  │  ├─ db/
│  │  │  └─ models/
│  │  │     ├─ __init__.py
│  │  │     ├─ file.py
│  │  │     └─ user.py
│  │  ├─ scripts/
│  │  │  ├─ __init__.py
│  │  │  └─ seed_admin.py
│  │  ├─ services/
│  │  │  ├─ __init__.py
│  │  │  ├─ metadata.py
│  │  │  ├─ s3.py
│  │  │  └─ tasks.py
│  │  ├─ __init__.py
│  │  └─ main.py
│  ├─ alembic.ini
│  ├─ Dockerfile
│  └─ requirements.txt
├─ .env
├─ .gitignore
├─ docker-compose.yml
└─ README.md
```

---

## 🚀 Запуск проекта

1. Клонируйте репозиторий:
```bash
https://github.com/W1lden/File_Storage_FastAPI.git
```

2. Создайте .env файл в каталоге src. Вот пример:
```env_example
# ======================
# Backend / FastAPI
# ======================
PROJECT_NAME=PyStorage
DESCRIPTION=Сервис для хранения файлов с метаданными и гибкой системой ролей и прав доступа.
Поддерживает ограничение форматов, размеров, видимости, а также извлечение метаданных из PDF и DOC/DOCX документов.
VERSION=1.0.0
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ======================
# База данных
# ======================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=file_storage
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/file_storage

# ======================
# Redis / Celery
# ======================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ======================
# MinIO (S3)
# ======================
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET_NAME=files

# ======================
# Данные админа
# ======================
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123
ADMIN_DEPARTMENT_ID=1

```

3. Соберите и запустите Docker контейнер:
```bash 
docker compose up --build -d
```
4. Примените миграции и создайте админа:
``` bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m storage.scripts.seed_admin

```
5. В браузере прейдите на страницу документации:
```bash
http://0.0.0.0:8000/docs
```

---



## 🌐 Ручки
🔑 Auth

POST /auth/token — получение JWT токена (OAuth2 Password flow).

POST /auth/login — авторизация по email и паролю.

GET /auth/me — информация о текущем пользователе.

👥 Users

POST /users/ — создать пользователя (доступно MANAGER, ADMIN).

GET /users/{user_id} — получить пользователя по id.

PUT /users/{user_id}/role — изменить роль пользователя.

GET /users/ — список пользователей (для MANAGER — только свой отдел, для ADMIN — все).

📂 Files

POST /files/upload — загрузить файл (учёт роли, типа, размера, видимости).

GET /files/{file_id} — информация о файле (метаданные, счётчик скачиваний).

GET /files/{file_id}/download — скачать файл.

DELETE /files/{file_id} — удалить файл.

GET /files/ — список доступных файлов (фильтрация по роли и отделу).

---

## 👤 Автор

[W1lden (GitHub)](https://github.com/W1lden)
