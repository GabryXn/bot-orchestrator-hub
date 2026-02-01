"""
Configuration for the Bot Orchestrator.
Uses Pydantic Settings for environment variable validation and type safety.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# =============================================================================
# SETTINGS CLASS
# =============================================================================


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic Settings automatically reads from:
    1. Environment variables
    2. .env file (if present)

    All fields support type validation and default values.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Core Settings
    # -------------------------------------------------------------------------
    telegram_token: str = Field(default="", description="Telegram Bot API token")
    orchestrator_secret: str = Field(
        default="dev-secret-key",
        description="Shared secret for authenticating satellite scripts",
    )

    # -------------------------------------------------------------------------
    # Project Metadata
    # -------------------------------------------------------------------------
    gcp_project_id: str = Field(
        default="bot-orchestrator-hub",
        description="Google Cloud Project ID",
    )
    service_name: str = Field(
        default="bot-orchestrator",
        description="Cloud Run service name",
    )

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return upper

    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    @property
    def telegram_api_base(self) -> str:
        """Telegram API base URL."""
        return f"https://api.telegram.org/bot{self.telegram_token}"

    @property
    def is_production(self) -> bool:
        """Check if running in production (non-default secret)."""
        return self.orchestrator_secret != "dev-secret-key"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to avoid re-reading environment on every access.
    """
    return Settings()


# =============================================================================
# BACKWARDS COMPATIBILITY - Export as module-level constants
# =============================================================================
# These provide backward compatibility with existing code that imports
# TELEGRAM_TOKEN, ORCHESTRATOR_SECRET, etc. directly from config.

_settings = get_settings()

TELEGRAM_TOKEN: str = _settings.telegram_token
ORCHESTRATOR_SECRET: str = _settings.orchestrator_secret
PROJECT_ID: str = _settings.gcp_project_id
SERVICE_NAME: str = _settings.service_name
LOG_LEVEL: str = _settings.log_level
TELEGRAM_API_BASE: str = _settings.telegram_api_base


# =============================================================================
# COMMAND REGISTRY
# =============================================================================
#
# Central registry for all bot commands.
# To add a new command:
#   1. Add an entry to COMMAND_REGISTRY below
#   2. If handler_type is "builtin", implement the handler in handlers/commands.py
#   3. If handler_type is "satellite", provide the target_url and action_name
#

COMMAND_REGISTRY: dict[str, dict[str, Any]] = {
    "/start": {
        "description": "Messaggio di benvenuto",
        "handler_type": "builtin",
        "category": "Comandi di Base",
    },
    "/help": {
        "description": "Mostra tutti i comandi disponibili",
        "handler_type": "builtin",
        "category": "Comandi di Base",
    },
    "/test": {
        "description": "Test di funzionamento del bot (debug)",
        "handler_type": "builtin",
        "category": "Admin & Debug",
    },
    "/ping": {
        "description": "Verifica che il bot sia online",
        "handler_type": "builtin",
        "category": "Admin & Debug",
    },
    "/status": {
        "description": "Mostra lo stato del sistema",
        "handler_type": "builtin",
        "category": "Admin & Debug",
    },
    "/sheet": {
        "description": "Apri il foglio spese",
        "handler_type": "satellite",
        "category": "Script Spese",
        "target_url": "https://script.google.com/macros/s/REDACTED_SCRIPT_ID/exec",
        "action_name": "get_sheet_link",
    },
    # ==========================================================================
    # SATELLITE COMMANDS
    # ==========================================================================
    "/report": {
        "description": "Genera report spese palestra",
        "handler_type": "satellite",
        "category": "Script Spese",
        "target_url": "https://script.google.com/macros/s/REDACTED_SCRIPT_ID/exec",
        "action_name": "process_gym_receipts",
    },
}


# =============================================================================
# VALIDATION
# =============================================================================


def validate_config() -> bool:
    """
    Validate that required configuration is present.

    Returns True if valid, raises ValueError otherwise.
    """
    errors: list[str] = []

    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN environment variable is not set")

    if ORCHESTRATOR_SECRET == "dev-secret-key":
        # Warning but not error - acceptable for development
        logging.warning(
            "ORCHESTRATOR_SECRET is using default value. Set a secure secret in production!"
        )

    if errors:
        raise ValueError("Configuration errors: " + "; ".join(errors))

    return True
