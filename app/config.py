import os
from datetime import timedelta


def _fix_database_uri(uri: str | None, default: str) -> str:
    """Normalize PostgreSQL database URI and provide safe fallback."""
    if uri:
        # SQLAlchemy requires postgresql:// instead of postgres://
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        return uri

    # If running in serverless environment (Vercel / AWS Lambda), root filesystem is read-only
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite:////tmp/smart_volunteer_connect.db"

    return default


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "dev-secret-key-please-change-to-something-secure-and-long"
    )
    DEBUG = False
    TESTING = False

    # Database
    SQLALCHEMY_DATABASE_URI = _fix_database_uri(
        os.environ.get("DATABASE_URL"),
        "sqlite:///smart_volunteer_connect.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # JWT (Key must be >= 32 bytes for HS256)
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "smart-volunteer-connect-jwt-secret-key-32bytes-min"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    )

    # CORS
    FRONTEND_ORIGIN = os.environ.get(
        "FRONTEND_ORIGIN", "*"
    )

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _fix_database_uri(
        os.environ.get("DATABASE_URL"),
        "sqlite:///smart_volunteer_connect_dev.db"
    )


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = _fix_database_uri(
        os.environ.get("DATABASE_URL"),
        "sqlite:////tmp/smart_volunteer_connect.db" if os.environ.get("VERCEL") else "postgresql://postgres:postgres@localhost:5432/smart_volunteer_connect"
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=120)


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
