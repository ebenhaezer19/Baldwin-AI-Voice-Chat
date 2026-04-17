"""
Text-to-Speech via Sarvam AI (bulbul:v1)
Converts text to audio bytes.
"""
import httpx
import base64
from typing import Optional
from config import settings
from utils.logger import logger


SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

# Available speakers - use one from Sarvam's list
SPEAKERS = {
    "id": "anushka",      # Female voice for Indian languages (includes Indonesian)
    "en": "anushka",      # Same speaker for English
}


async def synthesize_speech(
    text: str, language: str = "id-ID", speaker: Optional[str] = None
) -> bytes:
    """
    Send text to Sarvam AI TTS and return audio bytes.
    
    Args:
        text: text to synthesize
        language: 'id-ID' for Indonesian, 'en-IN' for English
        speaker: speaker name (default: 'meera')
    
    Returns:
        WAV audio bytes (16-bit mono, 16kHz)
    
    Raises:
        httpx.HTTPError: if API call fails
    """
    logger.info(f"[TTS] Synthesizing speech - Text: '{text[:50]}...'")
    
    # Determine speaker
    lang_code = language.split("-")[0].lower()
    speaker = speaker or SPEAKERS.get(lang_code, "anushka")
    
    payload = {
        "inputs": [text],
        "target_language_code": language,
        "speaker": speaker,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SARVAM_TTS_URL,
                json=payload,
                headers={"api-subscription-key": settings.sarvam_api_key},
                timeout=30.0,
            )
            response.raise_for_status()
            
            result = response.json()
            audio_b64 = result.get("audios", [None])[0]
            
            if not audio_b64:
                logger.error("[TTS ERROR] No audio returned from TTS API")
                raise ValueError("No audio data in TTS response")
            
            audio_bytes = base64.b64decode(audio_b64)
            logger.info(f"[TTS] Synthesized audio ({len(audio_bytes)} bytes)")
            return audio_bytes
        
        except httpx.HTTPError as e:
            logger.error(f"[TTS ERROR] {e}")
            raise


def get_language_code(language: str) -> str:
    """
    Convert language name to Sarvam language code.
    
    IMPORTANT: Sarvam AI TTS only supports a limited set of languages.
    Indonesian (id-ID) might not be fully supported. Fallback to English (en-IN) if needed.
    
    Args:
        language: 'id', 'en', 'id-ID', 'en-IN', etc.
    
    Returns:
        Sarvam language code
    """
    lang_lower = language.lower()
    if lang_lower.startswith("en"):
        return "en-IN"
    # Fallback to English for unsupported languages
    return "en-IN"
