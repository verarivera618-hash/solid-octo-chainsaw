"""
Local configuration management - No external API dependencies
This configuration allows the system to work completely offline
"""
import os
from typing import Optional

class LocalConfig:
    """Configuration class for local-only operation"""
    
    # Local Data Configuration
    USE_LOCAL_DATA: bool = True
    LOCAL_DATA_SOURCE: str = "csv"  # csv, json, sqlite
    DATA_PATH: str = os.path.join(os.getcwd(), "local_data")
    
    # Trading Configuration (for simulation)
    DEFAULT_STRATEGY: str = "momentum"
    PAPER_TRADING: bool = True  # Always true for local mode
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    RISK_TOLERANCE: float = 0.02  # 2% stop loss
    
    # Local Database Configuration
    DB_PATH: str = os.path.join(os.getcwd(), "local_trading.db")
    
    # Directory Configuration
    CURSOR_TASKS_DIR: str = "cursor_tasks"
    LOGS_DIR: str = "logs"
    DATA_DIR: str = "data"
    CACHE_DIR: str = "cache"
    
    # Local API Endpoints (for internal use only)
    LOCAL_API_HOST: str = "localhost"
    LOCAL_API_PORT: int = 8080
    LOCAL_API_BASE_URL: str = f"http://{LOCAL_API_HOST}:{LOCAL_API_PORT}/api"
    
    # Simulation Settings
    INITIAL_CAPITAL: float = 100000.0  # Starting capital for simulation
    COMMISSION_RATE: float = 0.001  # 0.1% commission per trade
    SLIPPAGE_RATE: float = 0.0005  # 0.05% slippage
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist"""
        dirs = [cls.DATA_PATH, cls.LOGS_DIR, cls.DATA_DIR, cls.CACHE_DIR, cls.CURSOR_TASKS_DIR]
        for directory in dirs:
            os.makedirs(directory, exist_ok=True)
    
    @classmethod
    def get_local_endpoints(cls) -> dict:
        """Get local API endpoints for internal communication"""
        return {
            "data": f"{cls.LOCAL_API_BASE_URL}/data",
            "trading": f"{cls.LOCAL_API_BASE_URL}/trading",
            "analysis": f"{cls.LOCAL_API_BASE_URL}/analysis",
            "backtest": f"{cls.LOCAL_API_BASE_URL}/backtest",
            "portfolio": f"{cls.LOCAL_API_BASE_URL}/portfolio"
        }