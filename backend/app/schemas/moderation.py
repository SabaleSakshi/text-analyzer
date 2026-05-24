from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class ModerateRequest(BaseModel):

    text: str


class ModerateResponse(BaseModel):

    id: str

    text: str

    is_toxic: bool

    confidence: float

    labels: Dict[str, float]

    triggered_labels: List[str]

    reason: str

    severity: str

    status: str


class ModerationRecord(BaseModel):

    id: str

    text: str

    is_toxic: Optional[bool] = None

    confidence: Optional[float] = None

    labels: Dict[str, float] = Field(default_factory=dict)

    triggered_labels: List[str] = Field(default_factory=list)

    reason: Optional[str] = None

    severity: Optional[str] = None

    status: str

    error: Optional[str] = None
