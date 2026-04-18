import { ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import type { NewsArticle } from "./types";

interface NewsArticlesProps {
  articles: NewsArticle[];
  totalResults?: number;
  query?: string;
}

export function NewsArticles({ articles, totalResults, query }: NewsArticlesProps) {
  if (!articles || articles.length === 0) {
    return (
      <div className="text-xs text-muted-foreground">
        No articles found {query ? `for "${query}"` : ""}
      </div>
    );
  }

  return (
    <div className="mt-2 space-y-2">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
        📰 {articles.length} Articles {totalResults ? `(${totalResults} total found)` : ""}
      </div>
      <div className="space-y-1.5">
        {articles.slice(0, 5).map((article, i) => {
          const publishDate = new Date(article.publishedAt).toLocaleDateString([], {
            month: "short",
            day: "numeric",
          });

          return (
            <div key={i} className="group">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className={cn(
                  "flex items-start gap-2 rounded-lg border border-transparent p-2 transition-all",
                  "hover:border-border hover:bg-background/50",
                  "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary",
                )}
              >
                <div className="mt-1 flex-shrink-0">
                  <ExternalLink className="h-3 w-3 text-muted-foreground transition-colors group-hover:text-primary" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-medium leading-snug group-hover:text-primary">
                    {article.title}
                  </div>
                  <div className="mt-0.5 flex items-center gap-2 text-[10px] text-muted-foreground">
                    <span>{article.source}</span>
                    <span>•</span>
                    <span>{publishDate}</span>
                  </div>
                  {article.description && (
                    <div className="mt-1 text-[11px] text-muted-foreground line-clamp-2">
                      {article.description}
                    </div>
                  )}
                </div>
              </a>
            </div>
          );
        })}
      </div>
    </div>
  );
}
