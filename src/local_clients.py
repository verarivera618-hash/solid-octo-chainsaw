"""
Local client implementations to replace external API dependencies
"""
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import pandas as pd
from .local_data_provider import LocalFinanceDataProvider, LocalTradingSimulator, extract_content
from .local_config import LocalConfig

class LocalPerplexityClient:
    """Local replacement for Perplexity API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        # API key not needed for local operation
        self.data_provider = LocalFinanceDataProvider()
        self.config = LocalConfig()
    
    def get_sec_filings_analysis(self, tickers: List[str], 
                                search_after_date: str = None) -> Dict[str, Any]:
        """Get SEC filings analysis using local data"""
        # Simulate API latency
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_sec_filings_analysis(tickers, search_after_date)
    
    def get_market_news_sentiment(self, tickers: List[str], 
                                 hours_back: int = 24) -> Dict[str, Any]:
        """Get market news and sentiment analysis using local data"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_market_news_sentiment(tickers, hours_back)
    
    def get_earnings_analysis(self, tickers: List[str]) -> Dict[str, Any]:
        """Get earnings analysis using local data"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_earnings_analysis(tickers)
    
    def get_technical_analysis(self, tickers: List[str], 
                              timeframe: str = "1D") -> Dict[str, Any]:
        """Get technical analysis using local data"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_technical_analysis(tickers, timeframe)
    
    def get_sector_analysis(self, sector: str) -> Dict[str, Any]:
        """Get sector analysis using local data"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_sector_analysis(sector)
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """Extract content from local API response"""
        return extract_content(response)

class LocalAlpacaDataClient:
    """Local replacement for Alpaca data client"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        # API keys not needed for local operation
        self.data_provider = LocalFinanceDataProvider()
        self.config = LocalConfig()
    
    def get_historical_bars(self, 
                          symbols: List[str], 
                          timeframe: str = "1Day",
                          start_date: datetime = None,
                          end_date: datetime = None,
                          limit: int = 1000) -> Dict[str, pd.DataFrame]:
        """Get historical bar data using local data"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_historical_bars(symbols, start_date, end_date, limit)
    
    def get_latest_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """Get latest quotes using local data"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        return self.data_provider.get_latest_quotes(symbols)
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        return self.data_provider.calculate_technical_indicators(df)

class LocalAlpacaTradingClient:
    """Local replacement for Alpaca trading client"""
    
    def __init__(self, api_key: str = None, secret_key: str = None, paper: bool = True):
        # API keys not needed for local operation
        self.simulator = LocalTradingSimulator()
        self.config = LocalConfig()
        self.paper = paper
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        return self.simulator.get_account()
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        return self.simulator.get_positions()
    
    def place_market_order(self, 
                          symbol: str, 
                          qty: float, 
                          side: str,
                          time_in_force: str = "day") -> Optional[Dict[str, Any]]:
        """Place a market order"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        try:
            return self.simulator.place_market_order(symbol, qty, side)
        except Exception as e:
            print(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(self, 
                         symbol: str, 
                         qty: float, 
                         side: str,
                         limit_price: float,
                         time_in_force: str = "day") -> Optional[Dict[str, Any]]:
        """Place a limit order"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        try:
            return self.simulator.place_limit_order(symbol, qty, side, limit_price)
        except Exception as e:
            print(f"Error placing limit order: {e}")
            return None
    
    def place_bracket_order(self, 
                           symbol: str, 
                           qty: float, 
                           side: str,
                           take_profit_price: float,
                           stop_loss_price: float) -> Optional[Dict[str, Any]]:
        """Place a bracket order with take profit and stop loss"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        
        try:
            # Simulate bracket order as market order for simplicity
            return self.simulator.place_market_order(symbol, qty, side)
        except Exception as e:
            print(f"Error placing bracket order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        return self.simulator.cancel_order(order_id)
    
    def get_orders(self, status: str = None) -> List[Dict[str, Any]]:
        """Get orders with optional status filter"""
        time.sleep(self.config.MOCK_LATENCY_MS / 1000)
        return self.simulator.get_orders(status)

class LocalStreamClient:
    """Local replacement for real-time data streaming"""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        # API keys not needed for local operation
        self.data_provider = LocalFinanceDataProvider()
        self.config = LocalConfig()
        self.subscriptions = set()
        self.callbacks = {}
        self.streaming = False
    
    async def subscribe_to_bars(self, symbols: List[str], callback: Callable):
        """Subscribe to real-time bar data simulation"""
        for symbol in symbols:
            self.subscriptions.add(symbol)
            self.callbacks[symbol] = callback
    
    async def subscribe_to_quotes(self, symbols: List[str], callback: Callable):
        """Subscribe to real-time quote data simulation"""
        for symbol in symbols:
            self.subscriptions.add(symbol)
            self.callbacks[f"{symbol}_quote"] = callback
    
    async def start_streaming(self):
        """Start the simulated data stream"""
        self.streaming = True
        
        while self.streaming:
            # Simulate streaming data by generating random updates
            for symbol in self.subscriptions:
                if symbol in self.callbacks:
                    # Generate mock bar data
                    mock_bar = self._generate_mock_bar(symbol)
                    await self.callbacks[symbol](mock_bar)
                
                if f"{symbol}_quote" in self.callbacks:
                    # Generate mock quote data
                    mock_quote = self._generate_mock_quote(symbol)
                    await self.callbacks[f"{symbol}_quote"](mock_quote)
            
            # Wait before next update (simulate real-time frequency)
            await asyncio.sleep(1)  # 1 second intervals
    
    async def stop_streaming(self):
        """Stop the data stream"""
        self.streaming = False
    
    def unsubscribe(self, symbols: List[str]):
        """Unsubscribe from symbols"""
        for symbol in symbols:
            if symbol in self.subscriptions:
                self.subscriptions.remove(symbol)
            if symbol in self.callbacks:
                del self.callbacks[symbol]
            if f"{symbol}_quote" in self.callbacks:
                del self.callbacks[f"{symbol}_quote"]
    
    def _generate_mock_bar(self, symbol: str) -> Dict[str, Any]:
        """Generate mock bar data"""
        import random
        
        base_price = random.uniform(100, 400)
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'open': base_price,
            'high': base_price * random.uniform(1.0, 1.02),
            'low': base_price * random.uniform(0.98, 1.0),
            'close': base_price * random.uniform(0.99, 1.01),
            'volume': random.randint(10000, 100000),
            'trade_count': random.randint(100, 500),
            'vwap': base_price
        }
    
    def _generate_mock_quote(self, symbol: str) -> Dict[str, Any]:
        """Generate mock quote data"""
        import random
        
        base_price = random.uniform(100, 400)
        spread = base_price * 0.001
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now(),
            'bid_price': base_price - spread/2,
            'ask_price': base_price + spread/2,
            'bid_size': random.randint(100, 1000),
            'ask_size': random.randint(100, 1000)
        }

# Compatibility aliases for existing code
PerplexityFinanceClient = LocalPerplexityClient
AlpacaDataClient = LocalAlpacaDataClient
AlpacaTradingClient = LocalAlpacaTradingClient
AlpacaStreamClient = LocalStreamClient