"""
NSE Socket Client Library
A professional Python client library for the NSE Socket server with WebSocket and REST API support.

This library provides:
- Real-time market data streaming via WebSocket
- Historical data access via REST API  
- Order management and trading operations
- JWT-based authentication
- Automatic reconnection and error handling
- Professional logging and monitoring

Example Usage:
    from nse_socket_client import NSEClient
    
    client = NSEClient("localhost")
    
    if client.authenticate("admin"):
        def handle_data(data):
            print(f"{data['symbol']}: {data['data']['close']}")
        
        client.on_ticks = handle_data
        client.connect_and_subscribe(["NIFTY", "RELIANCE"])
        client.run()

For complete documentation, see: https://github.com/your-repo/nse-socket-client/docs/
"""

from .nse_client import (
    NSEClient,
    NSESocketError,
    AuthenticationError,
    ConnectionError,
    SubscriptionError,
    HistoricalDataError,
    get_token,
)

__version__ = "0.8"
__author__ = "siddid"

__all__ = [
    "NSEClient",
    "NSESocketError", 
    "AuthenticationError",
    "ConnectionError",
    "SubscriptionError", 
    "HistoricalDataError",
    "get_token",
]