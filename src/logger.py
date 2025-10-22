"""
Logging utilities for the trading system
Provides structured logging with file and console handlers
"""

import os
import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname:8}"
                f"{self.RESET}"
            )
        else:
            record.levelname = f"{record.levelname:8}"
        
        return super().format(record)


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    use_colors: bool = True
) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (optional)
        console_output: Enable console output
        use_colors: Use colored output for console
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        if use_colors and sys.stdout.isatty():
            console_format = ColoredFormatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%H:%M:%S'
            )
        else:
            console_format = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%H:%M:%S'
            )
        
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Create log directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger


def get_trade_logger() -> logging.Logger:
    """Get logger specifically for trade logging"""
    log_file = f"logs/trades_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logger(
        name="trade",
        log_level="INFO",
        log_file=log_file,
        console_output=True,
        use_colors=True
    )


def log_trade_decision(
    logger: logging.Logger,
    symbol: str,
    action: str,
    reason: str,
    price: float,
    quantity: int,
    metadata: Optional[dict] = None
):
    """
    Log a trade decision with structured format
    
    Args:
        logger: Logger instance
        symbol: Stock symbol
        action: Trade action (BUY/SELL/HOLD)
        reason: Reasoning for the decision
        price: Price at decision time
        quantity: Number of shares
        metadata: Additional metadata dict
    """
    log_msg = (
        f"\n{'='*80}\n"
        f"TRADE DECISION\n"
        f"{'='*80}\n"
        f"Symbol:   {symbol}\n"
        f"Action:   {action}\n"
        f"Price:    ${price:.2f}\n"
        f"Quantity: {quantity}\n"
        f"Value:    ${price * quantity:,.2f}\n"
        f"Reason:   {reason}\n"
    )
    
    if metadata:
        log_msg += "Metadata:\n"
        for key, value in metadata.items():
            log_msg += f"  {key}: {value}\n"
    
    log_msg += f"{'='*80}\n"
    
    if action == 'BUY':
        logger.info(log_msg)
    elif action == 'SELL':
        logger.warning(log_msg)
    else:
        logger.debug(log_msg)


def log_order_execution(
    logger: logging.Logger,
    order_id: str,
    symbol: str,
    side: str,
    quantity: int,
    filled_price: Optional[float] = None,
    status: str = "submitted"
):
    """
    Log order execution details
    
    Args:
        logger: Logger instance
        order_id: Order ID from broker
        symbol: Stock symbol
        side: Order side (buy/sell)
        quantity: Number of shares
        filled_price: Fill price (if filled)
        status: Order status
    """
    log_msg = (
        f"ORDER {status.upper()}: {side.upper()} {quantity} {symbol} "
        f"(Order ID: {order_id})"
    )
    
    if filled_price:
        log_msg += f" @ ${filled_price:.2f}"
    
    if status == "filled":
        logger.info(log_msg)
    elif status in ["rejected", "cancelled", "failed"]:
        logger.error(log_msg)
    else:
        logger.debug(log_msg)


# Example usage
if __name__ == "__main__":
    # Setup logger
    logger = setup_logger(
        "test",
        log_level="DEBUG",
        log_file="logs/test.log",
        use_colors=True
    )
    
    # Test logging levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test trade logging
    log_trade_decision(
        logger,
        symbol="AAPL",
        action="BUY",
        reason="Momentum strategy signal",
        price=150.25,
        quantity=100,
        metadata={
            "strategy": "momentum",
            "signal_strength": 0.85,
            "stop_loss": 147.25,
            "take_profit": 157.76
        }
    )
    
    log_order_execution(
        logger,
        order_id="12345",
        symbol="AAPL",
        side="buy",
        quantity=100,
        filled_price=150.30,
        status="filled"
    )
