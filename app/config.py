from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URL: Optional[str] = None
    MONGODB_DB_NAME: str = "games_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()