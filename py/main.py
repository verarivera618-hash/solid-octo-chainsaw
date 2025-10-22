from __future__ import annotations
import argparse
import os

from .prompt_generator import FinancePromptGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Perplexity → Alpaca prompt generator")
    parser.add_argument("--tickers", nargs="+", default=["AMD", "NVDA", "INTC"], help="List of stock tickers")
    parser.add_argument("--strategy", default="semiconductor_momentum_strategy", help="Strategy name")
    parser.add_argument("--test", action="store_true", help="Run environment check only (no API calls)")
    parser.add_argument("--simulate", action="store_true", help="Simulate data and write a prompt without API calls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    def _save_prompt(prompt: str, strategy_name: str) -> str:
        import os
        from datetime import datetime
        out_dir = os.path.join(os.getcwd(), "cursor_tasks")
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(out_dir, f"{strategy_name}_{ts}.md")
        with open(filename, "w") as f:
            f.write(prompt)
        return filename

    if args.test:
        # Validate environment only
        print("Running environment check (--test)")
        missing = [k for k in ("PERPLEXITY_API_KEY", "ALPACA_API_KEY", "ALPACA_SECRET_KEY") if not os.getenv(k)]
        if missing:
            print("Missing environment variables:", ", ".join(missing))
        else:
            print("All required environment variables are set.")
        print("Tickers:", args.tickers)
        print("Strategy:", args.strategy)
        return

    if args.simulate:
        print("Simulating prompt generation (--simulate)")
        combined_data = f"""
## SEC Filings Analysis
Simulated SEC filings summary for {', '.join(args.tickers)}.

## Market News & Sentiment
Simulated market news and sentiment (mixed to bullish).

## Recent Price Action (Last 30 Days)
Simulated prices: {', '.join([t + ': $100.00 (+2.5%)' for t in args.tickers])}
"""
        prompt = FinancePromptGenerator().generate_cursor_prompt(combined_data, args.strategy)
        filename = _save_prompt(prompt, args.strategy)
        print(f"\n✅ Simulated Cursor prompt saved to: {filename}")
        return

    from .integration import PerplexityAlpacaIntegration
    integration = PerplexityAlpacaIntegration(
        perplexity_key=os.getenv("PERPLEXITY_API_KEY"),
        alpaca_key=os.getenv("ALPACA_API_KEY"),
        alpaca_secret=os.getenv("ALPACA_SECRET_KEY"),
    )

    filename = integration.analyze_and_generate_task(args.tickers, args.strategy)
    print("\n✅ Cursor prompt saved. Next steps:")
    print("1) Open Cursor and press Ctrl+Shift+B (or ⌘B on Mac)")
    print("2) Click 'New Background Agent'")
    print(f"3) Copy the contents of {filename} into the agent prompt")


if __name__ == "__main__":
    main()
