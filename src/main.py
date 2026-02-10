"""
Bot Orchestrator Hub - Main Application

A centralized, extensible bot orchestrator for managing messaging across platforms.
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.config import TELEGRAM_TOKEN, validate_config
from src.core.logging import configure_logging
from src.bot.client import telegram_client

# Import Routers
from src.api.bot import router as bot_router
from src.api.services import router as services_router

# Configure logging immediately
configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("🚀 Bot Orchestrator Hub starting...")
    
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


app = FastAPI(
    title="Bot Orchestrator Hub",
    description="Centralized bot orchestrator for multi-platform messaging and cloud services",
    version="2.0.0",
    lifespan=lifespan,
)

# Register Routers
app.include_router(bot_router)
app.include_router(services_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "bot-orchestrator-hub",
        "version": "2.0.0"
    }


@app.get("/")
async def root():
    """Root info endpoint."""
    return {
        "service": "Bot Orchestrator Hub",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }
