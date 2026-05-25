import asyncio
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

        last_error = None

        for attempt in range(1, 6):

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

            except (
                httpx.ConnectError,
                httpx.ConnectTimeout,
                httpx.ReadError,
                httpx.RemoteProtocolError,
                httpx.HTTPStatusError
            ) as exc:

                last_error = exc

                if (
                    isinstance(exc, httpx.HTTPStatusError)
                    and exc.response.status_code < 500
                ):
                    logger.error(
                        "AI service returned non-retryable status %s: %s",
                        exc.response.status_code,
                        exc.response.text
                    )
                    raise

                logger.warning(
                    "AI service request failed on attempt %s/5: %s",
                    attempt,
                    str(exc)
                )

                if attempt < 5:
                    await asyncio.sleep(2 * attempt)

            except Exception as exc:

                logger.error(
                    f"AI service failed: {str(exc)}"
                )

                raise

        logger.error(
            "AI service unavailable after retries: %s",
            str(last_error)
        )

        raise RuntimeError(
            "AI service is unavailable. Start the AI service on "
            f"{settings.AI_SERVICE_URL} and retry."
        )


ai_service = AIService()
