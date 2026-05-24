from fastapi import APIRouter, BackgroundTasks

from app.schemas.moderation import (
    ModerateRequest
)

from app.services.moderation_service import (
    moderation_service
)

router = APIRouter()


@router.post("")
@router.post("/")
async def moderate_text(
    request: ModerateRequest,
    background_tasks: BackgroundTasks
):

    created = await moderation_service.moderate(
        request.text
    )

    background_tasks.add_task(
        moderation_service.process_moderation,
        created["id"],
        request.text
    )

    return created


@router.post("/sync")
async def moderate_text_sync(
    request: ModerateRequest
):

    return await moderation_service.moderate_sync(
        request.text
    )


@router.get("/{moderation_id}")
async def get_moderation(
    moderation_id: str
):

    return await moderation_service.get_by_id(
        moderation_id
    )
