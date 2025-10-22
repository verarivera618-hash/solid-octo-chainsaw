"""
Configuration module for Alpaca Trading Bot with Perplexity Integration
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PerplexityConfig(BaseSettings):
    """Perplexity API configuration"""
    api_key: str = Field(..., env="PERPLEXITY_API_KEY")
    base_url: str = "https://api.perplexity.ai/chat/completions"
    model: str = "sonar-pro"
    deep_research_model: str = "sonar-deep-research"
    timeout: int = 30
    max_retries: int = 3
    
    class Config:
        env_prefix = "PERPLEXITY_"


class AlpacaConfig(BaseSettings):
    """Alpaca API configuration"""
    api_key: str = Field(..., env="ALPACA_API_KEY")
    secret_key: str = Field(..., env="ALPACA_SECRET_KEY")
    base_url: str = Field(
        default="https://paper-api.alpaca.markets",
        env="ALPACA_BASE_URL"
    )
    paper_trading: bool = Field(default=True, env="PAPER_TRADING")
    market_data_feed: str = Field(default="iex", env="MARKET_DATA_FEED")
    enable_websocket: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    
    @validator("market_data_feed")
    def validate_feed(cls, v):
        if v not in ["iex", "sip"]:
            raise ValueError("market_data_feed must be 'iex' or 'sip'")
        return v
    
    class Config:
        env_prefix = "ALPACA_"


class TradingConfig(BaseSettings):
    """Trading strategy configuration"""
    max_position_size: float = Field(default=0.1, env="MAX_POSITION_SIZE")
    default_stop_loss: float = Field(default=0.02, env="DEFAULT_STOP_LOSS")
    default_take_profit: float = Field(default=0.05, env="DEFAULT_TAKE_PROFIT")
    min_cash_reserve: float = Field(default=0.2, env="MIN_CASH_RESERVE")
    max_daily_trades: int = Field(default=10, env="MAX_DAILY_TRADES")
    enable_short_selling: bool = Field(default=False, env="ENABLE_SHORT_SELLING")
    
    @validator("max_position_size")
    def validate_position_size(cls, v):
        if not 0 < v <= 1:
            raise ValueError("max_position_size must be between 0 and 1")
        return v
    
    class Config:
        env_prefix = "TRADING_"


class SystemConfig(BaseSettings):
    """System configuration"""
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8000, env="METRICS_PORT")
    
    class Config:
        env_prefix = "SYSTEM_"


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.perplexity = PerplexityConfig()
        self.alpaca = AlpacaConfig()
        self.trading = TradingConfig()
        self.system = SystemConfig()
    
    def validate(self) -> bool:
        """Validate all configuration"""
        try:
            # Check API keys are not default values
            if "your_" in self.perplexity.api_key.lower():
                raise ValueError("Please set a valid PERPLEXITY_API_KEY")
            if "your_" in self.alpaca.api_key.lower():
                raise ValueError("Please set a valid ALPACA_API_KEY")
            if "your_" in self.alpaca.secret_key.lower():
                raise ValueError("Please set a valid ALPACA_SECRET_KEY")
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            "perplexity": self.perplexity.dict(),
            "alpaca": self.alpaca.dict(exclude={"secret_key"}),
            "trading": self.trading.dict(),
            "system": self.system.dict()
        }


# Singleton instance
config = Config()