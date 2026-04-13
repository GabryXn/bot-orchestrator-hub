"""
Google Cloud Vision API Service.
Wrapper for OCR and image analysis.
"""

import logging
from typing import Optional
from google.cloud import vision

from src.core.config import PROJECT_ID

logger = logging.getLogger(__name__)

class VisionService:
    """Service for interacting with Google Cloud Vision API."""

    def __init__(self):
        self._client: Optional[vision.ImageAnnotatorClient] = None

    @property
    def client(self) -> vision.ImageAnnotatorClient:
        """Lazy load the Vision client."""
        if not self._client:
            # Use the centralized project ID for billing and permissions
            self._client = vision.ImageAnnotatorClient(
                client_options={"api_endpoint": "eu-vision.googleapis.com"} if PROJECT_ID else None
            )
        return self._client

    def ocr_image(self, content: bytes, mime_type: str = "image/jpeg") -> str:
        """
        Perform OCR on an image (synchronous).
        
        Args:
            content: Image bytes
            mime_type: Mime type of the image
            
        Returns:
            Extracted text
        """
        try:
            image = vision.Image(content=content)
            response = self.client.text_detection(image=image)
            
            if hasattr(response, "error") and response.error.message:
                raise Exception(f"Vision API Error: {response.error.message}")

            # Using text_detection (TEXT_DETECTION) as generic OCR
            if response.full_text_annotation:
                return response.full_text_annotation.text
            return ""

        except Exception as e:
            logger.error(f"OCR Image Error: {e}")
            raise

    def ocr_document(self, content: bytes, mime_type: str) -> str:
        """
        Perform OCR on a document (PDF/TIFF) or Image.
        Handles generic OCR requests including PDF.
        """
        # Determine if it is a PDF/TIFF that needs file annotation
        if mime_type in ["application/pdf", "image/tiff"]:
             return self._ocr_pdf(content, mime_type)
        else:
             return self.ocr_image(content, mime_type)

    def _ocr_pdf(self, content: bytes, mime_type: str) -> str:
        """
        Perform OCR on a PDF/TIFF file (Small files inline).
        """
        try:
            # Prepare InputConfig
            input_config = vision.InputConfig(
                content=content,
                mime_type=mime_type,
            )

            # Feature
            feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

            # Request (1 page, or all supported pages for small files?)
            # For batch_annotate_files, we specify pages.
            # If we don't specify pages, it does up to 5 pages for synchronous.
            
            request = vision.AnnotateFileRequest(
                input_config=input_config,
                features=[feature],
            )

            response = self.client.batch_annotate_files(requests=[request])
            
            # Response is BatchAnnotateFilesResponse -> responses (list of AnnotateFileResponse)
            if not response.responses:
                return ""

            file_response = response.responses[0]
            if hasattr(file_response, "error") and file_response.error.message:
                raise Exception(f"Vision API File Error: {file_response.error.message}")
            
            # Combine text from all pages
            full_text = []
            for page_response in file_response.responses:
                if page_response.full_text_annotation:
                    full_text.append(page_response.full_text_annotation.text)
            
            return "\n\n".join(full_text)

        except Exception as e:
            logger.error(f"OCR PDF Error: {e}")
            raise

# UNUSED: verifica se eliminabile
vision_service = VisionService()
