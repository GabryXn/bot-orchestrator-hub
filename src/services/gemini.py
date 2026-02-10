"""
Vertex AI Geminin Service.
Wrapper for Google Cloud Vertex AI (Generative AI).
"""

import logging
from typing import Optional, Any, Dict, List
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content, GenerationConfig
from src.core.config import PROJECT_ID

logger = logging.getLogger(__name__)

class VertexAIService:
    """Service for interacting with Vertex AI Gemini models."""

    def __init__(self, location: str = "europe-west8", model_name: str = "gemini-1.5-flash-001"):
        self.location = location
        self.model_name = model_name
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of Vertex AI."""
        if not self._initialized:
            try:
                vertexai.init(project=PROJECT_ID, location=self.location)
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {e}")
                raise

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        response_mime_type: Optional[str] = None,
    ) -> str:
        """
        Generate content using Gemini.

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
            model = GenerativeModel(
                model_name=self.model_name,
                system_instruction=[system_instruction] if system_instruction else None,
            )

            config = GenerationConfig(
                temperature=temperature,
                response_mime_type=response_mime_type,
            )

            # Note: synchronous call in async wrapper for now, 
            # ideally use async generation if library supports it fully non-blocking
            # or run in executor. Vertex AI SDK has async methods now? 
            # generate_content_async is available.
            
            response = await model.generate_content_async(
                contents=[prompt],
                generation_config=config,
            )

            return response.text

        except Exception as e:
            logger.error(f"Vertex AI Generation Error: {e}")
            raise

gemini_service = VertexAIService()
