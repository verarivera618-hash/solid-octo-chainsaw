from __future__ import annotations

import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


class PerplexityAPIError(Exception):
    pass


@dataclass
class PerplexityRequest:
    model: str
    messages: List[Dict[str, str]]
    stream: bool = False
    search_domain: Optional[str] = None
    search_after_date_filter: Optional[str] = None
    web_search_options: Optional[Dict[str, str]] = None
    reasoning_effort: Optional[str] = None
    response_format: Optional[Dict[str, str]] = None

    def to_payload(self) -> Dict:
        payload: Dict[str, object] = {
            "model": self.model,
            "messages": self.messages,
            "stream": self.stream,
        }
        if self.search_domain:
            payload["search_domain"] = self.search_domain
        if self.search_after_date_filter:
            payload["search_after_date_filter"] = self.search_after_date_filter
        if self.web_search_options:
            payload["web_search_options"] = self.web_search_options
        if self.reasoning_effort:
            payload["reasoning_effort"] = self.reasoning_effort
        if self.response_format:
            payload["response_format"] = self.response_format
        return payload


class PerplexityClient:
    def __init__(self, api_key: Optional[str] = None, timeout_seconds: int = 60):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY must be provided via arg or environment")
        self.timeout_seconds = timeout_seconds

    @retry(
        retry=retry_if_exception_type(PerplexityAPIError),
        wait=wait_exponential_jitter(initial=1, max=16),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    def create_completion(self, request: PerplexityRequest) -> Dict:
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}",
            "content-type": "application/json",
        }
        try:
            response = requests.post(
                PERPLEXITY_API_URL, headers=headers, json=request.to_payload(), timeout=self.timeout_seconds
            )
        except requests.RequestException as exc:
            raise PerplexityAPIError(str(exc)) from exc

        if response.status_code >= 400:
            raise PerplexityAPIError(f"HTTP {response.status_code}: {response.text}")

        try:
            payload = response.json()
        except Exception as exc:  # noqa: BLE001
            raise PerplexityAPIError("Invalid JSON response from Perplexity") from exc
        return payload

    def extract_message_content(self, payload: Dict) -> str:
        try:
            return payload["choices"][0]["message"]["content"]
        except Exception as exc:  # noqa: BLE001
            raise PerplexityAPIError("Unexpected response schema; missing choices[0].message.content") from exc

    # Convenience methods for our workflows
    def summarize_sec_filings(self, tickers: List[str], after: Optional[str] = None) -> str:
        request = PerplexityRequest(
            model="sonar-pro",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the latest SEC filings for {', '.join(tickers)}. Include key metrics, risk factors, MD&A highlights, and any material events.",
                }
            ],
            search_domain="sec",
            search_after_date_filter=after or datetime.now().strftime("%Y-01-01"),
            stream=False,
            reasoning_effort="high",
        )
        payload = self.create_completion(request)
        return self.extract_message_content(payload)

    def market_news_sentiment(self, tickers: List[str]) -> str:
        request = PerplexityRequest(
            model="sonar-pro",
            messages=[
                {
                    "role": "user",
                    "content": f"What are the latest market developments for {', '.join(tickers)}? Include sentiment analysis and price-moving events.",
                }
            ],
            web_search_options={
                "latest_updated": datetime.now().strftime("%Y-%m-%d"),
                "search_context_size": "high",
            },
            stream=False,
        )
        payload = self.create_completion(request)
        return self.extract_message_content(payload)

    def structured_metrics(self, ticker: str) -> Dict:
        request = PerplexityRequest(
            model="sonar-pro",
            messages=[{"role": "user", "content": f"Extract key metrics from {ticker}'s latest 10-Q."}],
            search_domain="sec",
            response_format={"type": "json_object"},
            stream=False,
        )
        payload = self.create_completion(request)
        try:
            # Many LLMs put JSON content as string content; attempt to parse if needed
            content = self.extract_message_content(payload)
            import json

            return json.loads(content)
        except Exception:
            return {"raw": payload}
