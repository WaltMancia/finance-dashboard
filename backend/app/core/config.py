from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "Finance Dashboard API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Base de datos
    database_url: str
    test_database_url: str

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS
    frontend_url: str = "http://localhost:5173"

    # Pydantic lee automáticamente el archivo .env
    model_config = {"env_file": ".env"}


# lru_cache asegura que Settings se instancia una sola vez
# y se reutiliza en toda la aplicación (patrón Singleton)
@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
