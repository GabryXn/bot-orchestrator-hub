"""
Pydantic models for the Bot Orchestrator.
Defines standardized request/response schemas for all communication.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# =============================================================================
# ENUMS
# =============================================================================

class Platform(str, Enum):
    """Supported messaging platforms."""
    TELEGRAM = "telegram"
    # Future: DISCORD = "discord", SLACK = "slack", etc.


class ParseMode(str, Enum):
    """Telegram message parse modes."""
    HTML = "HTML"
    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"


# =============================================================================
# TELEGRAM WEBHOOK MODELS
# =============================================================================

class TelegramUser(BaseModel):
    """Telegram user object."""
    id: int
    is_bot: bool = False
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    """Telegram chat object."""
    id: int
    type: str  # "private", "group", "supergroup", "channel"
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramMessage(BaseModel):
    """Telegram message object (simplified)."""
    message_id: int
    date: int
    chat: TelegramChat
    from_user: Optional[TelegramUser] = Field(None, alias="from")
    text: Optional[str] = None
    # Add more fields as needed: photo, document, etc.

    class Config:
        populate_by_name = True


class CallbackQuery(BaseModel):
    """Telegram callback query object."""
    id: str
    from_user: TelegramUser = Field(..., alias="from")
    message: Optional[TelegramMessage] = None
    data: Optional[str] = None
    chat_instance: Optional[str] = None

class TelegramUpdate(BaseModel):
    """Telegram webhook update object."""
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    callback_query: Optional[CallbackQuery] = None


# =============================================================================
# STANDARDIZED PROTOCOL MODELS
# =============================================================================

class SatelliteRequestParams(BaseModel):
    """Parameters sent to satellite scripts."""
    chat_id: int
    user_id: Optional[int] = None
    text: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    extra: Optional[Dict[str, Any]] = None


class SatelliteRequest(BaseModel):
    """
    Standardized request format: Orchestrator → Satellite Script.
    Used when calling external Apps Scripts or services.
    """
    auth_key: str
    action: str
    source: Platform = Platform.TELEGRAM
    params: SatelliteRequestParams


class SatelliteResponse(BaseModel):
    """
    Expected response format: Satellite Script → Orchestrator.
    """
    success: bool
    action: str
    data: Optional[Dict[str, Any]] = None
    reply_message: Optional[str] = None
    error: Optional[str] = None


# =============================================================================
# PROACTIVE MESSAGE API MODELS
# =============================================================================

class InlineKeyboardButton(BaseModel):
    """Single inline keyboard button."""
    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None


class InlineKeyboardMarkup(BaseModel):
    """Inline keyboard markup (rows of buttons)."""
    inline_keyboard: List[List[InlineKeyboardButton]]


class MessageTarget(BaseModel):
    """Target for a proactive message."""
    chat_id: int


class MessageContent(BaseModel):
    """Content of a proactive message."""
    text: str
    parse_mode: Optional[ParseMode] = None
    disable_notification: bool = False
    reply_markup: Optional[InlineKeyboardMarkup] = None


class ProactiveMessageRequest(BaseModel):
    """
    Request format: External Script → Orchestrator (to send a message).
    POST /api/send
    """
    auth_key: str
    action: str = "send_message"
    platform: Platform = Platform.TELEGRAM
    target: MessageTarget
    message: MessageContent


class ProactiveMessageResponse(BaseModel):
    """Response from the proactive message API."""
    success: bool
    message_id: Optional[int] = None
    error: Optional[str] = None


class EditMessageRequest(BaseModel):
    """
    Request format: External Script → Orchestrator (to edit a message).
    POST /api/edit
    """
    auth_key: str
    platform: Platform = Platform.TELEGRAM
    target: MessageTarget
    message_id: int
    message: MessageContent


# =============================================================================
# INTERNAL MODELS
# =============================================================================

class CommandConfig(BaseModel):
    """Configuration for a bot command."""
    name: str  # e.g., "/test"
    description: str
    handler_type: str  # "builtin" or "satellite"
    target_url: Optional[str] = None  # For satellite commands
    action_name: Optional[str] = None  # Action to send to satellite


class RouterContext(BaseModel):
    """Context passed through the routing pipeline."""
    platform: Platform
    chat_id: int
    user_id: Optional[int]
    username: Optional[str]
    text: str
    is_command: bool
    command: Optional[str] = None
    command_args: Optional[str] = None
    raw_update: Dict[str, Any]
