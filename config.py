import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()


def _build_mysql_url(host: str) -> str:
    user = os.environ.get("MYSQLUSER", "root")
    password = quote_plus(os.environ.get("MYSQLPASSWORD", ""))
    port = os.environ.get("MYSQLPORT", "3306")
    database = os.environ.get("MYSQLDATABASE") or os.environ.get("MYSQL_DATABASE", "railway")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"


def _database_url() -> str:
    """Resolve SQLAlchemy URI — on Railway, MYSQLHOST wins over localhost DATABASE_URL."""
    host = os.environ.get("MYSQLHOST")
    url = (os.environ.get("DATABASE_URL") or "").strip()

    # Railway injects MYSQLHOST; ignore stale localhost DATABASE_URL from .env
    if host:
        if not url or "localhost" in url or "127.0.0.1" in url:
            return _build_mysql_url(host)

    if url:
        if url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+pymysql://", 1)
        return url

    if host:
        return _build_mysql_url(host)

    mysql_url = os.environ.get("MYSQL_URL")
    if mysql_url:
        if mysql_url.startswith("mysql://"):
            return mysql_url.replace("mysql://", "mysql+pymysql://", 1)
        return mysql_url

    return "mysql+pymysql://solargrid:solargrid_pass@localhost:3306/solargrid_db"


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
        "mysql+pymysql://solargrid:solargrid_pass@localhost:3306/solargrid_test_db",
    )


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @classmethod
    def init_app(cls, app):
        if not os.environ.get("SECRET_KEY"):
            raise ValueError("SECRET_KEY must be set in production")


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
