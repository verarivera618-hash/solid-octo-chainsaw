from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from src.config import AppConfig
from src.perplexity_client import PerplexityClient
from src.prompt_generator import FinancePromptGenerator
from src.data_handler import AlpacaDataHandler, HistoricalDataParams
from src.strategy import MomentumStrategy, PositionSizingConfig, RiskConfig

app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def analyze(
    tickers: str = typer.Option(..., help="Comma-separated tickers, e.g. AMD,NVDA,INTC"),
    strategy: str = typer.Option("momentum", help="Strategy type label for the prompt"),
    days: int = typer.Option(30, help="Historical days for context"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save generated prompt to cursor_tasks"),
    offline: bool = typer.Option(False, help="Skip live API calls; synthesize demo output"),
):
    """Fetch Perplexity insights, Alpaca historical data, and generate a Cursor background agent prompt."""
    ticker_list: List[str] = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    if offline:
        # Synthesize summaries and simple price lines without requiring any API keys
        sec_summary = "Demo SEC summary for: " + ", ".join(ticker_list)
        news_summary = "Demo news and sentiment for: " + ", ".join(ticker_list)
        price_lines = [f"{sym}: $100.00 (+2.00% over period)" for sym in ticker_list]
    else:
        cfg = AppConfig.from_env()
        pclient = PerplexityClient(api_key=cfg.perplexity_api_key)
        sec_summary = pclient.summarize_sec_filings(ticker_list)
        news_summary = pclient.market_news_sentiment(ticker_list)

        data = AlpacaDataHandler(cfg.alpaca.api_key, cfg.alpaca.secret_key)
        bars = data.get_historical_bars(HistoricalDataParams(tickers=ticker_list, days=days))

        # Summarize recent price action
        price_lines = []
        for symbol, df in bars.items():
            if df.empty:
                continue
            first = float(df.iloc[0]["close"]) if "close" in df.columns and not df.empty else 0.0
            last = float(df.iloc[-1]["close"]) if "close" in df.columns and not df.empty else 0.0
            change_pct = ((last - first) / first * 100) if first > 0 else 0.0
            price_lines.append(f"{symbol}: ${last:.2f} ({change_pct:+.2f}% over period)")

    combined = f"""
## SEC Filings Analysis
{sec_summary}

## Market News & Sentiment
{news_summary}

## Recent Price Action (Last {days} Days)
{os.linesep.join(price_lines)}
"""

    # Build Cursor prompt
    prompt = FinancePromptGenerator().generate_cursor_prompt(combined, strategy)

    # Optionally save prompt for background agent
    if save:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        fname = f"cursor_tasks/{strategy}_{ts}.md"
        os.makedirs("cursor_tasks", exist_ok=True)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(prompt)
        console.print(f"[green]Saved Cursor prompt to[/green] {fname}")

    # Display summary table
    table = Table(title="Generated Market Summary")
    table.add_column("Section")
    table.add_column("Content", overflow="fold")
    table.add_row("SEC", sec_summary[:300] + ("..." if len(sec_summary) > 300 else ""))
    table.add_row("News", news_summary[:300] + ("..." if len(news_summary) > 300 else ""))
    table.add_row("Prices", "\n".join(price_lines))
    console.print(table)


@app.command()
def backtest(
    tickers: str = typer.Option(..., help="Comma-separated tickers"),
    days: int = typer.Option(120, help="Historical window for backtest"),
    portfolio: float = typer.Option(100000.0, help="Starting portfolio value"),
):
    """Very simple momentum backtest as a placeholder."""
    cfg = AppConfig.from_env()
    ticker_list: List[str] = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    data = AlpacaDataHandler(cfg.alpaca.api_key, cfg.alpaca.secret_key)
    bars = data.get_historical_bars(HistoricalDataParams(tickers=ticker_list, days=days))

    strat = MomentumStrategy(PositionSizingConfig(portfolio_value=portfolio), RiskConfig())
    signals = strat.generate_signals(bars)

    table = Table(title="Backtest Signals (Most Recent)")
    table.add_column("Symbol")
    table.add_column("Side")
    table.add_column("Qty")
    table.add_column("Stop")
    table.add_column("Take")

    for s in signals:
        table.add_row(s.symbol, s.side, f"{s.qty:.0f}", f"{s.stop_loss:.2f}", f"{s.take_profit:.2f}")

    console.print(table)


if __name__ == "__main__":
    app()
