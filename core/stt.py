"""
Speech-to-Text via Sarvam AI (saaras:v2)
Converts audio bytes to text transcription.
"""
import httpx
import base64
from typing import Optional
from config import settings
from utils.logger import logger


SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"


async def transcribe_audio(
    audio_bytes: bytes, language: str = "id-ID"
) -> str:
    """
    Send audio to Sarvam AI STT and return transcription.
    
    Args:
        audio_bytes: WAV audio bytes (16-bit mono, 16kHz)
        language: 'id-ID' for Indonesian, 'en-IN' for English
    
    Returns:
        Transcribed text
    
    Raises:
        httpx.HTTPError: if API call fails
    """
    logger.info(f"[STT] Transcribing audio ({len(audio_bytes)} bytes) - Language: {language}")
    
    # Sarvam API requires multipart form data with 'file' field
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"language_code": language}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SARVAM_STT_URL,
                files=files,
                data=data,
                headers={"api-subscription-key": settings.sarvam_api_key},
                timeout=30.0,
            )
            response.raise_for_status()
            
            result = response.json()
            transcript = result.get("transcript", "")
            
            if not transcript:
                logger.warning("[STT] Empty transcription received")
                return ""
            
            logger.info(f"[STT] Transcription: '{transcript}'")
            return transcript
        
        except httpx.HTTPError as e:
            logger.error(f"[STT ERROR] {e}")
            raise


def get_language_code(language: str) -> str:
    """
    Convert language name to Sarvam language code.
    
    IMPORTANT: Sarvam AI only supports India-based languages (hi-IN, bn-IN, en-IN, etc.)
    Indonesian (id-ID) is NOT supported. Fallback to English (en-IN).
    
    Args:
        language: 'id', 'en', 'id-ID', 'en-IN', etc.
    
    Returns:
        Sarvam language code
    """
    lang_lower = language.lower()
    # Sarvam doesn't support Indonesian - fallback to English
    if lang_lower.startswith("id"):
        logger.warning("[STT] Indonesian not supported by Sarvam. Falling back to English (en-IN)")
        return "en-IN"
    return "en-IN"
