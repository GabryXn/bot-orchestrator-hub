"""
Telegram API client wrapper.
Provides async methods for interacting with the Telegram Bot API.
"""

import logging
from typing import Optional, Dict, Any
import httpx

from config import TELEGRAM_API_BASE, TELEGRAM_TOKEN
from models import ParseMode

logger = logging.getLogger(__name__)


class TelegramClient:
    """Async client for Telegram Bot API."""
    
    def __init__(self):
        self.base_url = TELEGRAM_API_BASE
        self.token = TELEGRAM_TOKEN
    
    async def _request(self, method: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Telegram API."""
        url = f"{self.base_url}/{method}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, timeout=30.0)
                result = response.json()
                
                if not result.get("ok"):
                    logger.error(f"Telegram API error: {result}")
                    return {"ok": False, "error": result.get("description", "Unknown error")}
                
                return result
            except Exception as e:
                logger.error(f"Request to Telegram failed: {e}")
                return {"ok": False, "error": str(e)}
    
    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: Optional[ParseMode] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Send a text message to a chat.
        
        Args:
            chat_id: Target chat ID
            text: Message text
            parse_mode: Optional parse mode (HTML, Markdown, MarkdownV2)
            disable_notification: Send silently
            reply_to_message_id: Reply to a specific message
            
        Returns:
            Telegram API response
        """
        data = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode:
            data["parse_mode"] = parse_mode.value
        if disable_notification:
            data["disable_notification"] = True
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        
        return await self._request("sendMessage", data)
    
    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Set the webhook URL for receiving updates.
        
        Args:
            url: HTTPS URL to receive updates
            secret_token: Optional secret token for verification
            
        Returns:
            Telegram API response
        """
        data = {"url": url}
        
        if secret_token:
            data["secret_token"] = secret_token
        
        return await self._request("setWebhook", data)
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """Remove the webhook."""
        return await self._request("deleteWebhook", {})
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/getWebhookInfo")
            return response.json()
    
    async def get_me(self) -> Dict[str, Any]:
        """Get bot information."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/getMe")
            return response.json()


# Singleton instance
telegram_client = TelegramClient()
