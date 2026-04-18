"""
OpenWeather API Integration
Fetch real-time weather data
"""
import asyncio
from typing import Optional
import httpx
from config import settings
from utils.logger import logger


async def get_weather(
    city: str = "Jakarta",
    country_code: Optional[str] = None,
    units: str = "metric",
) -> dict:
    """
    Get current weather for a city using OpenWeather API
    
    Args:
        city: City name (e.g., "Jakarta", "New York")
        country_code: Optional ISO 3166 country code (e.g., "ID", "US")
        units: Temperature units ("metric" for Celsius, "imperial" for Fahrenheit)
    
    Returns:
        Dict with weather information
    """
    try:
        if not settings.openweather_api_key:
            logger.warning("[WEATHER] OpenWeather API key not configured")
            return {"success": False, "error": "OpenWeather API key not configured"}
        
        # Build location string
        location = f"{city},{country_code}" if country_code else city
        
        logger.info(f"[WEATHER] Fetching weather for: {location}")
        
        # Get coordinates first (geocoding)
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Geocoding endpoint
            geo_response = await client.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q": location,
                    "limit": 1,
                    "appid": settings.openweather_api_key,
                }
            )
        
        if geo_response.status_code != 200:
            logger.error(f"[WEATHER] Geocoding error: {geo_response.text}")
            return {"success": False, "error": "City not found"}
        
        geo_data = geo_response.json()
        if not geo_data:
            return {"success": False, "error": f"City '{city}' not found"}
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        city_name = geo_data[0].get("name", city)
        country = geo_data[0].get("country", "")
        
        # Get weather data
        async with httpx.AsyncClient(timeout=10.0) as client:
            weather_response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "units": units,
                    "appid": settings.openweather_api_key,
                }
            )
        
        if weather_response.status_code != 200:
            logger.error(f"[WEATHER] Weather API error: {weather_response.text}")
            return {"success": False, "error": "Could not fetch weather data"}
        
        weather = weather_response.json()
        
        # Extract relevant data
        result = {
            "success": True,
            "city": city_name,
            "country": country,
            "temperature": weather["main"]["temp"],
            "feels_like": weather["main"]["feels_like"],
            "min_temp": weather["main"]["temp_min"],
            "max_temp": weather["main"]["temp_max"],
            "humidity": weather["main"]["humidity"],
            "pressure": weather["main"]["pressure"],
            "description": weather["weather"][0]["description"],
            "wind_speed": weather["wind"]["speed"],
            "clouds": weather["clouds"]["all"],
            "units": "°C" if units == "metric" else "°F",
        }
        
        logger.info(f"[WEATHER] Got weather for {city_name}: {result['description']}")
        return result
    
    except Exception as e:
        logger.error(f"[WEATHER] Error: {e}")
        return {"success": False, "error": str(e)}


# Tool definition for LLM function calling
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city. Use this when user asks about weather, temperature, or climate conditions.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (e.g., 'Jakarta', 'New York')",
                },
                "country_code": {
                    "type": "string",
                    "description": "ISO 3166 country code (e.g., 'ID', 'US') - optional",
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
