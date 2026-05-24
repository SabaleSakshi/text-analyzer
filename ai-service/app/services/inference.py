import time

from app.services.predictor import ToxicPredictor


class ModerationService:

    def __init__(self):

        self.model = ToxicPredictor.get_model()

    def get_severity(self, confidence: float):

        if confidence >= 0.85:
            return "HIGH"

        if confidence >= 0.60:
            return "MEDIUM"

        if confidence >= 0.40:
            return "LOW"

        return "SAFE"

    def moderate_text(self, text: str):

        start_time = time.time()

        result = self.model.explain(text)

        inference_time = (
            time.time() - start_time
        ) * 1000

        result["severity"] = self.get_severity(
            result["confidence"]
        )

        result["inference_time_ms"] = round(
            inference_time,
            2
        )

        return result