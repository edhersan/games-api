from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "games_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()