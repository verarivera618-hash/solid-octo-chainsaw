"""
Base classes for trading strategies.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
from loguru import logger

from alpaca_client import MarketData, Quote

class SignalType(Enum):
    """Types of trading signals."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"

@dataclass
class TradingSignal:
    """Structure for trading signals."""
    symbol: str
    signal_type: SignalType
    confidence: float  # 0.0 to 1.0
    price: float
    quantity: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    timestamp: datetime = None
    reason: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class StrategyParameters:
    """Base strategy parameters."""
    lookback_period: int = 20
    risk_per_trade: float = 0.02
    max_position_size: float = 0.1
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    
class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, parameters: StrategyParameters):
        self.parameters = parameters
        self.name = self.__class__.__name__
        self.positions: Dict[str, float] = {}  # symbol -> quantity
        self.price_history: Dict[str, List[MarketData]] = {}
        self.signals_history: List[TradingSignal] = []
        
        logger.info(f"Initialized {self.name} strategy")
    
    @abstractmethod
    def generate_signals(self, market_data: Dict[str, MarketData]) -> List[TradingSignal]:
        """
        Generate trading signals based on market data.
        
        Args:
            market_data: Dictionary mapping symbols to MarketData
        
        Returns:
            List of TradingSignal objects
        """
        pass
    
    @abstractmethod
    def update_indicators(self, market_data: Dict[str, MarketData]) -> None:
        """
        Update technical indicators with new market data.
        
        Args:
            market_data: Dictionary mapping symbols to MarketData
        """
        pass
    
    def add_market_data(self, symbol: str, data: MarketData) -> None:
        """
        Add market data to price history.
        
        Args:
            symbol: Stock symbol
            data: MarketData object
        """
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(data)
        
        # Keep only the required lookback period + some buffer
        max_history = self.parameters.lookback_period * 2
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol] = self.price_history[symbol][-max_history:]
    
    def get_price_dataframe(self, symbol: str) -> pd.DataFrame:
        """
        Get price history as pandas DataFrame.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            DataFrame with OHLCV data
        """
        if symbol not in self.price_history or not self.price_history[symbol]:
            return pd.DataFrame()
        
        data = []
        for market_data in self.price_history[symbol]:
            data.append({
                'timestamp': market_data.timestamp,
                'open': market_data.open,
                'high': market_data.high,
                'low': market_data.low,
                'close': market_data.close,
                'volume': market_data.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df
    
    def calculate_position_size(self, symbol: str, price: float, signal_confidence: float = 1.0) -> float:
        """
        Calculate position size based on risk management rules.
        
        Args:
            symbol: Stock symbol
            price: Current price
            signal_confidence: Confidence in the signal (0.0 to 1.0)
        
        Returns:
            Position size (number of shares)
        """
        # Base position size as percentage of portfolio
        base_size = self.parameters.max_position_size * signal_confidence
        
        # Calculate dollar amount
        # This would need portfolio value from account info
        portfolio_value = 100000  # Placeholder - should come from account
        dollar_amount = portfolio_value * base_size
        
        # Convert to shares
        shares = int(dollar_amount / price)
        
        return max(1, shares)  # Minimum 1 share
    
    def calculate_stop_loss(self, entry_price: float, signal_type: SignalType) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            signal_type: Type of signal (BUY/SELL)
        
        Returns:
            Stop loss price
        """
        if signal_type == SignalType.BUY:
            return entry_price * (1 - self.parameters.stop_loss_pct)
        elif signal_type == SignalType.SELL:
            return entry_price * (1 + self.parameters.stop_loss_pct)
        else:
            return entry_price
    
    def calculate_take_profit(self, entry_price: float, signal_type: SignalType) -> float:
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price
            signal_type: Type of signal (BUY/SELL)
        
        Returns:
            Take profit price
        """
        if signal_type == SignalType.BUY:
            return entry_price * (1 + self.parameters.take_profit_pct)
        elif signal_type == SignalType.SELL:
            return entry_price * (1 - self.parameters.take_profit_pct)
        else:
            return entry_price
    
    def update_position(self, symbol: str, quantity_change: float) -> None:
        """
        Update position tracking.
        
        Args:
            symbol: Stock symbol
            quantity_change: Change in position (positive for buy, negative for sell)
        """
        if symbol not in self.positions:
            self.positions[symbol] = 0
        
        self.positions[symbol] += quantity_change
        
        # Remove position if it's zero
        if abs(self.positions[symbol]) < 0.001:
            del self.positions[symbol]
    
    def get_current_position(self, symbol: str) -> float:
        """
        Get current position for symbol.
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Current position size
        """
        return self.positions.get(symbol, 0)
    
    def is_long(self, symbol: str) -> bool:
        """Check if we have a long position."""
        return self.get_current_position(symbol) > 0
    
    def is_short(self, symbol: str) -> bool:
        """Check if we have a short position."""
        return self.get_current_position(symbol) < 0
    
    def is_flat(self, symbol: str) -> bool:
        """Check if we have no position."""
        return abs(self.get_current_position(symbol)) < 0.001
    
    def add_signal(self, signal: TradingSignal) -> None:
        """
        Add signal to history.
        
        Args:
            signal: TradingSignal object
        """
        self.signals_history.append(signal)
        logger.info(f"Generated signal: {signal.signal_type.value} {signal.symbol} @ ${signal.price:.2f} (confidence: {signal.confidence:.2f})")
    
    def get_recent_signals(self, symbol: str, count: int = 10) -> List[TradingSignal]:
        """
        Get recent signals for a symbol.
        
        Args:
            symbol: Stock symbol
            count: Number of recent signals to return
        
        Returns:
            List of recent TradingSignal objects
        """
        symbol_signals = [s for s in self.signals_history if s.symbol == symbol]
        return symbol_signals[-count:]
    
    def validate_signal(self, signal: TradingSignal) -> bool:
        """
        Validate a trading signal before execution.
        
        Args:
            signal: TradingSignal to validate
        
        Returns:
            True if signal is valid
        """
        # Basic validation
        if signal.confidence < 0.5:
            logger.warning(f"Low confidence signal rejected: {signal.confidence}")
            return False
        
        if signal.price <= 0:
            logger.error(f"Invalid price in signal: {signal.price}")
            return False
        
        # Position size validation
        current_position = self.get_current_position(signal.symbol)
        
        if signal.signal_type == SignalType.BUY and current_position > 0:
            logger.warning(f"Already long {signal.symbol}, skipping BUY signal")
            return False
        
        if signal.signal_type == SignalType.SELL and current_position < 0:
            logger.warning(f"Already short {signal.symbol}, skipping SELL signal")
            return False
        
        return True
    
    def get_strategy_state(self) -> Dict[str, Any]:
        """
        Get current strategy state for monitoring.
        
        Returns:
            Dictionary with strategy state information
        """
        return {
            'name': self.name,
            'parameters': self.parameters.__dict__,
            'positions': self.positions.copy(),
            'total_signals': len(self.signals_history),
            'recent_signals': len([s for s in self.signals_history if (datetime.now() - s.timestamp).seconds < 3600])
        }

class RiskManager:
    """Risk management for trading strategies."""
    
    def __init__(self, max_daily_loss: float = 0.05, max_position_size: float = 0.1):
        self.max_daily_loss = max_daily_loss
        self.max_position_size = max_position_size
        self.daily_pnl = 0.0
        self.start_of_day_value = 0.0
        
    def check_daily_loss_limit(self, current_portfolio_value: float) -> bool:
        """
        Check if daily loss limit has been exceeded.
        
        Args:
            current_portfolio_value: Current portfolio value
        
        Returns:
            True if trading should continue, False if daily limit exceeded
        """
        if self.start_of_day_value == 0:
            self.start_of_day_value = current_portfolio_value
            return True
        
        daily_loss = (self.start_of_day_value - current_portfolio_value) / self.start_of_day_value
        
        if daily_loss > self.max_daily_loss:
            logger.error(f"Daily loss limit exceeded: {daily_loss:.2%} > {self.max_daily_loss:.2%}")
            return False
        
        return True
    
    def check_position_size_limit(self, position_value: float, portfolio_value: float) -> bool:
        """
        Check if position size limit has been exceeded.
        
        Args:
            position_value: Value of the position
            portfolio_value: Total portfolio value
        
        Returns:
            True if position size is acceptable
        """
        position_pct = abs(position_value) / portfolio_value
        
        if position_pct > self.max_position_size:
            logger.warning(f"Position size limit exceeded: {position_pct:.2%} > {self.max_position_size:.2%}")
            return False
        
        return True
    
    def reset_daily_tracking(self, portfolio_value: float) -> None:
        """
        Reset daily tracking (call at start of each trading day).
        
        Args:
            portfolio_value: Starting portfolio value for the day
        """
        self.start_of_day_value = portfolio_value
        self.daily_pnl = 0.0
        logger.info(f"Reset daily tracking with portfolio value: ${portfolio_value:,.2f}")

# Example implementation
class SimpleMovingAverageStrategy(BaseStrategy):
    """Simple moving average crossover strategy."""
    
    def __init__(self, parameters: StrategyParameters, short_ma: int = 10, long_ma: int = 20):
        super().__init__(parameters)
        self.short_ma = short_ma
        self.long_ma = long_ma
        self.indicators: Dict[str, Dict] = {}
    
    def update_indicators(self, market_data: Dict[str, MarketData]) -> None:
        """Update moving averages for all symbols."""
        for symbol, data in market_data.items():
            self.add_market_data(symbol, data)
            
            if symbol not in self.indicators:
                self.indicators[symbol] = {'short_ma': None, 'long_ma': None}
            
            df = self.get_price_dataframe(symbol)
            
            if len(df) >= self.long_ma:
                self.indicators[symbol]['short_ma'] = df['close'].rolling(self.short_ma).mean().iloc[-1]
                self.indicators[symbol]['long_ma'] = df['close'].rolling(self.long_ma).mean().iloc[-1]
    
    def generate_signals(self, market_data: Dict[str, MarketData]) -> List[TradingSignal]:
        """Generate signals based on moving average crossover."""
        self.update_indicators(market_data)
        signals = []
        
        for symbol, data in market_data.items():
            if symbol not in self.indicators:
                continue
            
            indicators = self.indicators[symbol]
            if indicators['short_ma'] is None or indicators['long_ma'] is None:
                continue
            
            current_price = data.close
            short_ma = indicators['short_ma']
            long_ma = indicators['long_ma']
            
            # Generate signals based on crossover
            if short_ma > long_ma and self.is_flat(symbol):
                # Bullish crossover - generate BUY signal
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    confidence=0.7,
                    price=current_price,
                    quantity=self.calculate_position_size(symbol, current_price),
                    stop_loss=self.calculate_stop_loss(current_price, SignalType.BUY),
                    take_profit=self.calculate_take_profit(current_price, SignalType.BUY),
                    reason=f"Short MA ({short_ma:.2f}) > Long MA ({long_ma:.2f})"
                )
                
                if self.validate_signal(signal):
                    signals.append(signal)
                    self.add_signal(signal)
            
            elif short_ma < long_ma and self.is_long(symbol):
                # Bearish crossover - close long position
                signal = TradingSignal(
                    symbol=symbol,
                    signal_type=SignalType.CLOSE_LONG,
                    confidence=0.8,
                    price=current_price,
                    quantity=abs(self.get_current_position(symbol)),
                    reason=f"Short MA ({short_ma:.2f}) < Long MA ({long_ma:.2f})"
                )
                
                if self.validate_signal(signal):
                    signals.append(signal)
                    self.add_signal(signal)
        
        return signals

if __name__ == "__main__":
    # Example usage
    params = StrategyParameters(
        lookback_period=50,
        risk_per_trade=0.02,
        max_position_size=0.1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04
    )
    
    strategy = SimpleMovingAverageStrategy(params, short_ma=10, long_ma=20)
    
    # Simulate some market data
    test_data = {
        'AAPL': MarketData(
            symbol='AAPL',
            timestamp=datetime.now(),
            open=150.0,
            high=152.0,
            low=149.0,
            close=151.0,
            volume=1000000
        )
    }
    
    signals = strategy.generate_signals(test_data)
    print(f"Generated {len(signals)} signals")
    
    for signal in signals:
        print(f"{signal.signal_type.value} {signal.symbol} @ ${signal.price:.2f}")