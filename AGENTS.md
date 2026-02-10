# Directives for AI Agents 🤖

This document provides context and guidelines for AI coding assistants (like Gemini, ChatGPT, Claude) interacting with this project.

## 🏛️ System Context (Hub-and-Spoke 2.0)

- **Central Hub**: `bot-orchestrator-hub` (this project) is the master controller.
- **AI Provider**: `YOUR_GCP_PROJECT_ID` (Personal Services) is the dedicated AI project.
- **Region**: ALWAYS use **`europe-west8` (Milan)** for everything.
- **Credentials**: Secrets are stored in GCP Secret Manager. Never hardcode them.

## 💻 Tech Stack & Standards

- **Language**: Python 3.12+ (Modern syntax).
- **Framework**: FastAPI (Async is the rule, not the exception).
- **Validation**: Pydantic V2 Models for all request/response bodies.
- **Config**: `pydantic-settings` via `src/core/config.py`.
- **Formatting**: `ruff` is used for linting and formatting.

## 🛠️ How to Extend this System (Agent Protocol)

When an agent is asked to add a new command or a new satellite:

1. **satellite Integration**:
    - Add the command to `COMMAND_REGISTRY` in `src/core/config.py`.
    - Ensure the satellite (e.g., Apps Script) has an `auth_key` check.
2. **Built-in Logic**:
    - Add logic to `src/api/router.py` or create a new handler in `src/bot/`.
3. **Deployment**:
    - Use `gcloud builds submit` for manual tests.
    - Push to `main` for production CI/CD.

## 🚦 Constraints

- **Free Tier**: Keep resources within Google Cloud Free Tier limits (1 CPU, 512Mi RAM).
- **Security**: The `SHARED_SECRET` (ORCHESTRATOR_SECRET) MUST be present in every inter-service call.
- **Logging**: Use the structured logger from `src.core.config`.

---
*Note: This file is a project standard. Updated 2026-02-10.*
