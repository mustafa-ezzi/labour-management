"""Local development settings."""
import os

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

database_url = os.environ.get("DATABASE_URL")  # noqa: F405

if database_url:
    # postgres://user:pass@host:port/db
    import re

    m = re.match(
        r"postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)",
        database_url,
    )
    if m:
        user, password, host, port, name = m.groups()
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": name.split("?")[0],
                "USER": user,
                "PASSWORD": password,
                "HOST": host,
                "PORT": port or "5432",
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
            }
        }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
