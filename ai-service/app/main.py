import asyncio

from fastapi import FastAPI
from app.services.inference import ModerationService
from app.schemas.moderation import (
    ModerateRequest
)


app = FastAPI(
    title="AI Moderation Service",
    version="1.0.0"
)

moderation_service = ModerationService()


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.post("/moderate")
async def moderate(
    request: ModerateRequest
):

    result = await asyncio.to_thread(
        moderation_service.moderate_text,
        request.text
    )

    return result
