import time
import logging
import httpx

from app.core.config import settings


logging.basicConfig(
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class AIService:

    async def moderate_text(self, text: str):

        logger.info(
            "Sending request to AI service..."
        )

        start = time.time()

        timeout = httpx.Timeout(
            300.0
        )

        try:

            async with httpx.AsyncClient(
                timeout=timeout
            ) as client:

                response = await client.post(

                    f"{settings.AI_SERVICE_URL}/moderate",

                    json={
                        "text": text
                    }

                )

                logger.info(
                    f"AI response status: {response.status_code}"
                )

                response.raise_for_status()

                elapsed = time.time() - start

                logger.info(
                    f"AI request completed in "
                    f"{elapsed:.2f} seconds"
                )

                return response.json()

        except Exception as e:

            logger.error(
                f"AI service failed: {str(e)}"
            )

            raise


ai_service = AIService()