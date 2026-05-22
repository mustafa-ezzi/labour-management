"""Production settings — set DJANGO_SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS in the environment."""
import os

from .base import *  # noqa: F403

DEBUG = os.environ.get("DJANGO_DEBUG", "").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production")

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL must be set in production")

import re

m = re.match(
    r"postgres(?:ql)?://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/(.+)",
    database_url,
)
if not m:
    raise ValueError("DATABASE_URL must be a PostgreSQL URL")

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

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(",") if o.strip()]
