"""
Telegram API client wrapper.
Provides async methods for interacting with the Telegram Bot API.

Features:
- Connection pooling for performance
- Graceful shutdown support
- Comprehensive error handling
"""

import logging
from typing import Optional, Dict, Any, Union

import httpx

from src.core.config import TELEGRAM_API_BASE, TELEGRAM_TOKEN
from src.bot.models import ParseMode

logger = logging.getLogger(__name__)


class TelegramClient:
    """
    Async client for Telegram Bot API with connection pooling.
    
    Uses a persistent httpx.AsyncClient for better performance
    through connection reuse.
    """
    
    def __init__(self) -> None:
        self.base_url = TELEGRAM_API_BASE
        self.token = TELEGRAM_TOKEN
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client. Call on application shutdown."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("Telegram client closed")
    
    async def _request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Telegram API."""
        url = f"{self.base_url}/{method}"
        client = await self._get_client()
        
        try:
            response = await client.post(url, json=data)
            result = response.json()
            
            if not result.get("ok"):
                logger.error(f"Telegram API error: {result}")
                return {"ok": False, "error": result.get("description", "Unknown error")}
            
            return result
        except httpx.TimeoutException as e:
            logger.error(f"Telegram API timeout: {e}")
            return {"ok": False, "error": f"Request timeout: {e}"}
        except httpx.RequestError as e:
            logger.error(f"Telegram API request error: {e}")
            return {"ok": False, "error": f"Request failed: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error calling Telegram: {e}")
            return {"ok": False, "error": str(e)}
    
    async def _get_request(self, method: str) -> Dict[str, Any]:
        """Make a GET request to the Telegram API."""
        url = f"{self.base_url}/{method}"
        client = await self._get_client()
        
        try:
            response = await client.get(url)
            return response.json()
        except Exception as e:
            logger.error(f"GET request failed: {e}")
            return {"ok": False, "error": str(e)}
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[Union[ParseMode, str]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a text message to a chat.
        
        Args:
            chat_id: Target chat ID
            text: Message text
            parse_mode: Optional parse mode (HTML, Markdown, MarkdownV2)
            disable_notification: Send silently
            reply_to_message_id: Reply to a specific message
            reply_markup: Optional inline keyboard markup
            
        Returns:
            Telegram API response
        """
        data: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode.value if isinstance(parse_mode, ParseMode) else parse_mode
        if disable_notification:
            data["disable_notification"] = True
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        return await self._request("sendMessage", data)
    
    async def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: Optional[Union[ParseMode, str]] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Edit the text of an existing message.
        
        Args:
            chat_id: Target chat ID
            message_id: ID of the message to edit
            text: New message text
            parse_mode: Optional parse mode
            reply_markup: Optional inline keyboard markup
            
        Returns:
            Telegram API response
        """
        data: Dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode.value if isinstance(parse_mode, ParseMode) else parse_mode
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        return await self._request("editMessageText", data)
    
    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Set the webhook URL for receiving updates.
        
        Args:
            url: HTTPS URL to receive updates
            secret_token: Optional secret token for verification
            
        Returns:
            Telegram API response
        """
        data: Dict[str, Any] = {"url": url}
        
        if secret_token:
            data["secret_token"] = secret_token
        
        return await self._request("setWebhook", data)
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """Remove the webhook."""
        return await self._request("deleteWebhook", {})
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook status."""
        return await self._get_request("getWebhookInfo")
    
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information."""
        return await self._get_request("getMe")


# Singleton instance
telegram_client = TelegramClient()
