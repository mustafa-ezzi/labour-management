"""Local development settings."""
import re

from .base import *  # noqa: F403
from .database import get_database_config

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "0.0.0.0"]

DATABASES = get_database_config(sqlite_path=BASE_DIR / "db.sqlite3")  # noqa: F405

# Local Nuxt dev (any port on localhost / 127.0.0.1 / LAN IP for phone testing)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
CORS_ALLOWED_ORIGIN_REGEXES = [
    re.compile(r"^http://localhost:\d+$"),
    re.compile(r"^http://127\.0\.0\.1:\d+$"),
    re.compile(r"^http://192\.168\.\d+\.\d+:\d+$"),
    re.compile(r"^http://10\.\d+\.\d+\.\d+:\d+$"),
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
