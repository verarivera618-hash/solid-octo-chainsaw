"""
Trading strategy implementation with multiple strategy types
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger
from enum import Enum
from dataclasses import dataclass


class Signal(Enum):
    """Trading signals"""
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2


@dataclass
class TradingSignal:
    """Trading signal with metadata"""
    symbol: str
    signal: Signal
    confidence: float  # 0-1
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reasons: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]


class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.positions = {}
        self.performance = {
            "total_signals": 0,
            "successful_signals": 0,
            "failed_signals": 0,
            "win_rate": 0.0,
            "total_return": 0.0
        }
    
    @abstractmethod
    def analyze(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Optional[TradingSignal]:
        """Analyze market data and generate trading signal"""
        pass
    
    @abstractmethod
    def should_exit(
        self,
        symbol: str,
        current_price: float,
        position: Dict[str, Any]
    ) -> bool:
        """Check if position should be closed"""
        pass
    
    def calculate_position_size(
        self,
        capital: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss: float
    ) -> float:
        """Calculate position size based on risk management"""
        
        if stop_loss >= entry_price:
            return 0.0
        
        risk_amount = capital * risk_per_trade
        price_risk = entry_price - stop_loss
        shares = risk_amount / price_risk
        
        # Apply maximum position size constraint
        max_position_value = capital * self.config.get("max_position_size", 0.1)
        max_shares = max_position_value / entry_price
        
        return min(shares, max_shares)
    
    def update_performance(self, signal: TradingSignal, outcome: str):
        """Update strategy performance metrics"""
        self.performance["total_signals"] += 1
        
        if outcome == "success":
            self.performance["successful_signals"] += 1
        else:
            self.performance["failed_signals"] += 1
        
        if self.performance["total_signals"] > 0:
            self.performance["win_rate"] = (
                self.performance["successful_signals"] /
                self.performance["total_signals"]
            )


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Momentum", config)
        self.rsi_threshold_buy = config.get("rsi_threshold_buy", 60)
        self.rsi_threshold_sell = config.get("rsi_threshold_sell", 40)
        self.volume_multiplier = config.get("volume_multiplier", 1.5)
        self.lookback_period = config.get("lookback_period", 20)
    
    def analyze(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Optional[TradingSignal]:
        """Generate momentum-based trading signal"""
        
        if len(market_data) < self.lookback_period:
            return None
        
        # Calculate indicators
        current_price = market_data['close'].iloc[-1]
        rsi = market_data['RSI'].iloc[-1] if 'RSI' in market_data else None
        macd = market_data['MACD'].iloc[-1] if 'MACD' in market_data else None
        macd_signal = market_data['MACD_signal'].iloc[-1] if 'MACD_signal' in market_data else None
        volume = market_data['volume'].iloc[-1]
        avg_volume = market_data['volume'].rolling(20).mean().iloc[-1]
        
        # Price momentum
        price_20d_high = market_data['high'].rolling(self.lookback_period).max().iloc[-1]
        price_20d_low = market_data['low'].rolling(self.lookback_period).min().iloc[-1]
        
        reasons = []
        confidence = 0.5
        signal = Signal.HOLD
        
        # Bullish signals
        if current_price >= price_20d_high * 0.99:  # Near 20-day high
            reasons.append("Price near 20-day high")
            confidence += 0.1
            
        if rsi and rsi > self.rsi_threshold_buy and rsi < 80:
            reasons.append(f"RSI bullish: {rsi:.2f}")
            confidence += 0.15
            
        if macd and macd_signal and macd > macd_signal:
            reasons.append("MACD bullish crossover")
            confidence += 0.15
            
        if volume > avg_volume * self.volume_multiplier:
            reasons.append("High volume breakout")
            confidence += 0.1
        
        # Bearish signals
        if current_price <= price_20d_low * 1.01:  # Near 20-day low
            reasons.append("Price near 20-day low")
            confidence -= 0.1
            
        if rsi and rsi < self.rsi_threshold_sell:
            reasons.append(f"RSI bearish: {rsi:.2f}")
            confidence -= 0.15
            
        if macd and macd_signal and macd < macd_signal:
            reasons.append("MACD bearish crossover")
            confidence -= 0.15
        
        # Add sentiment if available
        if sentiment_data and "sentiment_score" in sentiment_data:
            sentiment_score = sentiment_data["sentiment_score"]
            if sentiment_score > 0.6:
                reasons.append(f"Positive sentiment: {sentiment_score:.2f}")
                confidence += 0.1
            elif sentiment_score < 0.4:
                reasons.append(f"Negative sentiment: {sentiment_score:.2f}")
                confidence -= 0.1
        
        # Determine signal
        if confidence >= 0.7:
            signal = Signal.STRONG_BUY
        elif confidence >= 0.6:
            signal = Signal.BUY
        elif confidence <= 0.3:
            signal = Signal.STRONG_SELL
        elif confidence <= 0.4:
            signal = Signal.SELL
        
        if signal == Signal.HOLD:
            return None
        
        # Calculate stop loss and take profit
        atr = market_data['ATR'].iloc[-1] if 'ATR' in market_data else current_price * 0.02
        
        if signal in [Signal.BUY, Signal.STRONG_BUY]:
            stop_loss = current_price - (2 * atr)
            take_profit = current_price + (3 * atr)
        else:
            stop_loss = current_price + (2 * atr)
            take_profit = current_price - (3 * atr)
        
        # Calculate position size
        position_size = self.calculate_position_size(
            capital=100000,  # This should come from portfolio
            risk_per_trade=0.02,
            entry_price=current_price,
            stop_loss=stop_loss
        )
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=abs(confidence),
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            reasons=reasons,
            timestamp=datetime.now(),
            metadata={
                "rsi": rsi,
                "macd": macd,
                "volume_ratio": volume / avg_volume if avg_volume > 0 else 1
            }
        )
    
    def should_exit(
        self,
        symbol: str,
        current_price: float,
        position: Dict[str, Any]
    ) -> bool:
        """Check if position should be closed"""
        
        # Check stop loss
        if current_price <= position["stop_loss"]:
            logger.info(f"Stop loss triggered for {symbol}")
            return True
        
        # Check take profit
        if current_price >= position["take_profit"]:
            logger.info(f"Take profit triggered for {symbol}")
            return True
        
        # Check trailing stop if implemented
        if "trailing_stop" in position:
            if current_price <= position["trailing_stop"]:
                logger.info(f"Trailing stop triggered for {symbol}")
                return True
        
        return False


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("MeanReversion", config)
        self.bb_periods = config.get("bb_periods", 20)
        self.bb_std = config.get("bb_std", 2)
        self.rsi_oversold = config.get("rsi_oversold", 30)
        self.rsi_overbought = config.get("rsi_overbought", 70)
    
    def analyze(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Optional[TradingSignal]:
        """Generate mean reversion trading signal"""
        
        if len(market_data) < self.bb_periods:
            return None
        
        current_price = market_data['close'].iloc[-1]
        bb_upper = market_data['BB_upper'].iloc[-1] if 'BB_upper' in market_data else None
        bb_lower = market_data['BB_lower'].iloc[-1] if 'BB_lower' in market_data else None
        bb_middle = market_data['BB_middle'].iloc[-1] if 'BB_middle' in market_data else None
        rsi = market_data['RSI'].iloc[-1] if 'RSI' in market_data else None
        
        reasons = []
        confidence = 0.5
        signal = Signal.HOLD
        
        # Check for oversold conditions (buy signal)
        if bb_lower and current_price <= bb_lower:
            reasons.append("Price at lower Bollinger Band")
            confidence += 0.2
            
            if rsi and rsi < self.rsi_oversold:
                reasons.append(f"RSI oversold: {rsi:.2f}")
                confidence += 0.2
                signal = Signal.BUY
        
        # Check for overbought conditions (sell signal)
        elif bb_upper and current_price >= bb_upper:
            reasons.append("Price at upper Bollinger Band")
            confidence -= 0.2
            
            if rsi and rsi > self.rsi_overbought:
                reasons.append(f"RSI overbought: {rsi:.2f}")
                confidence -= 0.2
                signal = Signal.SELL
        
        # Z-score analysis
        if bb_middle and bb_upper and bb_lower:
            z_score = (current_price - bb_middle) / ((bb_upper - bb_lower) / 4)
            
            if z_score < -2:
                reasons.append(f"Z-score oversold: {z_score:.2f}")
                confidence += 0.15
                if signal != Signal.SELL:
                    signal = Signal.BUY
            elif z_score > 2:
                reasons.append(f"Z-score overbought: {z_score:.2f}")
                confidence -= 0.15
                if signal != Signal.BUY:
                    signal = Signal.SELL
        
        if signal == Signal.HOLD:
            return None
        
        # Set stop loss and take profit
        if signal == Signal.BUY:
            stop_loss = current_price * 0.97  # 3% stop loss
            take_profit = bb_middle if bb_middle else current_price * 1.02
        else:
            stop_loss = current_price * 1.03
            take_profit = bb_middle if bb_middle else current_price * 0.98
        
        position_size = self.calculate_position_size(
            capital=100000,
            risk_per_trade=0.02,
            entry_price=current_price,
            stop_loss=stop_loss
        )
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=abs(confidence),
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            reasons=reasons,
            timestamp=datetime.now(),
            metadata={
                "rsi": rsi,
                "bb_position": (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
            }
        )
    
    def should_exit(
        self,
        symbol: str,
        current_price: float,
        position: Dict[str, Any]
    ) -> bool:
        """Check if position should be closed"""
        
        # Standard stop loss and take profit
        if current_price <= position["stop_loss"] or current_price >= position["take_profit"]:
            return True
        
        # Mean reversion specific: close when price returns to mean
        if "target_price" in position:
            if position["side"] == "long" and current_price >= position["target_price"]:
                return True
            elif position["side"] == "short" and current_price <= position["target_price"]:
                return True
        
        return False


class SentimentStrategy(BaseStrategy):
    """Sentiment-based trading strategy using Perplexity data"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("Sentiment", config)
        self.sentiment_threshold = config.get("sentiment_threshold", 0.7)
        self.min_confidence = config.get("min_confidence", 0.6)
    
    def analyze(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Optional[TradingSignal]:
        """Generate sentiment-based trading signal"""
        
        if not sentiment_data:
            logger.warning(f"No sentiment data available for {symbol}")
            return None
        
        current_price = market_data['close'].iloc[-1]
        reasons = []
        confidence = 0.5
        signal = Signal.HOLD
        
        # Parse sentiment data
        if "sentiment_score" in sentiment_data:
            sentiment_score = sentiment_data["sentiment_score"]
            
            if sentiment_score >= self.sentiment_threshold:
                reasons.append(f"Strong positive sentiment: {sentiment_score:.2f}")
                confidence += 0.3
                signal = Signal.BUY
            elif sentiment_score <= (1 - self.sentiment_threshold):
                reasons.append(f"Strong negative sentiment: {sentiment_score:.2f}")
                confidence -= 0.3
                signal = Signal.SELL
        
        # Check news sentiment
        if "news_sentiment" in sentiment_data:
            news_sentiment = sentiment_data["news_sentiment"]
            if news_sentiment == "Bullish":
                reasons.append("Bullish news sentiment")
                confidence += 0.2
                if signal != Signal.SELL:
                    signal = Signal.BUY
            elif news_sentiment == "Bearish":
                reasons.append("Bearish news sentiment")
                confidence -= 0.2
                if signal != Signal.BUY:
                    signal = Signal.SELL
        
        # Check social media mentions
        if "social_mentions_trend" in sentiment_data:
            trend = sentiment_data["social_mentions_trend"]
            if trend > 1.5:  # 50% increase in mentions
                reasons.append(f"Surge in social mentions: {trend:.2f}x")
                confidence += 0.1
            elif trend < 0.5:  # 50% decrease
                reasons.append(f"Decline in social mentions: {trend:.2f}x")
                confidence -= 0.1
        
        # Check for specific catalysts
        if "catalyst" in sentiment_data:
            catalyst = sentiment_data["catalyst"]
            reasons.append(f"Catalyst: {catalyst}")
            confidence += 0.15
        
        if abs(confidence - 0.5) < 0.1 or signal == Signal.HOLD:
            return None
        
        # Risk management based on sentiment volatility
        sentiment_volatility = sentiment_data.get("volatility", 0.5)
        risk_multiplier = 1.0 if sentiment_volatility < 0.3 else 0.5
        
        # Set stops based on sentiment strength
        if signal == Signal.BUY:
            stop_loss = current_price * (1 - 0.03 / risk_multiplier)
            take_profit = current_price * (1 + 0.05 * risk_multiplier)
        else:
            stop_loss = current_price * (1 + 0.03 / risk_multiplier)
            take_profit = current_price * (1 - 0.05 * risk_multiplier)
        
        position_size = self.calculate_position_size(
            capital=100000,
            risk_per_trade=0.015 * risk_multiplier,
            entry_price=current_price,
            stop_loss=stop_loss
        )
        
        return TradingSignal(
            symbol=symbol,
            signal=signal,
            confidence=abs(confidence),
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=position_size,
            reasons=reasons,
            timestamp=datetime.now(),
            metadata=sentiment_data
        )
    
    def should_exit(
        self,
        symbol: str,
        current_price: float,
        position: Dict[str, Any]
    ) -> bool:
        """Check if position should be closed"""
        
        # Standard exits
        if current_price <= position["stop_loss"] or current_price >= position["take_profit"]:
            return True
        
        # Sentiment reversal exit
        if "current_sentiment" in position:
            original_sentiment = position.get("entry_sentiment", 0.5)
            current_sentiment = position["current_sentiment"]
            
            # Exit if sentiment has reversed significantly
            if abs(original_sentiment - current_sentiment) > 0.4:
                logger.info(f"Sentiment reversal detected for {symbol}")
                return True
        
        return False


class StrategyManager:
    """Manages multiple trading strategies"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.strategies = {}
        self.active_strategy = None
        self.initialize_strategies()
    
    def initialize_strategies(self):
        """Initialize available strategies"""
        
        strategy_configs = self.config.get("strategies", {})
        
        if strategy_configs.get("momentum", {}).get("enabled", True):
            self.strategies["momentum"] = MomentumStrategy(
                strategy_configs.get("momentum", {})
            )
        
        if strategy_configs.get("mean_reversion", {}).get("enabled", True):
            self.strategies["mean_reversion"] = MeanReversionStrategy(
                strategy_configs.get("mean_reversion", {})
            )
        
        if strategy_configs.get("sentiment", {}).get("enabled", True):
            self.strategies["sentiment"] = SentimentStrategy(
                strategy_configs.get("sentiment", {})
            )
        
        # Set default active strategy
        if self.strategies:
            self.active_strategy = list(self.strategies.keys())[0]
            logger.info(f"Active strategy: {self.active_strategy}")
    
    def get_signal(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        sentiment_data: Optional[Dict[str, Any]] = None,
        strategy_name: Optional[str] = None
    ) -> Optional[TradingSignal]:
        """Get trading signal from active or specified strategy"""
        
        strategy_name = strategy_name or self.active_strategy
        
        if strategy_name not in self.strategies:
            logger.error(f"Strategy {strategy_name} not found")
            return None
        
        strategy = self.strategies[strategy_name]
        return strategy.analyze(symbol, market_data, sentiment_data)
    
    def get_combined_signal(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        sentiment_data: Optional[Dict[str, Any]] = None
    ) -> Optional[TradingSignal]:
        """Get combined signal from all strategies"""
        
        signals = []
        weights = self.config.get("strategy_weights", {})
        
        for name, strategy in self.strategies.items():
            signal = strategy.analyze(symbol, market_data, sentiment_data)
            if signal:
                weight = weights.get(name, 1.0)
                signals.append((signal, weight))
        
        if not signals:
            return None
        
        # Combine signals
        total_weight = sum(w for _, w in signals)
        weighted_confidence = sum(s.confidence * w for s, w in signals) / total_weight
        
        # Majority voting for signal direction
        buy_weight = sum(w for s, w in signals if s.signal in [Signal.BUY, Signal.STRONG_BUY])
        sell_weight = sum(w for s, w in signals if s.signal in [Signal.SELL, Signal.STRONG_SELL])
        
        if buy_weight > sell_weight and buy_weight > total_weight * 0.5:
            combined_signal = Signal.BUY
        elif sell_weight > buy_weight and sell_weight > total_weight * 0.5:
            combined_signal = Signal.SELL
        else:
            return None  # No consensus
        
        # Use average stops and position size
        avg_stop = np.mean([s.stop_loss for s, _ in signals])
        avg_target = np.mean([s.take_profit for s, _ in signals])
        avg_size = np.mean([s.position_size for s, _ in signals])
        
        # Combine reasons
        all_reasons = []
        for signal, _ in signals:
            all_reasons.extend([f"[{signal.symbol}] {r}" for r in signal.reasons])
        
        return TradingSignal(
            symbol=symbol,
            signal=combined_signal,
            confidence=weighted_confidence,
            entry_price=market_data['close'].iloc[-1],
            stop_loss=avg_stop,
            take_profit=avg_target,
            position_size=avg_size,
            reasons=all_reasons,
            timestamp=datetime.now(),
            metadata={"combined": True, "strategies": len(signals)}
        )
    
    def switch_strategy(self, strategy_name: str):
        """Switch active strategy"""
        
        if strategy_name in self.strategies:
            self.active_strategy = strategy_name
            logger.info(f"Switched to strategy: {strategy_name}")
        else:
            logger.error(f"Strategy {strategy_name} not found")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report for all strategies"""
        
        report = {}
        for name, strategy in self.strategies.items():
            report[name] = strategy.performance
        
        return report