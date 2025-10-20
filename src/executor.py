from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, BracketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

logger = logging.getLogger(__name__)


@dataclass
class OrderResult:
    id: str
    symbol: str
    qty: float
    side: str


class TradingExecutor:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.client = TradingClient(api_key, secret_key, paper=paper)

    def place_market_order(self, symbol: str, qty: float, side: str) -> OrderResult:
        req = MarketOrderRequest(symbol=symbol, qty=qty, side=OrderSide(side), time_in_force=TimeInForce.DAY)
        order = self.client.submit_order(req)
        logger.info("Submitted market order %s %s x%.2f", side, symbol, qty)
        return OrderResult(id=order.id, symbol=order.symbol, qty=float(order.qty), side=order.side.value)

    def place_bracket_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        take_profit_limit_price: float,
        stop_loss_stop_price: float,
        stop_loss_limit_price: Optional[float] = None,
    ) -> OrderResult:
        req = BracketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            time_in_force=TimeInForce.DAY,
            take_profit_limit_price=take_profit_limit_price,
            stop_loss_stop_price=stop_loss_stop_price,
            stop_loss_limit_price=stop_loss_limit_price,
        )
        order = self.client.submit_order(req)
        logger.info("Submitted bracket order %s %s x%.2f", side, symbol, qty)
        return OrderResult(id=order.id, symbol=order.symbol, qty=float(order.qty), side=order.side.value)
