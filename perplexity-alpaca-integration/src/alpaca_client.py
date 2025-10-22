"""
Alpaca API client for market data and trading operations.
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
import pandas as pd
from loguru import logger

# Alpaca imports
from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest, StockTradesRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, StopOrderRequest,
    GetOrdersRequest, ClosePositionRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType, OrderStatus
from alpaca.common.exceptions import APIError

from config import get_settings

settings = get_settings()

@dataclass
class MarketData:
    """Structure for market data."""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None

@dataclass
class Quote:
    """Structure for quote data."""
    symbol: str
    timestamp: datetime
    bid_price: float
    ask_price: float
    bid_size: int
    ask_size: int

@dataclass
class Trade:
    """Structure for trade data."""
    symbol: str
    timestamp: datetime
    price: float
    size: int

class AlpacaDataClient:
    """Client for Alpaca market data operations."""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.api_key = api_key or settings.alpaca_api_key
        self.secret_key = secret_key or settings.alpaca_secret_key
        
        # Initialize clients
        self.historical_client = StockHistoricalDataClient(self.api_key, self.secret_key)
        self.stream_client = StockDataStream(self.api_key, self.secret_key)
        
        # Data handlers
        self.bar_handlers: List[Callable] = []
        self.quote_handlers: List[Callable] = []
        self.trade_handlers: List[Callable] = []
        
        # Rate limiting
        self.last_request_time = 0
        self.rate_limit = settings.alpaca_rate_limit
        
        # Data cache
        self.latest_bars: Dict[str, MarketData] = {}
        self.latest_quotes: Dict[str, Quote] = {}
        
        logger.info("Alpaca data client initialized")
    
    def _rate_limit_check(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit  # seconds between requests
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_historical_bars(
        self,
        symbols: List[str],
        timeframe: TimeFrame,
        start: datetime,
        end: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Get historical bar data for symbols.
        
        Args:
            symbols: List of stock symbols
            timeframe: Bar timeframe (TimeFrame.Day, TimeFrame.Hour, etc.)
            start: Start datetime
            end: End datetime (optional)
            limit: Maximum number of bars (optional)
        
        Returns:
            Dictionary mapping symbols to DataFrames with OHLCV data
        """
        self._rate_limit_check()
        
        try:
            request = StockBarsRequest(
                symbol_or_symbols=symbols,
                timeframe=timeframe,
                start=start,
                end=end,
                limit=limit
            )
            
            bars = self.historical_client.get_stock_bars(request)
            
            # Convert to DataFrames
            result = {}
            for symbol in symbols:
                if symbol in bars:
                    symbol_bars = bars[symbol]
                    df_data = []
                    
                    for bar in symbol_bars:
                        df_data.append({
                            'timestamp': bar.timestamp,
                            'open': bar.open,
                            'high': bar.high,
                            'low': bar.low,
                            'close': bar.close,
                            'volume': bar.volume,
                            'vwap': bar.vwap
                        })
                    
                    df = pd.DataFrame(df_data)
                    df.set_index('timestamp', inplace=True)
                    result[symbol] = df
                    
                    logger.debug(f"Retrieved {len(df)} bars for {symbol}")
            
            return result
        
        except APIError as e:
            logger.error(f"Alpaca API error getting historical bars: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting historical bars: {e}")
            raise
    
    def get_latest_quotes(self, symbols: List[str]) -> Dict[str, Quote]:
        """
        Get latest quotes for symbols.
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to Quote objects
        """
        self._rate_limit_check()
        
        try:
            request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
            quotes = self.historical_client.get_stock_latest_quote(request)
            
            result = {}
            for symbol, quote_data in quotes.items():
                quote = Quote(
                    symbol=symbol,
                    timestamp=quote_data.timestamp,
                    bid_price=quote_data.bid_price,
                    ask_price=quote_data.ask_price,
                    bid_size=quote_data.bid_size,
                    ask_size=quote_data.ask_size
                )
                result[symbol] = quote
                self.latest_quotes[symbol] = quote
            
            return result
        
        except APIError as e:
            logger.error(f"Alpaca API error getting latest quotes: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting latest quotes: {e}")
            raise
    
    def get_latest_bars(self, symbols: List[str]) -> Dict[str, MarketData]:
        """
        Get latest bar data for symbols.
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary mapping symbols to MarketData objects
        """
        # For latest bars, we'll get the most recent daily bar
        end_time = datetime.now()
        start_time = end_time - timedelta(days=5)  # Get last 5 days to ensure we have data
        
        bars_data = self.get_historical_bars(
            symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start_time,
            end=end_time,
            limit=1
        )
        
        result = {}
        for symbol, df in bars_data.items():
            if not df.empty:
                latest_bar = df.iloc[-1]
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=latest_bar.name,
                    open=latest_bar['open'],
                    high=latest_bar['high'],
                    low=latest_bar['low'],
                    close=latest_bar['close'],
                    volume=latest_bar['volume'],
                    vwap=latest_bar.get('vwap')
                )
                result[symbol] = market_data
                self.latest_bars[symbol] = market_data
        
        return result
    
    async def start_streaming(self, symbols: List[str]):
        """
        Start real-time data streaming for symbols.
        
        Args:
            symbols: List of stock symbols to stream
        """
        try:
            # Register handlers
            self.stream_client.subscribe_bars(self._handle_bar, *symbols)
            self.stream_client.subscribe_quotes(self._handle_quote, *symbols)
            self.stream_client.subscribe_trades(self._handle_trade, *symbols)
            
            logger.info(f"Starting data stream for {symbols}")
            await self.stream_client.run()
        
        except Exception as e:
            logger.error(f"Error in data streaming: {e}")
            raise
    
    async def _handle_bar(self, bar):
        """Handle incoming bar data."""
        market_data = MarketData(
            symbol=bar.symbol,
            timestamp=bar.timestamp,
            open=bar.open,
            high=bar.high,
            low=bar.low,
            close=bar.close,
            volume=bar.volume,
            vwap=bar.vwap
        )
        
        # Update cache
        self.latest_bars[bar.symbol] = market_data
        
        # Call registered handlers
        for handler in self.bar_handlers:
            try:
                await handler(market_data)
            except Exception as e:
                logger.error(f"Error in bar handler: {e}")
    
    async def _handle_quote(self, quote):
        """Handle incoming quote data."""
        quote_data = Quote(
            symbol=quote.symbol,
            timestamp=quote.timestamp,
            bid_price=quote.bid_price,
            ask_price=quote.ask_price,
            bid_size=quote.bid_size,
            ask_size=quote.ask_size
        )
        
        # Update cache
        self.latest_quotes[quote.symbol] = quote_data
        
        # Call registered handlers
        for handler in self.quote_handlers:
            try:
                await handler(quote_data)
            except Exception as e:
                logger.error(f"Error in quote handler: {e}")
    
    async def _handle_trade(self, trade):
        """Handle incoming trade data."""
        trade_data = Trade(
            symbol=trade.symbol,
            timestamp=trade.timestamp,
            price=trade.price,
            size=trade.size
        )
        
        # Call registered handlers
        for handler in self.trade_handlers:
            try:
                await handler(trade_data)
            except Exception as e:
                logger.error(f"Error in trade handler: {e}")
    
    def add_bar_handler(self, handler: Callable):
        """Add handler for bar data."""
        self.bar_handlers.append(handler)
    
    def add_quote_handler(self, handler: Callable):
        """Add handler for quote data."""
        self.quote_handlers.append(handler)
    
    def add_trade_handler(self, handler: Callable):
        """Add handler for trade data."""
        self.trade_handlers.append(handler)

class AlpacaTradingClient:
    """Client for Alpaca trading operations."""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None, paper: bool = True):
        self.api_key = api_key or settings.alpaca_api_key
        self.secret_key = secret_key or settings.alpaca_secret_key
        self.paper = paper
        
        # Initialize trading client
        self.client = TradingClient(self.api_key, self.secret_key, paper=paper)
        
        # Rate limiting
        self.last_request_time = 0
        self.rate_limit = settings.alpaca_rate_limit
        
        logger.info(f"Alpaca trading client initialized (paper={paper})")
    
    def _rate_limit_check(self):
        """Ensure we don't exceed rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 60 / self.rate_limit
        
        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information."""
        self._rate_limit_check()
        
        try:
            account = self.client.get_account()
            return {
                'id': account.id,
                'account_number': account.account_number,
                'status': account.status,
                'currency': account.currency,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'multiplier': float(account.multiplier),
                'initial_margin': float(account.initial_margin),
                'maintenance_margin': float(account.maintenance_margin),
                'daytrade_count': account.daytrade_count,
                'daytrading_buying_power': float(account.daytrading_buying_power)
            }
        except APIError as e:
            logger.error(f"Alpaca API error getting account: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting account: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions."""
        self._rate_limit_check()
        
        try:
            positions = self.client.get_all_positions()
            
            result = []
            for position in positions:
                result.append({
                    'symbol': position.symbol,
                    'qty': float(position.qty),
                    'side': position.side,
                    'market_value': float(position.market_value),
                    'cost_basis': float(position.cost_basis),
                    'unrealized_pl': float(position.unrealized_pl),
                    'unrealized_plpc': float(position.unrealized_plpc),
                    'current_price': float(position.current_price),
                    'lastday_price': float(position.lastday_price),
                    'change_today': float(position.change_today)
                })
            
            return result
        
        except APIError as e:
            logger.error(f"Alpaca API error getting positions: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise
    
    def submit_market_order(
        self,
        symbol: str,
        qty: float,
        side: OrderSide,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Dict[str, Any]:
        """
        Submit a market order.
        
        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: OrderSide.BUY or OrderSide.SELL
            time_in_force: Order time in force
        
        Returns:
            Order information dictionary
        """
        self._rate_limit_check()
        
        try:
            order_request = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=time_in_force
            )
            
            order = self.client.submit_order(order_request)
            
            logger.info(f"Submitted market order: {side.value} {qty} {symbol}")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'time_in_force': order.time_in_force,
                'status': order.status,
                'created_at': order.created_at,
                'filled_qty': float(order.filled_qty or 0),
                'filled_avg_price': float(order.filled_avg_price or 0)
            }
        
        except APIError as e:
            logger.error(f"Alpaca API error submitting market order: {e}")
            raise
        except Exception as e:
            logger.error(f"Error submitting market order: {e}")
            raise
    
    def submit_limit_order(
        self,
        symbol: str,
        qty: float,
        side: OrderSide,
        limit_price: float,
        time_in_force: TimeInForce = TimeInForce.DAY
    ) -> Dict[str, Any]:
        """
        Submit a limit order.
        
        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: OrderSide.BUY or OrderSide.SELL
            limit_price: Limit price
            time_in_force: Order time in force
        
        Returns:
            Order information dictionary
        """
        self._rate_limit_check()
        
        try:
            order_request = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                limit_price=limit_price,
                time_in_force=time_in_force
            )
            
            order = self.client.submit_order(order_request)
            
            logger.info(f"Submitted limit order: {side.value} {qty} {symbol} @ ${limit_price}")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'limit_price': float(order.limit_price),
                'time_in_force': order.time_in_force,
                'status': order.status,
                'created_at': order.created_at,
                'filled_qty': float(order.filled_qty or 0),
                'filled_avg_price': float(order.filled_avg_price or 0)
            }
        
        except APIError as e:
            logger.error(f"Alpaca API error submitting limit order: {e}")
            raise
        except Exception as e:
            logger.error(f"Error submitting limit order: {e}")
            raise
    
    def get_orders(self, status: Optional[OrderStatus] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get orders with optional status filter.
        
        Args:
            status: Optional order status filter
            limit: Maximum number of orders to return
        
        Returns:
            List of order dictionaries
        """
        self._rate_limit_check()
        
        try:
            request = GetOrdersRequest(
                status=status,
                limit=limit
            )
            
            orders = self.client.get_orders(request)
            
            result = []
            for order in orders:
                result.append({
                    'id': order.id,
                    'symbol': order.symbol,
                    'qty': float(order.qty),
                    'side': order.side,
                    'order_type': order.order_type,
                    'time_in_force': order.time_in_force,
                    'status': order.status,
                    'created_at': order.created_at,
                    'filled_qty': float(order.filled_qty or 0),
                    'filled_avg_price': float(order.filled_avg_price or 0),
                    'limit_price': float(order.limit_price) if order.limit_price else None,
                    'stop_price': float(order.stop_price) if order.stop_price else None
                })
            
            return result
        
        except APIError as e:
            logger.error(f"Alpaca API error getting orders: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order by ID.
        
        Args:
            order_id: Order ID to cancel
        
        Returns:
            True if successful
        """
        self._rate_limit_check()
        
        try:
            self.client.cancel_order_by_id(order_id)
            logger.info(f"Cancelled order {order_id}")
            return True
        
        except APIError as e:
            logger.error(f"Alpaca API error cancelling order: {e}")
            raise
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise
    
    def close_position(self, symbol: str, qty: Optional[float] = None) -> Dict[str, Any]:
        """
        Close a position (or part of it).
        
        Args:
            symbol: Stock symbol
            qty: Quantity to close (None for full position)
        
        Returns:
            Order information dictionary
        """
        self._rate_limit_check()
        
        try:
            request = ClosePositionRequest(qty=qty) if qty else ClosePositionRequest()
            order = self.client.close_position(symbol, request)
            
            logger.info(f"Closed position: {symbol} qty={qty or 'full'}")
            
            return {
                'id': order.id,
                'symbol': order.symbol,
                'qty': float(order.qty),
                'side': order.side,
                'order_type': order.order_type,
                'status': order.status,
                'created_at': order.created_at
            }
        
        except APIError as e:
            logger.error(f"Alpaca API error closing position: {e}")
            raise
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            raise

# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_data_client():
        """Test the data client functionality."""
        data_client = AlpacaDataClient()
        
        # Test historical data
        symbols = ["AAPL", "MSFT"]
        start_date = datetime.now() - timedelta(days=30)
        
        bars = data_client.get_historical_bars(
            symbols=symbols,
            timeframe=TimeFrame.Day,
            start=start_date
        )
        
        for symbol, df in bars.items():
            print(f"{symbol}: {len(df)} bars")
            print(df.head())
        
        # Test latest quotes
        quotes = data_client.get_latest_quotes(symbols)
        for symbol, quote in quotes.items():
            print(f"{symbol}: Bid ${quote.bid_price}, Ask ${quote.ask_price}")
    
    def test_trading_client():
        """Test the trading client functionality."""
        trading_client = AlpacaTradingClient(paper=True)
        
        # Test account info
        account = trading_client.get_account()
        print(f"Account: ${account['portfolio_value']} portfolio value")
        
        # Test positions
        positions = trading_client.get_positions()
        print(f"Positions: {len(positions)}")
        
        # Test orders
        orders = trading_client.get_orders()
        print(f"Recent orders: {len(orders)}")
    
    # Run tests
    asyncio.run(test_data_client())
    test_trading_client()