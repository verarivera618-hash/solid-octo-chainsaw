from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Awaitable, Callable, Dict, Iterable, List, Optional

import pandas as pd
from alpaca.data.live import StockDataStream
from alpaca.data import StockHistoricalDataClient, StockBarsRequest
from alpaca.data.timeframe import TimeFrame


logger = logging.getLogger(__name__)


@dataclass
class HistoricalDataParams:
    tickers: List[str]
    days: int = 30
    timeframe: TimeFrame = TimeFrame.Day


class AlpacaDataHandler:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.stream = StockDataStream(api_key, secret_key)
        self.historical_client = StockHistoricalDataClient(api_key, secret_key)

    async def start_stream(self, tickers: Iterable[str], on_bar: Callable[[object], Awaitable[None]]):
        async def _on_bar(bar):
            try:
                await on_bar(bar)
            except Exception:  # noqa: BLE001
                logger.exception("Error in on_bar handler")

        for symbol in tickers:
            self.stream.subscribe_bars(_on_bar, symbol)
        await self.stream.run()

    def get_historical_bars(self, params: HistoricalDataParams) -> Dict[str, pd.DataFrame]:
        request = StockBarsRequest(
            symbol_or_symbols=params.tickers,
            timeframe=params.timeframe,
            start=datetime.utcnow() - timedelta(days=params.days),
        )
        bars = self.historical_client.get_stock_bars(request)
        result: Dict[str, pd.DataFrame] = {}
        for symbol, bar_list in bars.items():
            df = pd.DataFrame(
                [
                    {
                        "timestamp": b.timestamp,
                        "open": b.open,
                        "high": b.high,
                        "low": b.low,
                        "close": b.close,
                        "volume": b.volume,
                    }
                    for b in bar_list
                ]
            ).set_index("timestamp")
            result[symbol] = df
        return result
