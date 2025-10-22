"""
Local financial data client - no external API dependencies
All functionality is provided by local clients with no external API calls
"""
from .local_clients import LocalPerplexityClient

# Export class with original name for compatibility
class PerplexityFinanceClient(LocalPerplexityClient):
    """Client for accessing local financial data - no external dependencies"""
    pass

# Compatibility exports
__all__ = ['PerplexityFinanceClient']