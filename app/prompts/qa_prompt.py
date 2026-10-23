from collections.abc import Mapping, Sequence

SYSTEM_INSTRUCTION = (
    "You are a helpful question-answering assistant. Answer the user's question "
    "clearly and be concise while providing sufficient detail. Admit when you "
    "do not know something and do not fabricate facts. Use the conversation "
    "history when answering follow-up questions. Format answers using Markdown "
    "when appropriate."
)


def build_contents(
    question: str,
    history: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    """Convert application chat history and the current question for Gemini."""
    contents: list[dict[str, object]] = []
    for message in history:
        role = "model" if message["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": message["content"]}]})
    contents.append({"role": "user", "parts": [{"text": question}]})
    return contents
