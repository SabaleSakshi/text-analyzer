import logging
import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    moderation,
    queue,
    stats
)
from app.core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def mask_mongo_url(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"//[^@/]+@", "//***:***@", value)

app = FastAPI(
    title="Content Moderation Backend"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    moderation.router,
    prefix="/api/moderate",
    tags=["Moderation"]
)

app.include_router(
    queue.router,
    prefix="/api/queue",
    tags=["Queue"]
)

app.include_router(
    stats.router,
    prefix="/api/stats",
    tags=["Stats"]
)


@app.on_event("startup")
async def log_backend_config():
    logger.info(
        "Mongo config: url=%s db=%s",
        mask_mongo_url(settings.MONGO_URL),
        settings.DATABASE_NAME
    )


@app.get("/")
async def root():

    return {
        "message": "Backend Running"
    }
