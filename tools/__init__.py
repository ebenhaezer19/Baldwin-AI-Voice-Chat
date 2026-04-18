"""
Tools module for Baldwin
Contains integrations with external APIs (News, Weather, Search, etc.)
"""
from tools.news import get_news, NEWS_TOOL
from tools.weather import get_weather, WEATHER_TOOL
from tools.exchange import get_exchange_rate, EXCHANGE_TOOL
from tools.search import search_web, SEARCH_TOOL
from tools.acled import get_conflict_data, ACLED_TOOL

# All available tools for LLM function calling
AVAILABLE_TOOLS = [
    NEWS_TOOL,
    WEATHER_TOOL,
    EXCHANGE_TOOL,
    SEARCH_TOOL,
    ACLED_TOOL,
]

# Tool execution mapping
TOOL_FUNCTIONS = {
    "get_news": get_news,
    "get_weather": get_weather,
    "get_exchange_rate": get_exchange_rate,
    "search_web": search_web,
    "get_conflict_data": get_conflict_data,
}

__all__ = [
    "get_news",
    "get_weather",
    "get_exchange_rate",
    "search_web",
    "get_conflict_data",
    "AVAILABLE_TOOLS",
    "TOOL_FUNCTIONS",
]
