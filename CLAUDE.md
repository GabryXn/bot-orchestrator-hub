# CLAUDE.md — Cloud Bot Controller

> Regole workspace globali: vedi `/home/gabry/Documents/Project/CLAUDE.md`

## Progetto

- **Nome:** Cloud Bot Controller
- **Tipo:** Python — Orchestratore serverless per bot Telegram su Google Cloud Run
- **Stack:** Python 3.12 / FastAPI / Uvicorn / Docker / Google Cloud Run / Google Gemini / Structlog
- **Deploy:** Google Cloud Build (`cloudbuild.yaml`) → Cloud Run

## Comandi

```bash
uv sync --dev                       # installa dipendenze + dev
uv run uvicorn main:app --reload    # sviluppo locale
uv run pytest                       # test
uv run ruff check .                 # linting
uv run ruff format .                # formatting
uv run mypy .                       # type checking

# Deploy
gcloud builds submit --config cloudbuild.yaml
```

## Struttura

- `main.py` / `app/` — FastAPI application
- `deploy/` — script e configurazioni di deploy
- `cloudbuild.yaml` — pipeline Google Cloud Build
- `Dockerfile` — immagine Docker multi-stage
- `.env` — variabili d'ambiente (NON committare, vedi `Envioment.txt` per la lista)

## Directory Vietate

- `.venv/`
- `__pycache__/`
- `.env`
- `Envioment.txt` (contiene riferimenti a segreti)

## Regole Operative

- MAI usare `pip` — solo `uv`
- È un **servizio web**, non una libreria — non ha `[build-system]` in pyproject.toml
- Le credenziali Google Cloud vanno via variabili d'ambiente, mai in codice
- Usare `structlog` per tutti i log (non `print`)
- Testare con `pytest-asyncio` per gli endpoint asincroni
- Il Dockerfile usa multi-stage build — non modificare senza capire entrambi gli stage
