"""Quick test of Groq API key"""
import asyncio
from config import settings
from groq import AsyncGroq

async def test():
    print(f"[CHECK] Groq API Key: {settings.groq_api_key[:15]}...")
    print(f"[CHECK] Key starts with 'gsk_': {settings.groq_api_key.startswith('gsk_')}")
    
    client = AsyncGroq(api_key=settings.groq_api_key)
    
    try:
        print("[TEST] Sending test request to Groq...")
        response = await client.chat.completions.create(
            messages=[{"role": "user", "content": "Say 'Hello'"}],
            model="llama-3.3-70b-versatile",
            max_tokens=10
        )
        print(f"[SUCCESS] Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")

asyncio.run(test())
