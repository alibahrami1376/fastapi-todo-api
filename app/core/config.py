from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always load app/.env regardless of the process working directory
_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str

    REDIS_URL: str = "redis://localhost:6379/0"

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

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_GLOBAL_REQUESTS: int = 100
    RATE_LIMIT_GLOBAL_WINDOW_SECONDS: int = 60
    RATE_LIMIT_AUTH_REQUESTS: int = 10
    RATE_LIMIT_AUTH_WINDOW_SECONDS: int = 60

    CACHE_ENABLED: bool = True
    CACHE_AUTH_TTL_SECONDS: int = 300  # 5 min
    CACHE_STATS_TTL_SECONDS: int = 60  # 1 min
    CACHE_LIST_TTL_SECONDS: int = 30  # 30 sec
    CACHE_DETAIL_TTL_SECONDS: int = 60  # 1 min

    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8")


# Instantiate settings (values are loaded from env variables automatically)
settings = Settings()
