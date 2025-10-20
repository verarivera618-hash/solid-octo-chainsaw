from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class PositionSizingConfig:
    portfolio_value: float
    risk_per_trade_pct: float = 0.01  # 1%


@dataclass
class RiskConfig:
    stop_loss_pct: float = 0.03
    take_profit_pct: float = 0.06


@dataclass
class Signal:
    symbol: str
    side: str  # "buy" or "sell"
    qty: float
    stop_loss: float
    take_profit: float


class MomentumStrategy:
    def __init__(self, position_cfg: PositionSizingConfig, risk_cfg: RiskConfig):
        self.position_cfg = position_cfg
        self.risk_cfg = risk_cfg

    @staticmethod
    def compute_returns(prices: pd.Series, window: int) -> float:
        if len(prices) < window + 1:
            return 0.0
        return float(prices.iloc[-1] / prices.iloc[-window - 1] - 1.0)

    def generate_signals(self, price_data: Dict[str, pd.DataFrame]) -> List[Signal]:
        signals: List[Signal] = []
        for symbol, df in price_data.items():
            if df.empty:
                continue
            close = df["close"].astype(float)
            mom_5 = self.compute_returns(close, 5)
            # Only require the long window if there is enough data; otherwise rely on short momentum
            has_long_window = len(close) >= 21
            mom_20 = self.compute_returns(close, 20) if has_long_window else None
            latest_price = float(close.iloc[-1])

            if mom_5 > 0 and (mom_20 is None or mom_20 > 0):
                side = "buy"
                stop_loss = latest_price * (1 - self.risk_cfg.stop_loss_pct)
                take_profit = latest_price * (1 + self.risk_cfg.take_profit_pct)
                risk_amount = self.position_cfg.portfolio_value * self.position_cfg.risk_per_trade_pct
                per_share_risk = latest_price - stop_loss
                qty = max(0.0, risk_amount / per_share_risk) if per_share_risk > 0 else 0.0
                signals.append(Signal(symbol=symbol, side=side, qty=float(np.floor(qty)), stop_loss=stop_loss, take_profit=take_profit))
            elif mom_5 < 0 and (mom_20 is None or mom_20 < 0):
                # For simplicity, skip shorting in this template
                continue
        return signals

    def bracket_prices(self, entry_price: float) -> Tuple[float, float]:
        stop = entry_price * (1 - self.risk_cfg.stop_loss_pct)
        take = entry_price * (1 + self.risk_cfg.take_profit_pct)
        return stop, take
