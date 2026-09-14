import logging
import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _build_mysql_url_from_parts(host: str, user: str, password: str, port: str, database: str) -> str:
    return (
        f"mysql+pymysql://{user}:{quote_plus(password or '')}"
        f"@{host}:{port or '3306'}/{database}"
    )


def _normalize_mysql_url(url: str) -> str:
    if url.startswith("mysql://"):
        return url.replace("mysql://", "mysql+pymysql://", 1)
    return url


def _url_points_to_localhost(url: str) -> bool:
    return "localhost" in url or "127.0.0.1" in url


def _build_mysql_url_from_railway() -> str | None:
    host = os.environ.get("MYSQLHOST")
    if not host:
        return None
    return _build_mysql_url_from_parts(
        host=host,
        user=os.environ.get("MYSQLUSER", "root"),
        password=os.environ.get("MYSQLPASSWORD", ""),
        port=os.environ.get("MYSQLPORT", "3306"),
        database=os.environ.get("MYSQLDATABASE") or os.environ.get("MYSQL_DATABASE", "railway"),
    )


def _build_mysql_url_from_db_env() -> str | None:
    host = os.environ.get("DB_HOST")
    if not host:
        return None
    return _build_mysql_url_from_parts(
        host=host,
        user=os.environ.get("DB_USER", "solargrid"),
        password=os.environ.get("DB_PASSWORD", ""),
        port=os.environ.get("DB_PORT", "3306"),
        database=os.environ.get("DB_NAME", "solargrid_db"),
    )


def _database_url() -> str:
    """Resolve SQLAlchemy URI from environment (local .env or Railway variables)."""
    url = (os.environ.get("DATABASE_URL") or "").strip()
    railway_url = _build_mysql_url_from_railway()
    db_env_url = _build_mysql_url_from_db_env()

    # Railway MySQL service variables — ignore stale localhost DATABASE_URL values
    if railway_url and (not url or _url_points_to_localhost(url)):
        return railway_url

    if url:
        return _normalize_mysql_url(url)

    if db_env_url:
        return db_env_url

    if railway_url:
        return railway_url

    mysql_url = (os.environ.get("MYSQL_URL") or "").strip()
    if mysql_url:
        return _normalize_mysql_url(mysql_url)

    # Local development fallback when no env vars are set
    return _build_mysql_url_from_parts(
        host="127.0.0.1",
        user="solargrid",
        password="solargrid_pass",
        port="3306",
        database="solargrid_db",
    )


def database_connection_label() -> str:
    """Safe connection label for logs — host/database only, never credentials."""
    host = os.environ.get("MYSQLHOST") or os.environ.get("DB_HOST")
    database = os.environ.get("MYSQLDATABASE") or os.environ.get("DB_NAME")
    if host and database:
        return f"{host}/{database}"

    resolved = _database_url()
    if "@" in resolved:
        return resolved.split("@", 1)[1].split("?", 1)[0]
    return "unknown"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = int(os.environ.get("SESSION_TIMEOUT_MINUTES", 30)) * 60
    BCRYPT_LOG_ROUNDS = int(os.environ.get("BCRYPT_LOG_ROUNDS", 12))
    RATE_LIMIT_LOGIN = os.environ.get("RATE_LIMIT_LOGIN", "5 per minute")
    ITEMS_PER_PAGE = 25


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "mysql+pymysql://solargrid:solargrid_pass@127.0.0.1:3306/solargrid_test_db",
    )


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        if not os.environ.get("SECRET_KEY"):
            raise ValueError("SECRET_KEY must be set in production")

        db_target = database_connection_label()
        if _url_points_to_localhost(db_target):
            raise ValueError(
                "Production must not use localhost for the database. "
                "Configure Railway MySQL variables on the Flask service."
            )
        app.logger.info("Production database target: %s", db_target)


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
