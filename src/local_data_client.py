"""
Local data client - Replaces Alpaca data client with local data sources
No external API calls required
"""
import pandas as pd
import numpy as np
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import os
from pathlib import Path
try:
    from .config_local import LocalConfig
except ImportError:
    from config_local import LocalConfig

class LocalDataClient:
    """Client for local market data operations - no external dependencies"""
    
    def __init__(self):
        self.config = LocalConfig
        self.config.ensure_directories()
        self.data_path = Path(self.config.DATA_PATH)
        self.db_path = self.config.DB_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize local SQLite database for storing market data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for local data storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(symbol, timestamp)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                bid REAL,
                ask REAL,
                bid_size INTEGER,
                ask_size INTEGER,
                UNIQUE(symbol, timestamp)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_sample_data(self, symbols: List[str], days: int = 365) -> Dict[str, pd.DataFrame]:
        """
        Generate sample market data for testing
        Uses realistic price movements and volumes
        """
        data = {}
        
        for symbol in symbols:
            # Generate realistic price data
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            
            # Base price and volatility
            base_price = np.random.uniform(50, 500)
            volatility = np.random.uniform(0.01, 0.03)
            
            # Generate price movements
            returns = np.random.normal(0.0005, volatility, days)
            prices = base_price * np.exp(np.cumsum(returns))
            
            # Generate OHLCV data
            df = pd.DataFrame(index=dates)
            df['close'] = prices
            df['open'] = df['close'].shift(1).fillna(base_price)
            df['high'] = df[['open', 'close']].max(axis=1) * np.random.uniform(1.001, 1.01, days)
            df['low'] = df[['open', 'close']].min(axis=1) * np.random.uniform(0.99, 0.999, days)
            df['volume'] = np.random.randint(1000000, 10000000, days)
            
            data[symbol] = df
            
            # Store in database
            self._store_data_to_db(symbol, df)
        
        return data
    
    def _store_data_to_db(self, symbol: str, df: pd.DataFrame):
        """Store data in local SQLite database"""
        conn = sqlite3.connect(self.db_path)
        
        # Prepare data for insertion
        df_to_store = df.copy()
        df_to_store['symbol'] = symbol
        df_to_store['timestamp'] = df_to_store.index
        
        # Store in database
        df_to_store.to_sql('stock_data', conn, if_exists='append', index=False)
        conn.close()
    
    def get_historical_bars(self, 
                          symbols: List[str], 
                          timeframe: str = "1D",
                          start_date: datetime = None,
                          end_date: datetime = None,
                          limit: int = 1000) -> Dict[str, pd.DataFrame]:
        """
        Get historical bar data for symbols from local sources
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        data = {}
        conn = sqlite3.connect(self.db_path)
        
        for symbol in symbols:
            query = """
                SELECT timestamp, open, high, low, close, volume
                FROM stock_data
                WHERE symbol = ? AND timestamp BETWEEN ? AND ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(
                query, 
                conn, 
                params=(symbol, start_date, end_date, limit),
                parse_dates=['timestamp'],
                index_col='timestamp'
            )
            
            if df.empty:
                # Generate sample data if not exists
                sample_data = self.generate_sample_data([symbol])
                df = sample_data[symbol]
                df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            data[symbol] = df
        
        conn.close()
        return data
    
    def get_latest_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Get latest quotes for symbols from local data
        """
        quotes = {}
        
        for symbol in symbols:
            # Get latest price from historical data
            hist_data = self.get_historical_bars([symbol], limit=1)
            
            if symbol in hist_data and not hist_data[symbol].empty:
                latest = hist_data[symbol].iloc[0]
                spread = latest['close'] * 0.001  # 0.1% spread
                
                quotes[symbol] = {
                    'bid': latest['close'] - spread/2,
                    'ask': latest['close'] + spread/2,
                    'bid_size': np.random.randint(100, 1000) * 100,
                    'ask_size': np.random.randint(100, 1000) * 100,
                    'timestamp': datetime.now()
                }
            else:
                # Generate random quote if no data
                price = np.random.uniform(50, 500)
                spread = price * 0.001
                
                quotes[symbol] = {
                    'bid': price - spread/2,
                    'ask': price + spread/2,
                    'bid_size': np.random.randint(100, 1000) * 100,
                    'ask_size': np.random.randint(100, 1000) * 100,
                    'timestamp': datetime.now()
                }
        
        return quotes
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for a DataFrame
        """
        df = df.copy()
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
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
    
    def load_csv_data(self, filepath: str, symbol: str) -> pd.DataFrame:
        """Load data from CSV file"""
        df = pd.read_csv(filepath, parse_dates=['Date'], index_col='Date')
        
        # Standardize column names
        column_mapping = {
            'date': 'Date',
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Store in database
        self._store_data_to_db(symbol, df)
        
        return df
    
    def load_json_data(self, filepath: str, symbol: str) -> pd.DataFrame:
        """Load data from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # Store in database
        self._store_data_to_db(symbol, df)
        
        return df