import { useEffect, useRef } from "react";
import { Bot } from "lucide-react";
import type { ChatMessage } from "./types";
import { MessageBubble } from "./MessageBubble";

interface ChatPanelProps {
  messages: ChatMessage[];
  thinking: boolean;
  toolRunning?: string | null;
}

export function ChatPanel({ messages, thinking, toolRunning }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages.length, thinking, toolRunning]);

  return (
    <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-6 md:px-6">
      <div className="mx-auto flex max-w-3xl flex-col gap-5">
        {messages.length === 0 && !thinking && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-primary-glow shadow-lg shadow-primary/30">
              <Bot className="h-6 w-6 text-primary-foreground" />
            </div>
            <h2 className="text-lg font-semibold">Hi, I'm Baldwin</h2>
            <p className="mt-1 max-w-sm text-sm text-muted-foreground">
              Tap the microphone and ask me about the weather, news, currency exchange, or just chat.
            </p>
          </div>
        )}

        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}

        {toolRunning && (
          <div className="flex animate-fade-in items-center gap-2 self-end rounded-full border border-border bg-card px-3 py-1.5 text-xs">
            <div className="h-2 w-2 animate-ping rounded-full bg-primary" />
            <span className="font-mono text-muted-foreground">{toolRunning}</span>
          </div>
        )}

        {thinking && (
          <div className="flex animate-fade-in flex-row-reverse gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary to-primary-glow shadow-md">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="flex items-center gap-1.5 rounded-2xl rounded-tr-sm bg-baldwin-bubble px-4 py-3">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-baldwin-bubble-foreground/60 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-baldwin-bubble-foreground/60 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-baldwin-bubble-foreground/60" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
