from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    MONGO_URL: str

    DATABASE_NAME: str

    AI_SERVICE_URL: str

    PORT: int = 5000

    class Config:
        env_file = ".env"


settings = Settings()