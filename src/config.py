"""
Configuration management for Local Trading System
No external API dependencies required
"""
import os
from typing import Optional
from .local_config import LocalConfig

class Config(LocalConfig):
    """Configuration class that inherits from LocalConfig for full local operation"""
    
    # Legacy compatibility - these are no longer required
    PERPLEXITY_API_KEY: str = "LOCAL_MODE"
    PERPLEXITY_BASE_URL: str = LocalConfig.LOCAL_ANALYSIS_ENDPOINT
    
    # Legacy compatibility - these are no longer required  
    ALPACA_API_KEY: str = "LOCAL_MODE"
    ALPACA_SECRET_KEY: str = "LOCAL_MODE"
    ALPACA_BASE_URL: str = LocalConfig.LOCAL_TRADING_ENDPOINT
    
    # Trading Configuration (inherited from LocalConfig)
    DEFAULT_STRATEGY: str = LocalConfig.DEFAULT_STRATEGY
    PAPER_TRADING: bool = LocalConfig.ENABLE_PAPER_TRADING
    MAX_POSITION_SIZE: float = LocalConfig.MAX_POSITION_SIZE
    RISK_TOLERANCE: float = LocalConfig.RISK_TOLERANCE
    
    # Data Configuration (inherited from LocalConfig)
    CURSOR_TASKS_DIR: str = LocalConfig.CURSOR_TASKS_DIR
    LOGS_DIR: str = LocalConfig.LOGS_DIR
    DATA_DIR: str = LocalConfig.DATA_DIR
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate local configuration - no API keys required"""
        print("Running in LOCAL MODE - no external API keys required")
        return LocalConfig.validate_config()
    
    @classmethod
    def get_perplexity_headers(cls) -> dict:
        """Get headers for local API requests"""
        return LocalConfig.get_local_headers()
