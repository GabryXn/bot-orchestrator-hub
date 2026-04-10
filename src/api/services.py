"""
Services API Endpoints.
Exposes Gemini and Vision capabilities to external scripts.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog
import base64

from src.core.config import ORCHESTRATOR_SECRET
from src.services.gemini import VertexAIService
from src.services.vision import VisionService

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/services")

# services are lazy loaded
_gemini_service = VertexAIService()
_vision_service = VisionService()

# =============================================================================
# MODELS
# =============================================================================

class GeminiAnalyzeRequest(BaseModel):
    auth_key: str
    user_text: str
    system_instruction: Optional[str] = None
    temperature: float = 0.2
    response_mime_type: Optional[str] = "application/json"

class GeminiResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None

class VisionRequest(BaseModel):
    auth_key: str
    image_base64: str
    mime_type: str = "image/jpeg"

class VisionResponse(BaseModel):
    success: bool
    text: Optional[str] = None
    error: Optional[str] = None

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/gemini/analyze", response_model=GeminiResponse)
async def gemini_analyze(request: GeminiAnalyzeRequest):
    """
    Analyze content using Vertex AI Gemini.
    """
    if request.auth_key != ORCHESTRATOR_SECRET:
        raise HTTPException(status_code=401, detail="Invalid auth_key")

    try:
        content = await _gemini_service.generate_content(
            prompt=request.user_text,
            system_instruction=request.system_instruction,
            temperature=request.temperature,
            response_mime_type=request.response_mime_type,
        )
        return GeminiResponse(success=True, content=content)
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return GeminiResponse(success=False, error=str(e))


@router.post("/vision/ocr", response_model=VisionResponse)
async def vision_ocr(request: VisionRequest):
    """
    Perform OCR on an image or PDF (base64 encoded).
    """
    if request.auth_key != ORCHESTRATOR_SECRET:
        raise HTTPException(status_code=401, detail="Invalid auth_key")

    try:
        # Decode base64
        try:
            content_bytes = base64.b64decode(request.image_base64)
        except Exception:
             return VisionResponse(success=False, error="Invalid base64 content")

        text = _vision_service.ocr_document(
            content=content_bytes,
            mime_type=request.mime_type
        )
        return VisionResponse(success=True, text=text)

    except Exception as e:
        logger.error(f"Vision API Error: {e}")
        return VisionResponse(success=False, error=str(e))
