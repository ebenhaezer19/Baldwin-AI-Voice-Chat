"""
Baldwin Configuration Management
Loads all environment variables and provides centralized config access.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration from .env file"""
    
    # ============ LLM ============
    groq_api_key: str
    
    # ============ STT & TTS ============
    sarvam_api_key: str
    elevenlabs_api_key: str = ""
    
    # ============ Info & Berita ============
    news_api_key: str = ""
    openweather_api_key: str = ""
    weatherapi_api_key: str = ""
    search_api_key: str = ""
    tmdb_api_key: str = ""
    exchangerate_api_key: str = ""
    xai_api_key: str = ""
    
    # ============ Global Intelligence ============
    acled_api_key: str = ""
    acled_email: str = ""
    acled_password: str = ""
    adsb_api_key: str = ""
    marinetraffic_api_key: str = ""
    alpha_vantage_api_key: str = ""
    
    # ============ Config ============
    baldwin_language: str = "id"  # id | en
    baldwin_city: str = "Jakarta"
    baldwin_timezone: str = "Asia/Jakarta"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Load settings
try:
    settings = Settings()  # type: ignore
except Exception as e:
    print(f"⚠️  Warning: Could not load .env file: {e}")
    print("   Make sure to copy .env.template to .env and fill in your API keys.")
    raise
