"""
Built-in command handlers.
These commands are handled directly by the orchestrator without calling external services.
"""

import logging
from datetime import datetime
from typing import Optional

from models import RouterContext
from config import COMMAND_REGISTRY
from telegram_client import telegram_client

logger = logging.getLogger(__name__)


async def handle_builtin_command(ctx: RouterContext) -> Optional[str]:
    """
    Handle a built-in command.
    
    Args:
        ctx: Router context with command information
        
    Returns:
        Response message or None if command not found
    """
    command = ctx.command
    
    if command == "/start":
        return await _handle_start(ctx)
    elif command == "/help":
        return await _handle_help(ctx)
    elif command == "/test":
        return await _handle_test(ctx)
    elif command == "/ping":
        return await _handle_ping(ctx)
    else:
        return None


async def _handle_start(ctx: RouterContext) -> str:
    """Welcome message for new users."""
    username = ctx.username or "utente"
    return (
        f"👋 Ciao {username}!\n\n"
        f"Sono il <b>Bot Orchestrator Hub</b>, il tuo assistente centralizzato.\n\n"
        f"Usa /help per vedere tutti i comandi disponibili."
    )


async def _handle_help(ctx: RouterContext) -> str:
    """List all available commands."""
    lines = ["📋 <b>Comandi disponibili:</b>\n"]
    
    for cmd, config in COMMAND_REGISTRY.items():
        description = config.get("description", "Nessuna descrizione")
        handler_type = config.get("handler_type", "unknown")
        type_emoji = "🔧" if handler_type == "builtin" else "🔗"
        lines.append(f"{type_emoji} {cmd} - {description}")
    
    lines.append("\n💡 <i>Legenda: 🔧 = comando interno, 🔗 = script esterno</i>")
    
    return "\n".join(lines)


async def _handle_test(ctx: RouterContext) -> str:
    """Test command for debugging."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    return (
        f"✅ <b>Test riuscito!</b>\n\n"
        f"📊 <b>Dettagli:</b>\n"
        f"• Platform: {ctx.platform.value}\n"
        f"• Chat ID: <code>{ctx.chat_id}</code>\n"
        f"• User ID: <code>{ctx.user_id}</code>\n"
        f"• Username: @{ctx.username or 'N/A'}\n"
        f"• Timestamp: {now}\n"
        f"• Command: {ctx.command}\n"
        f"• Args: {ctx.command_args or '(nessuno)'}\n\n"
        f"🟢 Il bot è operativo e funzionante!"
    )


async def _handle_ping(ctx: RouterContext) -> str:
    """Simple ping response."""
    return "🏓 Pong! Il bot è online."
