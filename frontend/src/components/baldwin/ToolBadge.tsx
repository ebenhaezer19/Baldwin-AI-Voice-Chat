import { Cloud, Newspaper, Calculator, Coins, ListChecks } from "lucide-react";
import type { ToolCall, ToolName } from "./types";

const ICONS: Record<ToolName, typeof Cloud> = {
  weather: Cloud,
  news: Newspaper,
  calculator: Calculator,
  currency: Coins,
  todo: ListChecks,
};

export function ToolBadge({ tool }: { tool: ToolCall }) {
  const Icon = ICONS[tool.name];
  return (
    <div className="flex items-start gap-2 rounded-lg border border-border bg-background/70 p-2.5 text-xs">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-accent text-accent-foreground">
        <Icon className="h-3.5 w-3.5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
            tool
          </span>
          <span className="font-semibold">{tool.label}</span>
        </div>
        <div className="mt-0.5 truncate text-muted-foreground">{tool.result}</div>
      </div>
    </div>
  );
}
