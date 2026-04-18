export type ToolName = "weather" | "news" | "calculator" | "currency" | "todo";

export interface NewsArticle {
  title: string;
  description?: string;
  source: string;
  publishedAt: string;
  url: string;
}

export interface ToolResult {
  tool_name: ToolName;
  success: boolean;
  articles?: NewsArticle[];
  total_results?: number;
  query?: string;
  data?: Record<string, unknown>;
  error?: string;
}

export interface ToolCall {
  name: ToolName;
  label: string;
  parameters: Record<string, string | number>;
  result: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "baldwin";
  content: string;
  timestamp: Date;
  responseMs?: number;
  confidence?: number;
  toolCalls?: ToolCall[];
  toolResults?: ToolResult[];
  audioDurationSec?: number;
}
