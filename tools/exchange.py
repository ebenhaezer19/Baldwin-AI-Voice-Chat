"""
Exchange Rate API Integration
Fetch currency exchange rates
"""
import asyncio
from typing import Optional
import httpx
from config import settings
from utils.logger import logger


async def get_exchange_rate(
    from_currency: str = "USD",
    to_currency: str = "IDR",
) -> dict:
    """
    Get exchange rate between two currencies
    
    Args:
        from_currency: Source currency code (e.g., "USD", "EUR")
        to_currency: Target currency code (e.g., "IDR", "SGD")
    
    Returns:
        Dict with exchange rate and conversion information
    """
    try:
        if not settings.exchangerate_api_key:
            logger.warning("[EXCHANGE] Exchange Rate API key not configured")
            return {"success": False, "error": "Exchange Rate API key not configured"}
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        logger.info(f"[EXCHANGE] Fetching rate: {from_currency} -> {to_currency}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://v6.exchangerate-api.com/v6/{settings.exchangerate_api_key}/latest/{from_currency}"
            )
        
        if response.status_code != 200:
            logger.error(f"[EXCHANGE] API error {response.status_code}: {response.text}")
            return {"success": False, "error": f"Could not fetch exchange rate"}
        
        data = response.json()
        
        if data.get("result") != "success":
            logger.error(f"[EXCHANGE] API returned error: {data}")
            return {"success": False, "error": f"Invalid currency code"}
        
        rates = data.get("conversion_rates", {})
        
        if to_currency not in rates:
            return {"success": False, "error": f"Currency {to_currency} not found"}
        
        rate = rates[to_currency]
        
        result = {
            "success": True,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": rate,
            "timestamp": data.get("time_last_updated", ""),
            "conversion_1": f"1 {from_currency} = {rate:.2f} {to_currency}",
            "conversion_100": f"100 {from_currency} = {rate * 100:.2f} {to_currency}",
        }
        
        logger.info(f"[EXCHANGE] Rate: 1 {from_currency} = {rate:.2f} {to_currency}")
        return result
    
    except Exception as e:
        logger.error(f"[EXCHANGE] Error: {e}")
        return {"success": False, "error": str(e)}


# Tool definition for LLM function calling
EXCHANGE_TOOL = {
    "type": "function",
    "function": {
        "name": "get_exchange_rate",
        "description": "Get currency exchange rate. Use this when user asks about currency conversion or exchange rates.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_currency": {
                    "type": "string",
                    "description": "Source currency code (e.g., 'USD', 'EUR', 'GBP')",
                },
                "to_currency": {
                    "type": "string",
                    "description": "Target currency code (e.g., 'IDR', 'SGD', 'MYR')",
                },
            },
            "required": ["from_currency", "to_currency"],
        },
    },
}
