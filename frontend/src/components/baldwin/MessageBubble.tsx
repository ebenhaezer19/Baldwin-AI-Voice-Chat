import { useState } from "react";
import { Bot, User, Copy, Check, Clock } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "./types";
import { ToolBadge } from "./ToolBadge";

function renderMarkdown(text: string) {
  // Minimal bold/italic/code support
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("*") && part.endsWith("*")) {
      return <em key={i}>{part.slice(1, -1)}</em>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} className="rounded bg-background/60 px-1 py-0.5 font-mono text-xs">
          {part.slice(1, -1)}
        </code>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div
      className={cn(
        "group flex animate-fade-in gap-3",
        isUser ? "flex-row" : "flex-row-reverse",
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
          isUser
            ? "bg-muted text-muted-foreground"
            : "bg-gradient-to-br from-primary to-primary-glow text-primary-foreground shadow-md shadow-primary/30",
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className={cn("flex max-w-[85%] flex-col gap-1", isUser ? "items-start" : "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm",
            isUser
              ? "rounded-tl-sm bg-user-bubble text-user-bubble-foreground"
              : "rounded-tr-sm bg-baldwin-bubble text-baldwin-bubble-foreground",
          )}
        >
          <div className="whitespace-pre-wrap break-words">{renderMarkdown(message.content)}</div>

          {message.toolCalls && message.toolCalls.length > 0 && (
            <div className="mt-2.5 space-y-1.5">
              {message.toolCalls.map((t, i) => (
                <ToolBadge key={i} tool={t} />
              ))}
            </div>
          )}
        </div>

        <div
          className={cn(
            "flex items-center gap-2 px-1 font-mono text-[10px] text-muted-foreground",
            isUser ? "flex-row" : "flex-row-reverse",
          )}
        >
          <span>{formatTime(message.timestamp)}</span>
          {message.responseMs && (
            <span className="flex items-center gap-0.5">
              <Clock className="h-2.5 w-2.5" />
              {(message.responseMs / 1000).toFixed(1)}s
            </span>
          )}
          {message.confidence !== undefined && (
            <span className="rounded bg-muted px-1 py-0.5">{message.confidence}% conf</span>
          )}
          <button
            onClick={handleCopy}
            className="opacity-0 transition-opacity hover:text-foreground group-hover:opacity-100"
            aria-label="Copy message"
          >
            {copied ? <Check className="h-2.5 w-2.5" /> : <Copy className="h-2.5 w-2.5" />}
          </button>
        </div>
      </div>
    </div>
  );
}
