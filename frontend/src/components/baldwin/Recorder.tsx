import { useEffect, useMemo, useState } from "react";
import { Mic, MicOff, Loader2, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface RecorderProps {
  recording: boolean;
  transcribing: boolean;
  liveTranscript: string;
  confidence: number | null;
  onToggle: () => void;
  onSendText: (text: string) => void;
}

function Waveform({ active }: { active: boolean }) {
  const bars = useMemo(() => Array.from({ length: 28 }), []);
  return (
    <div className="flex h-10 items-center justify-center gap-[3px]">
      {bars.map((_, i) => (
        <span
          key={i}
          className={cn(
            "w-[3px] rounded-full bg-gradient-to-t from-primary to-primary-glow",
            active ? "animate-wave" : "h-1 opacity-40",
          )}
          style={{
            height: active ? `${20 + Math.sin(i) * 18 + (i % 5) * 4}px` : undefined,
            animationDelay: active ? `${i * 50}ms` : undefined,
          }}
        />
      ))}
    </div>
  );
}

export function Recorder({
  recording,
  transcribing,
  liveTranscript,
  confidence,
  onToggle,
  onSendText,
}: RecorderProps) {
  const [seconds, setSeconds] = useState(0);
  const [text, setText] = useState("");

  useEffect(() => {
    if (!recording) {
      setSeconds(0);
      return;
    }
    const id = window.setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => window.clearInterval(id);
  }, [recording]);

  const status = transcribing
    ? "Transcribing…"
    : recording
      ? "Listening…"
      : "Tap mic or hold Space to talk";

  return (
    <div className="border-t border-border bg-card/60 backdrop-blur">
      <div className="mx-auto flex max-w-3xl flex-col gap-3 px-4 py-4 md:px-6">
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={onToggle}
            disabled={transcribing}
            aria-label={recording ? "Stop recording" : "Start recording"}
            className={cn(
              "relative flex h-16 w-16 shrink-0 items-center justify-center rounded-full border-2 text-primary-foreground transition-all cursor-pointer",
              recording
                ? "animate-pulse-ring border-destructive bg-destructive"
                : "neon-glow border-primary bg-primary hover:scale-105",
            )}
          >
            {transcribing ? (
              <Loader2 className="h-6 w-6 animate-spin" />
            ) : recording ? (
              <MicOff className="h-6 w-6" />
            ) : (
              <Mic className="h-6 w-6" />
            )}
          </button>

          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-3">
              <span
                className={cn(
                  "text-sm font-semibold",
                  recording && "text-destructive",
                  transcribing && "text-primary",
                )}
              >
                {status}
              </span>
              {recording && (
                <span className="font-mono text-xs tabular-nums text-muted-foreground">
                  {String(Math.floor(seconds / 60)).padStart(2, "0")}:
                  {String(seconds % 60).padStart(2, "0")}
                </span>
              )}
              {confidence !== null && !recording && (
                <span className="rounded-md bg-success/15 px-1.5 py-0.5 font-mono text-[10px] text-success">
                  {confidence}% confidence
                </span>
              )}
            </div>
            <Waveform active={recording} />
          </div>
        </div>

        {(liveTranscript || transcribing) && (
          <div className="animate-fade-in rounded-xl border border-border bg-background/70 px-3 py-2 text-sm">
            <span className="mr-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
              transcript
            </span>
            {liveTranscript || <span className="text-muted-foreground">Listening to audio…</span>}
            {transcribing && (
              <span className="ml-1 inline-block h-3 w-1 animate-pulse bg-primary align-middle" />
            )}
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (text.trim()) {
              onSendText(text.trim());
              setText("");
            }
          }}
          className="flex items-center gap-2"
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Or type a message…"
            className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none ring-ring focus:ring-2"
          />
          <Button type="submit" size="icon" disabled={!text.trim()} aria-label="Send">
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
