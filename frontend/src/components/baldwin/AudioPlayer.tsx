import { useEffect, useRef, useState } from "react";
import { Play, Pause, Download, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";

interface AudioPlayerProps {
  durationSec: number;
}

const SPEEDS = [0.75, 1, 1.5, 2] as const;

export function AudioPlayer({ durationSec }: AudioPlayerProps) {
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [volume, setVolume] = useState(80);
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(1);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!playing) {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = window.setInterval(() => {
      setProgress((p) => {
        const step = (0.1 / durationSec) * 100 * speed;
        const next = p + step;
        if (next >= 100) {
          setPlaying(false);
          return 100;
        }
        return next;
      });
    }, 100);
    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
    };
  }, [playing, speed, durationSec]);

  const elapsed = ((progress / 100) * durationSec).toFixed(1);

  return (
    <div className="mt-2 flex items-center gap-2 rounded-xl border border-border bg-background/70 p-2">
      <Button
        size="icon"
        variant="default"
        className="h-8 w-8 shrink-0 rounded-full"
        onClick={() => {
          if (progress >= 100) setProgress(0);
          setPlaying((p) => !p);
        }}
        aria-label={playing ? "Pause" : "Play"}
      >
        {playing ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
      </Button>

      <div className="flex min-w-0 flex-1 items-center gap-2">
        <div className="relative h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
          <div
            className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-primary to-primary-glow transition-[width] duration-100"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="font-mono text-[10px] tabular-nums text-muted-foreground">
          {elapsed}s / {durationSec.toFixed(1)}s
        </span>
      </div>

      <div className="hidden items-center gap-1.5 sm:flex">
        <Volume2 className="h-3.5 w-3.5 text-muted-foreground" />
        <Slider
          value={[volume]}
          onValueChange={(v) => setVolume(v[0])}
          max={100}
          step={1}
          className="w-16"
        />
      </div>

      <select
        value={speed}
        onChange={(e) => setSpeed(Number(e.target.value) as (typeof SPEEDS)[number])}
        className="rounded-md border border-border bg-background px-1.5 py-1 font-mono text-[10px]"
        aria-label="Playback speed"
      >
        {SPEEDS.map((s) => (
          <option key={s} value={s}>
            {s}×
          </option>
        ))}
      </select>

      <Button size="icon" variant="ghost" className="h-7 w-7" aria-label="Download MP3">
        <Download className="h-3.5 w-3.5" />
      </Button>
    </div>
  );
}
