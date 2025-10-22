"""
Configuration management for Perplexity-Alpaca Trading Integration
Handles API keys, trading parameters, and system settings
"""

import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class PerplexityConfig:
    """Perplexity API configuration"""
    api_key: str
    base_url: str = "https://api.perplexity.ai/chat/completions"
    default_model: str = "sonar-pro"
    deep_research_model: str = "sonar-deep-research"
    max_retries: int = 3
    timeout: int = 60


@dataclass
class AlpacaConfig:
    """Alpaca API configuration"""
    api_key: str
    secret_key: str
    paper_trading: bool = True
    base_url: Optional[str] = None
    data_url: Optional[str] = None
    
    def __post_init__(self):
        if self.base_url is None:
            self.base_url = (
                "https://paper-api.alpaca.markets" 
                if self.paper_trading 
                else "https://api.alpaca.markets"
            )
        if self.data_url is None:
            self.data_url = "https://data.alpaca.markets"


@dataclass
class TradingConfig:
    """Trading strategy configuration"""
    max_position_size: float = 0.1  # 10% of portfolio per position
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.05  # 5% take profit
    max_daily_trades: int = 10
    risk_per_trade: float = 0.01  # 1% risk per trade
    use_bracket_orders: bool = True
    enable_short_selling: bool = False


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.perplexity = PerplexityConfig(
            api_key=self._get_env("PERPLEXITY_API_KEY")
        )
        
        self.alpaca = AlpacaConfig(
            api_key=self._get_env("ALPACA_API_KEY"),
            secret_key=self._get_env("ALPACA_SECRET_KEY"),
            paper_trading=self._get_env("ALPACA_PAPER_TRADING", "true").lower() == "true"
        )
        
        self.trading = TradingConfig(
            max_position_size=float(self._get_env("MAX_POSITION_SIZE", "0.1")),
            stop_loss_pct=float(self._get_env("STOP_LOSS_PCT", "0.02")),
            take_profit_pct=float(self._get_env("TAKE_PROFIT_PCT", "0.05")),
            max_daily_trades=int(self._get_env("MAX_DAILY_TRADES", "10")),
            risk_per_trade=float(self._get_env("RISK_PER_TRADE", "0.01"))
        )
        
        # Logging configuration
        self.log_level = self._get_env("LOG_LEVEL", "INFO")
        self.log_file = self._get_env("LOG_FILE", "logs/trading.log")
        
        # Cursor tasks directory
        self.cursor_tasks_dir = self._get_env("CURSOR_TASKS_DIR", "cursor_tasks")
    
    @staticmethod
    def _get_env(key: str, default: str = None) -> str:
        """Get environment variable with optional default"""
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable {key} is required but not set")
        return value
    
    def validate(self) -> bool:
        """Validate configuration"""
        try:
            assert self.perplexity.api_key, "Perplexity API key required"
            assert self.alpaca.api_key, "Alpaca API key required"
            assert self.alpaca.secret_key, "Alpaca secret key required"
            assert 0 < self.trading.max_position_size <= 1, "Invalid max position size"
            assert 0 < self.trading.risk_per_trade <= 0.1, "Risk per trade too high"
            return True
        except AssertionError as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global config instance
config = Config()
