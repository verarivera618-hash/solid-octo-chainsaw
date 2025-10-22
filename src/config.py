"""
Configuration management for Local Trading System
No external API dependencies - fully local operation
"""
import os
from typing import Optional

class Config:
    """Configuration class for local trading system settings"""
    
    # Local System Configuration
    SYSTEM_MODE: str = "local"  # Always local, no external APIs
    
    # Trading Configuration
    DEFAULT_STRATEGY: str = os.getenv("DEFAULT_STRATEGY", "momentum")
    PAPER_TRADING: bool = True  # Always paper trading in local mode
    MAX_POSITION_SIZE: float = float(os.getenv("MAX_POSITION_SIZE", "0.1"))
    RISK_TOLERANCE: float = float(os.getenv("RISK_TOLERANCE", "0.02"))
    INITIAL_CASH: float = float(os.getenv("INITIAL_CASH", "100000.0"))
    
    # Data Configuration
    CURSOR_TASKS_DIR: str = "cursor_tasks"
    LOGS_DIR: str = "logs"
    DATA_DIR: str = "data"
    
    # Local Data Settings
    DATA_DAYS: int = int(os.getenv("DATA_DAYS", "30"))
    ENABLE_SIMULATION: bool = True
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration (always valid for local mode)"""
        print("✅ Local mode configuration validated - no external dependencies required")
        return True
    
    @classmethod
    def get_system_info(cls) -> dict:
        """Get system information"""
        return {
            "mode": cls.SYSTEM_MODE,
            "paper_trading": cls.PAPER_TRADING,
            "initial_cash": cls.INITIAL_CASH,
            "max_position_size": cls.MAX_POSITION_SIZE,
            "risk_tolerance": cls.RISK_TOLERANCE,
            "data_days": cls.DATA_DAYS
        }
