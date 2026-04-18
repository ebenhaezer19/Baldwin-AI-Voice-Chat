"""
News API Integration
Fetch latest news from NewsAPI.org
"""
import asyncio
from typing import Optional
import httpx
from config import settings
from utils.logger import logger


async def get_news(
    query: str = "cybersecurity",
    category: Optional[str] = None,
    language: str = "id",
    page_size: int = 5,
) -> dict:
    """
    Get latest news from NewsAPI.org
    
    Args:
        query: Search query (e.g., "cybersecurity", "berita hari ini")
        category: News category (business, health, sports, technology, etc.)
        language: Language code (id for Indonesian, en for English)
        page_size: Number of articles to return (max 100)
    
    Returns:
        Dict with articles list and total count
    """
    try:
        if not settings.news_api_key:
            logger.warning("[NEWS] News API key not configured")
            return {"success": False, "error": "News API key not configured", "articles": []}
        
        # Determine endpoint
        if category:
            endpoint = "https://newsapi.org/v2/top-headlines"
            params = {
                "category": category,
                "language": language,
                "pageSize": page_size,
                "apiKey": settings.news_api_key,
            }
        else:
            endpoint = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": language,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "apiKey": settings.news_api_key,
            }
        
        logger.info(f"[NEWS] Fetching news for query: {query}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(endpoint, params=params)
        
        if response.status_code != 200:
            logger.error(f"[NEWS] API error {response.status_code}: {response.text}")
            return {"success": False, "error": f"API error {response.status_code}", "articles": []}
        
        data = response.json()
        
        # Format articles
        articles = []
        for article in data.get("articles", [])[:page_size]:
            articles.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "source": article.get("source", {}).get("name", ""),
                "publishedAt": article.get("publishedAt", ""),
                "url": article.get("url", ""),
            })
        
        result = {
            "success": True,
            "query": query,
            "total_results": data.get("totalResults", 0),
            "articles": articles,
        }
        
        logger.info(f"[NEWS] Found {len(articles)} articles")
        return result
    
    except Exception as e:
        logger.error(f"[NEWS] Error: {e}")
        return {"success": False, "error": str(e), "articles": []}


# Tool definition for LLM function calling
NEWS_TOOL = {
    "type": "function",
    "function": {
        "name": "get_news",
        "description": "Fetch latest news from NewsAPI. Use this when user asks about news, current events, or latest updates.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'cybersecurity', 'berita teknologi', 'politics')",
                },
                "category": {
                    "type": "string",
                    "enum": ["business", "health", "sports", "technology", "entertainment", "politics"],
                    "description": "News category (optional)",
                },
                "language": {
                    "type": "string",
                    "enum": ["id", "en"],
                    "description": "Language code (id for Indonesian, en for English)",
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of articles to return (1-100, default 5)",
                },
            },
            "required": ["query"],
        },
    },
}
