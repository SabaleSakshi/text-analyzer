from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException

from app.core.database import (
    moderation_collection
)

from app.services.ai_service import (
    ai_service
)

from app.models.moderation import (
    moderation_helper
)


class ModerationService:

    async def moderate(self, text: str):

        now = datetime.utcnow()

        moderation_data = {

            "text": text,

            "is_toxic": None,

            "confidence": None,

            "labels": {},

            "triggered_labels": [],

            "reason": None,

            "severity": None,

            "status": "PROCESSING",

            "created_at": now,

            "updated_at": now,

            "error": None
        }

        result = await moderation_collection.insert_one(
            moderation_data
        )

        created = await moderation_collection.find_one(
            {"_id": result.inserted_id}
        )

        return moderation_helper(created)

    async def process_moderation(
        self,
        moderation_id: str,
        text: str
    ):

        try:

            ai_result = await ai_service.moderate_text(
                text
            )

            update_data = {

                "text": ai_result["text"],

                "is_toxic": ai_result["is_toxic"],

                "confidence": ai_result["confidence"],

                "labels": ai_result["labels"],

                "triggered_labels": ai_result[
                    "triggered_labels"
                ],

                "reason": ai_result["reason"],

                "severity": ai_result["severity"],

                "status": (
                    "PENDING_REVIEW"
                    if ai_result["is_toxic"]
                    else "APPROVED"
                ),

                "updated_at": datetime.utcnow(),

                "error": None
            }

        except Exception as exc:

            update_data = {

                "status": "ERROR",

                "updated_at": datetime.utcnow(),

                "error": str(exc)
            }

        await moderation_collection.update_one(
            {"_id": ObjectId(moderation_id)},
            {"$set": update_data}
        )

    async def moderate_sync(self, text: str):

        now = datetime.utcnow()

        ai_result = await ai_service.moderate_text(
            text
        )

        moderation_data = {

            "text": ai_result["text"],

            "is_toxic": ai_result["is_toxic"],

            "confidence": ai_result["confidence"],

            "labels": ai_result["labels"],

            "triggered_labels": ai_result[
                "triggered_labels"
            ],

            "reason": ai_result["reason"],

            "severity": ai_result["severity"],

            "status": (
                "PENDING_REVIEW"
                if ai_result["is_toxic"]
                else "APPROVED"
            ),

            "created_at": now,

            "updated_at": now,

            "error": None
        }

        result = await moderation_collection.insert_one(
            moderation_data
        )

        created = await moderation_collection.find_one(
            {"_id": result.inserted_id}
        )

        return moderation_helper(created)

    async def get_by_id(self, moderation_id: str):

        if not ObjectId.is_valid(moderation_id):

            raise HTTPException(
                status_code=400,
                detail="Invalid moderation id"
            )

        document = await moderation_collection.find_one({
            "_id": ObjectId(moderation_id)
        })

        if document is None:

            raise HTTPException(
                status_code=404,
                detail="Moderation item not found"
            )

        return moderation_helper(document)


moderation_service = ModerationService()
