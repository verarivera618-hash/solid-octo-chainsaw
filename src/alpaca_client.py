"""
Alpaca Trading API client for data streaming and order execution

Local-first: gracefully degrades to local simulation when Alpaca SDK/keys are unavailable.
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable

try:
    from alpaca.data import StockHistoricalDataClient, StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from alpaca.data.live import StockDataStream
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, BracketOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderClass
    from alpaca.trading.models import Position, Order
    _ALPACA_AVAILABLE = True
except Exception:  # pragma: no cover - only hit in environments without alpaca-py
    _ALPACA_AVAILABLE = False

    class TimeFrame:  # minimal stub
        Day = '1D'

    class TimeFrameUnit:
        Day = 'day'

    class StockHistoricalDataClient:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def get_stock_bars(self, request):
            return {}

    class StockBarsRequest:  # type: ignore
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class StockDataStream:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        async def subscribe_bars(self, symbols):
            return None

        async def subscribe_quotes(self, symbols):
            return None

        async def _run_forever(self):
            return None

        async def close(self):
            return None

        def on_bar(self, func):
            return func

        def on_quote(self, func):
            return func

    class TradingClient:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def get_account(self):
            class _Acct:
                id = 'local'
                equity = 100000.0
                cash = 100000.0
                buying_power = 200000.0
                portfolio_value = 100000.0
                day_trade_count = 0
                pattern_day_trader = False
            return _Acct()

        def get_all_positions(self):
            return []

        def submit_order(self, *args, **kwargs):
            class _Order:
                id = 'local-order'
                symbol = kwargs.get('symbol', 'SPY') if isinstance(kwargs, dict) else 'SPY'
                qty = kwargs.get('qty', 1.0) if isinstance(kwargs, dict) else 1.0
                side = 'buy'
            return _Order()

        def cancel_order_by_id(self, order_id):
            return None

        def get_all_orders(self, status=None):
            return []

    class MarketOrderRequest:  # type: ignore
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class LimitOrderRequest:  # type: ignore
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class BracketOrderRequest:  # type: ignore
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class Position:  # type: ignore
        pass

    class Order:  # type: ignore
        pass

    class OrderSide:  # type: ignore
        BUY = 'buy'
        SELL = 'sell'

    class TimeInForce:  # type: ignore
        DAY = 'day'

    class OrderClass:  # type: ignore
        BRACKET = 'bracket'

from .config import Config

class AlpacaDataClient:
    """Client for Alpaca market data operations"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or Config.ALPACA_API_KEY
        self.secret_key = secret_key or Config.ALPACA_SECRET_KEY
        self.data_client = None
        if _ALPACA_AVAILABLE and self.api_key and self.secret_key:
            self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)
    
    def get_historical_bars(self, 
                          symbols: List[str], 
                          timeframe: TimeFrame = TimeFrame.Day,
                          start_date: datetime = None,
                          end_date: datetime = None,
                          limit: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        Get historical bar data for symbols
        
        Args:
            symbols: List of stock symbols
            timeframe: TimeFrame for data
            start_date: Start date for data
            end_date: End date for data
            limit: Maximum number of bars to return
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # If real client not available, generate local synthetic data
        if not self.data_client:
            rng = np.random.default_rng(42)
            dataframes: Dict[str, pd.DataFrame] = {}
            periods = max(2, min(1000, limit))
            date_index = pd.date_range(start=start_date, end=end_date, periods=periods)
            for symbol in symbols:
                base = 100.0 + rng.normal(0, 1)
                returns = rng.normal(0.0005, 0.02, size=len(date_index))
                prices = base * np.cumprod(1 + returns)
                highs = prices * (1 + np.abs(rng.normal(0.001, 0.01, size=len(date_index))))
                lows = prices * (1 - np.abs(rng.normal(0.001, 0.01, size=len(date_index))))
                opens = prices * (1 + rng.normal(0, 0.005, size=len(date_index)))
                volumes = rng.integers(5e5, 2e6, size=len(date_index))
                df = pd.DataFrame({
                    'open': opens,
                    'high': np.maximum.reduce([highs, opens, prices]),
                    'low': np.minimum.reduce([lows, opens, prices]),
                    'close': prices,
                    'volume': volumes,
                    'trade_count': rng.integers(500, 5000, size=len(date_index)),
                    'vwap': prices
                }, index=date_index)
                dataframes[symbol] = df
            return dataframes

        request_params = StockBarsRequest(
            symbol_or_symbols=symbols,
            timeframe=timeframe,
            start=start_date,
            end=end_date,
            limit=limit
        )

        try:
            bars = self.data_client.get_stock_bars(request_params)

            # Convert to pandas DataFrames
            dataframes = {}
            for symbol, bar_data in bars.items():
                df = pd.DataFrame([{
                    'timestamp': bar.timestamp,
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume,
                    'trade_count': bar.trade_count,
                    'vwap': bar.vwap
                } for bar in bar_data])
                df.set_index('timestamp', inplace=True)
                dataframes[symbol] = df

            return dataframes
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {}
    
    def get_latest_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get latest quotes for symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary with latest quote data
        """
        try:
            quotes = self.data_client.get_latest_quotes(symbols)
            quote_data = {}
            for symbol, quote in quotes.items():
                quote_data[symbol] = {
                    'bid': quote.bid_price,
                    'ask': quote.ask_price,
                    'bid_size': quote.bid_size,
                    'ask_size': quote.ask_size,
                    'timestamp': quote.timestamp
                }
            return quote_data
        except Exception as e:
            print(f"Error fetching latest quotes: {e}")
            return {}
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for a DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with additional technical indicators
        """
        df = df.copy()
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df['atr'] = true_range.rolling(window=14).mean()
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price change indicators
        df['price_change'] = df['close'].pct_change()
        df['price_change_5d'] = df['close'].pct_change(5)
        df['price_change_20d'] = df['close'].pct_change(20)
        
        return df

class AlpacaTradingClient:
    """Client for Alpaca trading operations"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, paper: bool = True):
        self.api_key = api_key or Config.ALPACA_API_KEY
        self.secret_key = secret_key or Config.ALPACA_SECRET_KEY
        self.paper = paper
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=paper)
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            account = self.trading_client.get_account()
            return {
                'account_id': account.id,
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value),
                'day_trade_count': account.day_trade_count,
                'pattern_day_trader': account.pattern_day_trader
            }
        except Exception as e:
            print(f"Error fetching account info: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        try:
            positions = self.trading_client.get_all_positions()
            position_data = []
            for pos in positions:
                position_data.append({
                    'symbol': pos.symbol,
                    'qty': float(pos.qty),
                    'side': pos.side,
                    'market_value': float(pos.market_value),
                    'cost_basis': float(pos.cost_basis),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc),
                    'current_price': float(pos.current_price)
                })
            return position_data
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
    
    def place_market_order(self, 
                          symbol: str, 
                          qty: float, 
                          side: OrderSide,
                          time_in_force: TimeInForce = TimeInForce.DAY) -> Optional[Order]:
        """Place a market order"""
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=time_in_force
            )
            order = self.trading_client.submit_order(order_data)
            return order
        except Exception as e:
            print(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(self, 
                         symbol: str, 
                         qty: float, 
                         side: OrderSide,
                         limit_price: float,
                         time_in_force: TimeInForce = TimeInForce.DAY) -> Optional[Order]:
        """Place a limit order"""
        try:
            order_data = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                limit_price=limit_price,
                time_in_force=time_in_force
            )
            order = self.trading_client.submit_order(order_data)
            return order
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None
    
    def place_bracket_order(self, 
                           symbol: str, 
                           qty: float, 
                           side: OrderSide,
                           take_profit_price: float,
                           stop_loss_price: float) -> Optional[Order]:
        """Place a bracket order with take profit and stop loss"""
        try:
            order_data = BracketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                take_profit_limit_price=take_profit_price,
                stop_loss_stop_price=stop_loss_price,
                time_in_force=TimeInForce.DAY
            )
            order = self.trading_client.submit_order(order_data)
            return order
        except Exception as e:
            print(f"Error placing bracket order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.trading_client.cancel_order_by_id(order_id)
            return True
        except Exception as e:
            print(f"Error canceling order: {e}")
            return False
    
    def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """Get orders with optional status filter"""
        try:
            orders = self.trading_client.get_all_orders(status=status)
            order_data = []
            for order in orders:
                order_data.append({
                    'id': order.id,
                    'symbol': order.symbol,
                    'qty': float(order.qty),
                    'side': order.side,
                    'order_type': order.order_type,
                    'status': order.status,
                    'created_at': order.created_at,
                    'filled_at': order.filled_at,
                    'filled_qty': float(order.filled_qty) if order.filled_qty else 0,
                    'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else 0
                })
            return order_data
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []

class AlpacaStreamClient:
    """Client for real-time data streaming"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        self.api_key = api_key or Config.ALPACA_API_KEY
        self.secret_key = secret_key or Config.ALPACA_SECRET_KEY
        self.data_stream = StockDataStream(self.api_key, self.secret_key)
        self.subscriptions = set()
        self.callbacks = {}
    
    async def subscribe_to_bars(self, symbols: List[str], callback: Callable):
        """
        Subscribe to real-time bar data
        
        Args:
            symbols: List of symbols to subscribe to
            callback: Function to call when new data arrives
        """
        for symbol in symbols:
            self.subscriptions.add(symbol)
            self.callbacks[symbol] = callback
        
        @self.data_stream.on_bar
        async def on_bar(bar):
            if bar.symbol in self.callbacks:
                await self.callbacks[bar.symbol](bar)
        
        await self.data_stream.subscribe_bars(symbols)
    
    async def subscribe_to_quotes(self, symbols: List[str], callback: Callable):
        """
        Subscribe to real-time quote data
        
        Args:
            symbols: List of symbols to subscribe to
            callback: Function to call when new data arrives
        """
        for symbol in symbols:
            self.subscriptions.add(symbol)
            self.callbacks[f"{symbol}_quote"] = callback
        
        @self.data_stream.on_quote
        async def on_quote(quote):
            if f"{quote.symbol}_quote" in self.callbacks:
                await self.callbacks[f"{quote.symbol}_quote"](quote)
        
        await self.data_stream.subscribe_quotes(symbols)
    
    async def start_streaming(self):
        """Start the data stream"""
        await self.data_stream._run_forever()
    
    async def stop_streaming(self):
        """Stop the data stream"""
        await self.data_stream.close()
    
    def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols"""
        for symbol in symbols:
            if symbol in self.subscriptions:
                self.subscriptions.remove(symbol)
            if symbol in self.callbacks:
                del self.callbacks[symbol]
            if f"{symbol}_quote" in self.callbacks:
                del self.callbacks[f"{symbol}_quote"]