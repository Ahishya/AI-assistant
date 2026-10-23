from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors

from app.config.settings import Settings
from app.services.gemini_service import GeminiServiceError, generate_answer


def _mock_client(response_text: str | None = "Answer") -> MagicMock:
    client = MagicMock()
    client.__enter__.return_value = client
    client.models.generate_content.return_value = SimpleNamespace(text=response_text)
    return client


def test_generate_answer_sends_question_history_and_settings() -> None:
    settings = Settings(api_key="test-api-key", model="gemini-test", temperature=0.3)
    client = _mock_client()

    with patch(
        "app.services.gemini_service.genai.Client", return_value=client
    ) as client_factory:
        answer = generate_answer(
            "Follow-up",
            [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
            ],
            settings,
        )

    client_factory.assert_called_once_with(api_key="test-api-key")
    client.__exit__.assert_called_once_with(None, None, None)
    assert answer == "Answer"
    request = client.models.generate_content.call_args.kwargs
    assert request["model"] == "gemini-test"
    assert request["contents"] == [
        {"role": "user", "parts": [{"text": "First question"}]},
        {"role": "model", "parts": [{"text": "First answer"}]},
        {"role": "user", "parts": [{"text": "Follow-up"}]},
    ]
    assert request["config"].temperature == 0.3
    assert request["config"].system_instruction


def test_generate_answer_logs_safe_completion_context(
    caplog: pytest.LogCaptureFixture,
) -> None:
    settings = Settings(api_key="private-api-key", model="gemini-test", temperature=0.7)
    client = _mock_client("Private user answer")

    with patch("app.services.gemini_service.genai.Client", return_value=client):
        with caplog.at_level("INFO", logger="app.services.gemini_service"):
            answer = generate_answer("Private user question", [], settings)

    assert answer == "Private user answer"
    assert "Gemini API request completed" in caplog.text
    assert "gemini-test" in caplog.text
    assert "Private user" not in caplog.text
    assert "private-api-key" not in caplog.text


def test_generate_answer_rejects_empty_question_without_api_call() -> None:
    settings = Settings(api_key="test-api-key", model="gemini-test", temperature=0.7)

    with patch("app.services.gemini_service.genai.Client") as client:
        with pytest.raises(ValueError, match="must not be empty"):
            generate_answer("  ", [], settings)

    client.assert_not_called()


def test_generate_answer_handles_api_errors_without_exposing_details(
    caplog: pytest.LogCaptureFixture,
) -> None:
    api_key = "sensitive-api-key"
    settings = Settings(api_key=api_key, model="gemini-test", temperature=0.7)
    client = _mock_client()
    client.models.generate_content.side_effect = errors.APIError(
        500, {"message": f"sensitive failure detail: {api_key}"}
    )

    with patch("app.services.gemini_service.genai.Client", return_value=client):
        with pytest.raises(
            GeminiServiceError,
            match="Gemini API request failed",
        ) as exc:
            generate_answer("Question", [], settings)

    assert "sensitive failure detail" not in str(exc.value)
    assert exc.value.__cause__ is None
    assert "sensitive failure detail" not in caplog.text
    assert api_key not in caplog.text


def test_generate_answer_rejects_empty_model_response() -> None:
    settings = Settings(api_key="test-api-key", model="gemini-test", temperature=0.7)
    client = _mock_client(None)

    with patch("app.services.gemini_service.genai.Client", return_value=client):
        with pytest.raises(GeminiServiceError, match="empty answer"):
            generate_answer("Question", [], settings)


def test_generate_answer_rejects_whitespace_model_response() -> None:
    settings = Settings(api_key="test-api-key", model="gemini-test", temperature=0.7)
    client = _mock_client("  \n")

    with patch("app.services.gemini_service.genai.Client", return_value=client):
        with pytest.raises(GeminiServiceError, match="empty answer"):
            generate_answer("Question", [], settings)
