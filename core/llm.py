"""
LLM Integration via Groq API
Handles conversation with Claude-like responses via Groq's fast LLM.
"""
import asyncio
from typing import Optional, Any
from groq import AsyncGroq
from config import settings
from utils.logger import logger

# Import tools
from tools import AVAILABLE_TOOLS

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
    use_default_tools: bool = True,
) -> dict[str, Any]:
    """
    Send conversation to Groq LLM and get response.
    
    Args:
        messages: conversation history (list of {'role': 'user'|'assistant', 'content': '...'})
        tools: optional list of tools for function calling (uses AVAILABLE_TOOLS by default)
        model: LLM model to use
        max_tokens: max tokens in response
        temperature: creativity level (0-1)
        use_default_tools: whether to use default tools (news, weather, etc.)
    
    Returns:
        Response dict with 'role', 'content', and optional 'tool_calls'
    
    Raises:
        Exception: if API call fails
    """
    logger.info(f"[LLM] Sending {len(messages)} messages to Groq")
    
    # Use default tools if not provided
    if use_default_tools and not tools:
        tools = AVAILABLE_TOOLS
    
    # Prepare request kwargs
    kwargs = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    # Enable tool calling for available tools
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"
    
    try:
        response = await client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        content = message.content or ""
        logger.info(f"[LLM] Response: '{content[:100]}...'")
        
        # Check for tool calls
        tool_calls = None
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = []
            for tool_call in message.tool_calls:
                tool_calls.append({
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    }
                })
            logger.info(f"[LLM] Tool calls detected: {[tc['function']['name'] for tc in tool_calls]}")
        
        return {
            "role": message.role or "assistant",
            "content": content,
            "tool_calls": tool_calls,
        }
    
    except Exception as e:
        error_str = str(e)
        # Handle Groq tool_use_failed error by retrying without problematic tools
        if "tool_use_failed" in error_str and tools and len(tools) > 1:
            logger.warning(f"[LLM] Tool call failed, retrying with fewer tools: {error_str[:100]}")
            # Retry with only weather tool (most reliable)
            weather_tools = [t for t in tools if t.get("function", {}).get("name") == "get_weather"]
            if weather_tools:
                kwargs["tools"] = weather_tools
                try:
                    response = await client.chat.completions.create(**kwargs)
                    message = response.choices[0].message
                    content = message.content or ""
                    
                    tool_calls = None
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        tool_calls = []
                        for tool_call in message.tool_calls:
                            tool_calls.append({
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                }
                            })
                    
                    return {
                        "role": message.role or "assistant",
                        "content": content,
                        "tool_calls": tool_calls,
                    }
                except Exception as retry_error:
                    logger.error(f"[LLM] Retry also failed: {retry_error}")
                    # Fall back to no tools
                    kwargs.pop("tools", None)
                    kwargs.pop("tool_choice", None)
                    response = await client.chat.completions.create(**kwargs)
                    message = response.choices[0].message
                    return {
                        "role": message.role or "assistant",
                        "content": message.content or "",
                        "tool_calls": None,
                    }
            else:
                # No tools available, just get response without tools
                kwargs.pop("tools", None)
                kwargs.pop("tool_choice", None)
                response = await client.chat.completions.create(**kwargs)
                message = response.choices[0].message
                return {
                    "role": message.role or "assistant",
                    "content": message.content or "",
                    "tool_calls": None,
                }
        else:
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
