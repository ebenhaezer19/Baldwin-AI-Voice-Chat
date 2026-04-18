"""
Search API Integration
Perform web searches using Serper/SerpAPI
"""
import asyncio
from typing import Optional
import httpx
from config import settings
from utils.logger import logger


async def search_web(
    query: str,
    num_results: int = 5,
) -> dict:
    """
    Perform web search using Serper API
    
    Args:
        query: Search query
        num_results: Number of results to return (1-10)
    
    Returns:
        Dict with search results
    """
    try:
        if not settings.search_api_key:
            logger.warning("[SEARCH] Search API key not configured")
            return {"success": False, "error": "Search API key not configured", "results": []}
        
        logger.info(f"[SEARCH] Searching for: {query}")
        
        payload = {
            "q": query,
            "num": min(num_results, 10),
        }
        
        headers = {
            "X-API-KEY": settings.search_api_key,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                json=payload,
                headers=headers,
            )
        
        if response.status_code != 200:
            logger.error(f"[SEARCH] API error {response.status_code}: {response.text}")
            return {"success": False, "error": f"API error {response.status_code}", "results": []}
        
        data = response.json()
        
        # Extract search results
        results = []
        for item in data.get("organic", [])[:num_results]:
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })
        
        result = {
            "success": True,
            "query": query,
            "total_results": len(results),
            "results": results,
        }
        
        logger.info(f"[SEARCH] Found {len(results)} results for: {query}")
        return result
    
    except Exception as e:
        logger.error(f"[SEARCH] Error: {e}")
        return {"success": False, "error": str(e), "results": []}


# Tool definition for LLM function calling
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Perform web search. Use this when user asks to search for information online.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'berapa harga laptop terbaru', 'cara membuat kopi espresso')",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return (1-10, default 5)",
                },
            },
            "required": ["query"],
        },
    },
}
