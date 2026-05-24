from app.services.explainability import (
    ToxicIntegratedExplainer
)

from app.core.config import settings


class ToxicPredictor:

    _instance = None

    @classmethod
    def get_model(cls):

        if cls._instance is None:

            cls._instance = ToxicIntegratedExplainer(
                checkpoint_path=settings.MODEL_PATH,
                model_name=settings.MODEL_NAME,
                max_len=settings.MAX_LEN
            )

        return cls._instance