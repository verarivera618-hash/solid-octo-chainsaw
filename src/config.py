"""
Configuration management for Perplexity-Alpaca Trading Integration
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for API keys and settings"""
    
    # Perplexity API Configuration
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai/chat/completions"
    
    # Alpaca Configuration
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
    ALPACA_BASE_URL: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    
    # Trading Configuration
    DEFAULT_STRATEGY: str = os.getenv("DEFAULT_STRATEGY", "semiconductor_momentum")
    PAPER_TRADING: bool = os.getenv("PAPER_TRADING", "true").lower() == "true"
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "0.1"))
    RISK_TOLERANCE: float = float(os.getenv("RISK_TOLERANCE", "0.02"))
    
    # Data Configuration
    CURSOR_TASKS_DIR: str = "cursor_tasks"
    LOGS_DIR: str = "logs"
    DATA_DIR: str = "data"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required API keys are present"""
        required_keys = [
            cls.PERPLEXITY_API_KEY,
            cls.ALPACA_API_KEY,
            cls.ALPACA_SECRET_KEY
        ]
        
        missing_keys = [key for key in required_keys if not key]
        if missing_keys:
            print(f"Missing required API keys: {missing_keys}")
            return False
        return True
    
    @classmethod
    def get_perplexity_headers(cls) -> dict:
        """Get headers for Perplexity API requests"""
        return {
            "accept": "application/json",
            "authorization": f"Bearer {cls.PERPLEXITY_API_KEY}",
            "content-type": "application/json"
        }
