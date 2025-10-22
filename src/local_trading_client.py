"""
Local trading client - Simulates trading operations without external APIs
"""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid
import pandas as pd
try:
    from .config_local import LocalConfig
except ImportError:
    from config_local import LocalConfig

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderStatus(Enum):
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PENDING = "pending"

class TimeInForce(Enum):
    DAY = "day"
    GTC = "gtc"  # Good Till Cancelled
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill

class LocalTradingClient:
    """Local trading client for paper trading simulation"""
    
    def __init__(self):
        self.config = LocalConfig
        self.db_path = self.config.DB_PATH
        self._init_trading_database()
        self._init_account()
    
    def _init_trading_database(self):
        """Initialize trading-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Account table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account (
                id TEXT PRIMARY KEY,
                equity REAL,
                cash REAL,
                buying_power REAL,
                portfolio_value REAL,
                day_trade_count INTEGER,
                pattern_day_trader BOOLEAN,
                updated_at DATETIME
            )
        """)
        
        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                qty REAL,
                side TEXT,
                market_value REAL,
                cost_basis REAL,
                unrealized_pl REAL,
                unrealized_plpc REAL,
                current_price REAL,
                updated_at DATETIME
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                qty REAL,
                side TEXT,
                order_type TEXT,
                status TEXT,
                limit_price REAL,
                stop_price REAL,
                time_in_force TEXT,
                created_at DATETIME,
                filled_at DATETIME,
                filled_qty REAL,
                filled_avg_price REAL
            )
        """)
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                order_id TEXT,
                symbol TEXT,
                qty REAL,
                price REAL,
                side TEXT,
                timestamp DATETIME,
                commission REAL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_account(self):
        """Initialize account with starting capital"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if account exists
        cursor.execute("SELECT id FROM account LIMIT 1")
        existing = cursor.fetchone()
        
        if not existing:
            account_id = str(uuid.uuid4())
            initial_capital = self.config.INITIAL_CAPITAL
            
            cursor.execute("""
                INSERT INTO account (id, equity, cash, buying_power, portfolio_value, 
                                    day_trade_count, pattern_day_trader, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, 0, ?)
            """, (account_id, initial_capital, initial_capital, initial_capital, 
                  initial_capital, datetime.now()))
            conn.commit()
        
        conn.close()
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, equity, cash, buying_power, portfolio_value, 
                   day_trade_count, pattern_day_trader
            FROM account
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'account_id': row[0],
                'equity': row[1],
                'cash': row[2],
                'buying_power': row[3],
                'portfolio_value': row[4],
                'day_trade_count': row[5],
                'pattern_day_trader': bool(row[6])
            }
        return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, qty, side, market_value, cost_basis, 
                   unrealized_pl, unrealized_plpc, current_price
            FROM positions
            WHERE qty > 0
        """)
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'symbol': row[0],
                'qty': row[1],
                'side': row[2],
                'market_value': row[3],
                'cost_basis': row[4],
                'unrealized_pl': row[5],
                'unrealized_plpc': row[6],
                'current_price': row[7]
            })
        
        conn.close()
        return positions
    
    def place_market_order(self, 
                          symbol: str, 
                          qty: float, 
                          side: OrderSide,
                          time_in_force: TimeInForce = TimeInForce.DAY) -> Dict[str, Any]:
        """Place a simulated market order"""
        order_id = str(uuid.uuid4())
        
        # Get current market price (simulated)
        try:
            from .local_data_client import LocalDataClient
        except ImportError:
            from local_data_client import LocalDataClient
        data_client = LocalDataClient()
        quotes = data_client.get_latest_quotes([symbol])
        
        if symbol in quotes:
            if side == OrderSide.BUY:
                fill_price = quotes[symbol]['ask']
            else:
                fill_price = quotes[symbol]['bid']
        else:
            fill_price = 100.0  # Default price
        
        # Calculate commission
        commission = qty * fill_price * self.config.COMMISSION_RATE
        
        # Apply slippage
        slippage = fill_price * self.config.SLIPPAGE_RATE
        if side == OrderSide.BUY:
            fill_price += slippage
        else:
            fill_price -= slippage
        
        # Create order
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO orders (id, symbol, qty, side, order_type, status, 
                              time_in_force, created_at, filled_at, 
                              filled_qty, filled_avg_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, symbol, qty, side.value, OrderType.MARKET.value, 
              OrderStatus.FILLED.value, time_in_force.value, 
              datetime.now(), datetime.now(), qty, fill_price))
        
        # Update positions
        self._update_position(symbol, qty if side == OrderSide.BUY else -qty, fill_price)
        
        # Update account cash
        total_cost = qty * fill_price + commission
        if side == OrderSide.BUY:
            self._update_cash(-total_cost)
        else:
            self._update_cash(total_cost - 2 * commission)  # Subtract commission on sell
        
        # Record trade
        cursor.execute("""
            INSERT INTO trades (id, order_id, symbol, qty, price, side, timestamp, commission)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), order_id, symbol, qty, fill_price, 
              side.value, datetime.now(), commission))
        
        conn.commit()
        conn.close()
        
        return {
            'id': order_id,
            'symbol': symbol,
            'qty': qty,
            'side': side.value,
            'order_type': OrderType.MARKET.value,
            'status': OrderStatus.FILLED.value,
            'filled_qty': qty,
            'filled_avg_price': fill_price,
            'commission': commission
        }
    
    def place_limit_order(self, 
                         symbol: str, 
                         qty: float, 
                         side: OrderSide,
                         limit_price: float,
                         time_in_force: TimeInForce = TimeInForce.DAY) -> Dict[str, Any]:
        """Place a simulated limit order"""
        order_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO orders (id, symbol, qty, side, order_type, status, 
                              limit_price, time_in_force, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, symbol, qty, side.value, OrderType.LIMIT.value, 
              OrderStatus.PENDING.value, limit_price, time_in_force.value, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Simulate order fill check
        self._check_pending_orders()
        
        return {
            'id': order_id,
            'symbol': symbol,
            'qty': qty,
            'side': side.value,
            'order_type': OrderType.LIMIT.value,
            'status': OrderStatus.PENDING.value,
            'limit_price': limit_price
        }
    
    def _update_position(self, symbol: str, qty_change: float, price: float):
        """Update or create position"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if position exists
        cursor.execute("SELECT id, qty, cost_basis FROM positions WHERE symbol = ?", (symbol,))
        existing = cursor.fetchone()
        
        if existing:
            position_id, current_qty, current_cost = existing
            new_qty = current_qty + qty_change
            
            if new_qty > 0:
                # Update position
                if qty_change > 0:  # Buying
                    new_cost_basis = current_cost + (qty_change * price)
                else:  # Selling
                    new_cost_basis = current_cost * (new_qty / current_qty)
                
                market_value = new_qty * price
                unrealized_pl = market_value - new_cost_basis
                unrealized_plpc = (unrealized_pl / new_cost_basis) * 100 if new_cost_basis > 0 else 0
                
                cursor.execute("""
                    UPDATE positions 
                    SET qty = ?, cost_basis = ?, market_value = ?, 
                        unrealized_pl = ?, unrealized_plpc = ?, 
                        current_price = ?, updated_at = ?
                    WHERE id = ?
                """, (new_qty, new_cost_basis, market_value, unrealized_pl, 
                      unrealized_plpc, price, datetime.now(), position_id))
            else:
                # Close position
                cursor.execute("DELETE FROM positions WHERE id = ?", (position_id,))
        
        elif qty_change > 0:
            # Create new position
            position_id = str(uuid.uuid4())
            cost_basis = qty_change * price
            market_value = cost_basis
            
            cursor.execute("""
                INSERT INTO positions (id, symbol, qty, side, market_value, cost_basis,
                                     unrealized_pl, unrealized_plpc, current_price, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
            """, (position_id, symbol, qty_change, 'long', market_value, 
                  cost_basis, price, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _update_cash(self, amount: float):
        """Update account cash balance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE account 
            SET cash = cash + ?, 
                equity = equity + ?,
                buying_power = buying_power + ?,
                portfolio_value = portfolio_value + ?,
                updated_at = ?
        """, (amount, amount, amount, amount, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def _check_pending_orders(self):
        """Check and fill pending limit orders based on current prices"""
        try:
            from .local_data_client import LocalDataClient
        except ImportError:
            from local_data_client import LocalDataClient
        data_client = LocalDataClient()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pending orders
        cursor.execute("""
            SELECT id, symbol, qty, side, limit_price
            FROM orders
            WHERE status = ?
        """, (OrderStatus.PENDING.value,))
        
        pending_orders = cursor.fetchall()
        
        for order_id, symbol, qty, side, limit_price in pending_orders:
            quotes = data_client.get_latest_quotes([symbol])
            
            if symbol in quotes:
                current_bid = quotes[symbol]['bid']
                current_ask = quotes[symbol]['ask']
                
                # Check if order should be filled
                should_fill = False
                fill_price = limit_price
                
                if side == OrderSide.BUY.value and current_ask <= limit_price:
                    should_fill = True
                    fill_price = min(current_ask, limit_price)
                elif side == OrderSide.SELL.value and current_bid >= limit_price:
                    should_fill = True
                    fill_price = max(current_bid, limit_price)
                
                if should_fill:
                    # Fill the order
                    commission = qty * fill_price * self.config.COMMISSION_RATE
                    
                    cursor.execute("""
                        UPDATE orders
                        SET status = ?, filled_at = ?, filled_qty = ?, filled_avg_price = ?
                        WHERE id = ?
                    """, (OrderStatus.FILLED.value, datetime.now(), qty, fill_price, order_id))
                    
                    # Update position and cash
                    self._update_position(symbol, qty if side == OrderSide.BUY.value else -qty, fill_price)
                    
                    total_cost = qty * fill_price + commission
                    if side == OrderSide.BUY.value:
                        self._update_cash(-total_cost)
                    else:
                        self._update_cash(total_cost - 2 * commission)
                    
                    # Record trade
                    cursor.execute("""
                        INSERT INTO trades (id, order_id, symbol, qty, price, side, timestamp, commission)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), order_id, symbol, qty, fill_price, 
                          side, datetime.now(), commission))
        
        conn.commit()
        conn.close()
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE orders
            SET status = ?
            WHERE id = ? AND status IN (?, ?)
        """, (OrderStatus.CANCELLED.value, order_id, 
              OrderStatus.PENDING.value, OrderStatus.NEW.value))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """Get orders with optional status filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT id, symbol, qty, side, order_type, status, 
                       created_at, filled_at, filled_qty, filled_avg_price
                FROM orders
                WHERE status = ?
                ORDER BY created_at DESC
            """, (status,))
        else:
            cursor.execute("""
                SELECT id, symbol, qty, side, order_type, status, 
                       created_at, filled_at, filled_qty, filled_avg_price
                FROM orders
                ORDER BY created_at DESC
            """)
        
        orders = []
        for row in cursor.fetchall():
            orders.append({
                'id': row[0],
                'symbol': row[1],
                'qty': row[2],
                'side': row[3],
                'order_type': row[4],
                'status': row[5],
                'created_at': row[6],
                'filled_at': row[7],
                'filled_qty': row[8] or 0,
                'filled_avg_price': row[9] or 0
            })
        
        conn.close()
        return orders
    
    def get_portfolio_history(self, days: int = 30) -> pd.DataFrame:
        """Get portfolio value history"""
        # This would typically track portfolio value over time
        # For now, return simulated data
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        account = self.get_account()
        
        base_value = account.get('portfolio_value', self.config.INITIAL_CAPITAL)
        
        # Simulate portfolio growth/decline
        returns = np.random.normal(0.001, 0.02, days)
        values = base_value * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'date': dates,
            'portfolio_value': values,
            'daily_return': np.concatenate([[0], np.diff(values) / values[:-1]])
        })
        df.set_index('date', inplace=True)
        
        return df