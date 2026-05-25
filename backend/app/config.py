from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "ScholarGraph AI"
    app_version: str = "0.1.0"
    upload_dir: str = "uploads"
    processed_dir: str = "processed"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()