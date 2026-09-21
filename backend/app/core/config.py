# Implementing the configuration settings for the application

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Holter ECG Analysis Platform API"
    app_version: str = "0.1.0"
    database_url: str
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = False,
        extra = "ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()