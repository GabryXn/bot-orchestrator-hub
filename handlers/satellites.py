"""
Satellite script dispatcher.
Handles communication with external Apps Scripts and services.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

from models import RouterContext, SatelliteRequest, SatelliteRequestParams, SatelliteResponse
from config import ORCHESTRATOR_SECRET

logger = logging.getLogger(__name__)


async def dispatch_to_satellite(
    ctx: RouterContext,
    target_url: str,
    action_name: str,
) -> Optional[str]:
    """
    Send a request to a satellite script and return its response.
    
    Args:
        ctx: Router context with message information
        target_url: URL of the satellite script
        action_name: Action to execute on the satellite
        
    Returns:
        Reply message from the satellite, or error message
    """
    # Build standardized request
    request = SatelliteRequest(
        auth_key=ORCHESTRATOR_SECRET,
        action=action_name,
        source=ctx.platform,
        params=SatelliteRequestParams(
            chat_id=ctx.chat_id,
            user_id=ctx.user_id,
            text=ctx.text,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    )
    
    logger.info(f"Dispatching to satellite: {target_url} | action: {action_name}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                target_url,
                json=request.model_dump(),
                timeout=30.0,
                follow_redirects=True,  # Apps Scripts redirect on POST
            )
            
            # Try to parse as our standard response format
            try:
                data = response.json()
                satellite_response = SatelliteResponse(**data)
                
                if satellite_response.success:
                    return satellite_response.reply_message or "✅ Operazione completata."
                else:
                    error = satellite_response.error or "Errore sconosciuto"
                    logger.error(f"Satellite returned error: {error}")
                    return f"❌ Errore dallo script: {error}"
                    
            except Exception as parse_error:
                # Script didn't return our standard format - just use raw response
                logger.warning(f"Could not parse satellite response: {parse_error}")
                return f"📩 Risposta: {response.text[:500]}"
                
    except httpx.TimeoutException:
        logger.error(f"Timeout calling satellite: {target_url}")
        return "⏱️ Lo script esterno ha impiegato troppo tempo. Riprova più tardi."
        
    except Exception as e:
        logger.error(f"Error calling satellite: {e}")
        return f"❌ Errore di comunicazione con lo script: {str(e)}"


async def call_satellite_action(
    target_url: str,
    action_name: str,
    params: Dict[str, Any],
) -> SatelliteResponse:
    """
    Low-level function to call a satellite with custom parameters.
    Used internally or for non-command triggers.
    
    Args:
        target_url: URL of the satellite script
        action_name: Action to execute
        params: Custom parameters to send
        
    Returns:
        SatelliteResponse object
    """
    request_data = {
        "auth_key": ORCHESTRATOR_SECRET,
        "action": action_name,
        "params": params,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                target_url,
                json=request_data,
                timeout=30.0,
                follow_redirects=True,
            )
            
            data = response.json()
            return SatelliteResponse(**data)
            
    except Exception as e:
        logger.error(f"Error in call_satellite_action: {e}")
        return SatelliteResponse(
            success=False,
            action=action_name,
            error=str(e),
        )
