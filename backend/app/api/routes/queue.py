from fastapi import APIRouter

from app.services.queue_service import (
    queue_service
)

from app.schemas.queue import (
    ReviewDecisionRequest
)

router = APIRouter()


@router.get("")
@router.get("/")
async def get_queue():

    return await queue_service.get_queue()


@router.post("/{moderation_id}/decide")
async def decide(
    moderation_id: str,
    request: ReviewDecisionRequest
):

    return await queue_service.decide(
        moderation_id,
        request.decision.value
    )
