import math
import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigurationError(ValueError):
    """Raised when application configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    """Validated application settings loaded from the environment."""

    api_key: str
    model: str
    temperature: float


def get_settings() -> Settings:
    """Load `.env` values and return validated application settings."""
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ConfigurationError(
            "Gemini is not configured. Create a .env file from .env.example "
            "and add GEMINI_API_KEY."
        )

    raw_temperature = os.getenv("TEMPERATURE", "0.2")
    try:
        temperature = float(raw_temperature)
    except ValueError as error:
        raise ConfigurationError(
            "TEMPERATURE must be a number between 0 and 2."
        ) from error

    if not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise ConfigurationError("TEMPERATURE must be a number between 0 and 2.")

    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    if not model:
        raise ConfigurationError("GEMINI_MODEL must not be empty.")

    return Settings(
        api_key=api_key,
        model=model,
        temperature=temperature,
    )
