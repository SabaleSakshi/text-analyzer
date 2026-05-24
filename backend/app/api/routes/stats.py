from fastapi import APIRouter

from app.services.stats_service import (
    stats_service
)

router = APIRouter()


@router.get("")
@router.get("/")
async def get_stats():

    return await stats_service.get_stats()
