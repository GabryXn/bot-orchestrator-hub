"""
Vertex AI Gemini Service.
Wrapper for Google AI Studio (Generative AI) - Free Tier.
"""

import logging
from typing import Optional
from google import genai
from google.genai import types
from src.core.config import _settings

logger = logging.getLogger(__name__)

class VertexAIService:
    """Service for interacting with Google AI Studio Gemini models (Free Tier)."""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name
        self.client: Optional[genai.Client] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of AI Studio Client."""
        if not self._initialized:
            try:
                if not _settings.gemini_api_key:
                    logger.warning("GEMINI_API_KEY not set. AI features may fail.")
                
                self.client = genai.Client(api_key=_settings.gemini_api_key)
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize AI Studio Client: {e}")
                raise

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        response_mime_type: Optional[str] = None,
    ) -> str:
        """
        Generate content using Gemini via AI Studio.

        Args:
            prompt: User prompt
            system_instruction: System prompt/instruction
            temperature: Randomness (0.0 - 1.0)
            response_mime_type: e.g., "application/json" for JSON mode

        Returns:
            Generated text content
        """
        self._ensure_initialized()

        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type=response_mime_type,
                system_instruction=system_instruction
            )

            # AI Studio SDK (google-genai) supports async
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            return response.text

        except Exception as e:
            logger.error(f"AI Studio Generation Error: {e}")
            raise

# UNUSED: verifica se eliminabile
gemini_service = VertexAIService()
