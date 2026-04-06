# Contributing

Thank you for your interest in contributing to Bot Orchestrator Hub.

## Getting Started

```bash
# Clone and set up
git clone <repo>
cd cloud-bot-controller

uv sync --dev

cp .env.example .env
# Edit .env with your credentials

uv run uvicorn src.main:app --reload
```

## Development Workflow

1. Fork the repository and create a feature branch from `master`
2. Make your changes — keep commits atomic and focused
3. Run tests and linting before opening a PR:
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy .
   ```
4. Open a pull request with a clear description of what changed and why

## Code Style

- Python 3.12+, formatted with `ruff format`
- Type annotations required for all public functions
- Logs via `structlog`, not `print`
- No secrets in code — all configuration via environment variables

## Adding a New Satellite Command

See [docs/EXTENDING.md](docs/EXTENDING.md) for the step-by-step guide.

## Reporting Bugs

Open a GitHub issue with reproduction steps and expected vs. actual behavior.
For security vulnerabilities, see [SECURITY.md](SECURITY.md).
