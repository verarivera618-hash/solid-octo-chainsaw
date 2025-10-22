"""
Configuration management for Local Trading System
All external API dependencies removed - fully local operation
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for local trading system settings"""
    
    # Trading Configuration (local only)
    DEFAULT_STRATEGY: str = os.getenv("DEFAULT_STRATEGY", "momentum")
    PAPER_TRADING: bool = os.getenv("PAPER_TRADING", "true").lower() == "true"
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "0.1"))
    RISK_TOLERANCE: float = float(os.getenv("RISK_TOLERANCE", "0.02"))
    
    # Data Configuration (local only)
    CURSOR_TASKS_DIR: str = "cursor_tasks"
    LOGS_DIR: str = "logs"
    DATA_DIR: str = "data"
    USE_MOCK_DATA: bool = os.getenv("USE_MOCK_DATA", "true").lower() == "true"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration - no external API keys required"""
        # All local configuration - always valid
        return True
