"""
Configuration settings for the backend
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/regional_analytics"
    )
    
    # VK API (optional, for VK group parsing)
    vk_access_token: str = os.getenv("VK_ACCESS_TOKEN", "")
    
    # Telegram (optional, for better parsing)
    telegram_api_id: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    telegram_api_hash: str = os.getenv("TELEGRAM_API_HASH", "")
    
    # Application
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Parsing settings
    default_parse_interval: int = 15  # minutes
    max_concurrent_parsers: int = 5
    request_timeout: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
