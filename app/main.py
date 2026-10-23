import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.config.settings import ConfigurationError, get_settings  # noqa: E402
from app.services.gemini_service import (  # noqa: E402
    GeminiServiceError,
    generate_answer,
)
from app.utils.logging_config import configure_logging  # noqa: E402


def main() -> None:
    """Render the Streamlit chat and handle the current user interaction."""
    configure_logging()
    st.set_page_config(page_title="AI Question & Answering System", page_icon="💬")
    st.title("AI Question & Answering System")
    st.write(
        "Ask questions and get helpful responses from a Google Gemini AI model. "
        "Your conversation stays available for follow-up questions during this session."
    )

    if "conversation" not in st.session_state:
        st.session_state.conversation = []

    try:
        settings = get_settings()
    except ConfigurationError as error:
        st.error(str(error))
        return

    with st.sidebar:
        st.subheader("Gemini Settings")
        st.write(f"Model: `{settings.model}`")
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.conversation = []
            st.rerun()

    for message in st.session_state.conversation:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("What would you like to know?")
    if question is None:
        return
    question = question.strip()
    if not question:
        st.warning("Please enter a question before submitting.")
        return
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = generate_answer(
                    question=question,
                    history=st.session_state.conversation,
                    settings=settings,
                )
                st.markdown(answer)
    except GeminiServiceError:
        st.error("The Gemini request failed. Check your configuration and try again.")
        return

    st.session_state.conversation.extend(
        [
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ]
    )


if __name__ == "__main__":
    main()
