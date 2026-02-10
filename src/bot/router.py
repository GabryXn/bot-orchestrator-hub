"""
Message router for the Bot Orchestrator.
Routes incoming messages to the appropriate handlers.
"""

import logging
from typing import Optional

from src.bot.models import RouterContext, TelegramUpdate, Platform
from src.core.config import COMMAND_REGISTRY
from src.bot.handlers.commands import handle_builtin_command
from src.bot.handlers.satellites import dispatch_to_satellite
from src.bot.client import telegram_client

logger = logging.getLogger(__name__)


def parse_telegram_update(update: TelegramUpdate) -> Optional[RouterContext]:
    """
    Parse a Telegram update into a RouterContext.
    
    Args:
        update: Telegram update object
        
    Returns:
        RouterContext or None if update cannot be processed
    """
    message = update.message or update.edited_message
    
    if not message:
        logger.debug("Update has no message")
        return None
    
    if not message.text:
        logger.debug("Message has no text")
        return None
    
    text = message.text.strip()
    is_command = text.startswith("/")
    command = None
    command_args = None
    
    if is_command:
        parts = text.split(maxsplit=1)
        command = parts[0].lower()
        # Remove @botname from command if present (e.g., /test@MyBot)
        if "@" in command:
            command = command.split("@")[0]
        command_args = parts[1] if len(parts) > 1 else None
    
    return RouterContext(
        platform=Platform.TELEGRAM,
        chat_id=message.chat.id,
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        text=text,
        is_command=is_command,
        command=command,
        command_args=command_args,
        raw_update=update.model_dump(),
    )


async def route_message(ctx: RouterContext) -> None:
    """
    Route a message to the appropriate handler and send the response.
    
    Args:
        ctx: Router context with message information
    """
    response: Optional[str] = None
    
    if ctx.is_command and ctx.command:
        # Look up command in registry
        command_config = COMMAND_REGISTRY.get(ctx.command)
        
        if command_config:
            handler_type = command_config.get("handler_type")
            
            if handler_type == "builtin":
                response = await handle_builtin_command(ctx)
            
            elif handler_type == "satellite":
                target_url = command_config.get("target_url")
                action_name = command_config.get("action_name")
                
                if target_url and action_name:
                    response = await dispatch_to_satellite(ctx, target_url, action_name)
                else:
                    response = "⚠️ Comando configurato in modo errato. Contatta l'amministratore."
            
            else:
                response = f"⚠️ Tipo di handler sconosciuto: {handler_type}"
        
        else:
            # Unknown command
            response = (
                f"❓ Comando <code>{ctx.command}</code> non riconosciuto.\n"
                f"Usa /help per vedere i comandi disponibili."
            )
    
    else:
        # Non-command message (conversation)
        # For now, just acknowledge. Future: AI integration here.
        response = await handle_conversation(ctx)
    
    # Send response if we have one
    if response:
        await telegram_client.send_message(
            chat_id=ctx.chat_id,
            text=response,
            parse_mode="HTML",
        )


async def handle_conversation(ctx: RouterContext) -> Optional[str]:
    """
    Handle non-command messages (conversations).
    
    Future: This is where AI/NLU integration would go.
    For now, provide a simple acknowledgment.
    
    Args:
        ctx: Router context with message information
        
    Returns:
        Response message or None
    """
    # Placeholder for future AI integration
    # For now, only respond if message seems like a question or greeting
    
    text_lower = ctx.text.lower()
    
    # Simple greetings
    greetings = ["ciao", "salve", "buongiorno", "buonasera", "hey", "hi", "hello"]
    if any(text_lower.startswith(g) for g in greetings):
        return (
            f"👋 Ciao! Sono il Bot Orchestrator.\n"
            f"Per vedere cosa posso fare, usa il comando /help"
        )
    
    # Don't respond to every message to avoid spam
    # In production, you might want to enable AI here
    logger.info(f"Received non-command message: {ctx.text[:50]}...")
    return None
