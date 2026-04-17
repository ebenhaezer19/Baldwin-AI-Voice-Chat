"""
Audio recording and playback utilities
Handles microphone input and speaker output via PyAudio and SimpleAudio.
"""
import pyaudio
import wave
import io
from pathlib import Path
from typing import Optional
import asyncio

# Audio settings (Sarvam requires 16kHz mono WAV)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 16 kHz for Sarvam AI


def record_audio(duration_seconds: int = 5) -> bytes:
    """
    Record audio from microphone and return WAV bytes.
    
    Args:
        duration_seconds: how long to record (default 5 seconds)
    
    Returns:
        WAV audio bytes (16-bit mono, 16kHz)
    """
    print(f"[AUDIO] Recording for {duration_seconds} seconds...")
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * duration_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
    finally:
        p.terminate()
    
    # Encode to WAV bytes
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    
    wav_bytes = buf.getvalue()
    print(f"[AUDIO] Recording complete ({len(wav_bytes)} bytes)")
    return wav_bytes


def play_audio(audio_bytes: bytes, save_to_file: Optional[str] = None) -> None:
    """
    Play audio bytes through speaker.
    
    IMPORTANT: simpleaudio requires Microsoft Visual C++ 14.0+ to build from source.
    For now, audio is saved to file for testing. Install separately if needed:
    pip install --only-binary :all: simpleaudio
    
    Args:
        audio_bytes: WAV audio bytes (16-bit mono, 16kHz)
        save_to_file: optional path to save audio to disk
    """
    try:
        import simpleaudio as sa
        
        # If simpleaudio is available, play through speaker
        if save_to_file:
            Path(save_to_file).write_bytes(audio_bytes)
            print(f"[SAVE] Audio saved to {save_to_file}")
        
        try:
            buf = io.BytesIO(audio_bytes)
            with wave.open(buf, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                wave_obj = sa.WaveObject(
                    frames,
                    wf.getnchannels(),
                    wf.getsampwidth(),
                    wf.getframerate(),
                )
            
            print("[AUDIO] Playing audio...")
            play_obj = wave_obj.play()
            play_obj.wait_done()
            print("[AUDIO] Playback complete")
        except Exception as e:
            print(f"[ERROR] Error playing audio: {e}")
    
    except ImportError:
        # Fallback: save to file if simpleaudio not available
        print("[INFO] simpleaudio not available. Saving audio to data/output.wav")
        save_path = Path("data/output.wav")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(audio_bytes)
        print(f"[SAVE] Audio saved to {save_path}")


async def record_audio_async(duration_seconds: int = 5) -> bytes:
    """
    Async wrapper for record_audio (runs in thread pool).
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, record_audio, duration_seconds)


async def play_audio_async(audio_bytes: bytes) -> None:
    """
    Async wrapper for play_audio (runs in thread pool).
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, play_audio, audio_bytes)
