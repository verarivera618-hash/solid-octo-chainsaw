import os
import requests
from typing import List, Literal, Optional
from datetime import datetime

PerplexityQueryType = Literal["sec_filings", "market_news"]


class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        self.base_url = "https://api.perplexity.ai/chat/completions"

    def _headers(self) -> dict:
        return {
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
            "accept": "application/json",
        }

    def get_market_insights(
        self,
        tickers: List[str],
        query_type: PerplexityQueryType,
    ) -> str:
        if query_type == "sec_filings":
            payload = {
                "model": "sonar-deep-research",
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Analyze the latest SEC filings for {', '.join(tickers)}. "
                            "Extract key financial metrics, risk factors, and management discussion points."
                        ),
                    }
                ],
                "search_domain": "sec",
                "reasoning_effort": "high",
            }
        elif query_type == "market_news":
            payload = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"What are the latest market developments for {', '.join(tickers)}? "
                            "Include sentiment analysis and price-moving events."
                        ),
                    }
                ],
                "web_search_options": {
                    "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                    "search_context_size": "high",
                },
            }
        else:
            raise ValueError(f"Unsupported query_type: {query_type}")

        response = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            return str(data)
