"""
Local Trading Client
Replaces Alpaca API with local simulation and mock trading
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Literal, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MockPosition:
    """Mock position data"""
    symbol: str
    qty: int
    side: str
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    avg_entry_price: float
    current_price: float


@dataclass
class MockOrder:
    """Mock order data"""
    id: str
    symbol: str
    qty: int
    side: str
    status: str
    filled_qty: int
    filled_avg_price: float
    created_at: datetime
    updated_at: datetime


class LocalTradingClient:
    """
    Local trading client that simulates trading operations
    Replaces Alpaca Trading API with local simulation
    """
    
    def __init__(self, paper: bool = True, initial_cash: float = 100000.0):
        self.paper = paper
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, MockPosition] = {}
        self.orders: Dict[str, MockOrder] = {}
        self.order_counter = 0
        self.trade_history: List[Dict] = []
        
        logger.info(f"LocalTradingClient initialized (paper={paper}, cash=${initial_cash:,.2f})")
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        total_value = self.cash + sum(pos.market_value for pos in self.positions.values())
        
        return {
            'equity': total_value,
            'cash': self.cash,
            'buying_power': self.cash * 2,  # Margin simulation
            'portfolio_value': total_value,
            'pattern_day_trader': False,
            'trading_blocked': False,
            'account_blocked': False,
            'daytrade_count': 0
        }
    
    def get_positions(self) -> List[MockPosition]:
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_position(self, symbol: str) -> Optional[MockPosition]:
        """Get position for specific symbol"""
        return self.positions.get(symbol)
    
    def submit_market_order(
        self,
        symbol: str,
        qty: int,
        side: Literal['buy', 'sell'],
        time_in_force: str = 'day'
    ) -> MockOrder:
        """
        Submit a market order
        
        Args:
            symbol: Stock symbol
            qty: Number of shares
            side: 'buy' or 'sell'
            time_in_force: Order duration
            
        Returns:
            MockOrder object
        """
        # Generate realistic price
        current_price = self._get_current_price(symbol)
        
        # Check if we have enough cash for buy orders
        if side.lower() == 'buy':
            required_cash = qty * current_price
            if required_cash > self.cash:
                raise ValueError(f"Insufficient cash. Required: ${required_cash:,.2f}, Available: ${self.cash:,.2f}")
        
        # Check if we have enough shares for sell orders
        if side.lower() == 'sell':
            current_position = self.positions.get(symbol)
            if not current_position or current_position.qty < qty:
                raise ValueError(f"Insufficient shares. Required: {qty}, Available: {current_position.qty if current_position else 0}")
        
        # Create order
        order_id = f"order_{self.order_counter:06d}"
        self.order_counter += 1
        
        order = MockOrder(
            id=order_id,
            symbol=symbol,
            qty=qty,
            side=side,
            status='filled',  # Simulate immediate fill
            filled_qty=qty,
            filled_avg_price=current_price,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Execute the trade
        self._execute_trade(order)
        
        # Store order
        self.orders[order_id] = order
        
        logger.info(f"Market order executed: {side.upper()} {qty} {symbol} @ ${current_price:.2f}")
        return order
    
    def submit_bracket_order(
        self,
        symbol: str,
        qty: int,
        side: Literal['buy', 'sell'],
        stop_loss_price: float,
        take_profit_price: float,
        time_in_force: str = 'day'
    ) -> MockOrder:
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
        # For simulation, just execute the main order
        # In a real implementation, you'd track the bracket orders
        return self.submit_market_order(symbol, qty, side, time_in_force)
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order by ID"""
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status in ['pending', 'accepted']:
                order.status = 'cancelled'
                order.updated_at = datetime.now()
                logger.info(f"Order {order_id} cancelled")
                return True
            else:
                logger.warning(f"Cannot cancel order {order_id} with status {order.status}")
                return False
        else:
            logger.error(f"Order {order_id} not found")
            return False
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        cancelled_count = 0
        for order in self.orders.values():
            if order.status in ['pending', 'accepted']:
                order.status = 'cancelled'
                order.updated_at = datetime.now()
                cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} orders")
        return True
    
    def get_order(self, order_id: str) -> Optional[MockOrder]:
        """Get order by ID"""
        return self.orders.get(order_id)
    
    def get_orders(self, status: Optional[str] = None, limit: int = 100) -> List[MockOrder]:
        """Get orders with optional status filter"""
        orders = list(self.orders.values())
        
        if status:
            orders = [order for order in orders if order.status == status]
        
        return orders[-limit:]  # Return most recent orders
    
    def close_position(self, symbol: str, qty: Optional[int] = None, percentage: Optional[float] = None) -> bool:
        """
        Close a position (fully or partially)
        
        Args:
            symbol: Stock symbol
            qty: Number of shares to close (None = all)
            percentage: Percentage of position to close (0-1)
        
        Returns:
            Success status
        """
        position = self.positions.get(symbol)
        if not position:
            logger.warning(f"No position found for {symbol}")
            return False
        
        # Calculate shares to close
        if qty is None and percentage is None:
            qty = position.qty  # Close all
        elif percentage is not None:
            qty = int(position.qty * percentage)
        
        qty = min(qty, position.qty)  # Don't close more than we have
        
        if qty <= 0:
            logger.warning(f"Invalid quantity to close: {qty}")
            return False
        
        # Execute sell order
        try:
            order = self.submit_market_order(symbol, qty, 'sell')
            logger.info(f"Closed {qty} shares of {symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
            return False
    
    def close_all_positions(self) -> bool:
        """Close all open positions"""
        success = True
        for symbol in list(self.positions.keys()):
            if not self.close_position(symbol):
                success = False
        
        logger.info("Closed all positions")
        return success
    
    def _execute_trade(self, order: MockOrder):
        """Execute a trade and update positions"""
        symbol = order.symbol
        qty = order.filled_qty
        price = order.filled_avg_price
        side = order.side
        
        # Update cash
        if side.lower() == 'buy':
            self.cash -= qty * price
        else:  # sell
            self.cash += qty * price
        
        # Update positions
        if symbol not in self.positions:
            if side.lower() == 'buy':
                self.positions[symbol] = MockPosition(
                    symbol=symbol,
                    qty=qty,
                    side='long',
                    market_value=qty * price,
                    cost_basis=qty * price,
                    unrealized_pl=0.0,
                    unrealized_plpc=0.0,
                    avg_entry_price=price,
                    current_price=price
                )
        else:
            position = self.positions[symbol]
            
            if side.lower() == 'buy':
                # Add to position
                total_qty = position.qty + qty
                total_cost = position.cost_basis + (qty * price)
                position.qty = total_qty
                position.cost_basis = total_cost
                position.avg_entry_price = total_cost / total_qty
                position.market_value = total_qty * price
                position.current_price = price
            else:  # sell
                # Reduce position
                position.qty -= qty
                if position.qty <= 0:
                    # Position closed
                    del self.positions[symbol]
                else:
                    # Update remaining position
                    position.market_value = position.qty * price
                    position.current_price = price
        
        # Record trade
        self.trade_history.append({
            'timestamp': order.created_at,
            'symbol': symbol,
            'side': side,
            'qty': qty,
            'price': price,
            'order_id': order.id
        })
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol (simulated)"""
        # Use cached price if available, otherwise generate new one
        if symbol in self.positions:
            # Add some price movement
            current_price = self.positions[symbol].current_price
            change = random.uniform(-0.05, 0.05)  # ±5% change
            return current_price * (1 + change)
        else:
            # Generate new price
            return random.uniform(50, 500)
    
    def update_position_prices(self):
        """Update all position prices with simulated market movements"""
        for symbol, position in self.positions.items():
            current_price = self._get_current_price(symbol)
            position.current_price = current_price
            position.market_value = position.qty * current_price
            
            # Calculate P&L
            if position.side == 'long':
                position.unrealized_pl = (current_price - position.avg_entry_price) * position.qty
            else:
                position.unrealized_pl = (position.avg_entry_price - current_price) * position.qty
            
            position.unrealized_plpc = (position.unrealized_pl / position.cost_basis) * 100
    
    def get_position_summary(self) -> Dict:
        """Get summary of all positions"""
        self.update_position_prices()  # Update prices first
        
        if not self.positions:
            return {
                'total_positions': 0,
                'total_value': 0.0,
                'total_pnl': 0.0,
                'positions': []
            }
        
        total_value = sum(pos.market_value for pos in self.positions.values())
        total_pnl = sum(pos.unrealized_pl for pos in self.positions.values())
        
        return {
            'total_positions': len(self.positions),
            'total_value': total_value,
            'total_pnl': total_pnl,
            'positions': [
                {
                    'symbol': pos.symbol,
                    'qty': pos.qty,
                    'avg_entry_price': pos.avg_entry_price,
                    'current_price': pos.current_price,
                    'market_value': pos.market_value,
                    'unrealized_pl': pos.unrealized_pl,
                    'unrealized_plpc': pos.unrealized_plpc,
                    'side': pos.side
                }
                for pos in self.positions.values()
            ]
        }
    
    def get_performance_summary(self) -> Dict:
        """Get trading performance summary"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_trade_pnl': 0.0
            }
        
        # Calculate performance metrics
        total_trades = len(self.trade_history)
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0.0
        
        # Simple P&L calculation based on current positions
        for position in self.positions.values():
            total_pnl += position.unrealized_pl
        
        # Add realized P&L from closed positions (simplified)
        # In a real implementation, you'd track this more carefully
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_trade_pnl': avg_trade_pnl
        }
    
    def reset_account(self, initial_cash: float = 100000.0):
        """Reset account to initial state"""
        self.cash = initial_cash
        self.positions.clear()
        self.orders.clear()
        self.trade_history.clear()
        self.order_counter = 0
        logger.info(f"Account reset with ${initial_cash:,.2f}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass