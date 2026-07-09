"""Production settings — set DJANGO_SECRET_KEY, database vars, ALLOWED_HOSTS in Railway."""
import os

from .base import *  # noqa: F403
from .database import get_database_config

DEBUG = os.environ.get("DJANGO_DEBUG", "").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "").split(",") if h.strip()]

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production (comma-separated domains).")

DATABASES = get_database_config(required=True)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins.split(",") if o.strip()]
