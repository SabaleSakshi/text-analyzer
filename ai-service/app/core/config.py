from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    MODEL_PATH: str = (
        "app/models/best_model_v2.ckpt"
    )

    MODEL_NAME: str = "roberta-base"

    MAX_LEN: int = 128


settings = Settings()
