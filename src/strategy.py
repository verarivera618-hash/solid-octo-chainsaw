"""
Trading Strategy Framework
Base classes and example implementations for various trading strategies
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Literal
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import logging

from src.config import config

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Trading signal"""
    symbol: str
    action: Literal['BUY', 'SELL', 'HOLD']
    strength: float  # 0.0 to 1.0
    timestamp: datetime
    reason: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[int] = None


@dataclass
class Position:
    """Current position information"""
    symbol: str
    quantity: int
    entry_price: float
    current_price: float
    side: Literal['long', 'short']
    unrealized_pnl: float
    unrealized_pnl_pct: float
    entry_time: datetime


class TradingStrategy(ABC):
    """Base class for trading strategies"""
    
    def __init__(self, name: str):
        self.name = name
        self.config = config.trading
        self.positions: Dict[str, Position] = {}
        self.signals_history: list = []
    
    @abstractmethod
    def analyze(self, symbol: str, data: pd.DataFrame) -> Signal:
        """
        Analyze market data and generate trading signal
        
        Args:
            symbol: Stock symbol
            data: DataFrame with OHLCV and indicators
        
        Returns:
            Signal object
        """
        pass
    
    def calculate_position_size(
        self, 
        account_value: float,
        entry_price: float,
        stop_loss_price: float,
        signal_strength: float = 1.0
    ) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            account_value: Total account value
            entry_price: Intended entry price
            stop_loss_price: Stop loss price
            signal_strength: Signal confidence (0.0 to 1.0)
        
        Returns:
            Number of shares to trade
        """
        # Maximum position value based on portfolio percentage
        max_position_value = account_value * self.config.max_position_size
        
        # Risk-based position sizing
        risk_amount = account_value * self.config.risk_per_trade
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            shares_by_risk = int(max_position_value / entry_price)
        else:
            shares_by_risk = int(risk_amount / price_risk)
        
        # Maximum shares by position size limit
        shares_by_limit = int(max_position_value / entry_price)
        
        # Take minimum to respect both constraints
        shares = min(shares_by_risk, shares_by_limit)
        
        # Adjust by signal strength
        shares = int(shares * signal_strength)
        
        # Ensure at least 1 share if signal is strong enough
        if shares == 0 and signal_strength > 0.5:
            shares = 1
        
        logger.debug(f"Position size calculated: {shares} shares @ ${entry_price}")
        return shares
    
    def calculate_stop_loss(
        self, 
        entry_price: float, 
        side: Literal['long', 'short']
    ) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            side: Position side (long/short)
        
        Returns:
            Stop loss price
        """
        if side == 'long':
            stop_loss = entry_price * (1 - self.config.stop_loss_pct)
        else:
            stop_loss = entry_price * (1 + self.config.stop_loss_pct)
        
        return round(stop_loss, 2)
    
    def calculate_take_profit(
        self, 
        entry_price: float, 
        side: Literal['long', 'short']
    ) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            side: Position side (long/short)
        
        Returns:
            Take profit price
        """
        if side == 'long':
            take_profit = entry_price * (1 + self.config.take_profit_pct)
        else:
            take_profit = entry_price * (1 - self.config.take_profit_pct)
        
        return round(take_profit, 2)
    
    def should_exit_position(
        self, 
        symbol: str, 
        current_data: pd.DataFrame
    ) -> tuple[bool, str]:
        """
        Determine if position should be exited
        
        Args:
            symbol: Stock symbol
            current_data: Current market data with indicators
        
        Returns:
            Tuple of (should_exit, reason)
        """
        if symbol not in self.positions:
            return False, "No position"
        
        position = self.positions[symbol]
        current_price = current_data['close'].iloc[-1]
        
        # Check stop loss
        if position.side == 'long' and current_price <= position.entry_price * (1 - self.config.stop_loss_pct):
            return True, "Stop loss triggered"
        elif position.side == 'short' and current_price >= position.entry_price * (1 + self.config.stop_loss_pct):
            return True, "Stop loss triggered"
        
        # Check take profit
        if position.side == 'long' and current_price >= position.entry_price * (1 + self.config.take_profit_pct):
            return True, "Take profit triggered"
        elif position.side == 'short' and current_price <= position.entry_price * (1 - self.config.take_profit_pct):
            return True, "Take profit triggered"
        
        # Strategy-specific exit logic
        signal = self.analyze(symbol, current_data)
        if signal.action == 'SELL' and position.side == 'long':
            return True, f"Strategy exit signal: {signal.reason}"
        elif signal.action == 'BUY' and position.side == 'short':
            return True, f"Strategy exit signal: {signal.reason}"
        
        return False, "Hold position"
    
    def update_position(self, symbol: str, current_price: float):
        """Update position with current price"""
        if symbol in self.positions:
            position = self.positions[symbol]
            position.current_price = current_price
            
            if position.side == 'long':
                position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
            else:
                position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
            
            position.unrealized_pnl_pct = (position.unrealized_pnl / (position.entry_price * position.quantity)) * 100


class MomentumStrategy(TradingStrategy):
    """
    Momentum trading strategy
    Enters on strong upward momentum with confirmation
    """
    
    def __init__(self):
        super().__init__("Momentum Strategy")
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Analyze momentum signals"""
        if len(data) < 50:
            return Signal(
                symbol=symbol,
                action='HOLD',
                strength=0.0,
                timestamp=datetime.now(),
                reason="Insufficient data"
            )
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # Default to HOLD
        action = 'HOLD'
        strength = 0.0
        reason = "No clear signal"
        
        # Check if required indicators exist
        required_cols = ['SMA_20', 'SMA_50', 'RSI', 'MACD', 'MACD_Signal']
        if not all(col in data.columns for col in required_cols):
            return Signal(
                symbol=symbol,
                action='HOLD',
                strength=0.0,
                timestamp=datetime.now(),
                reason="Missing indicators"
            )
        
        # Bullish momentum criteria
        price_above_sma20 = latest['close'] > latest['SMA_20']
        price_above_sma50 = latest['close'] > latest['SMA_50']
        sma20_above_sma50 = latest['SMA_20'] > latest['SMA_50']
        rsi_bullish = 50 < latest['RSI'] < 70
        macd_crossover = prev['MACD'] <= prev['MACD_Signal'] and latest['MACD'] > latest['MACD_Signal']
        
        # Volume confirmation
        has_volume = 'Volume_Ratio' in data.columns
        volume_surge = latest['Volume_Ratio'] > 1.2 if has_volume else True
        
        # Entry signal
        if (price_above_sma20 and price_above_sma50 and 
            sma20_above_sma50 and rsi_bullish and volume_surge):
            
            action = 'BUY'
            # Calculate signal strength
            strength = 0.6  # Base strength
            if macd_crossover:
                strength += 0.2
            if volume_surge:
                strength += 0.2
            
            strength = min(strength, 1.0)
            reason = "Bullish momentum: Price above SMAs, RSI favorable, volume surge"
        
        # Exit signal (for existing long positions)
        elif latest['RSI'] > 70 or latest['close'] < latest['SMA_20']:
            action = 'SELL'
            strength = 0.7
            reason = "Exit signal: Overbought or price below SMA_20"
        
        # Calculate stop loss and take profit
        entry_price = latest['close']
        stop_loss = self.calculate_stop_loss(entry_price, 'long')
        take_profit = self.calculate_take_profit(entry_price, 'long')
        
        return Signal(
            symbol=symbol,
            action=action,
            strength=strength,
            timestamp=datetime.now(),
            reason=reason,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )


class MeanReversionStrategy(TradingStrategy):
    """
    Mean reversion strategy
    Enters when price deviates from mean and shows reversal signs
    """
    
    def __init__(self):
        super().__init__("Mean Reversion Strategy")
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Analyze mean reversion signals"""
        if len(data) < 20:
            return Signal(
                symbol=symbol,
                action='HOLD',
                strength=0.0,
                timestamp=datetime.now(),
                reason="Insufficient data"
            )
        
        latest = data.iloc[-1]
        
        action = 'HOLD'
        strength = 0.0
        reason = "No clear signal"
        
        # Check for Bollinger Bands
        if 'BB_Lower' not in data.columns or 'BB_Upper' not in data.columns:
            return Signal(
                symbol=symbol,
                action='HOLD',
                strength=0.0,
                timestamp=datetime.now(),
                reason="Missing Bollinger Bands"
            )
        
        # Oversold condition (buy signal)
        touching_lower_band = latest['close'] <= latest['BB_Lower'] * 1.01
        rsi_oversold = latest.get('RSI', 50) < 30
        
        if touching_lower_band and rsi_oversold:
            action = 'BUY'
            strength = 0.7
            if latest.get('RSI', 50) < 25:
                strength = 0.9
            reason = "Mean reversion buy: Price at lower BB, RSI oversold"
        
        # Overbought condition (sell signal)
        touching_upper_band = latest['close'] >= latest['BB_Upper'] * 0.99
        rsi_overbought = latest.get('RSI', 50) > 70
        
        if touching_upper_band and rsi_overbought:
            action = 'SELL'
            strength = 0.7
            if latest.get('RSI', 50) > 75:
                strength = 0.9
            reason = "Mean reversion sell: Price at upper BB, RSI overbought"
        
        entry_price = latest['close']
        stop_loss = self.calculate_stop_loss(entry_price, 'long')
        take_profit = self.calculate_take_profit(entry_price, 'long')
        
        return Signal(
            symbol=symbol,
            action=action,
            strength=strength,
            timestamp=datetime.now(),
            reason=reason,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )


class BreakoutStrategy(TradingStrategy):
    """
    Breakout trading strategy
    Enters on breakouts from consolidation with volume confirmation
    """
    
    def __init__(self, lookback_period: int = 20):
        super().__init__("Breakout Strategy")
        self.lookback_period = lookback_period
    
    def analyze(self, symbol: str, data: pd.DataFrame) -> Signal:
        """Analyze breakout signals"""
        if len(data) < self.lookback_period:
            return Signal(
                symbol=symbol,
                action='HOLD',
                strength=0.0,
                timestamp=datetime.now(),
                reason="Insufficient data"
            )
        
        latest = data.iloc[-1]
        lookback_data = data.iloc[-self.lookback_period:]
        
        # Calculate consolidation range
        range_high = lookback_data['high'].max()
        range_low = lookback_data['low'].min()
        range_size = (range_high - range_low) / range_low
        
        action = 'HOLD'
        strength = 0.0
        reason = "No clear signal"
        
        # Breakout above range
        if latest['close'] > range_high and range_size < 0.10:  # Tight range
            volume_confirm = latest.get('Volume_Ratio', 1.0) > 1.5
            
            if volume_confirm:
                action = 'BUY'
                strength = 0.8
                reason = f"Bullish breakout above {self.lookback_period}-day range with volume"
            else:
                strength = 0.5
                reason = f"Potential breakout above range (low volume)"
        
        # Breakdown below range
        elif latest['close'] < range_low and range_size < 0.10:
            action = 'SELL'
            strength = 0.7
            reason = f"Bearish breakdown below {self.lookback_period}-day range"
        
        entry_price = latest['close']
        stop_loss = self.calculate_stop_loss(entry_price, 'long')
        take_profit = self.calculate_take_profit(entry_price, 'long')
        
        return Signal(
            symbol=symbol,
            action=action,
            strength=strength,
            timestamp=datetime.now(),
            reason=reason,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )


# Strategy factory
def get_strategy(strategy_type: str) -> TradingStrategy:
    """Get strategy instance by type"""
    strategies = {
        'momentum': MomentumStrategy,
        'mean_reversion': MeanReversionStrategy,
        'breakout': BreakoutStrategy
    }
    
    strategy_class = strategies.get(strategy_type.lower())
    if strategy_class is None:
        raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    return strategy_class()
