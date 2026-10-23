import logging
from collections.abc import Mapping, Sequence
from time import perf_counter

from google import genai
from google.genai import errors, types

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_INSTRUCTION, build_contents

logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot provide an answer."""


def generate_answer(
    question: str,
    history: Sequence[Mapping[str, str]],
    settings: Settings,
) -> str:
    """Generate an answer from Gemini using the supplied conversation history."""
    question = question.strip()
    if not question:
        raise ValueError("Question must not be empty.")

    started_at = perf_counter()
    try:
        with genai.Client(api_key=settings.api_key) as client:
            response = client.models.generate_content(
                model=settings.model,
                contents=build_contents(question, history),
                config=types.GenerateContentConfig(
                    temperature=settings.temperature,
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )
    except errors.APIError as error:
        status_code = getattr(error, "code", None)
        if isinstance(status_code, int):
            logger.error(
                "Gemini API request failed (model=%s, status_code=%d).",
                settings.model,
                status_code,
            )
        else:
            logger.error("Gemini API request failed (model=%s).", settings.model)
        raise GeminiServiceError("Gemini API request failed.") from None

    answer = (response.text or "").strip()
    if not answer:
        logger.warning("Gemini returned an empty answer (model=%s).", settings.model)
        raise GeminiServiceError("Gemini returned an empty answer.")
    logger.info(
        "Gemini API request completed (model=%s, duration_ms=%d).",
        settings.model,
        round((perf_counter() - started_at) * 1000),
    )
    return answer
