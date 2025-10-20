from __future__ import annotations

import pandas as pd

from src.strategy import MomentumStrategy, PositionSizingConfig, RiskConfig


def make_df(prices):
    return pd.DataFrame({"close": prices}, index=pd.date_range(start="2024-01-01", periods=len(prices)))


def test_momentum_buy_signal():
    price_data = {
        "AMD": make_df([100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110]),
    }
    strat = MomentumStrategy(PositionSizingConfig(portfolio_value=100000), RiskConfig())
    signals = strat.generate_signals(price_data)
    assert any(s.symbol == "AMD" and s.side == "buy" and s.qty > 0 for s in signals)


def test_no_signal_on_downtrend():
    price_data = {
        "AMD": make_df([110, 109, 108, 107, 106, 105, 104, 103, 102, 101, 100]),
    }
    strat = MomentumStrategy(PositionSizingConfig(portfolio_value=100000), RiskConfig())
    signals = strat.generate_signals(price_data)
    assert len(signals) == 0
