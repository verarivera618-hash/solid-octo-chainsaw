from __future__ import annotations
import os
from datetime import datetime
from typing import List

from .perplexity_client import PerplexityClient
from .prompt_generator import FinancePromptGenerator
from .alpaca_context import AlpacaContext


class PerplexityAlpacaIntegration:
    def __init__(self, perplexity_key: str | None = None, alpaca_key: str | None = None, alpaca_secret: str | None = None):
        self.perplexity = PerplexityClient(perplexity_key)
        self.prompt_gen = FinancePromptGenerator()
        self.alpaca = AlpacaContext(alpaca_key, alpaca_secret)

    def analyze_and_generate_task(self, tickers: List[str], strategy_name: str) -> str:
        print("Fetching SEC filings analysis...")
        sec_data = self.perplexity.get_market_insights(tickers, "sec_filings")

        print("Fetching market news and sentiment...")
        news_data = self.perplexity.get_market_insights(tickers, "market_news")

        print("Fetching recent historical bars from Alpaca...")
        bars = self.alpaca.fetch_recent_bars(tickers, days=30)

        combined_data = f"""
## SEC Filings Analysis
{sec_data}

## Market News & Sentiment
{news_data}

## Recent Price Action (Last 30 Days)
{self.alpaca.summarize_bars(bars)}
"""

        cursor_prompt = self.prompt_gen.generate_cursor_prompt(combined_data, strategy_name)
        filename = self._save_prompt_for_cursor(cursor_prompt, strategy_name)

        print(f"\nSaved Cursor task to: {filename}")
        return filename

    @staticmethod
    def _save_prompt_for_cursor(prompt: str, strategy_name: str) -> str:
        # Use a relative path so it works inside Docker (WORKDIR) and locally
        out_dir = os.path.join(os.getcwd(), "cursor_tasks")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(out_dir, f"{strategy_name}_{ts}.md")
        with open(filename, "w") as f:
            f.write(prompt)
        return filename
