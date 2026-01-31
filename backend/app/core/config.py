"""
Configuration module for the FastAPI backend.
Loads environment variables and provides global settings.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database Configuration
    DATABASE_URL: str
    
    # JWT Configuration (shared with Better Auth)
    BETTER_AUTH_SECRET: str
    
    # Application Configuration
    APP_NAME: str = "Todo API"
    DEBUG: bool = False
    
    # CORS Configuration
    FRONTEND_URL: str = "http://localhost:3000"
    
    # JWT Algorithm (Better Auth uses HS256 by default)
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings loader.
    Returns a singleton Settings instance.
    """
    return Settings()


# Export settings instance for easy import
settings = get_settings()
