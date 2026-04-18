import { Terminal, Settings, HelpCircle, Power } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  connected: boolean;
  onOpenSettings: () => void;
}

export function Header({ connected, onOpenSettings }: HeaderProps) {
  return (
    <header className="relative flex items-center justify-between border-b border-border bg-card/80 px-4 py-3 backdrop-blur md:px-6">
      <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-primary to-transparent opacity-60" />

      <div className="flex items-center gap-3">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-md border border-primary/40 bg-background neon-border">
          <Terminal className="h-4 w-4 text-primary neon-text" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-bold uppercase tracking-[0.2em] text-primary neon-text">
              Baldwin
            </h1>
            <span className="rounded border border-primary/40 px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-widest text-primary">
              v1.0
            </span>
          </div>
          <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
            &gt; voice_assistant.exe
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="hidden items-center gap-2 rounded border border-primary/30 bg-background/60 px-3 py-1.5 sm:flex">
          <span
            className={`h-2 w-2 rounded-full ${
              connected ? "bg-primary shadow-[0_0_8px_var(--primary)]" : "bg-destructive"
            } animate-pulse`}
          />
          <span className="font-mono text-[10px] uppercase tracking-widest text-primary">
            {connected ? "online" : "offline"}
          </span>
        </div>
        <Button variant="ghost" size="icon" aria-label="Help" className="text-primary hover:bg-primary/10">
          <HelpCircle className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Settings"
          onClick={onOpenSettings}
          className="text-primary hover:bg-primary/10"
        >
          <Settings className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" aria-label="Power" className="hidden text-primary hover:bg-primary/10 md:inline-flex">
          <Power className="h-4 w-4" />
        </Button>
      </div>
    </header>
  );
}
