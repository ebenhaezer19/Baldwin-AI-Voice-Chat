"""
WeatherAPI.com Integration
Fetch real-time weather data using WeatherAPI.com
"""
import asyncio
from typing import Optional
import httpx
from config import settings
from utils.logger import logger


async def get_weather(
    city: str = "Jakarta",
    units: str = "metric",
) -> dict:
    """
    Get current weather for a city using WeatherAPI.com
    
    Args:
        city: City name (e.g., "Jakarta", "New York")
        units: Temperature units ("metric" for Celsius, "imperial" for Fahrenheit)
    
    Returns:
        Dict with weather information
    """
    try:
        # Get API key from config (check both weatherapi_api_key and openweather_api_key for backward compatibility)
        api_key = getattr(settings, 'weatherapi_api_key', None) or getattr(settings, 'openweather_api_key', None)
        
        if not api_key:
            logger.warning("[WEATHER] WeatherAPI key not configured")
            return {"success": False, "error": "WeatherAPI key not configured"}
        
        logger.info(f"[WEATHER] Fetching weather for: {city}")
        
        # WeatherAPI.com endpoint
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.weatherapi.com/v1/current.json",
                params={
                    "key": api_key,
                    "q": city,
                    "aqi": "yes",  # Include air quality data
                }
            )
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            logger.error(f"[WEATHER] API error {response.status_code}: {error_msg}")
            return {"success": False, "error": error_msg}
        
        data = response.json()
        location = data.get("location", {})
        current = data.get("current", {})
        
        # Determine temperature symbol based on units
        temp_symbol = "°C" if units == "metric" else "°F"
        
        # Extract relevant data
        result = {
            "success": True,
            "city": location.get("name", city),
            "region": location.get("region", ""),
            "country": location.get("country", ""),
            "temperature": current.get("temp_c") if units == "metric" else current.get("temp_f"),
            "feels_like": current.get("feelslike_c") if units == "metric" else current.get("feelslike_f"),
            "humidity": current.get("humidity"),
            "condition": current.get("condition", {}).get("text", ""),
            "wind_speed": current.get("wind_kph") if units == "metric" else current.get("wind_mph"),
            "wind_direction": current.get("wind_dir", ""),
            "pressure": current.get("pressure_mb"),
            "cloud": current.get("cloud"),
            "precipitation": current.get("precip_mm") if units == "metric" else current.get("precip_in"),
            "visibility": current.get("vis_km") if units == "metric" else current.get("vis_miles"),
            "uv_index": current.get("uv"),
            "units": temp_symbol,
            "last_updated": current.get("last_updated", ""),
        }
        
        # Add air quality if available
        if "air_quality" in current:
            aqi = current.get("air_quality", {})
            result["aqi"] = {
                "us_epa_index": aqi.get("us-epa-index"),
                "pm2_5": aqi.get("pm2_5"),
                "pm10": aqi.get("pm10"),
            }
        
        logger.info(f"[WEATHER] Got weather for {result['city']}: {result['condition']} {result['temperature']}{temp_symbol}")
        return result
    
    except Exception as e:
        logger.error(f"[WEATHER] Error: {e}")
        return {"success": False, "error": str(e)}


# Tool definition for LLM function calling
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city using WeatherAPI.com. Use this when user asks about weather, temperature, or climate conditions.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (e.g., 'Jakarta', 'New York', 'London')",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "description": "Temperature units (metric=Celsius, imperial=Fahrenheit)",
                },
            },
            "required": ["city"],
        },
    },
}
