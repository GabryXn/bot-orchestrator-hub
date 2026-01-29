"""
Configuration for the Bot Orchestrator.
Loads environment variables and defines the command registry.
"""

import os
from typing import Dict, Any


# =============================================================================
# ENVIRONMENT VARIABLES
# =============================================================================

# Telegram Bot Token - REQUIRED
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()

# Shared secret for authenticating satellite scripts and API calls
ORCHESTRATOR_SECRET = os.getenv("ORCHESTRATOR_SECRET", "dev-secret-key").strip()

# Project metadata
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "bot-orchestrator-hub")
SERVICE_NAME = os.getenv("SERVICE_NAME", "bot-orchestrator")

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Telegram API base URL
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =============================================================================
# COMMAND REGISTRY
# =============================================================================
# 
# This is the central registry for all bot commands.
# To add a new command:
#   1. Add an entry to COMMAND_REGISTRY below
#   2. If handler_type is "builtin", implement the handler in handlers/commands.py
#   3. If handler_type is "satellite", provide the target_url and action_name
#
# Format:
#   "/command": {
#       "description": "Human-readable description",
#       "handler_type": "builtin" | "satellite",
#       "target_url": "https://...",  # Only for satellite
#       "action_name": "action_to_call",  # Only for satellite
#   }

COMMAND_REGISTRY: Dict[str, Dict[str, Any]] = {
    "/start": {
        "description": "Messaggio di benvenuto",
        "handler_type": "builtin",
    },
    "/help": {
        "description": "Mostra tutti i comandi disponibili",
        "handler_type": "builtin",
    },
    "/test": {
        "description": "Test di funzionamento del bot (debug)",
        "handler_type": "builtin",
    },
    "/ping": {
        "description": "Verifica che il bot sia online",
        "handler_type": "builtin",
    },
    "/status": {
        "description": "Mostra lo stato del sistema",
        "handler_type": "builtin",
    },
    "/sheet": {
        "description": "Apri il foglio spese",
        "handler_type": "satellite",
        "target_url": "https://script.google.com/macros/s/AKfycbwSICkW_XDdpaK89VvrAAnTvIhD6TVNMX6Z9i5cXEYJ9qAPit8GRfp0n3fjPoaAOjVY/exec",
        "action_name": "get_sheet_link",
    },
    # ==========================================================================
    # SATELLITE COMMANDS
    # ==========================================================================
    "/report": {
        "description": "Genera report spese palestra",
        "handler_type": "satellite",
        "target_url": "https://script.google.com/macros/s/AKfycbwSICkW_XDdpaK89VvrAAnTvIhD6TVNMX6Z9i5cXEYJ9qAPit8GRfp0n3fjPoaAOjVY/exec",
        "action_name": "process_gym_receipts",
    },
}


# =============================================================================
# PLATFORM CONFIGURATION
# =============================================================================

# Telegram API base URL
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =============================================================================
# VALIDATION
# =============================================================================

def validate_config() -> bool:
    """
    Validate that required configuration is present.
    Returns True if valid, raises ValueError otherwise.
    """
    errors = []
    
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN environment variable is not set")
    
    if ORCHESTRATOR_SECRET == "dev-secret-key":
        # Warning but not error - acceptable for development
        import logging
        logging.warning("ORCHESTRATOR_SECRET is using default value. Set a secure secret in production!")
    
    if errors:
        raise ValueError("Configuration errors: " + "; ".join(errors))
    
    return True
