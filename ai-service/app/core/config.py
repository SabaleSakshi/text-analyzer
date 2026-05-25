from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    HF_REPO_ID: str
    MODEL_FILENAME: str

    MODEL_NAME: str = "roberta-base"
    MAX_LEN: int = 128

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()