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
        try:
            llm_response = await llm.chat(history)
        except Exception as llm_error:
            error_str = str(llm_error)
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
        
        response_text = llm_response.get("content", "")
        tool_calls = llm_response.get("tool_calls", [])
        
        # Add Baldwin response to session
        baldwin_session.add_message("assistant", response_text, tool_calls)
        
        # Generate audio response - try ElevenLabs first, fallback to Sarvam
        audio_base64 = None
        try:
            audio_bytes = None
            
            # Try ElevenLabs first if API key is configured
            if settings.elevenlabs_api_key:
                try:
                    audio_bytes = await tts_elevenlabs.synthesize_speech(
                        response_text, 
                        voice="george"
                    )
                except Exception as el_error:
                    logger.warning(f"[API] ElevenLabs failed: {el_error}, falling back to Sarvam")
                    audio_bytes = None
            
            # Fallback to Sarvam if ElevenLabs failed or no API key
            if not audio_bytes:
                language_code = stt.get_language_code(request.language or "english")
                audio_bytes = await tts.synthesize_speech(response_text, language=language_code)
            
            # Convert audio to base64 if we got audio data
            if audio_bytes:
                audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
                logger.info("[API] Audio synthesis successful")
            else:
                logger.warning("[API] No audio bytes generated")
        except Exception as e:
            logger.warning(f"[API] Audio synthesis failed: {e}")
            # Continue without audio - not a fatal error
        
        
        processing_time = (time.time() - start_time) * 1000
        
        return ChatResponse(
            success=True,
            content=response_text,
            audio_url=f"data:audio/mpeg;base64,{audio_base64}" if audio_base64 else None,
            tool_calls=tool_calls,
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
