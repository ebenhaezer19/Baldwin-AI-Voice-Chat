"""
ElevenLabs Text-to-Speech Integration
Provides natural male/female voice synthesis using ElevenLabs API
"""
import asyncio
import base64
from typing import Optional

import httpx

from config import settings
from utils.logger import logger


# Voice mapping with IDs from ElevenLabs
VOICES = {
    "george": {
        "id": "6xPz2opT0y5qtoRh1U1Y",  # Male voice (American accent)
        "name": "George",
        "gender": "male",
        "accent": "American",
    },
    "bella": {
        "id": "EXAVITQu4vr4xnSDxMaL",  # Female voice (Italian accent)
        "name": "Bella",
        "gender": "female",
        "accent": "Italian",
    },
}


async def synthesize_speech(
    text: str,
    voice: str = "george",
    model_id: str = "eleven_multilingual_v2",
) -> Optional[bytes]:
    """
    Synthesize text to speech using ElevenLabs API.
    
    Args:
        text: Text to synthesize
        voice: Voice name ("george" for male, "bella" for female)
        model_id: ElevenLabs model ID (default: eleven_multilingual_v2)
    
    Returns:
        MP3 audio bytes or None if failed
    """
    try:
        if not settings.elevenlabs_api_key:
            logger.warning("[TTS_ELEVENLABS] API key not configured, skipping")
            return None
        
        if voice not in VOICES:
            logger.warning(f"[TTS_ELEVENLABS] Unknown voice '{voice}', using 'george'")
            voice = "george"
        
        voice_id = VOICES[voice]["id"]
        voice_name = VOICES[voice]["name"]
        
        logger.info(f"[TTS_ELEVENLABS] Synthesizing with {voice_name} ({voice})...")
        
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
        }
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }
        
        # Make async request
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            audio_bytes = response.content
            logger.info(
                f"[TTS_ELEVENLABS] Success ({len(audio_bytes)} bytes, {voice_name})"
            )
            return audio_bytes
        else:
            logger.error(
                f"[TTS_ELEVENLABS] API error {response.status_code}: {response.text}"
            )
            return None
    
    except Exception as e:
        logger.error(f"[TTS_ELEVENLABS] Error: {e}")
        return None


def get_available_voices() -> dict:
    """Get list of available voices"""
    return VOICES
