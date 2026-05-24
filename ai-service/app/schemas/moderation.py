# Pydantic data schemas
from pydantic import BaseModel
from typing import Dict, List


class ModerateRequest(BaseModel):

    text: str


class WordImportance(BaseModel):

    word: str
    importance: float


class ModerateResponse(BaseModel):

    text: str

    is_toxic: bool

    confidence: float

    labels: Dict[str, float]

    triggered_labels: List[str]

    top_words: List[WordImportance]

    toxic_phrases: List[str]

    reason: str

    severity: str

    inference_time_ms: float