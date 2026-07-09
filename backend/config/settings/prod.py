"""Production settings — set DJANGO_SECRET_KEY, database vars, ALLOWED_HOSTS in Railway."""
import os
import re

from .base import *  # noqa: F403
from .database import get_database_config


def _split_env_list(value: str) -> list[str]:
    """Parse comma-separated env values; strip spaces and optional quotes."""
    items = []
    for part in value.split(","):
        cleaned = part.strip().strip('"').strip("'")
        if cleaned:
            items.append(cleaned)
    return items


def _normalize_origin(url: str) -> str:
    return url.strip().rstrip("/")


DEBUG = os.environ.get("DJANGO_DEBUG", "").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = _split_env_list(os.environ.get("ALLOWED_HOSTS", ""))

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set in production (comma-separated domains).")

DATABASES = get_database_config(required=True)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ── CORS / CSRF for SPA on Railway ───────────────────────────────────────────
cors_origins = _split_env_list(os.environ.get("CORS_ALLOWED_ORIGINS", ""))
frontend_url = os.environ.get("FRONTEND_URL", "").strip().strip('"').strip("'")
if frontend_url:
    cors_origins.append(_normalize_origin(frontend_url))

CORS_ALLOWED_ORIGINS = list(dict.fromkeys(_normalize_origin(o) for o in cors_origins if o))

# Allow any Railway *.up.railway.app frontend (register/login from deployed Nuxt app)
CORS_ALLOWED_ORIGIN_REGEXES = [
    re.compile(r"^https://[a-z0-9-]+\.up\.railway\.app$"),
]

if not CORS_ALLOWED_ORIGINS and not os.environ.get("CORS_ALLOW_RAILWAY_REGEX", "1") == "0":
    # Regex above covers Railway; explicit list still preferred for non-Railway frontends
    pass

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS.copy()

CORS_ALLOW_CREDENTIALS = True
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
