"""
Session Memory Management
Tracks conversation history and activity logs for the current session.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from utils.logger import logger


LOG_FILE = Path("data/session_log.json")


class SessionManager:
    """
    Manages Baldwin's session state:
    - Conversation history (for LLM context)
    - Activity log (for recap)
    - Timing information
    """
    
    def __init__(self, max_history_turns: int = 20):
        """
        Initialize session manager.
        
        Args:
            max_history_turns: max conversation turns to keep in memory
        """
        self.history: list[dict[str, str]] = []  # For LLM context
        self.activity_log: list[str] = []  # For recap/logging
        self.start_time = datetime.now()
        self.max_history_turns = max_history_turns
        
        logger.info("[SESSION] Started")
    
    def add_exchange(
        self,
        user_input: str,
        assistant_response: str,
        tool_used: Optional[str] = None,
    ) -> None:
        """
        Log a user-assistant exchange.
        
        Args:
            user_input: what the user said/asked
            assistant_response: Baldwin's response
            tool_used: optional tool that was invoked
        """
        # Add to conversation history
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": assistant_response})
        
        # Add to activity log
        timestamp = datetime.now().strftime("%H:%M:%S")
        summary = user_input[:60].replace("\n", " ")
        entry = f"[{timestamp}] User: {summary}"
        if tool_used:
            entry += f" → {tool_used}"
        
        self.activity_log.append(entry)
        
        # Keep history within limits
        self.trim_history()
        
        # Save to disk
        self._save_log()
        
        logger.info(f"[LOG] Session: {len(self.activity_log)} interactions logged")
    
    def add_message(
        self,
        role: str,
        content: str,
        tool_calls: Optional[list] = None,
    ) -> None:
        """
        Add a message to conversation history (flexible method).
        
        Args:
            role: "user" or "assistant"
            content: message content
            tool_calls: optional list of tool calls (for assistant messages)
        """
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        
        self.history.append(msg)
        
        # Log activity if it's a user message
        if role == "user":
            timestamp = datetime.now().strftime("%H:%M:%S")
            summary = content[:60].replace("\n", " ")
            entry = f"[{timestamp}] User: {summary}"
            self.activity_log.append(entry)
        
        # Keep history within limits
        self.trim_history()
        
        # Save to disk
        self._save_log()
    
    def get_session_info(self) -> dict:
        """Get current session information."""
        duration_seconds = (datetime.now() - self.start_time).total_seconds()
        return {
            "started_at": self.start_time.isoformat(),
            "duration_seconds": int(duration_seconds),
            "message_count": len(self.history),
            "activity_count": len(self.activity_log),
        }
    
    def get_recap(self) -> str:
        """
        Get a summary of the current session.
        
        Returns:
            Human-readable recap string
        """
        duration_seconds = (datetime.now() - self.start_time).total_seconds()
        duration_minutes = int(duration_seconds // 60)
        
        recap = (
            f"Sesi dimulai pukul {self.start_time.strftime('%H:%M:%S')}, "
            f"durasi {duration_minutes} menit. "
            f"Total {len(self.activity_log)} interaksi."
        )
        
        if self.activity_log:
            recap += f" Terakhir: {self.activity_log[-1]}"
        
        return recap
    
    def trim_history(self) -> None:
        """
        Keep conversation history within max_history_turns.
        Prevents context window overflow.
        """
        max_messages = self.max_history_turns * 2  # user + assistant pairs
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
            logger.debug(f"Trimmed history to {len(self.history)} messages")
    
    def _save_log(self) -> None:
        """Save activity log to disk as JSON."""
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            LOG_FILE.write_text(
                json.dumps(self.activity_log, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Failed to save session log: {e}")
    
    def get_history_for_llm(self) -> list[dict[str, str]]:
        """
        Get conversation history in LLM-compatible format.
        
        Returns:
            List of {'role': 'user'|'assistant', 'content': '...'}
        """
        return self.history.copy()
