"""
Order Executor
Handles order submission, management, and position tracking with Alpaca
"""

import time
from typing import List, Dict, Optional, Literal
from datetime import datetime
import logging

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopLossRequest,
    TakeProfitRequest,
    GetOrdersRequest,
    ClosePositionRequest
)
from alpaca.trading.enums import (
    OrderSide, 
    TimeInForce, 
    OrderClass,
    QueryOrderStatus
)
from alpaca.trading.models import Order, Position as AlpacaPosition

from src.config import config
from src.strategy import Signal

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_requests: int = 200, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests 
                        if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            sleep_time = self.time_window - (now - self.requests[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
                self.requests = []
        
        self.requests.append(now)


class OrderExecutor:
    """
    Execute and manage orders on Alpaca
    Handles bracket orders, position tracking, and risk management
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        paper: Optional[bool] = None
    ):
        self.api_key = api_key or config.alpaca.api_key
        self.secret_key = secret_key or config.alpaca.secret_key
        self.paper = paper if paper is not None else config.alpaca.paper_trading
        
        self.client = TradingClient(
            self.api_key,
            self.secret_key,
            paper=self.paper
        )
        
        self.rate_limiter = RateLimiter()
        self.orders_cache: Dict[str, Order] = {}
        self.daily_trades_count = 0
        self.last_trade_date = None
        
        logger.info(f"OrderExecutor initialized (paper={self.paper})")
    
    # ============= Account Methods =============
    
    def get_account(self) -> Dict:
        """Get account information"""
        self.rate_limiter.wait_if_needed()
        
        try:
            account = self.client.get_account()
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'account_blocked': account.account_blocked,
                'daytrade_count': account.daytrade_count
            }
        except Exception as e:
            logger.error(f"Failed to get account: {e}")
            raise
    
    def get_positions(self) -> List[AlpacaPosition]:
        """Get all open positions"""
        self.rate_limiter.wait_if_needed()
        
        try:
            positions = self.client.get_all_positions()
            return positions
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[AlpacaPosition]:
        """Get position for specific symbol"""
        self.rate_limiter.wait_if_needed()
        
        try:
            position = self.client.get_open_position(symbol)
            return position
        except Exception as e:
            if "position does not exist" in str(e).lower():
                return None
            logger.error(f"Failed to get position for {symbol}: {e}")
            raise
    
    # ============= Order Submission Methods =============
    
    def submit_market_order(
        self,
        symbol: str,
        qty: int,
        side: Literal['buy', 'sell'],
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Order:
        """
        Submit a market order
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            side: 'buy' or 'sell'
            time_in_force: Order duration
        
        Returns:
            Order object
        """
        self._check_trading_limits()
        self.rate_limiter.wait_if_needed()
        
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=time_in_force
        )
        
        try:
            order = self.client.submit_order(request)
            self._update_trade_count()
            self.orders_cache[order.id] = order
            
            logger.info(f"Market order submitted: {side.upper()} {qty} {symbol} (Order ID: {order.id})")
            return order
        
        except Exception as e:
            logger.error(f"Failed to submit market order: {e}")
            raise
    
    def submit_bracket_order(
        self,
        symbol: str,
        qty: int,
        side: Literal['buy', 'sell'],
        stop_loss_price: float,
        take_profit_price: float,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Order:
        """
        Submit a bracket order (entry + stop loss + take profit)
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            side: 'buy' or 'sell'
            stop_loss_price: Stop loss trigger price
            take_profit_price: Take profit limit price
            time_in_force: Order duration
        
        Returns:
            Parent order object
        """
        self._check_trading_limits()
        self.rate_limiter.wait_if_needed()
        
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        
        request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=time_in_force,
            order_class=OrderClass.BRACKET,
            stop_loss=StopLossRequest(stop_price=stop_loss_price),
            take_profit=TakeProfitRequest(limit_price=take_profit_price)
        )
        
        try:
            order = self.client.submit_order(request)
            self._update_trade_count()
            self.orders_cache[order.id] = order
            
            logger.info(
                f"Bracket order submitted: {side.upper()} {qty} {symbol} "
                f"(SL: ${stop_loss_price}, TP: ${take_profit_price}, Order ID: {order.id})"
            )
            return order
        
        except Exception as e:
            logger.error(f"Failed to submit bracket order: {e}")
            raise
    
    def submit_signal_order(
        self,
        signal: Signal,
        account_value: float,
        use_bracket: bool = True
    ) -> Optional[Order]:
        """
        Submit order based on trading signal
        
        Args:
            signal: Signal object from strategy
            account_value: Current account value
            use_bracket: Use bracket orders (recommended)
        
        Returns:
            Order object or None if no action taken
        """
        if signal.action == 'HOLD':
            logger.debug(f"Signal is HOLD for {signal.symbol}, no order submitted")
            return None
        
        if signal.strength < 0.5:
            logger.debug(f"Signal strength too low ({signal.strength}) for {signal.symbol}")
            return None
        
        # Calculate position size
        from src.strategy import TradingStrategy
        strategy = TradingStrategy("temp")
        
        qty = strategy.calculate_position_size(
            account_value=account_value,
            entry_price=signal.entry_price or 0,
            stop_loss_price=signal.stop_loss or 0,
            signal_strength=signal.strength
        )
        
        if qty == 0:
            logger.warning(f"Position size calculated as 0 for {signal.symbol}")
            return None
        
        side = 'buy' if signal.action == 'BUY' else 'sell'
        
        # Submit order
        if use_bracket and signal.stop_loss and signal.take_profit:
            return self.submit_bracket_order(
                symbol=signal.symbol,
                qty=qty,
                side=side,
                stop_loss_price=signal.stop_loss,
                take_profit_price=signal.take_profit
            )
        else:
            return self.submit_market_order(
                symbol=signal.symbol,
                qty=qty,
                side=side
            )
    
    # ============= Order Management Methods =============
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order by ID"""
        self.rate_limiter.wait_if_needed()
        
        try:
            self.client.cancel_order_by_id(order_id)
            logger.info(f"Order {order_id} cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            return False
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        self.rate_limiter.wait_if_needed()
        
        try:
            self.client.cancel_orders()
            logger.info("All orders cancelled")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel all orders: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        self.rate_limiter.wait_if_needed()
        
        try:
            order = self.client.get_order_by_id(order_id)
            self.orders_cache[order_id] = order
            return order
        except Exception as e:
            logger.error(f"Failed to get order {order_id}: {e}")
            return None
    
    def get_orders(
        self,
        status: Optional[QueryOrderStatus] = None,
        limit: int = 100
    ) -> List[Order]:
        """Get orders with optional status filter"""
        self.rate_limiter.wait_if_needed()
        
        try:
            request = GetOrdersRequest(
                status=status,
                limit=limit
            )
            orders = self.client.get_orders(request)
            return orders
        except Exception as e:
            logger.error(f"Failed to get orders: {e}")
            return []
    
    # ============= Position Management Methods =============
    
    def close_position(
        self,
        symbol: str,
        qty: Optional[int] = None,
        percentage: Optional[float] = None
    ) -> bool:
        """
        Close a position (fully or partially)
        
        Args:
            symbol: Stock symbol
            qty: Number of shares to close (None = all)
            percentage: Percentage of position to close (0-1)
        
        Returns:
            Success status
        """
        self.rate_limiter.wait_if_needed()
        
        try:
            if qty or percentage:
                request = ClosePositionRequest(
                    qty=str(qty) if qty else None,
                    percentage=str(percentage) if percentage else None
                )
                self.client.close_position(symbol, request)
            else:
                self.client.close_position(symbol)
            
            logger.info(f"Position closed for {symbol}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to close position for {symbol}: {e}")
            return False
    
    def close_all_positions(self) -> bool:
        """Close all open positions"""
        self.rate_limiter.wait_if_needed()
        
        try:
            self.client.close_all_positions(cancel_orders=True)
            logger.info("All positions closed")
            return True
        except Exception as e:
            logger.error(f"Failed to close all positions: {e}")
            return False
    
    # ============= Helper Methods =============
    
    def _check_trading_limits(self):
        """Check if trading limits have been reached"""
        today = datetime.now().date()
        
        # Reset counter if new day
        if self.last_trade_date != today:
            self.daily_trades_count = 0
            self.last_trade_date = today
        
        # Check daily limit
        if self.daily_trades_count >= config.trading.max_daily_trades:
            raise Exception(f"Daily trade limit reached ({config.trading.max_daily_trades})")
    
    def _update_trade_count(self):
        """Update daily trade counter"""
        self.daily_trades_count += 1
    
    def get_position_summary(self) -> Dict:
        """Get summary of all positions"""
        positions = self.get_positions()
        
        if not positions:
            return {
                'total_positions': 0,
                'total_value': 0.0,
                'total_pnl': 0.0,
                'positions': []
            }
        
        total_value = sum(float(p.market_value) for p in positions)
        total_pnl = sum(float(p.unrealized_pl) for p in positions)
        
        return {
            'total_positions': len(positions),
            'total_value': total_value,
            'total_pnl': total_pnl,
            'positions': [
                {
                    'symbol': p.symbol,
                    'qty': int(p.qty),
                    'avg_entry_price': float(p.avg_entry_price),
                    'current_price': float(p.current_price),
                    'market_value': float(p.market_value),
                    'unrealized_pl': float(p.unrealized_pl),
                    'unrealized_plpc': float(p.unrealized_plpc),
                    'side': p.side
                }
                for p in positions
            ]
        }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
