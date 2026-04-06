# Security Policy

## Supported Versions

This project is actively maintained. Security fixes are applied to the latest version on `master`.

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

Please report security issues by emailing the maintainer directly (see the GitHub profile).
Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

You will receive a response within 72 hours. Once confirmed, a fix will be released as soon as possible.

## Security Design Notes

- **Secrets**: All secrets (`TELEGRAM_TOKEN`, `ORCHESTRATOR_SECRET`, `SATELLITE_APPS_SCRIPT_URL`) are loaded exclusively from environment variables or GCP Secret Manager. They are never hardcoded.
- **Satellite authentication**: Every request from the hub to a satellite script includes the `ORCHESTRATOR_SECRET` as a shared HMAC-like bearer. Satellites must validate it before processing.
- **Webhook validation**: Incoming Telegram webhooks are validated against the bot token.
- **No credentials in code**: The `.env` file is gitignored. See `.env.example` for required variables.
