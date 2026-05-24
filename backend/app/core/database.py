from motor.motor_asyncio import (
    AsyncIOMotorClient
)

from app.core.config import settings


client = AsyncIOMotorClient(
    settings.MONGO_URL
)

database = client[
    settings.DATABASE_NAME
]


moderation_collection = database.get_collection(
    "moderation_logs"
)