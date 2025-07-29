"""
NSE Socket Client Library
A professional Python client library for the NSE Socket server with WebSocket and REST API support.
"""

from .nse_client import (
    NSEClient,
    NSESocketError,
    AuthenticationError,
    ConnectionError,
    SubscriptionError,
    HistoricalDataError,
    AdminError,
    get_token,
)

__version__ = "0.7"
__author__ = "siddid"

__all__ = [
    "NSEClient",
    "NSESocketError", 
    "AuthenticationError",
    "ConnectionError",
    "SubscriptionError", 
    "HistoricalDataError",
    "AdminError",
    "get_token",
] 