# AI Question & Answering System

A conversational question-answering application built with Streamlit and Google's Gemini API. Ask questions in a chat interface, receive Markdown-formatted answers, and ask follow-ups using the conversation history stored for the current Streamlit session.

## Project overview

The application uses the official `google-genai` Python SDK to send each question and relevant conversation turns to a configurable Gemini model. Streamlit renders the chat interface and stores the conversation in session state. The API key and generation settings are loaded from a local `.env` file.

## Features

- Chat-style Streamlit interface with separate user and assistant messages.
- Multi-turn conversations maintained for the current Streamlit session.
- Configurable Gemini model and response temperature.
- Loading indicator while Gemini generates an answer.
- Empty-question validation and friendly configuration/API error messages.
- Clear Conversation control.
- Logging that avoids recording API keys and conversation content.
- Pytest coverage for configuration and Gemini service behavior.

## Architecture

- **UI (`app/main.py`)** handles Streamlit rendering, input validation, and session conversation state.
- **Configuration (`app/config/settings.py`)** loads and validates settings from `.env`.
- **Service (`app/services/gemini_service.py`)** owns Gemini client initialization and all API communication.
- **Prompts (`app/prompts/qa_prompt.py`)** defines the system instruction and converts conversation history to Gemini message format.
- **Logging (`app/utils/logging_config.py`)** configures standard Python logging.
- **Tests (`tests/`)** validate configuration and service behavior without making live API calls.

## Project structure

```text
.
├── app/
│   ├── config/
│   │   └── settings.py
│   ├── prompts/
│   │   └── qa_prompt.py
│   ├── services/
│   │   └── gemini_service.py
│   ├── utils/
│   │   └── logging_config.py
│   └── main.py
├── tests/
│   ├── test_config.py
│   └── test_gemini_service.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.sh
```

## Prerequisites

- Python **3.11 or newer** (the current Streamlit dependency requires Python 3.11+).
- Internet access to reach the Gemini API.
- A Google Gemini API key.

## Obtain a Google Gemini API key

Create or manage a key in [Google AI Studio](https://aistudio.google.com/apikey). Keep the key private. Do not paste it into source code, commit it, or include it in screenshots or logs.

## Create and activate a virtual environment

Run these commands from the project root.

Create the environment (all platforms):

```shell
python -m venv .venv
```

Activate on macOS/Linux:

```shell
source .venv/bin/activate
```

Activate on Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation due to its execution policy, use Command Prompt or follow your organization's approved PowerShell policy rather than weakening security settings globally.

## Install dependencies

With the virtual environment activated:

```shell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements include Streamlit, the official `google-genai` SDK, `python-dotenv`, and pytest.

## Configure `.env`

Create a local `.env` file by copying the example.

macOS/Linux:

```shell
cp .env.example .env
```

Windows Command Prompt:

```bat
copy .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and replace the API-key placeholder with your own key:

```dotenv
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-3.8-flash
TEMPERATURE=0.2
```

`GEMINI_API_KEY` is required. The model and temperature are optional and default to `gemini-3.8-flash` and `0.2`. Temperature must be a finite number from `0` to `2`.

The `.gitignore` ignores `.env` and `.env.*`, then explicitly unignores `.env.example` with `!.env.example`. This keeps the example configuration trackable without tracking local environment files.

## Run the Streamlit application

With the virtual environment activated and `.env` configured:

```shell
streamlit run app/main.py
```

Streamlit prints a local URL in the terminal and usually opens the application in your browser. To stop the running server, press **Ctrl+C** in that terminal.

## Run tests

With development dependencies installed and the virtual environment activated:

```shell
pytest
```

Alternatively:

```shell
python -m pytest
```

The tests mock Gemini client requests; they do not require a live API key or make billable API calls.

## Example questions

- “Explain photosynthesis in three short sections.”
- “What are the main differences between lists and tuples in Python?”
- “Suggest a simple weekly meal-planning approach.”
- “Summarize the causes of the French Revolution.”
- After an answer, ask a follow-up such as “Can you give me an example?”

## Troubleshooting

- **`ModuleNotFoundError: No module named 'app'`:** Run `streamlit run app/main.py` from the project root, or use `sh run.sh` on macOS/Linux. The app entry point also adds the project root to Python's import path when launched directly.
- **The app says the API key is missing:** Check that `.env` is in the project root, that `GEMINI_API_KEY` is set, and that the key has no accidental surrounding quotes or spaces. Restart Streamlit after changing environment configuration.
- **Authentication or API request fails:** Confirm the key is valid, the Gemini API is enabled/available for your account, and your network can reach Google's API. The app intentionally hides raw provider errors.
- **Model not found or unavailable:** Check the model code and access in the [official Gemini API model catalog](https://ai.google.dev/gemini-api/docs/models), then update `GEMINI_MODEL` in `.env`.
- **Invalid temperature:** Set `TEMPERATURE` to a finite numeric value from `0` to `2`, such as `0.2`.
- **`streamlit` or `pytest` is not recognized:** Activate `.venv` and reinstall dependencies with `python -m pip install -r requirements.txt`.
- **PowerShell cannot activate the environment:** Use Command Prompt activation or your organization's approved Python environment workflow.
- **Port is already in use:** Start Streamlit with another port, for example `streamlit run app/main.py --server.port 8502`.

## Security considerations

- Store credentials only in the ignored local `.env` file (or a managed secret store in deployment).
- Never commit `.env`; commit `.env.example` only, with placeholder values.
- The API key is not shown in the interface or written to application logs.
- Application logs include operational context but do not include full prompts, answers, or conversation history.
- API errors shown in the UI are intentionally generic and omit provider exception details.
- Avoid sharing sensitive personal or confidential information in questions unless you are authorized to submit it to the Gemini API.

## Change the Gemini model and generation settings

Edit `.env` and set `GEMINI_MODEL` to a model code currently available to your account. The example uses `gemini-3.8-flash`, listed as stable in Google's [Gemini API model catalog](https://ai.google.dev/gemini-api/docs/models). Check the catalog for current availability and capabilities before selecting a different model.

Change `TEMPERATURE` to adjust generation variability, for example:

```dotenv
GEMINI_MODEL=gemini-3.8-flash
TEMPERATURE=0.2
```

The application accepts temperatures from `0` to `2`; lower values generally produce less variable responses. Restart Streamlit after editing `.env`.

## Deactivate the virtual environment

When finished:

```shell
deactivate
```

## Future enhancements

- Add configurable generation controls in the sidebar.
- Add support for exporting or downloading a conversation.
- Add optional streaming responses.
- Expand test coverage for UI workflows and additional provider error cases.
- Add deployment guidance for managed secrets and hosted Streamlit environments.
