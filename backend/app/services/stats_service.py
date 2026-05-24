from app.core.database import (
    moderation_collection
)


class StatsService:

    async def get_stats(self):

        total = await moderation_collection.count_documents({})

        toxic = await moderation_collection.count_documents({
            "is_toxic": True
        })

        safe = await moderation_collection.count_documents({
            "is_toxic": False
        })

        pending = await moderation_collection.count_documents({
            "status": "PENDING_REVIEW"
        })

        processing = await moderation_collection.count_documents({
            "status": "PROCESSING"
        })

        approved = await moderation_collection.count_documents({
            "status": "APPROVED"
        })

        rejected = await moderation_collection.count_documents({
            "status": "REJECTED"
        })

        errors = await moderation_collection.count_documents({
            "status": "ERROR"
        })

        return {

            "total": total,

            "toxic": toxic,

            "safe": safe,

            "pending_review": pending,

            "processing": processing,

            "approved": approved,

            "rejected": rejected,

            "errors": errors
        }


stats_service = StatsService()
