"""
Configuration management for Perplexity-Alpaca integration.
"""
import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Perplexity API Configuration
    perplexity_api_key: str = Field(..., env="PERPLEXITY_API_KEY")
    perplexity_base_url: str = Field(
        default="https://api.perplexity.ai/chat/completions",
        env="PERPLEXITY_BASE_URL"
    )
    
    # Alpaca API Configuration
    alpaca_api_key: str = Field(..., env="ALPACA_API_KEY")
    alpaca_secret_key: str = Field(..., env="ALPACA_SECRET_KEY")
    alpaca_base_url: str = Field(
        default="https://paper-api.alpaca.markets",
        env="ALPACA_BASE_URL"
    )
    
    # Trading Configuration
    portfolio_size: float = Field(default=100000.0, env="PORTFOLIO_SIZE")
    max_position_size: float = Field(default=0.1, env="MAX_POSITION_SIZE")
    risk_per_trade: float = Field(default=0.02, env="RISK_PER_TRADE")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/trading.log", env="LOG_FILE")
    
    # Rate Limiting
    perplexity_rate_limit: int = Field(default=60, env="PERPLEXITY_RATE_LIMIT")  # requests per minute
    alpaca_rate_limit: int = Field(default=200, env="ALPACA_RATE_LIMIT")  # requests per minute
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings."""
    return settings