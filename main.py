"""
Baldwin - Voice Assistant AI
Main entry point: Orchestrates the core loop
Audio → STT → LLM → TTS → Audio
"""
import asyncio
import sys
from typing import Optional

from config import settings
from core import stt, tts, llm, session
from utils import audio
from utils.logger import logger


class Baldwin:
    """Main Baldwin assistant orchestrator"""
    
    def __init__(self):
        """Initialize Baldwin with session manager"""
        self.session = session.SessionManager()
        self.default_language = settings.baldwin_language
        self.is_running = False
        logger.info(f"[INIT] Baldwin initialized (Language: {self.default_language})")
    
    async def process_audio_input(
        self, audio_bytes: bytes, auto_detect_language: bool = True
    ) -> Optional[str]:
        """
        Process audio input through STT.
        
        Args:
            audio_bytes: WAV audio bytes (16-bit mono, 16kHz)
            auto_detect_language: auto-detect language from transcript
        
        Returns:
            Transcribed text or None if failed
        """
        try:
            # Determine language for STT
            language = stt.get_language_code(self.default_language)
            
            # Transcribe audio
            transcript = await stt.transcribe_audio(audio_bytes, language=language)
            
            if not transcript:
                logger.warning("[WARN] Empty transcript received")
                return None
            
            return transcript
        
        except Exception as e:
            logger.error(f"[AUDIO ERROR] {e}")
            return None
    
    async def get_llm_response(
        self, user_input: str
    ) -> Optional[str]:
        """
        Get LLM response to user input.
        
        Args:
            user_input: user's text input
        
        Returns:
            LLM response text or None if failed
        """
        try:
            # Get conversation history
            history = self.session.get_history_for_llm()
            
            # Get LLM response
            response = await llm.chat(history + [{"role": "user", "content": user_input}])
            
            return response.get("content", "")
        
        except Exception as e:
            logger.error(f"[ERROR] LLM processing failed: {e}")
            return None
    
    async def synthesize_response(
        self, text: str
    ) -> Optional[bytes]:
        """
        Convert text response to audio.
        
        Args:
            text: response text to synthesize
        
        Returns:
            WAV audio bytes or None if failed
        """
        try:
            # Determine language for TTS
            language = tts.get_language_code(self.default_language)
            
            # Synthesize speech
            audio_bytes = await tts.synthesize_speech(text, language=language)
            
            return audio_bytes
        
        except Exception as e:
            logger.error(f"[ERROR] Audio synthesis failed: {e}")
            return None
    
    async def process_voice_input(self, duration_seconds: int = 5) -> None:
        """
        Main voice processing loop:
        1. Record audio
        2. Transcribe (STT)
        3. Get LLM response
        4. Synthesize (TTS)
        5. Play audio
        6. Log to session
        
        Args:
            duration_seconds: how long to record
        """
        try:
            # Step 1: Record audio from microphone
            print("\n" + "="*60)
            print("[AUDIO] Listening... Speak now!")
            print("="*60)
            
            audio_bytes = await audio.record_audio_async(duration_seconds)
            
            # Step 2: Transcribe
            transcript = await self.process_audio_input(audio_bytes)
            
            if not transcript:
                print("[ERROR] Could not understand. Please try again.")
                return
            
            print(f"\n[YOU] {transcript}")
            
            # Step 3: Get LLM response
            response_text = await self.get_llm_response(transcript)
            
            if not response_text:
                print("[ERROR] LLM failed to respond. Please try again.")
                return
            
            print(f"[BALDWIN] {response_text}")
            
            # Step 4: Synthesize response
            response_audio = await self.synthesize_response(response_text)
            
            if not response_audio:
                print("[ERROR] Could not synthesize audio. Please try again.")
                return
            
            # Step 5: Play audio
            await audio.play_audio_async(response_audio)
            
            # Step 6: Log to session
            self.session.add_exchange(transcript, response_text)
        
        except KeyboardInterrupt:
            print("\n[STOP] Interrupted by user")
        except Exception as e:
            logger.error(f"[ERROR] Processing failed: {e}")
            print(f"Error: {e}")
    
    async def run_interactive_loop(self, record_duration: int = 5) -> None:
        """
        Run Baldwin in interactive mode (continuous voice assistant).
        
        Args:
            record_duration: seconds to record per turn
        """
        self.is_running = True
        print("\n" + "="*60)
        print("[START] Baldwin Voice Assistant Started")
        print("="*60)
        print("Commands:")
        print("  - Speak naturally (will be automatically detected)")
        print("  - Type 'quit' or 'exit' to stop")
        print("  - Type 'recap' to see session summary")
        print("  - Press Ctrl+C to interrupt")
        print("="*60 + "\n")
        
        turn_count = 0
        
        while self.is_running:
            try:
                turn_count += 1
                print(f"\n[Turn {turn_count}]")
                
                # Process voice input
                await self.process_voice_input(record_duration)
                
                # Ask if user wants to continue
                try:
                    # Non-blocking check for user input (in real app, could be voice-based)
                    # For now, we'll just continue
                    await asyncio.sleep(1)
                except KeyboardInterrupt:
                    break
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                continue
        
        self.is_running = False
        print("\n" + "="*60)
        print("[END] Goodbye!")
        print(self.session.get_recap())
        print("="*60 + "\n")
    
    async def run_single_interaction(self) -> None:
        """Run a single voice interaction for testing."""
        await self.process_voice_input(duration_seconds=5)


async def main():
    """Main entry point"""
    try:
        baldwin = Baldwin()
        
        # Check if we have required API keys
        if not settings.groq_api_key or not settings.sarvam_api_key:
            print("\n[ERROR] Missing required API keys!")
            print("Please create .env file with:")
            print("  - GROQ_API_KEY")
            print("  - SARVAM_API_KEY")
            print("\nCopy .env.template to .env and fill in your keys.")
            sys.exit(1)
        
        # Run interactive loop
        await baldwin.run_interactive_loop(record_duration=5)
    
    except KeyboardInterrupt:
        print("\n\n[STOP] Stopped by user")
    except Exception as e:
        logger.error(f"[FATAL] {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the main async event loop
    asyncio.run(main())
