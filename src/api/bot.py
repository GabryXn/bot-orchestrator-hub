"""
Bot API Endpoints.
Handles Telegram webhooks and proactive messaging.
"""

from typing import Any, Dict
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Depends
from pydantic import ValidationError
import structlog

from src.core.config import ORCHESTRATOR_SECRET, TELEGRAM_TOKEN
from src.bot.models import (
    TelegramUpdate,
    ProactiveMessageRequest,
    ProactiveMessageResponse,
    EditMessageRequest,
)
from src.bot.router import parse_telegram_update, route_message
from src.bot.client import telegram_client

logger = structlog.get_logger(__name__)

router = APIRouter()

# =============================================================================
# TELEGRAM WEBHOOK
# =============================================================================

async def process_telegram_update(update_data: Dict[str, Any]):
    """
    Background task to process Telegram updates.
    """
    try:
        # Parse the update
        update = TelegramUpdate(**update_data)
        
        # Create router context
        ctx = parse_telegram_update(update)
        
        if ctx:
            # Route the message
            await route_message(ctx)
        else:
            logger.debug("Update could not be parsed into context")
            
    except ValidationError as e:
        logger.warning(f"Invalid Telegram update format: {e}")
    except Exception as e:
        logger.error(f"Error processing Telegram update: {e}", exc_info=True)


@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Telegram webhook endpoint.
    Immediate 200 OK to prevent retries.
    """
    try:
        data = await request.json()
        logger.debug(f"Received webhook: {data.get('update_id')}")
        
        background_tasks.add_task(process_telegram_update, data)
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"ok": True, "error": "Processing error"}


# =============================================================================
# PROACTIVE MESSAGING
# =============================================================================

@router.post("/api/send", response_model=ProactiveMessageResponse)
async def send_proactive_message(request: ProactiveMessageRequest):
    """
    API endpoint to send messages via the bot.
    """
    if request.auth_key != ORCHESTRATOR_SECRET:
        logger.warning("Unauthorized API call attempt")
        raise HTTPException(status_code=401, detail="Invalid auth_key")
    
    if request.platform.value == "telegram":
        try:
            reply_markup = None
            if request.message.reply_markup:
                reply_markup = request.message.reply_markup.model_dump(exclude_none=True)
            
            result = await telegram_client.send_message(
                chat_id=request.target.chat_id,
                text=request.message.text,
                parse_mode=request.message.parse_mode,
                disable_notification=request.message.disable_notification,
                reply_markup=reply_markup,
            )
            
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                return ProactiveMessageResponse(success=True, message_id=message_id)
            else:
                error = result.get("error", "Unknown error")
                return ProactiveMessageResponse(success=False, error=error)
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return ProactiveMessageResponse(success=False, error=str(e))
    
    return ProactiveMessageResponse(success=False, error="Platform not supported")


@router.post("/api/edit", response_model=ProactiveMessageResponse)
async def edit_message(request: EditMessageRequest):
    """
    API endpoint to edit existing messages.
    """
    if request.auth_key != ORCHESTRATOR_SECRET:
        raise HTTPException(status_code=401, detail="Invalid auth_key")
    
    if request.platform.value == "telegram":
        try:
            reply_markup = None
            if request.message.reply_markup:
                reply_markup = request.message.reply_markup.model_dump(exclude_none=True)
            
            result = await telegram_client.edit_message_text(
                chat_id=request.target.chat_id,
                message_id=request.message_id,
                text=request.message.text,
                parse_mode=request.message.parse_mode,
                reply_markup=reply_markup,
            )
            
            if result.get("ok"):
                return ProactiveMessageResponse(success=True, message_id=request.message_id)
            else:
                error = result.get("error", "Unknown error")
                return ProactiveMessageResponse(success=False, error=error)
                
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return ProactiveMessageResponse(success=False, error=str(e))
            
    return ProactiveMessageResponse(success=False, error="Platform not supported")


# =============================================================================
# ADMIN
# =============================================================================

@router.get("/admin/webhook-info")
async def get_webhook_info():
    """Get current Telegram webhook configuration."""
    if not TELEGRAM_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    return await telegram_client.get_webhook_info()


@router.post("/admin/set-webhook")
async def set_webhook(webhook_url: str):
    """Set the Telegram webhook URL."""
    if not TELEGRAM_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    
    result = await telegram_client.set_webhook(webhook_url)
    
    if result.get("ok"):
        return {"success": True, "webhook_url": webhook_url}
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))
