from huggingface_hub import hf_hub_download

from app.services.explainability import (
    ToxicIntegratedExplainer
)

from app.core.config import settings


class ToxicPredictor:

    _instance = None

    @classmethod
    def get_model(cls):

        if cls._instance is None:

            # Download model from Hugging Face
            model_path = hf_hub_download(
                repo_id=settings.HF_REPO_ID,
                filename=settings.MODEL_FILENAME
            )

            # Load model
            cls._instance = ToxicIntegratedExplainer(
                checkpoint_path=model_path,
                model_name=settings.MODEL_NAME,
                max_len=settings.MAX_LEN
            )

        return cls._instance