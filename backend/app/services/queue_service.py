from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException

from app.core.database import (
    moderation_collection
)

from app.models.moderation import (
    moderation_helper
)


class QueueService:

    async def get_queue(self):

        items = []

        cursor = moderation_collection.find({

            "status": "PENDING_REVIEW"

        }).sort("created_at", -1)

        async for document in cursor:

            items.append(
                moderation_helper(document)
            )

        return items

    async def decide(
        self,
        moderation_id: str,
        decision: str
    ):

        if not ObjectId.is_valid(moderation_id):

            raise HTTPException(
                status_code=400,
                detail="Invalid moderation id"
            )

        result = await moderation_collection.update_one(

            {
                "_id": ObjectId(moderation_id)
            },

            {
                "$set": {
                    "status": decision,

                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.matched_count == 0:

            raise HTTPException(
                status_code=404,
                detail="Queue item not found"
            )

        updated = await moderation_collection.find_one({

            "_id": ObjectId(moderation_id)

        })

        return moderation_helper(updated)


queue_service = QueueService()
