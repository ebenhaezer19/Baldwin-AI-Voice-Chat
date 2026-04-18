"""
Baldwin Voice Assistant - FastAPI Server
Provides REST API endpoints for the web frontend
Bridges frontend UI with Baldwin backend (STT, LLM, TTS)
"""
import asyncio
import json
import logging
from typing import Optional
from io import BytesIO
import base64

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from config import settings
from core import stt, tts, tts_elevenlabs, llm, session
from tools import TOOL_FUNCTIONS
from utils.logger import logger


# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI(
    title="Baldwin API",
    description="Voice Assistant REST API",
    version="1.0.0",
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global session manager
baldwin_session = session.SessionManager()


# ==================== REQUEST/RESPONSE MODELS ====================

class ChatRequest(BaseModel):
    """Chat request payload"""
    message: str
    language: Optional[str] = "english"


class ChatResponse(BaseModel):
    """Chat response payload"""
    success: bool
    content: str
    audio_url: Optional[str] = None
    tool_calls: Optional[list] = None
    tool_results: Optional[list] = None
    processing_time_ms: Optional[float] = None
    error: Optional[str] = None


class TranscribeResponse(BaseModel):
    """Transcription response payload"""
    success: bool
    text: str
    confidence: Optional[float] = None
    language: Optional[str] = None
    error: Optional[str] = None


class AudioSynthesisResponse(BaseModel):
    """Audio synthesis response payload"""
    success: bool
    audio_base64: Optional[str] = None
    format: str = "mp3"
    error: Optional[str] = None


class StatusResponse(BaseModel):
    """API status response"""
    success: bool
    groq: dict
    sarvam: dict
    elevenlabs: dict
    session_info: dict


# ==================== API ENDPOINTS ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "baldwin-api"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user message and get Baldwin response
    
    Request:
        - message: User's text input
        - language: Optional language (english, indonesian)
    
    Response:
        - content: Baldwin's response text
        - audio_url: Base64-encoded MP3 audio
        - tool_calls: List of tool calls made
        - processing_time_ms: Response time
    """
    try:
        import time
        start_time = time.time()
        
        user_message = request.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Add user message to session
        baldwin_session.add_message("user", user_message)
        
        # Get conversation history for LLM
        history = baldwin_session.get_history_for_llm()
        
        # Get LLM response
        logger.info(f"[API] Processing message: {user_message}")
        llm_start = time.time()
        try:
            llm_response = await llm.chat(history)
        except Exception as llm_error:
            llm_time = (time.time() - llm_start) * 1000
            error_str = str(llm_error)
            logger.error(f"[API] LLM failed in {llm_time:.0f}ms: {error_str}")
            # Check for rate limit (429)
            if "429" in error_str or "rate_limit" in error_str:
                logger.warning(f"[API] Groq rate limited: {error_str}")
                return ChatResponse(
                    success=False,
                    content="",
                    error="API quota exceeded. Please try again in a few minutes."
                )
            # Check for other LLM errors
            elif "401" in error_str or "authentication" in error_str.lower():
                logger.error(f"[API] Auth error: {error_str}")
                return ChatResponse(
                    success=False,
                    content="",
                    error="Authentication failed. Please check API keys."
                )
            else:
                # Re-raise unknown errors
                raise
        
        llm_time = (time.time() - llm_start) * 1000
        logger.info(f"[API] LLM response ready in {llm_time:.0f}ms")
        
        response_text = llm_response.get("content", "")
        tool_calls = llm_response.get("tool_calls", [])
        formatted_tool_results = []  # Initialize for all cases
        
        # Handle tool calls if LLM made any
        if tool_calls:
            logger.info(f"[API] Executing {len(tool_calls)} tool calls")
            tool_results = []
            formatted_tool_results = []
            
            for tool_call in tool_calls:
                tool_name = tool_call.get("function", {}).get("name")
                tool_args = tool_call.get("function", {}).get("arguments")
                
                if not tool_name or tool_name not in TOOL_FUNCTIONS:
                    logger.warning(f"[API] Unknown tool: {tool_name}")
                    continue
                
                try:
                    logger.info(f"[API] Calling tool: {tool_name} with args: {tool_args}")
                    
                    # Parse arguments if they're JSON string
                    if isinstance(tool_args, str):
                        import json
                        tool_args = json.loads(tool_args)
                    
                    # Execute the tool
                    tool_func = TOOL_FUNCTIONS[tool_name]
                    tool_result = await tool_func(**tool_args)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.get("id"),
                        "tool_name": tool_name,
                        "result": tool_result,
                    })
                    
                    # Format result for frontend (include articles if news tool)
                    formatted_result = {
                        "tool_name": tool_name,
                        "success": tool_result.get("success", False),
                    }
                    
                    if tool_name == "news" and tool_result.get("success"):
                        # Include articles for news tool
                        formatted_result["articles"] = tool_result.get("articles", [])
                        formatted_result["total_results"] = tool_result.get("total_results", 0)
                        formatted_result["query"] = tool_result.get("query", "")
                    elif tool_name == "weather" and tool_result.get("success"):
                        # Include weather data
                        formatted_result["data"] = tool_result
                    
                    formatted_tool_results.append(formatted_result)
                    logger.info(f"[API] Tool {tool_name} result: {str(tool_result)[:200]}")
                
                except Exception as tool_error:
                    logger.error(f"[API] Tool execution error ({tool_name}): {tool_error}")
                    tool_results.append({
                        "tool_call_id": tool_call.get("id"),
                        "tool_name": tool_name,
                        "error": str(tool_error),
                    })
                    formatted_tool_results.append({
                        "tool_name": tool_name,
                        "success": False,
                        "error": str(tool_error),
                    })
            
            # If we have tool results, send them back to LLM for a follow-up response
            if tool_results:
                # Add assistant response to history
                history.append({"role": "assistant", "content": response_text, "tool_calls": tool_calls})
                
                # Add tool results to history
                for result in tool_results:
                    history.append({
                        "role": "user",
                        "content": f"Tool {result['tool_name']} returned: {json.dumps(result.get('result', result.get('error')))}"
                    })
                
                # Get follow-up response from LLM with tool results
                logger.info("[API] Getting follow-up response from LLM with tool results")
                llm_followup_start = time.time()
                try:
                    llm_followup = await llm.chat(history, use_default_tools=False)
                    response_text = llm_followup.get("content", response_text)
                    tool_calls = []  # Clear tool calls for final response
                except Exception as followup_error:
                    logger.error(f"[API] LLM follow-up failed: {followup_error}")
                    # Use original response if follow-up fails
                    pass
        
        # Add Baldwin response to session
        baldwin_session.add_message("assistant", response_text, tool_calls)
        
        # Generate audio response with TTS (ElevenLabs primary, Sarvam fallback)
        audio_base64 = None
        audio_time = 0
        tts_start = time.time()
        try:
            language_code = stt.get_language_code(request.language or "english")
            logger.info(f"[API] Starting TTS synthesis for language: {language_code}")
            
            audio_bytes = None
            
            # Try ElevenLabs first (primary provider)
            try:
                logger.info("[API] Attempting ElevenLabs TTS...")
                audio_bytes = await tts_elevenlabs.synthesize_speech(response_text, voice="default")
                if audio_bytes:
                    logger.info(f"[API] ElevenLabs TTS successful - {len(audio_bytes)} bytes")
            except Exception as e:
                logger.warning(f"[API] ElevenLabs TTS failed: {e}. Falling back to Sarvam...")
            
            # Fall back to Sarvam if ElevenLabs fails
            if not audio_bytes:
                logger.info("[API] Using Sarvam TTS as fallback...")
                audio_bytes = await tts.synthesize_speech(response_text, language=language_code)
                if audio_bytes:
                    logger.info(f"[API] Sarvam TTS successful - {len(audio_bytes)} bytes")
            
            # Convert audio to base64 if we got audio data
            if audio_bytes:
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                audio_time = (time.time() - tts_start) * 1000
                logger.info(f"[API] Audio ready in {audio_time:.0f}ms ({len(audio_bytes)} bytes)")
            else:
                audio_time = (time.time() - tts_start) * 1000
                logger.warning(f"[API] No audio bytes generated ({audio_time:.0f}ms)")
        except Exception as e:
            audio_time = (time.time() - tts_start) * 1000
            logger.warning(f"[API] TTS synthesis error ({audio_time:.0f}ms): {e}")
            # Continue without audio - not a fatal error
        
        
        processing_time = (time.time() - start_time) * 1000
        logger.info(f"[API] Total response time: {processing_time:.0f}ms (LLM: {llm_time:.0f}ms, TTS: {audio_time:.0f}ms)")
        
        return ChatResponse(
            success=True,
            content=response_text,
            audio_url=f"data:audio/mpeg;base64,{audio_base64}" if audio_base64 else None,
            tool_calls=tool_calls,
            tool_results=formatted_tool_results if formatted_tool_results else None,
            processing_time_ms=processing_time,
        )
    
    except Exception as e:
        logger.error(f"[API ERROR] Chat failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@app.post("/api/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file to text
    
    Request:
        - file: WAV audio file (16-bit mono, 16kHz)
    
    Response:
        - text: Transcribed text
        - confidence: Confidence score (0-100)
        - language: Detected language
    """
    try:
        if not file.filename.endswith(".wav"):
            raise HTTPException(status_code=400, detail="Only WAV files supported")
        
        # Read audio file
        audio_bytes = await file.read()
        
        # Transcribe
        logger.info("[API] Transcribing audio...")
        language_code = "en-IN"  # Default to English (India)
        transcript = await stt.transcribe_audio(audio_bytes, language=language_code)
        
        if not transcript:
            return TranscribeResponse(
                success=False,
                text="",
                error="Empty transcript received"
            )
        
        logger.info(f"[API] Transcription: {transcript}")
        
        return TranscribeResponse(
            success=True,
            text=transcript,
            confidence=0.95,  # Mock confidence for now
            language=language_code,
        )
    
    except Exception as e:
        logger.error(f"[API ERROR] Transcription failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@app.post("/api/audio-synthesis")
async def synthesize_audio(request: ChatRequest):
    """
    Convert text to speech audio
    
    Request:
        - message: Text to synthesize
    
    Response:
        - Base64-encoded MP3 audio data
    """
    try:
        text = request.message.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        logger.info(f"[API] Synthesizing: {text}")
        
        # Use ElevenLabs for male voice
        if settings.elevenlabs_api_key:
            audio_bytes = await tts_elevenlabs.synthesize_speech(text, voice="george")
        else:
            # Fallback to Sarvam
            language_code = stt.get_language_code(request.language or "english")
            audio_bytes = await tts.synthesize_speech(text, language=language_code)
        
        # Return as base64-encoded data URL
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        return {
            "success": True,
            "audio_url": f"data:audio/mpeg;base64,{audio_base64}"
        }
    
    except Exception as e:
        logger.error(f"[API ERROR] Audio synthesis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio synthesis failed: {str(e)}"
        )


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """
    Get API integration status for all services
    
    Response:
        - groq: Groq LLM status
        - sarvam: Sarvam STT status
        - elevenlabs: ElevenLabs TTS status
        - session_info: Current session info
    """
    return StatusResponse(
        success=True,
        groq={
            "status": "connected" if settings.groq_api_key else "not_configured",
            "model": "llama-3.3-70b-versatile",
            "provider": "Groq",
        },
        sarvam={
            "status": "connected" if settings.sarvam_api_key else "not_configured",
            "models": ["saaras (STT)", "bulbul (TTS)"],
            "provider": "Sarvam AI",
        },
        elevenlabs={
            "status": "connected" if settings.elevenlabs_api_key else "not_configured",
            "default_voice": "george (male)",
            "provider": "ElevenLabs",
        },
        session_info={
            "session_id": baldwin_session.session_id,
            "message_count": len(baldwin_session.messages),
            "language": settings.baldwin_language,
        }
    )


@app.post("/api/session/reset")
async def reset_session():
    """Reset the current session"""
    global baldwin_session
    baldwin_session = session.SessionManager()
    logger.info("[API] Session reset")
    return {"success": True, "message": "Session reset"}


@app.get("/api/session/history")
async def get_session_history():
    """Get current session conversation history"""
    return {
        "success": True,
        "session_id": baldwin_session.session_id,
        "messages": baldwin_session.messages,
    }


@app.post("/api/session/download")
async def download_session():
    """Download session transcript as JSON"""
    transcript = {
        "session_id": baldwin_session.session_id,
        "messages": baldwin_session.messages,
    }
    
    return JSONResponse(
        content=transcript,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=baldwin_transcript.json"}
    )


# ==================== WEBSOCKET (Optional for real-time) ====================

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat
    Allows streaming responses and audio data
    """
    await websocket.accept()
    logger.info("[WS] Client connected")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                await websocket.send_json({"error": "Empty message"})
                continue
            
            # Add to session
            baldwin_session.add_message("user", user_message)
            
            # Get LLM response
            history = baldwin_session.get_history_for_llm()
            try:
                llm_response = await llm.chat(history)
                response_text = llm_response.get("content", "")
                tool_calls = llm_response.get("tool_calls", [])
                
                # Add to session
                baldwin_session.add_message("assistant", response_text, tool_calls)
                
                # Send response back
                await websocket.send_json({
                    "success": True,
                    "content": response_text,
                    "tool_calls": tool_calls,
                })
                
                # Generate and send audio
                try:
                    if settings.elevenlabs_api_key:
                        audio_bytes = await tts_elevenlabs.synthesize_speech(
                            response_text, 
                            voice="george"
                        )
                    else:
                        language_code = stt.get_language_code("english")
                        audio_bytes = await tts.synthesize_speech(
                            response_text, 
                            language=language_code
                        )
                    
                    audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                    await websocket.send_json({
                        "type": "audio",
                        "audio_url": f"data:audio/mpeg;base64,{audio_base64}"
                    })
                except Exception as e:
                    logger.warning(f"[WS] Audio generation failed: {e}")
            
            except Exception as e:
                logger.error(f"[WS] LLM failed: {e}")
                await websocket.send_json({
                    "success": False,
                    "error": str(e)
                })
    
    except Exception as e:
        logger.error(f"[WS] Connection error: {e}")
    finally:
        logger.info("[WS] Client disconnected")


# ==================== ROOT ENDPOINT ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Baldwin Voice Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health",
            "chat": "POST /api/chat",
            "transcribe": "POST /api/transcribe",
            "audio_synthesis": "POST /api/audio-synthesis",
            "status": "GET /api/status",
            "session_history": "GET /api/session/history",
            "session_reset": "POST /api/session/reset",
            "websocket": "WS /ws/chat",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
