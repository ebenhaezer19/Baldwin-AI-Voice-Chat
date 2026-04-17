"""Test main.py's TTS call directly"""
import asyncio
from core import tts

async def test():
    text = "Halo, saya Baldwin, bukan Buckwheat. Saya adalah asisten pribadi berbasis suara. Saya bisa membantu dengan cuaca, berita, kalkulator, to-do list, dan masih banyak lagi."
    language = tts.get_language_code("id")  # This should return "en-IN"
    
    print(f"[CHECK] Language code: {language}")
    print(f"[TEST] Calling synthesize_speech...")
    
    try:
        audio = await tts.synthesize_speech(text, language=language)
        print(f"[SUCCESS] Got {len(audio)} bytes")
    except Exception as e:
        print(f"[ERROR] {e}")

asyncio.run(test())
