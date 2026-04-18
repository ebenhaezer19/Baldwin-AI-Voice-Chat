import { Download, Trash2, Activity, MessageSquare, Timer } from "lucide-react";
import { useId } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import type { ChatMessage } from "./types";

interface SessionSidebarProps {
  messages: ChatMessage[];
  startedAt: Date;
  durationSec: number;
  onClear: () => void;
  onDownload: () => void;
}

const APIS = [
  { name: "Groq", status: "ok", detail: "89,234 / 100,000 tokens" },
  { name: "Sarvam", status: "ok", detail: "STT online" },
  { name: "ElevenLabs", status: "ok", detail: "TTS — Default" },
] as const;

function fmt(d: number) {
  const m = Math.floor(d / 60);
  const s = d % 60;
  return `${m}m ${String(s).padStart(2, "0")}s`;
}

export function SessionSidebar({
  messages,
  startedAt,
  durationSec,
  onClear,
  onDownload,
}: SessionSidebarProps) {
  const baseId = useId();
  const sessionId = `bw_${baseId.replace(/[^a-z0-9]/g, '')}`.slice(0, 12);

  return (
    <aside className="flex w-full flex-col gap-4 border-l border-border bg-sidebar p-4 lg:w-80">
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Session
        </h3>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <div className="rounded-lg border border-border bg-card p-3">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Timer className="h-3 w-3" />
              Duration
            </div>
            <div className="mt-1 font-mono text-sm font-semibold tabular-nums">
              {fmt(durationSec)}
            </div>
          </div>
          <div className="rounded-lg border border-border bg-card p-3">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <MessageSquare className="h-3 w-3" />
              Messages
            </div>
            <div className="mt-1 font-mono text-sm font-semibold tabular-nums">
              {messages.length}
            </div>
          </div>
        </div>
        <div className="mt-2 truncate rounded-md bg-muted px-2 py-1 font-mono text-[10px] text-muted-foreground" suppressHydrationWarning>
          {sessionId}
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          <Activity className="h-3 w-3" /> API Status
        </h3>
        <div className="space-y-1.5">
          {APIS.map((a) => (
            <div
              key={a.name}
              className="flex items-center justify-between rounded-lg border border-border bg-card px-2.5 py-2"
            >
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 animate-pulse rounded-full bg-success" />
                <span className="text-sm font-medium">{a.name}</span>
              </div>
              <span className="font-mono text-[10px] text-muted-foreground">{a.detail}</span>
            </div>
          ))}
        </div>
      </div>

      <Separator />

      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Model
        </h3>
        <div className="rounded-lg border border-border bg-card p-3 text-xs">
          <div className="flex justify-between">
            <span className="text-muted-foreground">LLM</span>
            <span className="font-mono">llama-3.3-70b</span>
          </div>
          <div className="mt-1 flex justify-between">
            <span className="text-muted-foreground">Voice</span>
            <span className="font-mono">Default</span>
          </div>
          <div className="mt-1 flex justify-between">
            <span className="text-muted-foreground">Lang</span>
            <span className="font-mono">en-IN / id-ID</span>
          </div>
        </div>
      </div>

      <div className="mt-auto flex flex-col gap-2">
        <Button variant="outline" size="sm" onClick={onDownload}>
          <Download className="mr-2 h-3.5 w-3.5" /> Download transcript
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClear}
          className="text-destructive hover:text-destructive"
        >
          <Trash2 className="mr-2 h-3.5 w-3.5" /> Clear session
        </Button>
      </div>
    </aside>
  );
}
