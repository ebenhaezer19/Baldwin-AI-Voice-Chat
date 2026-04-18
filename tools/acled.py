"""
ACLED API Integration
Fetch conflict and event data from Armed Conflict Location & Event Data project
"""
import asyncio
from typing import Optional
import httpx
from config import settings
from utils.logger import logger


async def get_conflict_data(
    country: Optional[str] = None,
    region: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 10,
) -> dict:
    """
    Get conflict and crisis event data from ACLED
    
    Args:
        country: Country name or ISO code
        region: Region name
        year: Year to filter events
        limit: Number of events to return (1-100, default 10)
    
    Returns:
        Dict with conflict/event data
    """
    try:
        if not settings.acled_email or not settings.acled_password:
            logger.warning("[ACLED] ACLED credentials not configured")
            return {"success": False, "error": "ACLED credentials not configured", "events": []}
        
        logger.info(f"[ACLED] Fetching conflict data")
        
        # ACLED API endpoint
        url = "https://api.acleddata.com/epics"
        
        params = {
            "email": settings.acled_email,
            "password": settings.acled_password,
            "limit": min(limit, 100),
        }
        
        if country:
            params["country"] = country
        if region:
            params["region"] = region
        if year:
            params["year"] = year
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
        
        if response.status_code != 200:
            logger.error(f"[ACLED] API error {response.status_code}: {response.text}")
            return {"success": False, "error": f"API error {response.status_code}", "events": []}
        
        data = response.json()
        
        # Extract events
        events = []
        for event in data.get("data", [])[:limit]:
            events.append({
                "event": event.get("event_id_cnty", ""),
                "event_type": event.get("event_type", ""),
                "date": event.get("event_date", ""),
                "country": event.get("country", ""),
                "location": event.get("location", ""),
                "deaths": event.get("deaths", 0),
            })
        
        result = {
            "success": True,
            "total_events": len(events),
            "events": events,
        }
        
        logger.info(f"[ACLED] Found {len(events)} events")
        return result
    
    except Exception as e:
        logger.error(f"[ACLED] Error: {e}")
        return {"success": False, "error": str(e), "events": []}


# Tool definition for LLM function calling
ACLED_TOOL = {
    "type": "function",
    "function": {
        "name": "get_conflict_data",
        "description": "Get conflict and crisis event data from ACLED database. Use when user asks about conflicts, crises, or violence events.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Country name or ISO code (e.g., 'Indonesia', 'Philippines')",
                },
                "region": {
                    "type": "string",
                    "description": "Region name (e.g., 'Southeast Asia', 'Middle East')",
                },
                "year": {
                    "type": "integer",
                    "description": "Year to filter events (e.g., 2024, 2025)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of events to return (1-100, default 10)",
                },
            },
        },
    },
}
