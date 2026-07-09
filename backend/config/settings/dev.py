"""Local development settings."""
from .base import *  # noqa: F403
from .database import get_database_config

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

DATABASES = get_database_config(sqlite_path=BASE_DIR / "db.sqlite3")  # noqa: F405

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
