"""Build Django DATABASES from Railway / env vars."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import unquote, urlparse


def _postgres_engine() -> str:
    return "django.db.backends.postgresql"


def _from_database_url(url: str) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ValueError("DATABASE_URL must be a PostgreSQL URL (postgres:// or postgresql://).")

    name = unquote(parsed.path.lstrip("/")).split("?")[0]
    if not name:
        raise ValueError("DATABASE_URL is missing a database name.")

    return {
        "ENGINE": _postgres_engine(),
        "NAME": name,
        "USER": unquote(parsed.username or ""),
        "PASSWORD": unquote(parsed.password or ""),
        "HOST": parsed.hostname or "",
        "PORT": str(parsed.port or 5432),
    }


def _from_env_vars() -> dict | None:
    """
    Individual fields — Railway also exposes PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE.
    You can set DB_* in .env or use Railway's PG* variables directly.
    """
    host = os.environ.get("DB_HOST") or os.environ.get("PGHOST")
    password = os.environ.get("DB_PASSWORD") or os.environ.get("PGPASSWORD")
    name = os.environ.get("DB_NAME") or os.environ.get("PGDATABASE") or "railway"
    user = os.environ.get("DB_USER") or os.environ.get("PGUSER") or "postgres"
    port = os.environ.get("DB_PORT") or os.environ.get("PGPORT") or "5432"

    if not host:
        return None

    return {
        "ENGINE": _postgres_engine(),
        "NAME": name,
        "USER": user,
        "PASSWORD": password or "",
        "HOST": host,
        "PORT": port,
    }


def get_database_config(*, required: bool = False, sqlite_path: Path | None = None) -> dict:
    """
    Priority:
    1. DATABASE_URL (recommended on Railway — copy from Postgres → Connect)
    2. DB_* or Railway PG* variables (HOST, PASSWORD, etc.)
    3. SQLite (dev only, when required=False)
    """
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return {"default": _from_database_url(database_url)}

    pg = _from_env_vars()
    if pg:
        return {"default": pg}

    if required:
        raise ValueError(
            "Database not configured. Set DATABASE_URL or DB_HOST/DB_PASSWORD "
            "(or Railway PGHOST/PGPASSWORD) in the environment."
        )

    if sqlite_path is not None:
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": sqlite_path,
            }
        }

    raise ValueError("No database configuration found.")
