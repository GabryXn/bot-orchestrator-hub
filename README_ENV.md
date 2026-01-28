# Google Cloud Development Environment & Bot Controller

This directory contains:

1. **GCP_Shared_Env**: A standard Python Virtual Environment intended to be shared across your local GCP projects.
2. **Cloud Bot Controller**: The project files for your Telegram Bot hub.

## 1. Using the Shared Environment

This environment (`GCP_Shared_Env`) is pre-installed with:

* `fastapi`, `uvicorn` (Web Framework)
* `google-cloud-storage`, `pubsub`, `logging` (GCP Standard Libs)
* `functions-framework` (For testing Cloud Functions locally)

### How to use in VSCode

1. Open VSCode in `d:\Desktop\Cloud Bot Controller` (or your future project folder).
2. Open a Python file (e.g., `main.py`).
3. Click the Interpreter selector in the bottom right (or `Ctrl+Shift+P` -> `Python: Select Interpreter`).
4. Choose "Enter interpreter path..." -> "Find..." and browse to:
    `d:\Desktop\Cloud Bot Controller\GCP_Shared_Env\Scripts\python.exe`

**For Future Projects:**
You do NOT need to create a new `venv` or run `pip install` for standard packages. Just configure VSCode to use this same interpreter path.

## 2. Cloud Bot Controller Project

### Structure

* `main.py`: Entry point for the bot. Handles Webhooks.
* `config.py`: Maps slash commands (e.g., `/stock`) to your external Apps Scripts.
* `deploy.sh`: Helper commands to deploy to Cloud Run.

### Local Testing

To run the bot locally using the shared environment:

```powershell
# Activate env (optional if using full path)
.\GCP_Shared_Env\Scripts\Activate.ps1

# Run server
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

### Deployment

1. Ensure you are authenticated:

    ```powershell
    gcloud auth login
    gcloud config set project YOUR_PROJECT_ID
    ```

2. Edit `deploy.sh` to set your PROJECT_ID and env vars.
3. Run the build/deploy commands found in `deploy.sh`.
