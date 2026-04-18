import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState, useId } from "react";
import { Header } from "@/components/baldwin/Header";
import { ChatPanel } from "@/components/baldwin/ChatPanel";
import { Recorder } from "@/components/baldwin/Recorder";
import { SessionSidebar } from "@/components/baldwin/SessionSidebar";
import { SettingsSheet } from "@/components/baldwin/SettingsSheet";
import type { ChatMessage, ToolCall } from "@/components/baldwin/types";
import { sendChatMessage, transcribeAudio, checkApiHealth } from "@/services/api";

export const Route = createFileRoute("/")({
  component: BaldwinApp,
  head: () => ({
    meta: [
      { title: "Baldwin — Personal Voice Assistant" },
      {
        name: "description",
        content:
          "Baldwin is a personal AI voice assistant with real-time speech-to-text, tool calling, and natural voice responses.",
      },
    ],
  }),
});

const SAMPLE_TRANSCRIPTS = [
  "Hey Baldwin, what's the weather in Jakarta?",
  "Convert one US dollar to rupiah.",
  "Give me today's top news headline.",
  "What is six times seven?",
  "Add buy groceries to my todo list.",
];

function BaldwinApp() {
  const componentId = useId();
  const messageCounterRef = useRef(0);
  
  // Generate deterministic IDs for SSR compatibility
  const generateMessageId = () => {
    return `${componentId}-msg-${++messageCounterRef.current}`;
  };
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [confidence, setConfidence] = useState<number | null>(null);
  const [thinking, setThinking] = useState(false);
  const [toolRunning, setToolRunning] = useState<string | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [startedAt] = useState(() => new Date());
  const [now, setNow] = useState(() => Date.now());
  const [apiConnected, setApiConnected] = useState(true);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const timerRef = useRef<number | null>(null);

  // Check API health on mount
  useEffect(() => {
    checkApiHealth().then(setApiConnected).catch(() => setApiConnected(false));
  }, []);

  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(id);
  }, []);

  // Spacebar to toggle recording
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.code === "Space" && e.target === document.body) {
        e.preventDefault();
        handleToggleRecord();
      }
      if (e.code === "Escape") setSettingsOpen(false);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recording, transcribing]);

  // Initialize audio context
  const initAudioContext = async () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
    }
    return audioContextRef.current;
  };

  // Start recording
  const startRecording = async () => {
    try {
      console.log("[AUDIO] Requesting microphone permission...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log("[AUDIO] Microphone access granted");
      
      const mediaRecorder = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstart = () => {
        console.log("[AUDIO] Recording started");
        setRecording(true);
        setLiveTranscript("");
        setConfidence(null);
      };

      mediaRecorder.onstop = () => {
        console.log("[AUDIO] Recording stopped");
        setRecording(false);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      console.log("[AUDIO] MediaRecorder.start() called");
    } catch (error) {
      console.error("[AUDIO ERROR] Failed to start recording:", error);
      if (error instanceof DOMException) {
        if (error.name === "NotAllowedError") {
          alert("Microphone permission denied. Please enable microphone access in your browser settings.");
        } else if (error.name === "NotFoundError") {
          alert("No microphone found. Please check your audio device.");
        }
      }
      setRecording(false);
    }
  };

  // Stop recording and transcribe
  const stopRecordingAndTranscribe = async () => {
    if (!mediaRecorderRef.current) {
      console.warn("[AUDIO] No active recording to stop");
      return;
    }

    mediaRecorderRef.current.onstop = async () => {
      console.log("[AUDIO] Recording stopped, audio chunks:", chunksRef.current.length);
      setRecording(false);
      setTranscribing(true);

      try {
        if (chunksRef.current.length === 0) {
          console.warn("[AUDIO] No audio data recorded");
          setLiveTranscript("No audio detected. Please try again.");
          setTranscribing(false);
          return;
        }

        const audioBlob = new Blob(chunksRef.current, { type: "audio/wav" });
        console.log("[AUDIO] Audio blob created:", audioBlob.size, "bytes");
        
        const audioFile = new File([audioBlob], "audio.wav", { type: "audio/wav" });

        // Call backend to transcribe
        console.log("[AUDIO] Sending to transcribe endpoint...");
        const result = await transcribeAudio(audioFile);
        console.log("[AUDIO] Transcription result:", result);

        if (result.success && result.text) {
          setLiveTranscript(result.text);
          setConfidence(result.confidence ? Math.round(result.confidence * 100) : 95);

          // Give user a moment to see the transcription
          await new Promise((r) => setTimeout(r, 400));

          setTranscribing(false);
          processInput(result.text, result.confidence ? Math.round(result.confidence * 100) : 95);
        } else {
          setTranscribing(false);
          setLiveTranscript(result.error || "Failed to transcribe. Please try again.");
        }
      } catch (error) {
        console.error("[AUDIO ERROR] Transcription error:", error);
        setTranscribing(false);
        setLiveTranscript("Error: " + (error instanceof Error ? error.message : "Unknown error"));
      }

      // Stop all tracks
      mediaRecorderRef.current?.stream.getTracks().forEach((track) => {
        console.log("[AUDIO] Stopping track:", track.kind);
        track.stop();
      });
    };

    console.log("[AUDIO] Calling mediaRecorder.stop()");
    mediaRecorderRef.current.stop();
  };

  // Process user input with real API call
  async function processInput(text: string, conf?: number) {
    const userMsg: ChatMessage = {
      id: generateMessageId(),
      role: "user",
      content: text,
      timestamp: new Date(),
      confidence: conf,
    };
    setMessages((m) => [...m, userMsg]);
    setThinking(true);
    setToolRunning("Processing your request...");

    try {
      const start = performance.now();
      const response = await sendChatMessage(text, "english");

      if (response.success) {
        const toolCalls: ToolCall[] | undefined = response.tool_calls?.map((tc: unknown) => {
          const typedTc = tc as Record<string, unknown>;
          return {
            name: typedTc.name as string,
            label: (typedTc.name as string).charAt(0).toUpperCase() + (typedTc.name as string).slice(1),
            parameters: typedTc.parameters as Record<string, unknown>,
            result: typedTc.result as string,
          };
        });

        const baldwinMsg: ChatMessage = {
          id: generateMessageId(),
          role: "baldwin",
          content: response.content,
          timestamp: new Date(),
          responseMs: response.processing_time_ms || Math.round(performance.now() - start),
          toolCalls,
          audioDurationSec: 3 + Math.random() * 4,
        };

        // Play audio if available
        if (response.audio_url) {
          try {
            const audio = new Audio(response.audio_url);
            audio.play().catch((e) => console.warn("Could not auto-play audio:", e));
          } catch (error) {
            console.warn("Audio playback error:", error);
          }
        }

        setMessages((m) => [...m, baldwinMsg]);
      } else {
        const errorMsg: ChatMessage = {
          id: generateMessageId(),
          role: "baldwin",
          content: `Error: ${response.error || "Failed to process your request"}. Please try again.`,
          timestamp: new Date(),
        };
        setMessages((m) => [...m, errorMsg]);
      }
    } catch (error) {
      console.error("API error:", error);
      const errorMsg: ChatMessage = {
        id: generateMessageId(),
        role: "baldwin",
        content: "Sorry, I encountered an error. Please make sure the backend API is running.",
        timestamp: new Date(),
      };
      setMessages((m) => [...m, errorMsg]);
      setApiConnected(false);
    } finally {
      setThinking(false);
      setToolRunning(null);
    }
  }

  function handleToggleRecord() {
    console.log("[RECORDER] Toggle record called - recording:", recording, "transcribing:", transcribing);
    if (transcribing) {
      console.warn("[RECORDER] Cannot record while transcribing");
      return;
    }
    if (recording) {
      console.log("[RECORDER] Stopping recording");
      stopRecordingAndTranscribe();
    } else {
      console.log("[RECORDER] Starting recording");
      startRecording();
    }
  }

  function handleClear() {
    setMessages([]);
    setConfidence(null);
    setLiveTranscript("");
  }

  function handleDownload() {
    const text = messages
      .map(
        (m) =>
          `[${m.timestamp.toLocaleTimeString()}] ${m.role === "user" ? "You" : "Baldwin"}: ${m.content}`,
      )
      .join("\n\n");
    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `baldwin-session-${startedAt.toISOString().slice(0, 19)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const durationSec = Math.floor((now - startedAt.getTime()) / 1000);

  return (
    <div className="flex h-screen flex-col bg-background">
      <Header connected={apiConnected} onOpenSettings={() => setSettingsOpen(true)} />

      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <main className="flex min-h-0 flex-1 flex-col">
          <ChatPanel messages={messages} thinking={thinking} toolRunning={toolRunning} />
          <Recorder
            recording={recording}
            transcribing={transcribing}
            liveTranscript={liveTranscript}
            confidence={confidence}
            onToggle={handleToggleRecord}
            onSendText={(t) => processInput(t)}
          />
        </main>

        <div className="hidden lg:flex" suppressHydrationWarning>
          <SessionSidebar
            messages={messages}
            startedAt={startedAt}
            durationSec={durationSec}
            onClear={handleClear}
            onDownload={handleDownload}
          />
        </div>
      </div>

      <SettingsSheet open={settingsOpen} onOpenChange={setSettingsOpen} />
    </div>
  );
}
