from datetime import datetime


def moderation_helper(data) -> dict:

    return {

        "id": str(data["_id"]),

        "text": data["text"],

        "is_toxic": data.get("is_toxic"),

        "confidence": data.get("confidence"),

        "labels": data.get("labels", {}),

        "triggered_labels": data.get("triggered_labels", []),

        "reason": data.get("reason"),

        "severity": data.get("severity"),

        "status": data["status"],

        "created_at": data["created_at"],

        "updated_at": data.get("updated_at"),

        "error": data.get("error")
    }
