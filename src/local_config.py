"""
Local configuration for fully offline trading system
No external API dependencies required
"""
import os
from typing import Optional

class LocalConfig:
    """Configuration class for local-only operation"""
    
    # Local Data Provider Configuration
    USE_LOCAL_DATA: bool = True
    LOCAL_DATA_CACHE_DIR: str = "data/local_cache"
    
    # Simulation Configuration
    SIMULATION_MODE: bool = True
    INITIAL_CAPITAL: float = 100000.0
    ENABLE_PAPER_TRADING: bool = True
    
    # Trading Configuration
    DEFAULT_STRATEGY: str = "local_momentum"
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio per position
    RISK_TOLERANCE: float = 0.02    # 2% stop loss
    
    # Data Configuration
    CURSOR_TASKS_DIR: str = "cursor_tasks"
    LOGS_DIR: str = "logs"
    DATA_DIR: str = "data"
    RESULTS_DIR: str = "results"
    
    # Mock API Configuration
    MOCK_LATENCY_MS: int = 100  # Simulate API latency
    ENABLE_MOCK_ERRORS: bool = False  # Simulate occasional API errors
    
    # Local Endpoints (for copy-paste compatibility)
    LOCAL_API_BASE: str = "http://localhost:8000"
    LOCAL_DATA_ENDPOINT: str = f"{LOCAL_API_BASE}/api/data"
    LOCAL_TRADING_ENDPOINT: str = f"{LOCAL_API_BASE}/api/trading"
    LOCAL_ANALYSIS_ENDPOINT: str = f"{LOCAL_API_BASE}/api/analysis"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate local configuration"""
        # Create necessary directories
        directories = [
            cls.CURSOR_TASKS_DIR,
            cls.LOGS_DIR, 
            cls.DATA_DIR,
            cls.RESULTS_DIR,
            cls.LOCAL_DATA_CACHE_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        return True
    
    @classmethod
    def get_local_headers(cls) -> dict:
        """Get headers for local API requests (for compatibility)"""
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "x-local-mode": "true"
        }
    
    @classmethod
    def get_supported_symbols(cls) -> list:
        """Get list of supported symbols for local simulation"""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'NOW', 'SNOW', 'PLTR',
            'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'TQQQ', 'SQQQ'
        ]
    
    @classmethod
    def get_local_strategies(cls) -> list:
        """Get list of available local strategies"""
        return [
            'local_momentum',
            'local_mean_reversion', 
            'local_breakout',
            'local_rsi_divergence',
            'local_moving_average_crossover',
            'local_bollinger_squeeze',
            'local_volume_breakout'
        ]