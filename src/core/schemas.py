from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

class HubRequest(BaseModel):
    """
    Standard request payload from Hub to Satellite (Spoke).
    """
    auth_key: str = Field(..., description="Shared secret for authentication")
    action: str = Field(..., description="Action identifier (e.g., 'process_gym_receipts')")
    source: Literal["telegram", "discord", "scheduler", "manual"] = Field("telegram", description="Source of the trigger")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters (chat_id, user_id, text, etc.)")

class SatelliteResponse(BaseModel):
    """
    Standard response payload from Satellite to Hub.
    """
    success: bool = Field(..., description="Whether the action was successful")
    action: Optional[str] = Field(None, description="Echo of the requested action")
    reply_message: Optional[str] = Field(None, description="Message to send back to the user")
    reply_markup: Optional[Dict[str, Any]] = Field(None, description="Telegram/Discord keyboard markup")
    data: Optional[Dict[str, Any]] = Field(None, description="Any additional structured data returned")
    error: Optional[str] = Field(None, description="Error message if success is False")
