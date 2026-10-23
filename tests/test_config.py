from unittest.mock import patch

import pytest

from app.config.settings import ConfigurationError, get_settings


def test_get_settings_loads_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

    with patch("app.config.settings.load_dotenv") as load_dotenv:
        settings = get_settings()

    assert settings.api_key == "test-api-key"
    load_dotenv.assert_called_once_with()


def test_get_settings_reads_values_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test")
    monkeypatch.setenv("TEMPERATURE", "0.4")

    settings = get_settings()

    assert settings.api_key == "test-api-key"
    assert settings.model == "gemini-test"
    assert settings.temperature == 0.4


def test_get_settings_uses_defaults_with_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    monkeypatch.delenv("TEMPERATURE", raising=False)

    settings = get_settings()

    assert settings.api_key == "test-api-key"
    assert settings.model == "gemini-3.8-flash"
    assert settings.temperature == 0.2


def test_get_settings_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with patch("app.config.settings.load_dotenv"):
        with pytest.raises(ConfigurationError, match="Create a .env file"):
            get_settings()


@pytest.mark.parametrize("temperature", ["invalid", "-0.1", "2.1", "nan", "inf"])
def test_get_settings_rejects_invalid_temperature(
    monkeypatch: pytest.MonkeyPatch,
    temperature: str,
) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("TEMPERATURE", temperature)

    with pytest.raises(ConfigurationError):
        get_settings()


def test_get_settings_rejects_empty_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")
    monkeypatch.setenv("GEMINI_MODEL", "  ")

    with pytest.raises(ConfigurationError, match="GEMINI_MODEL"):
        get_settings()
