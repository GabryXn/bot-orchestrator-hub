"""
Bot Orchestrator Hub - Main Application

A centralized, extensible bot orchestrator for managing messaging across platforms.
Currently supports Telegram, designed for easy expansion to other platforms.

Endpoints:
    POST /webhook          - Telegram webhook receiver
    POST /api/send         - API for external scripts to send messages
    GET  /health           - Health check endpoint
    GET  /                  - Basic info endpoint
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from pydantic import ValidationError

from config import (
    LOG_LEVEL,
    ORCHESTRATOR_SECRET,
    TELEGRAM_TOKEN,
    validate_config,
)
from models import (
    EditMessageRequest,
    ParseMode,
    ProactiveMessageRequest,
    ProactiveMessageResponse,
    TelegramUpdate,
)
from router import parse_telegram_update, route_message
from telegram_client import telegram_client


# =============================================================================
# STRUCTURED LOGGING CONFIGURATION
# =============================================================================

def configure_logging() -> None:
    """Configure structlog for JSON structured logging."""
    # Determine if we're in production (Cloud Run sets this)
    is_production = "K_SERVICE" in __import__("os").environ

    # Configure processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_production:
        # JSON output for Cloud Run logs
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )


configure_logging()
logger = structlog.get_logger(__name__)


# =============================================================================
# APPLICATION LIFECYCLE
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("🚀 Bot Orchestrator Hub starting...")
    
    # Validate configuration (will raise if invalid)
    try:
        if TELEGRAM_TOKEN:
            validate_config()
            bot_info = await telegram_client.get_me()
            if bot_info.get("ok"):
                bot_name = bot_info.get("result", {}).get("username", "Unknown")
                logger.info(f"✅ Connected to Telegram bot: @{bot_name}")
            else:
                logger.warning("⚠️ Could not verify Telegram bot connection")
        else:
            logger.warning("⚠️ TELEGRAM_TOKEN not set - Telegram features disabled")
    except Exception as e:
        logger.error(f"❌ Startup validation failed: {e}")
    
    logger.info("✅ Bot Orchestrator Hub ready!")
    
    yield
    
    # Shutdown
    logger.info("👋 Bot Orchestrator Hub shutting down...")
    await telegram_client.close()
    logger.info("✅ Cleanup complete")


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="Bot Orchestrator Hub",
    description="Centralized bot orchestrator for multi-platform messaging",
    version="1.0.0",
    lifespan=lifespan,
)


# =============================================================================
# TELEGRAM WEBHOOK ENDPOINT
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


@app.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Telegram webhook endpoint.
    
    Immediately returns 200 OK and processes the update in the background
    to prevent Telegram retry loops.
    """
    try:
        data = await request.json()
        logger.debug(f"Received webhook: {data.get('update_id')}")
        
        # Process in background
        background_tasks.add_task(process_telegram_update, data)
        
        return {"ok": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        # Return 200 anyway to prevent Telegram retries
        return {"ok": True, "error": "Processing error"}


# =============================================================================
# PROACTIVE MESSAGE API
# =============================================================================

@app.post("/api/send", response_model=ProactiveMessageResponse)
async def send_proactive_message(request: ProactiveMessageRequest):
    """
    API endpoint for external scripts to send messages through the bot.
    
    This allows Apps Scripts and other services to trigger bot messages
    (e.g., sending notifications when a scheduled task completes).
    
    Authentication: Include the ORCHESTRATOR_SECRET in the auth_key field.
    """
    # Verify authentication
    if request.auth_key != ORCHESTRATOR_SECRET:
        logger.warning(f"Unauthorized API call attempt")
        raise HTTPException(status_code=401, detail="Invalid auth_key")
    
    # Route based on platform
    if request.platform.value == "telegram":
        try:
            # Convert reply_markup to dict if present
            reply_markup = None
            if request.message.reply_markup:
                reply_markup = request.message.reply_markup.model_dump()
            
            result = await telegram_client.send_message(
                chat_id=request.target.chat_id,
                text=request.message.text,
                parse_mode=request.message.parse_mode,
                disable_notification=request.message.disable_notification,
                reply_markup=reply_markup,
            )
            
            if result.get("ok"):
                message_id = result.get("result", {}).get("message_id")
                logger.info(f"Proactive message sent: {message_id}")
                return ProactiveMessageResponse(success=True, message_id=message_id)
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Failed to send proactive message: {error}")
                return ProactiveMessageResponse(success=False, error=error)
                
        except Exception as e:
            logger.error(f"Error sending proactive message: {e}")
            return ProactiveMessageResponse(success=False, error=str(e))
    
    else:
        return ProactiveMessageResponse(
            success=False, 
            error=f"Platform {request.platform.value} not yet supported"
        )


@app.post("/api/edit", response_model=ProactiveMessageResponse)
async def edit_message(request: EditMessageRequest):
    """
    API endpoint for external scripts to edit existing messages.
    
    Useful for progress indicators: send initial message, then edit with final result.
    
    Authentication: Include the ORCHESTRATOR_SECRET in the auth_key field.
    """
    # Verify authentication
    if request.auth_key != ORCHESTRATOR_SECRET:
        logger.warning(f"Unauthorized API edit attempt")
        raise HTTPException(status_code=401, detail="Invalid auth_key")
    
    # Route based on platform
    if request.platform.value == "telegram":
        try:
            # Convert reply_markup to dict if present
            reply_markup = None
            if request.message.reply_markup:
                reply_markup = request.message.reply_markup.model_dump()
            
            result = await telegram_client.edit_message_text(
                chat_id=request.target.chat_id,
                message_id=request.message_id,
                text=request.message.text,
                parse_mode=request.message.parse_mode,
                reply_markup=reply_markup,
            )
            
            if result.get("ok"):
                logger.info(f"Message {request.message_id} edited successfully")
                return ProactiveMessageResponse(success=True, message_id=request.message_id)
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Failed to edit message: {error}")
                return ProactiveMessageResponse(success=False, error=error)
                
        except Exception as e:
            logger.error(f"Error editing message: {e}")
            return ProactiveMessageResponse(success=False, error=str(e))
    
    else:
        return ProactiveMessageResponse(
            success=False, 
            error=f"Platform {request.platform.value} not yet supported"
        )


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run and monitoring."""
    return {
        "status": "healthy",
        "service": "bot-orchestrator-hub",
        "telegram_configured": bool(TELEGRAM_TOKEN),
    }


@app.get("/")
async def root():
    """Root endpoint with basic service info."""
    return {
        "service": "Bot Orchestrator Hub",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "webhook": "POST /webhook",
            "send": "POST /api/send",
            "health": "GET /health",
        }
    }


# =============================================================================
# ADMIN ENDPOINTS (for setup/debugging)
# =============================================================================

@app.get("/admin/webhook-info")
async def get_webhook_info():
    """Get current Telegram webhook configuration. For debugging."""
    if not TELEGRAM_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    
    return await telegram_client.get_webhook_info()


@app.post("/admin/set-webhook")
async def set_webhook(webhook_url: str):
    """
    Set the Telegram webhook URL.
    
    Call this after deployment to configure Telegram to send updates to this service.
    Example: POST /admin/set-webhook?webhook_url=https://your-service-xyz.run.app/webhook
    """
    if not TELEGRAM_TOKEN:
        raise HTTPException(status_code=400, detail="Telegram not configured")
    
    result = await telegram_client.set_webhook(webhook_url)
    
    if result.get("ok"):
        logger.info(f"Webhook set to: {webhook_url}")
        return {"success": True, "webhook_url": webhook_url}
    else:
        error = result.get("error", "Unknown error")
        logger.error(f"Failed to set webhook: {error}")
        raise HTTPException(status_code=500, detail=error)
