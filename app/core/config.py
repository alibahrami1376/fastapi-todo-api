from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    AUTH_JWT_SECRET_KEY: str = "change me"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    AUTH_COOKIE_HTTPONLY: bool = False
    AUTH_COOKIE_SECURE: bool = True
    AUTH_COOKIE_SAMESITE: str = "none"
    TIMEZONE: str = "Asia/Tehran"

    model_config = SettingsConfigDict(env_file=".env")


# Instantiate settings (values are loaded from env variables automatically)
settings = Settings()
