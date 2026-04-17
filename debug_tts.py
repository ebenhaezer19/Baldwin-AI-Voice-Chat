"""Debug TTS API issues"""
import asyncio
import httpx
import json
from config import settings

async def test_tts():
    text = "Hello, this is a test."
    language = "en-IN"  # Use English since Indonesian not supported
    
    # Test 1: Current format
    print("[TEST 1] Current JSON format...")
    payload = {
        "inputs": [text],
        "target_language_code": language,
        "speaker": "meera",
        "model": "bulbul:v1",
        "pitch": 0,
        "pace": 1.0,
        "loudness": 1.5,
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sarvam.ai/text-to-speech",
            json=payload,
            headers={"api-subscription-key": settings.sarvam_api_key},
            timeout=30.0,
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    
    # Test 2: Without optional fields
    print("\n[TEST 2] Minimal payload...")
    payload2 = {
        "inputs": [text],
        "target_language_code": language,
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sarvam.ai/text-to-speech",
            json=payload2,
            headers={"api-subscription-key": settings.sarvam_api_key},
            timeout=30.0,
        )
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")

asyncio.run(test_tts())
