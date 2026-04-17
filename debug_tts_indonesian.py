"""Debug TTS with Indonesian text"""
import asyncio
import httpx
from config import settings

async def test_tts_with_indonesian():
    # Test with the actual text from Baldwin's response
    text = "Halo, saya Baldwin, bukan Buckwheat. Saya adalah asisten pribadi berbasis suara. Saya bisa membantu dengan cuaca, berita, kalkulator, to-do list, dan masih banyak lagi."
    
    print(f"[TEST] Sending Indonesian text with en-IN language code")
    print(f"Text: {text[:50]}...")
    
    payload = {
        "inputs": [text],
        "target_language_code": "en-IN",
        "speaker": "anushka",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sarvam.ai/text-to-speech",
            json=payload,
            headers={"api-subscription-key": settings.sarvam_api_key},
            timeout=30.0,
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.json()}")
        else:
            print(f"Success: {len(resp.json().get('audios', [''])[0])} audio bytes")
    
    # Test 2: Try with language detection
    print(f"\n[TEST 2] Try with language auto-detection or id-IN")
    payload2 = {
        "inputs": [text],
        "target_language_code": "id-IN",
        "speaker": "anushka",
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.sarvam.ai/text-to-speech",
            json=payload2,
            headers={"api-subscription-key": settings.sarvam_api_key},
            timeout=30.0,
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error: {resp.json()}")
        else:
            print(f"Success")

asyncio.run(test_tts_with_indonesian())
