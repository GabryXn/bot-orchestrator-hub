# Project Specification: Telegram Bot Controller Hub on GCP (Serverless)

**Role:** You are a Senior Cloud Architect and Python Developer.
**Objective:** Create, configure, and deploy a centralized Telegram Bot Controller on Google Cloud Run using Python.
**Constraint:** The solution must stay strictly within the **Google Cloud Free Tier** limits (Cloud Run, Artifact Registry, Build).

## 1. Architectural Overview

The system follows a "Hub & Spoke" microservices architecture:

* **The Hub (This Project):** A Python-based `FastAPI` application hosted on Cloud Run. It acts as the router/controller.
* **The Spokes (External):** Existing Google Apps Scripts (GAS) deployed as Web Apps.
* **Communication:** The Hub communicates with Spokes via asynchronous HTTPS requests (RPC style).

## 2. Core Functional Requirements

### A. Asynchronous Webhook Handling (Critical)

* **Problem to Solve:** Telegram retry loops caused by slow processing.
* **Requirement:** The Webhook endpoint must accept the `POST` request from Telegram, immediately return `HTTP 200 OK` to close the connection, and process the logic using **Background Tasks** (e.g., FastAPI `BackgroundTasks`).
* **Stack:** Use `FastAPI` (ASGI) and `uvicorn`. Use `httpx` for asynchronous HTTP client calls to the external scripts.

### B. Standardized Command Dispatcher

* **Requirement:** The bot must map specific Telegram slash commands (e.g., `/report`, `/stock`) to specific external Apps Script URLs.
* **Implementation:**
  * Create a scalable configuration structure (e.g., a Dictionary or JSON config) mapping: `Command -> {Target_URL, Action_Name, Description}`.
  * The system must be easily extensible. Adding a new command should only require updating this config, not the core logic.

### C. Standardized Protocol (RPC Interface)

* **Requirement:** When calling a Satellite Script (GAS), the Hub must send a standardized JSON payload.
* **Payload Schema:**

    ```json
    {
      "auth_key": "<SECRET_ENV_VAR>",
      "action": "<function_name_defined_in_config>",
      "params": {
         "chat_id": "<telegram_chat_id>",
         "text": "<full_message_text>",
         "user_id": "<telegram_user_id>"
      }
    }
    ```

### D. AI Readiness

* **Requirement:** Structure the code to easily allow the injection of an AI Logic layer (e.g., Gemini/OpenAI) in the future to handle non-command messages (natural language query parsing).

## 3. Implementation Steps for the Agent

### Step 1: Project Structure & Code Generation

Generate the following file structure:

* `main.py`: Contains the FastAPI app, webhook route, background processor, and command dispatcher logic.
* `config.py`: Contains the `COMMAND_MAP` and environment variable loading.
* `requirements.txt`: Must include `fastapi`, `uvicorn`, `httpx`, `pydantic`.
* `Dockerfile`: Optimized for Python (slim), exposing port 8080 (Cloud Run default).

### Step 2: Deployment Scripts (gcloud CLI)

Create a shell script (`deploy.sh`) or provide the exact `gcloud` commands to:

1. **Project Setup:** Set the current project ID.
2. **Build:** Submit the build to Cloud Build or build locally and push to Artifact Registry (`gcloud builds submit` or `docker push`).
3. **Deploy:** Deploy the container to **Cloud Run** with the following flags:
    * `--platform managed`
    * `--allow-unauthenticated` (Required for Telegram Webhook).
    * `--region us-central1` (or a Tier 1 region compatible with Free Tier).
    * `--memory 512Mi` (Keep it low for free tier).
    * `--max-instances 1` (To prevent cost overruns, can be increased later).
    * `--set-env-vars` for `TELEGRAM_TOKEN` and `SATELLITE_SECRET_KEY`.

## 4. Execution Instructions

Please generate the complete codebase based on these specifications. Once the code is generated, guide me through the execution of the deployment commands using my installed `gcloud` CLI.
