"""
Debug script to test Sarvam AI STT API
Test different audio formats to understand why 400 error occurs
"""
import asyncio
import httpx
import io
import wave
import pyaudio
from config import settings

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

async def record_debug_audio(duration=3):
    """Record audio for testing"""
    print("[RECORD] Recording 3 seconds of audio...")
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        frames.append(stream.read(CHUNK))
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Return as WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    return buf.getvalue()

async def test_sarvam_stt(audio_bytes):
    """Test Sarvam STT API with multipart form data"""
    print(f"\n[TEST] Audio bytes: {len(audio_bytes)}")
    
    # Test: multipart form data with file field (CORRECT FORMAT)
    print("\n--- Test: Multipart form-data with 'file' field ---")
    files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
    data = {"language_code": "id-ID"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "https://api.sarvam.ai/speech-to-text",
                files=files,
                data=data,
                headers={"api-subscription-key": settings.sarvam_api_key},
                timeout=30.0,
            )
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            if resp.status_code == 200:
                result = resp.json()
                print(f"Transcript: {result.get('transcript', 'N/A')}")
        except Exception as e:
            print(f"Exception: {e}")

async def main():
    """Main debug script"""
    print("[DEBUG] Testing Sarvam AI API with correct format...")
    print(f"API Key: {settings.sarvam_api_key[:20]}...")
    
    audio = await record_debug_audio(duration=3)
    await test_sarvam_stt(audio)

if __name__ == "__main__":
    asyncio.run(main())
