"""
Order execution module for Alpaca trading
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal
from loguru import logger
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, StopOrderRequest,
    StopLimitOrderRequest, TrailingStopOrderRequest, BracketOrderRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, OrderStatus
from alpaca.trading.models import Order, Position, Asset
from src.strategy import TradingSignal, Signal
import uuid


class OrderExecutor:
    """Handles order execution on Alpaca"""
    
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        paper: bool = True,
        max_retries: int = 3
    ):
        self.trading_client = TradingClient(api_key, secret_key, paper=paper)
        self.max_retries = max_retries
        self.pending_orders = {}
        self.executed_orders = []
        self.order_history = []
        
        # Performance metrics
        self.metrics = {
            "total_orders": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "cancelled_orders": 0,
            "total_volume": 0,
            "total_commission": 0
        }
    
    def execute_signal(
        self,
        signal: TradingSignal,
        order_type: str = "bracket",
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Optional[Order]:
        """Execute a trading signal"""
        
        try:
            # Validate signal
            if not self._validate_signal(signal):
                logger.error(f"Invalid signal for {signal.symbol}")
                return None
            
            # Check if we can trade this asset
            if not self._check_asset_tradeable(signal.symbol):
                logger.warning(f"Asset {signal.symbol} is not tradeable")
                return None
            
            # Determine order side
            if signal.signal in [Signal.BUY, Signal.STRONG_BUY]:
                side = OrderSide.BUY
            elif signal.signal in [Signal.SELL, Signal.STRONG_SELL]:
                side = OrderSide.SELL
            else:
                logger.info(f"No action needed for {signal.symbol} (HOLD signal)")
                return None
            
            # Round position size
            qty = int(signal.position_size)
            if qty <= 0:
                logger.warning(f"Position size too small for {signal.symbol}")
                return None
            
            # Create order based on type
            if order_type == "bracket":
                order = self._create_bracket_order(
                    symbol=signal.symbol,
                    qty=qty,
                    side=side,
                    entry_price=signal.entry_price,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    time_in_force=time_in_force
                )
            elif order_type == "market":
                order = self._create_market_order(
                    symbol=signal.symbol,
                    qty=qty,
                    side=side,
                    time_in_force=time_in_force
                )
            elif order_type == "limit":
                order = self._create_limit_order(
                    symbol=signal.symbol,
                    qty=qty,
                    side=side,
                    limit_price=signal.entry_price,
                    time_in_force=time_in_force
                )
            else:
                logger.error(f"Unknown order type: {order_type}")
                return None
            
            # Execute order
            result = self._submit_order_with_retry(order)
            
            if result:
                logger.info(f"Order executed for {signal.symbol}: {result.id}")
                self._record_order(result, signal)
                self.metrics["total_orders"] += 1
                self.metrics["successful_orders"] += 1
                self.metrics["total_volume"] += qty * signal.entry_price
            else:
                self.metrics["failed_orders"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            self.metrics["failed_orders"] += 1
            return None
    
    def _validate_signal(self, signal: TradingSignal) -> bool:
        """Validate trading signal"""
        
        if signal.position_size <= 0:
            logger.warning("Invalid position size")
            return False
        
        if signal.entry_price <= 0:
            logger.warning("Invalid entry price")
            return False
        
        if signal.signal in [Signal.BUY, Signal.STRONG_BUY]:
            if signal.stop_loss >= signal.entry_price:
                logger.warning("Stop loss must be below entry for buy signal")
                return False
            if signal.take_profit <= signal.entry_price:
                logger.warning("Take profit must be above entry for buy signal")
                return False
        
        elif signal.signal in [Signal.SELL, Signal.STRONG_SELL]:
            if signal.stop_loss <= signal.entry_price:
                logger.warning("Stop loss must be above entry for sell signal")
                return False
            if signal.take_profit >= signal.entry_price:
                logger.warning("Take profit must be below entry for sell signal")
                return False
        
        return True
    
    def _check_asset_tradeable(self, symbol: str) -> bool:
        """Check if asset is tradeable"""
        
        try:
            asset = self.trading_client.get_asset(symbol)
            return asset.tradable and asset.status == "active"
        except Exception as e:
            logger.error(f"Error checking asset {symbol}: {e}")
            return False
    
    def _create_bracket_order(
        self,
        symbol: str,
        qty: int,
        side: OrderSide,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        time_in_force: TimeInForce
    ) -> BracketOrderRequest:
        """Create a bracket order (entry + stop loss + take profit)"""
        
        return BracketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force,
            order_class="bracket",
            limit_price=round(entry_price, 2),
            stop_loss={"stop_price": round(stop_loss, 2)},
            take_profit={"limit_price": round(take_profit, 2)}
        )
    
    def _create_market_order(
        self,
        symbol: str,
        qty: int,
        side: OrderSide,
        time_in_force: TimeInForce
    ) -> MarketOrderRequest:
        """Create a market order"""
        
        return MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force
        )
    
    def _create_limit_order(
        self,
        symbol: str,
        qty: int,
        side: OrderSide,
        limit_price: float,
        time_in_force: TimeInForce
    ) -> LimitOrderRequest:
        """Create a limit order"""
        
        return LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=time_in_force,
            limit_price=round(limit_price, 2)
        )
    
    def _submit_order_with_retry(
        self,
        order_request: Any,
        retries: int = None
    ) -> Optional[Order]:
        """Submit order with retry logic"""
        
        retries = retries or self.max_retries
        
        for attempt in range(retries):
            try:
                order = self.trading_client.submit_order(order_request)
                return order
                
            except Exception as e:
                logger.warning(f"Order submission attempt {attempt + 1} failed: {e}")
                
                if attempt < retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    asyncio.sleep(wait_time)
                else:
                    logger.error(f"Order submission failed after {retries} attempts")
                    return None
        
        return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        
        try:
            self.trading_client.cancel_order_by_id(order_id)
            logger.info(f"Order {order_id} cancelled")
            self.metrics["cancelled_orders"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self) -> int:
        """Cancel all open orders"""
        
        try:
            cancelled = self.trading_client.cancel_orders()
            count = len(cancelled)
            logger.info(f"Cancelled {count} orders")
            self.metrics["cancelled_orders"] += count
            return count
            
        except Exception as e:
            logger.error(f"Error cancelling all orders: {e}")
            return 0
    
    def get_order_status(self, order_id: str) -> Optional[Order]:
        """Get order status"""
        
        try:
            return self.trading_client.get_order_by_id(order_id)
        except Exception as e:
            logger.error(f"Error getting order status: {e}")
            return None
    
    def get_open_orders(self) -> List[Order]:
        """Get all open orders"""
        
        try:
            return self.trading_client.get_orders(status="open")
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_positions(self) -> List[Position]:
        """Get all positions"""
        
        try:
            return self.trading_client.get_all_positions()
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return []
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a symbol"""
        
        try:
            return self.trading_client.get_position(symbol)
        except Exception as e:
            # Position might not exist
            logger.debug(f"No position found for {symbol}")
            return None
    
    def close_position(self, symbol: str) -> bool:
        """Close a position"""
        
        try:
            self.trading_client.close_position(symbol)
            logger.info(f"Position closed for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            return False
    
    def close_all_positions(self) -> int:
        """Close all positions"""
        
        try:
            positions = self.get_positions()
            count = 0
            
            for position in positions:
                if self.close_position(position.symbol):
                    count += 1
            
            logger.info(f"Closed {count} positions")
            return count
            
        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
            return 0
    
    def _record_order(self, order: Order, signal: TradingSignal):
        """Record order for tracking"""
        
        order_record = {
            "id": order.id,
            "symbol": order.symbol,
            "side": order.side,
            "qty": order.qty,
            "type": order.order_type,
            "status": order.status,
            "submitted_at": order.submitted_at,
            "signal": signal,
            "metadata": {
                "confidence": signal.confidence,
                "reasons": signal.reasons,
                "strategy": signal.metadata
            }
        }
        
        self.order_history.append(order_record)
        self.pending_orders[order.id] = order_record
    
    def update_order_status(self):
        """Update status of pending orders"""
        
        for order_id in list(self.pending_orders.keys()):
            order = self.get_order_status(order_id)
            
            if order:
                if order.status in [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]:
                    logger.info(f"Order {order_id} filled")
                    self.executed_orders.append(self.pending_orders[order_id])
                    del self.pending_orders[order_id]
                    
                elif order.status in [OrderStatus.CANCELED, OrderStatus.EXPIRED, OrderStatus.REJECTED]:
                    logger.info(f"Order {order_id} {order.status}")
                    del self.pending_orders[order_id]
    
    def get_execution_report(self) -> Dict[str, Any]:
        """Get execution report"""
        
        return {
            "metrics": self.metrics,
            "pending_orders": len(self.pending_orders),
            "executed_orders": len(self.executed_orders),
            "total_orders": len(self.order_history),
            "success_rate": (
                self.metrics["successful_orders"] / self.metrics["total_orders"]
                if self.metrics["total_orders"] > 0 else 0
            )
        }


class RiskManager:
    """Risk management for trading operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_position_size = config.get("max_position_size", 0.1)
        self.max_daily_loss = config.get("max_daily_loss", 0.02)
        self.max_drawdown = config.get("max_drawdown", 0.1)
        self.max_positions = config.get("max_positions", 5)
        self.min_cash_reserve = config.get("min_cash_reserve", 0.2)
        
        # Risk tracking
        self.daily_pnl = 0
        self.peak_value = 0
        self.current_drawdown = 0
        self.positions_count = 0
        self.risk_violations = []
    
    def validate_trade(
        self,
        signal: TradingSignal,
        portfolio_value: float,
        cash_available: float,
        current_positions: List[Position]
    ) -> Tuple[bool, List[str]]:
        """Validate if trade meets risk criteria"""
        
        violations = []
        
        # Check position size limit
        position_value = signal.position_size * signal.entry_price
        if position_value > portfolio_value * self.max_position_size:
            violations.append(f"Position size exceeds limit: {position_value:.2f} > {portfolio_value * self.max_position_size:.2f}")
        
        # Check cash reserve
        if cash_available - position_value < portfolio_value * self.min_cash_reserve:
            violations.append(f"Insufficient cash reserve after trade")
        
        # Check maximum positions
        self.positions_count = len(current_positions)
        if self.positions_count >= self.max_positions:
            violations.append(f"Maximum positions reached: {self.positions_count}")
        
        # Check daily loss limit
        if self.daily_pnl < -portfolio_value * self.max_daily_loss:
            violations.append(f"Daily loss limit exceeded: {self.daily_pnl:.2f}")
        
        # Check drawdown limit
        if self.current_drawdown > self.max_drawdown:
            violations.append(f"Maximum drawdown exceeded: {self.current_drawdown:.2%}")
        
        # Check correlation (avoid concentration risk)
        if self._check_concentration_risk(signal.symbol, current_positions):
            violations.append(f"Concentration risk: too much exposure to similar assets")
        
        if violations:
            logger.warning(f"Risk violations for {signal.symbol}: {violations}")
            self.risk_violations.extend(violations)
            return False, violations
        
        return True, []
    
    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: Optional[float] = None
    ) -> int:
        """Calculate position size based on risk"""
        
        risk_per_trade = risk_per_trade or self.config.get("risk_per_trade", 0.02)
        
        # Risk amount in dollars
        risk_amount = capital * risk_per_trade
        
        # Price risk per share
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            logger.warning("Invalid stop loss - no price risk")
            return 0
        
        # Calculate shares
        shares = risk_amount / price_risk
        
        # Apply position size limit
        max_shares = (capital * self.max_position_size) / entry_price
        
        return int(min(shares, max_shares))
    
    def update_portfolio_metrics(
        self,
        portfolio_value: float,
        daily_pnl: float
    ):
        """Update portfolio metrics"""
        
        self.daily_pnl = daily_pnl
        
        # Track peak value for drawdown calculation
        if portfolio_value > self.peak_value:
            self.peak_value = portfolio_value
        
        # Calculate drawdown
        if self.peak_value > 0:
            self.current_drawdown = (self.peak_value - portfolio_value) / self.peak_value
    
    def _check_concentration_risk(
        self,
        symbol: str,
        current_positions: List[Position]
    ) -> bool:
        """Check for concentration risk"""
        
        # This is simplified - in practice you'd check:
        # - Sector concentration
        # - Correlation between assets
        # - Beta exposure
        
        # For now, just check if we already have a position in this symbol
        for position in current_positions:
            if position.symbol == symbol:
                return True
        
        return False
    
    def should_stop_trading(self) -> bool:
        """Check if trading should be stopped due to risk limits"""
        
        if self.daily_pnl < -self.max_daily_loss:
            logger.warning("Daily loss limit reached - stopping trading")
            return True
        
        if self.current_drawdown > self.max_drawdown:
            logger.warning("Maximum drawdown reached - stopping trading")
            return True
        
        return False
    
    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        atr: float,
        multiplier: float = 2.0
    ) -> float:
        """Calculate trailing stop price"""
        
        if current_price > entry_price:
            # For long position
            return current_price - (atr * multiplier)
        else:
            # For short position
            return current_price + (atr * multiplier)
    
    def get_risk_report(self) -> Dict[str, Any]:
        """Get risk management report"""
        
        return {
            "daily_pnl": self.daily_pnl,
            "current_drawdown": self.current_drawdown,
            "peak_value": self.peak_value,
            "positions_count": self.positions_count,
            "max_positions": self.max_positions,
            "risk_violations": self.risk_violations[-10:],  # Last 10 violations
            "trading_enabled": not self.should_stop_trading()
        }