"""
Local trading client - no external API dependencies
All functionality is provided by local clients with no external API calls
"""
from .local_clients import (
    LocalAlpacaDataClient, 
    LocalAlpacaTradingClient, 
    LocalStreamClient
)

# Export classes with original names for compatibility
class AlpacaDataClient(LocalAlpacaDataClient):
    """Client for local market data operations - no external dependencies"""
    pass

class AlpacaTradingClient(LocalAlpacaTradingClient):
    """Client for local trading operations - no external dependencies"""
    pass

class AlpacaStreamClient(LocalStreamClient):
    """Client for local real-time data streaming - no external dependencies"""
    pass

# Compatibility exports
__all__ = ['AlpacaDataClient', 'AlpacaTradingClient', 'AlpacaStreamClient']