from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AlpacaConfig:
    api_key: str
    secret_key: str
    paper: bool = True


@dataclass
class AppConfig:
    perplexity_api_key: str
    alpaca: AlpacaConfig

    @staticmethod
    def from_env() -> "AppConfig":
        perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        if not perplexity_key:
            raise ValueError("Missing PERPLEXITY_API_KEY in environment")
        alpaca_key = os.getenv("ALPACA_API_KEY")
        alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
        if not alpaca_key or not alpaca_secret:
            raise ValueError("Missing ALPACA_API_KEY or ALPACA_SECRET_KEY in environment")
        paper = os.getenv("ALPACA_PAPER", "true").lower() in {"1", "true", "yes"}
        return AppConfig(
            perplexity_api_key=perplexity_key,
            alpaca=AlpacaConfig(api_key=alpaca_key, secret_key=alpaca_secret, paper=paper),
        )
