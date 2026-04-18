/**
 * Baldwin API Client
 * Provides methods to communicate with the backend API
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export interface ChatResponse {
  success: boolean;
  content: string;
  audio_url?: string;
  tool_calls?: ToolCall[];
  processing_time_ms?: number;
  error?: string;
}

export interface TranscribeResponse {
  success: boolean;
  text: string;
  confidence?: number;
  language?: string;
  error?: string;
}

export interface AudioSynthesisResponse {
  success: boolean;
  audio_url?: string;
  format?: string;
  error?: string;
}

export interface StatusResponse {
  success: boolean;
  groq: {
    status: string;
    model: string;
    provider: string;
  };
  sarvam: {
    status: string;
    models: string[];
    provider: string;
  };
  elevenlabs: {
    status: string;
    default_voice: string;
    provider: string;
  };
  session_info: {
    session_id: string;
    message_count: number;
    language: string;
  };
}

export interface ToolCall {
  name: string;
  label?: string;
  parameters: Record<string, unknown>;
  result?: string;
}

/**
 * Send a chat message to Baldwin and get a response
 */
export async function sendChatMessage(
  message: string,
  language: string = "english"
): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        language,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to process chat message");
    }

    return await response.json();
  } catch (error) {
    console.error("Chat error:", error);
    return {
      success: false,
      content: "",
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * Transcribe audio file to text
 */
export async function transcribeAudio(
  audioFile: File
): Promise<TranscribeResponse> {
  try {
    const formData = new FormData();
    formData.append("file", audioFile);

    const response = await fetch(`${API_BASE_URL}/api/transcribe`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to transcribe audio");
    }

    return await response.json();
  } catch (error) {
    console.error("Transcription error:", error);
    return {
      success: false,
      text: "",
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * Synthesize text to speech audio
 */
export async function synthesizeAudio(
  text: string,
  language: string = "english"
): Promise<AudioSynthesisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/audio-synthesis`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: text,
        language,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to synthesize audio");
    }

    return await response.json();
  } catch (error) {
    console.error("Audio synthesis error:", error);
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * Get API status and service health
 */
export async function getApiStatus(): Promise<StatusResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/status`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Failed to get API status");
    }

    return await response.json();
  } catch (error) {
    console.error("Status check error:", error);
    return null;
  }
}

/**
 * Get current session history
 */
export async function getSessionHistory(): Promise<{
  success: boolean;
  session_id: string;
  messages: unknown[];
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/session/history`, {
      method: "GET",
    });

    if (!response.ok) {
      throw new Error("Failed to get session history");
    }

    return await response.json();
  } catch (error) {
    console.error("Session history error:", error);
    return {
      success: false,
      session_id: "",
      messages: [],
    };
  }
}

/**
 * Reset the current session
 */
export async function resetSession(): Promise<{ success: boolean }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/session/reset`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to reset session");
    }

    return await response.json();
  } catch (error) {
    console.error("Session reset error:", error);
    return { success: false };
  }
}

/**
 * Download session transcript
 */
export async function downloadSessionTranscript(): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/session/download`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to download transcript");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "baldwin_transcript.json";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Download error:", error);
  }
}

/**
 * Create a WebSocket connection for real-time chat
 */
export function createWebSocket(
  onMessage: (data: unknown) => void,
  onError: (error: string) => void
): WebSocket {
  const protocol = API_BASE_URL.startsWith("https") ? "wss" : "ws";
  const wsUrl = `${protocol}://${API_BASE_URL.replace(/^https?:\/\//, "")}/ws/chat`;

  const ws = new WebSocket(wsUrl);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  ws.onerror = () => {
    onError("WebSocket connection failed");
  };

  return ws;
}

/**
 * Check if API is available
 */
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}
