"""
LLM Integration via Groq API
Handles conversation with Claude-like responses via Groq's fast LLM.
"""
import asyncio
from typing import Optional, Any
from groq import AsyncGroq
from config import settings
from utils.logger import logger


# Initialize Groq client
client = AsyncGroq(api_key=settings.groq_api_key)

# System prompt for Baldwin
SYSTEM_PROMPT = """
Kamu adalah Baldwin, asisten AI pribadi yang cerdas, ringkas, dan ramah.
Kamu berbicara dalam bahasa yang sama dengan pengguna (Indonesia atau English).
Jawaban kamu selalu singkat dan to-the-point karena akan diucapkan lewat TTS.
Jangan gunakan markdown, bullet points, atau simbol khusus dalam jawaban.
Maksimal 3 kalimat untuk jawaban biasa, kecuali diminta detail.
Jika pengguna bertanya tentang kemampuan kamu, katakan:
"Saya adalah Baldwin, asisten pribadi berbasis suara. Saya bisa membantu dengan cuaca, berita, kalkulator, to-do list, dan masih banyak lagi."
"""


async def chat(
    messages: list[dict[str, str]],
    tools: Optional[list[dict[str, Any]]] = None,
    model: str = "llama-3.3-70b-versatile",
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> dict[str, Any]:
    """
    Send conversation to Groq LLM and get response.
    
    Args:
        messages: conversation history (list of {'role': 'user'|'assistant', 'content': '...'})
        tools: optional list of tools for function calling
        model: LLM model to use
        max_tokens: max tokens in response
        temperature: creativity level (0-1)
    
    Returns:
        Response message dict with 'role' and 'content'
    
    Raises:
        Exception: if API call fails
    """
    logger.info(f"[LLM] Sending {len(messages)} messages to Groq")
    
    # Prepare request kwargs
    kwargs = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    # Add tools if provided
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    
    try:
        response = await client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        logger.info(f"[LLM] Response: '{message.content[:100]}...'")
        
        return {
            "role": message.role or "assistant",
            "content": message.content or "",
        }
    
    except Exception as e:
        logger.error(f"[LLM ERROR] {e}")
        raise


async def simple_response(user_input: str, history: Optional[list[dict[str, str]]] = None) -> str:
    """
    Get a simple text response for user input (no tools).
    
    Args:
        user_input: user's text input
        history: optional conversation history
    
    Returns:
        Assistant's response text
    """
    messages = history or []
    messages.append({"role": "user", "content": user_input})
    
    response = await chat(messages)
    return response.get("content", "")
