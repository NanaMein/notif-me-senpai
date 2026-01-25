Notify Me Senpai

Notify Me Senpai — a lightweight, open-source chatbot + notification prototype.
This project is a simple FastAPI-based chat assistant that keeps a short in-memory conversation history (deque, max 5 messages) and uses CrewAI Flow to orchestrate multi-step LLM workflows and decision logic (eg. “remember this”, schedule a notification, send SMTP/webhook). Pydantic models validate LLM inputs/outputs. The focus is simplicity: fast local development, clear orchestration, and easy extension — not long-term persistence (no DB required by default).


---

Table of contents

Why this project exists

Key features

Architecture overview

Quick start

Configuration / environment

API examples

Behavior details

Extending & roadmap

Contributing

License



---

Why this project exists

A simple, opinionated template for experimenting with LLM-driven workflows and notifications without the overhead of persistent storage.

Demonstrates using CrewAI Flow to route multi-step logic inside a chatbot.

Useful as a sandbox for building scheduled reminders, email/webhook notifications, and LLM-driven task extraction.



---

Key features

Minimal FastAPI service that exposes chat and task endpoints.

In-memory conversation store using collections.deque (configurable max size, default 5).

CrewAI Flow orchestrates routing and multi-step LLM interactions.

Pydantic schemas for robust input/output validation of LLM and API data.

Simple notification handlers (SMTP, webhook, local callback) pluggable via configuration.

Provider-agnostic LLM integration (environment-configurable; supports OpenAI, other HTTP-based LLMs, or local adapters).



---

Architecture overview

FastAPI: HTTP API and web server.

CrewAI Flow: Orchestration layer that decides how to handle user messages (chat vs task vs schedule).

LLM Adapter: Small abstraction over your LLM provider (configurable).

In-memory memory: deque for latest N messages (default N=5).

Notification system: Internal scheduler + workers that send notifications via configured channels (SMTP, webhook, site notification).

Pydantic models: Validate LLM IO and API payloads.


Simple request flow:

1. User sends message → FastAPI endpoint.


2. Endpoint pushes message into the deque.


3. CrewAI Flow inspects intent (chat, reminder request, etc.) and routes:

Simple chat: call chat LLM step(s) and reply.

Task (e.g., remember / notify): parse details via LLM, schedule notification, acknowledge to user.



4. If scheduled, internal clock checks tasks and triggers notification handlers.




---

Quick start

Requirements

Python 3.10+ (recommended 3.11)

pip and virtualenv

An LLM API key (if using a hosted provider) — the project supports configuring the provider via env vars.


Install

git clone https://github.com/your-username/notify-me-senpai.git
cd notify-me-senpai
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

Run (development)

uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for automatic API docs.


---

Configuration / environment

Configure via environment variables (example .env or export in shell):

# LLM provider
LLM_PROVIDER=openai
LLM_API_KEY=sk-...

# CrewAI / Flow options
CREWAI_CONFIG_PATH=./config/flow.yaml

# Deque size for in-memory conversation history
CONVERSATION_MAX_LENGTH=5

# Notification (SMTP example)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASS=supersecret

# Optional: webhook url for notifications
WEBHOOK_URL=https://hooks.example.com/notify

# Other flags
LOG_LEVEL=info

The LLM adapter loads LLM_PROVIDER and LLM_API_KEY. You can implement additional adapters to call Groq, Anthropic, local LLMs, etc.


---

API examples

1) Chat endpoint

POST /chat

{
  "user_id": "user-123",
  "message": "Hey, can you remember my dentist appointment next Friday at 3pm?"
}

Response

{
  "reply": "Got it — I scheduled a reminder for your dentist appointment on 2026-02-06 at 15:00. I'll notify you then.",
  "conversation_length": 3
}

2) Task endpoint (explicit)

POST /task/remember

{
  "user_id": "user-123",
  "title": "Dentist appointment",
  "when": "2026-02-06T15:00:00+08:00",
  "channel": "email",
  "meta": {"email": "you@example.com"}
}

Response

{
  "status": "scheduled",
  "task_id": "task-abc123",
  "notify_at": "2026-02-06T15:00:00+08:00"
}


---

Behavior details

In-memory conversation store

Implemented with Python collections.deque.

Default max length: 5 (configurable via CONVERSATION_MAX_LENGTH).

On each new user message, the message is appended; if the deque is already at capacity, the oldest message is popped off.

Important: This is intentionally ephemeral — restarting the process clears all memory.


CrewAI Flow routing

Flow is responsible for:

Intent classification (chat vs task vs other).

Calling LLM steps and Pydantic validation chains.

Scheduling notifications or invoking handlers as required.


Flow files/configs live in config/ (example flow.yaml).


Notifications & scheduling

Minimal in-process scheduler (suitable for demo and light load).

Pluggable handlers:

smtp_handler — sends emails.

webhook_handler — POST to an external URL.

local_callback — for local integrations (invoke a function).


For production, replace the in-process scheduler with a persistent job queue (Redis+RQ, Celery, or external scheduler).


Pydantic validation

All LLM I/O passes through Pydantic models to reduce hallucination-induced schema errors.

Example schema files live in app/schemas/ and include models such as ReminderModel, NotificationModel, ChatMessage.



---

Extending & roadmap

Planned/optional improvements you might add:

Persistent memory backend (Postgres / SQLite / vector DB) for long-term history and RAG.

Authentication + multi-user support with per-user deques.

Production-grade scheduler (Redis queue or serverless scheduler).

Front-end UI (React) for richer interactions and notification display.

More LLM adapters (Groq, Llama via local server, Anthropic, etc.).

Test suite + CI for deterministic workflows.

Docker compose + example deployment for test/demo.



---

Contributing

Contributions welcome. Suggested workflow:

1. Fork the repo.


2. Create a feature branch: feature/your-feature.


3. Write tests and update documentation.


4. Open a pull request with a clear description.



Please follow the code style in the repo and add Pydantic models for any new API surface.


---

Development notes / tips

Use .env for local testing and python-dotenv to load env vars in dev.

For testing LLM steps locally without API calls, use the mock_llm_adapter (look for it in app/adapters/mock.py) and set LLM_PROVIDER=mock.

Keep the deque small for demo purposes; increase carefully if you want larger conversational context.



---

License

This project is provided under the MIT License. See LICENSE for details.


---

Acknowledgements

CrewAI Flow for orchestration ideas.

FastAPI and Pydantic for API & data validation foundations.

Inspirations from many small scheduler and reminder projects.



---

If you want, I can:

generate a README file as a ready-to-commit README.md, or

produce example flow.yaml, Pydantic schemas, and a minimal main.py FastAPI starter (single-file) that matches this README.


Tell me which of those you'd like next and I’ll produce it.
