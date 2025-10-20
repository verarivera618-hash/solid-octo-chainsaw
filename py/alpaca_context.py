from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Dict, List

from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame


class AlpacaContext:
    def __init__(self, api_key: str | None = None, api_secret: str | None = None):
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.api_secret = api_secret or os.getenv("ALPACA_SECRET_KEY")
        if not self.api_key or not self.api_secret:
            raise ValueError("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set")
        self.client = StockHistoricalDataClient(self.api_key, self.api_secret)

    def fetch_recent_bars(self, tickers: List[str], days: int = 30):
        request_params = StockBarsRequest(
            symbol_or_symbols=tickers,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=days),
        )
        return self.client.get_stock_bars(request_params)

    @staticmethod
    def summarize_bars(bars) -> str:
        summary_lines: List[str] = []
        for symbol, symbol_bars in bars.items():
            latest = symbol_bars[-1]
            oldest = symbol_bars[0]
            change_pct = ((latest.close - oldest.close) / oldest.close) * 100
            summary_lines.append(f"{symbol}: ${latest.close:.2f} ({change_pct:+.2f}% over period)")
        return "\n".join(summary_lines)
