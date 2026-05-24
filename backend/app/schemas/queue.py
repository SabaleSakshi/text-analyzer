from enum import Enum

from pydantic import BaseModel


class ReviewDecision(str, Enum):

    approved = "APPROVED"

    rejected = "REJECTED"


class ReviewDecisionRequest(BaseModel):

    decision: ReviewDecision
