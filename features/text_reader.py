"""Text Reader Feature - OCR text extraction from images"""
import logging
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class TextReader:
    """Extracts and reads text from images using OCR"""
    
    def __init__(self, language: str = "en"):
        """
        Initialize text reader
        
        Args:
            language: Language code for OCR (e.g., 'en', 'id')
        """
        self.language = language
        self.recognizer = None
        logger.info(f"TextReader initialized with language: {language}")
    
    def extract_text(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Extract text from image frame
        
        Args:
            frame: Input image frame (numpy array)
        
        Returns:
            List of text regions with coordinates and content
        """
        try:
            if frame is None or frame.size == 0:
                return []
            
            # Placeholder for OCR
            # In production, this would use EasyOCR or Tesseract
            text_regions = []
            
            logger.debug(f"Extracted text from {len(text_regions)} regions")
            return text_regions
        
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return []
    
    def read_text_aloud(self, text: str, speech_engine) -> None:
        """
        Convert extracted text to speech
        
        Args:
            text: Text to read aloud
            speech_engine: SpeechEngine instance for TTS
        """
        if text and speech_engine:
            try:
                speech_engine.speak(text)
            except Exception as e:
                logger.error(f"Error reading text aloud: {e}")
    
    def get_text_description(self, text_regions: List[Dict]) -> str:
        """
        Generate description of extracted text
        
        Args:
            text_regions: List of text regions with content
        
        Returns:
            Formatted text description
        """
        if not text_regions:
            return "No text found in the image."
        
        extracted_text = " ".join([region.get("text", "") for region in text_regions])
        return f"I found the following text: {extracted_text}"
    
    def set_language(self, language: str) -> None:
        """
        Change OCR language
        
        Args:
            language: Language code (e.g., 'en', 'id')
        """
        self.language = language
        logger.info(f"Language changed to: {language}")
