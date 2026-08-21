from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always load app/.env regardless of the process working directory
_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    AUTH_JWT_SECRET_KEY: str = "change me"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    AUTH_COOKIE_HTTPONLY: bool = False
    AUTH_COOKIE_SECURE: bool = True
    AUTH_COOKIE_SAMESITE: str = "none"

    TIMEZONE: str = "Asia/Tehran"

    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "14 days"

    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8")


# Instantiate settings (values are loaded from env variables automatically)
settings = Settings()
