#!/usr/bin/env python3
"""
NSE Socket Client Library
A professional Python client library for the NSE Socket server with WebSocket and REST API support.
"""

import json
import time
import threading
import requests
import websocket
from typing import Optional, Dict, Any, Callable, List, Set, Union
from datetime import datetime, date
import logging
import signal
import sys

# Configure professional logging format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_token(api_uri: str, username: str) -> Optional[str]:
    """
    Standalone function to request JWT token from the NSE server.
    
    Args:
        api_uri: HTTP API server URI (e.g., "http://localhost:3000")
        username: Username for token generation
        
    Returns:
        str: JWT token string if successful, None if failed
        
    Raises:
        AuthenticationError: If token retrieval fails
        
    Example:
        token = get_token("http://localhost:3000", "admin")
        if token:
            print(f"Token: {token}")
    """
    try:
        logger.info(f"Requesting JWT token for user: {username}")
        
        response = requests.post(
            f"http://{api_uri}:3000/api/login",
            json={"username": username},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("token"):
                token = data["token"]
                user_id = data.get("user_id", username)
                permissions = data.get("permissions", [])
                
                logger.info(f"JWT token obtained successfully for user: {user_id}")
                logger.info(f"Granted permissions: {', '.join(permissions)}")
                
                return token
            else:
                error_msg = data.get("message", "Token generation failed")
                raise AuthenticationError(f"Token generation failed: {error_msg}")
        else:
            raise AuthenticationError(f"Token request failed with status {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        raise AuthenticationError(f"Token request failed: {str(e)}")
    except Exception as e:
        raise AuthenticationError(f"Token generation error: {str(e)}")


class NSESocketError(Exception):
    """Base exception for NSE Socket client errors."""
    pass


class AuthenticationError(NSESocketError):
    """Exception raised for authentication-related errors."""
    pass


class ConnectionError(NSESocketError):
    """Exception raised for connection-related errors."""
    pass


class SubscriptionError(NSESocketError):
    """Exception raised for subscription-related errors."""
    pass


class HistoricalDataError(NSESocketError):
    """Exception raised for historical data API errors."""
    pass


class AdminError(NSESocketError):
    """Exception raised for admin operation errors."""
    pass


class NSEClient:
    """
    Professional NSE Socket Client for real-time market data streaming and order management.
    
    This client provides a robust interface for connecting to the NSE Socket server,
    subscribing to real-time market data feeds, managing trading orders, and accessing
    historical market data with advanced filtering and date scaling capabilities.
    
    Example Usage:
        # Method 1: Request token and connect
        client = NSEClient("ws://localhost:8080", "http://localhost:3000")
        if client.authenticate("username"):
            # Real-time data
            client.connect_and_subscribe(["NIFTY", "RELIANCE", "TCS"])
            
            # Historical data
            historical_data = client.get_historical_data("NIFTY", limit=100)
            daily_data = client.get_historical_data("NIFTY", time_period="day", limit=30)
            
            client.run()
        
        # Method 2: Use existing token
        client = NSEClient("localhost", "jwt-token")
        client.on_ticks = lambda data: print(f"Received: {data}")
        client.connect_and_subscribe(["NIFTY", "RELIANCE"])
        client.run()
    """
    
    def __init__(self, uri, token: Optional[str] = None):
        """
        Initialize NSE Socket Client.
        
        Args:
            ws_uri: WebSocket server URI (e.g., "ws://localhost:8080")
            api_uri: HTTP API server URI (e.g., "http://localhost:3000")  
            token: JWT authentication token (optional, can be obtained via authenticate())
        
        Raises:
            ValueError: If URIs are invalid
        """
        # Validate and normalize URIs
        if not uri:
            raise ValueError("WebSocket and API URIs must be provided")
            
        self.ws_uri = f"ws://{uri}:8080/ws"
        self.api_uri = f"http://{uri}:3000/"
        self.token = token
        
        # Connection state
        self.ws = None
        self.connected = False
        self.running = False
        self.ws_thread = None
        self._stop_event = threading.Event()
        
        # Subscription management
        self.subscribed_symbols: Set[str] = set()
        
        # API configuration
        self.headers = self._get_headers()
        
        # Event callbacks
        self.on_ticks: Optional[Callable[[Dict], None]] = None
        self.on_connect: Optional[Callable[[], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None
        self.on_error: Optional[Callable[[Exception], None]] = None
        self.on_order_update: Optional[Callable[[Dict], None]] = None
        
        # Connection settings
        self.auto_reconnect = True
        self.reconnect_interval = 5
        self.max_reconnect_attempts = 10
        self.reconnect_attempts = 0
        
        # Heartbeat configuration
        self.heartbeat_enabled = True
        self.heartbeat_interval = 25
        self.ping_timeout = 10
        self.last_pong_time = None
        
        # Setup graceful shutdown
        self._setup_signal_handlers()

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _setup_signal_handlers(self):
        """Configure signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info("⚠️ Shutdown signal received - forcing immediate stop")
            self.force_shutdown()
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def get_token(self, username: str) -> Optional[str]:
        """
        Request JWT token from the server using username.
        Uses the standalone get_token function and updates internal state.
        
        Args:
            username: Username for token generation
            
        Returns:
            str: JWT token string if successful, None if failed
            
        Raises:
            AuthenticationError: If token retrieval fails
        """
        try:
            token = get_token(self.api_uri, username)
            if token:
                self.token = token
                self.headers = self._get_headers()
            return token
        except Exception as e:
            raise e

    def ws_connect(self, blocking: bool = True, keep_alive: bool = True) -> bool:
        """
        Connect to WebSocket server.
        Use client.on_ticks to set callback for data streaming.
        
        Args:
            blocking: If True, waits for connection to establish. If False, returns immediately.
            keep_alive: If True (and blocking=True), keeps program alive to receive data.
        
        Returns:
            bool: True if connection successful (blocking) or initiated (non-blocking)
            
        Example:
            def handle_data(data):
                print(f"Received: {data['symbol']} - Price: {data['data']['close']}")
            
            client.on_ticks = handle_data
            client.ws_connect()  # Connects, waits, and keeps alive automatically
        """
        try:
            if self.connected:
                logger.warning("Already connected to WebSocket")
                return True
                
            logger.info(f"Connecting to WebSocket: {self.ws_uri}")
            
            # Reset connection state
            self.connected = False
            self._stop_event.clear()
            
            if blocking:
                # Synchronous connection - wait for connection before returning
                logger.info("⏳ Establishing WebSocket connection...")
                
                # Use a connection event to wait for connection
                connection_event = threading.Event()
                connection_success = [False]  # Use list to modify from callback
                
                def on_open_blocking(ws):
                    self.connected = True
                    connection_success[0] = True
                    connection_event.set()
                    logger.info("✅ WebSocket connected successfully")
                    if self.on_connect:
                        try:
                            self.on_connect()
                        except Exception as e:
                            logger.error(f"Error in connect callback: {e}")
                
                def on_error_blocking(ws, error):
                    logger.error(f"❌ WebSocket connection error: {error}")
                    connection_success[0] = False
                    connection_event.set()
                    if self.on_error:
                        try:
                            self.on_error(error)
                        except Exception as e:
                            logger.error(f"Error in error callback: {e}")
                
                # Create WebSocket with blocking callbacks
                self.ws = websocket.WebSocketApp(
                    self.ws_uri,
                    header=[f"Authorization: Bearer {self.token}"],
                    on_open=on_open_blocking,
                    on_message=self._on_ws_message,
                    on_error=on_error_blocking,
                    on_close=self._on_ws_close,
                    on_ping=self._on_ws_ping,
                    on_pong=self._on_ws_pong
                )
                
                # Start WebSocket in separate thread
                self.running = True
                if self.heartbeat_enabled:
                    self.ws_thread = threading.Thread(target=self._run_websocket_with_ping)
                else:
                    self.ws_thread = threading.Thread(target=self._run_websocket_simple)
                    
                self.ws_thread.daemon = True
                self.ws_thread.start()
                
                # Wait for connection event with timeout
                if connection_event.wait(timeout=10):
                    if connection_success[0]:
                        self.reconnect_attempts = 0
                        if self.heartbeat_enabled:
                            logger.info(f"💓 Heartbeat enabled (ping every {self.heartbeat_interval}s)")
                        if self.on_ticks:
                            logger.info("💡 Streaming callback ready - data will be received")
                        
                        # Keep alive if requested
                        if keep_alive:
                            logger.info("🚀 Connection established. Keeping program alive... Press Ctrl+C to stop")
                            try:
                                # Run until stop event is set
                                self._stop_event.wait()
                            except KeyboardInterrupt:
                                logger.info("🛑 Interrupted by user")
                                self.stop()
                            except Exception as e:
                                logger.error(f"❌ Error while keeping alive: {e}")
                                self.stop()
                        
                        return True
                    else:
                        logger.error("❌ WebSocket connection failed")
                        return False
                else:
                    logger.error("❌ WebSocket connection timeout")
                    return False
            else:
                # Non-blocking connection - original behavior
                self.ws = websocket.WebSocketApp(
                    self.ws_uri,
                    header=[f"Authorization: Bearer {self.token}"],
                    on_open=self._on_ws_open,
                    on_message=self._on_ws_message,
                    on_error=self._on_ws_error,
                    on_close=self._on_ws_close,
                    on_ping=self._on_ws_ping,
                    on_pong=self._on_ws_pong
                )
                
                # Start WebSocket in separate thread
                self.running = True
                if self.heartbeat_enabled:
                    self.ws_thread = threading.Thread(target=self._run_websocket_with_ping)
                else:
                    self.ws_thread = threading.Thread(target=self._run_websocket_simple)
                    
                self.ws_thread.daemon = True
                self.ws_thread.start()
                
                # Non-blocking - return immediately
                logger.info("🚀 WebSocket connecting in background...")
                if self.on_ticks:
                    logger.info("💡 Streaming callback ready - data will be received when connected")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            return False

    def connect_and_subscribe(self, symbols: List[str]) -> bool:
        """
        Connect to WebSocket and subscribe to multiple symbols in one call.
        Uses client.on_ticks for data callback.
        
        Args:
            symbols: List of symbols to subscribe to
            
        Returns:
            bool: True if connection and all subscriptions successful
            
        Example:
            def handle_data(data):
                print(f"Received: {data['symbol']} - Price: {data['data']['close']}")
            
            client.on_ticks = handle_data
            client.connect_and_subscribe(["NIFTY", "RELIANCE"])
            # Data will be received via callback, no sleep() or run() needed
        """
        # Connect with blocking=True to wait for connection
        if not self.ws_connect(blocking=True):
            logger.error("❌ Failed to establish WebSocket connection")
            return False
            
        # Connection is guaranteed to be established at this point
        logger.info(f"📡 Subscribing to {len(symbols)} symbols...")
        results = self.subscribe_multiple(symbols)
        success_count = sum(1 for success in results.values() if success)
        
        if success_count > 0:
            logger.info(f"✅ Successfully subscribed to {success_count}/{len(symbols)} symbols")
            if self.on_ticks:
                logger.info("🚀 Data will be received via callback - no sleep() or run() needed")
        else:
            logger.error("❌ Failed to subscribe to any symbols")
        
        return success_count > 0

    def run(self, timeout: Optional[float] = None):
        """
        Run the client in blocking mode until stopped or disconnected.
        This eliminates the need for sleep in your main program.
        
        Args:
            timeout: Maximum time to run in seconds (None = run indefinitely)
        """
        if not self.connected:
            logger.error("❌ Not connected. Call ws_connect() or connect_and_subscribe() first")
            return
            
        logger.info("🚀 Starting data stream... Press Ctrl+C to stop")
        
        try:
            if timeout:
                self._stop_event.wait(timeout)
            else:
                # Run until stop event is set
                self._stop_event.wait()
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrupted by user - forcing shutdown")
            self.force_shutdown()
            return
        finally:
            # Only call normal stop if we weren't force-shutdown
            if self.running:
                self.stop()

    def stop(self):
        """Stop the client and disconnect."""
        logger.info("🛑 Stopping NSE Client...")
        
        # Set stop event first to signal all threads
        self._stop_event.set()
        self.running = False
        self.auto_reconnect = False
        
        # Disconnect WebSocket
        self.ws_disconnect()
        
        # Give a moment for everything to cleanup
        time.sleep(0.1)
        
        logger.info("✅ NSE Client stopped")

    def ws_disconnect(self):
        """Disconnect from WebSocket server."""
        try:
            logger.info("Disconnecting from WebSocket...")
            self.running = False
            self.auto_reconnect = False
            
            # Stop heartbeat
            self._stop_heartbeat()
            
            # Close WebSocket connection first
            if self.ws:
                try:
                    self.ws.close()
                except Exception as e:
                    logger.debug(f"Error closing WebSocket: {e}")
                    
            # Force thread to stop by setting stop event
            self._stop_event.set()
            
            # Wait for thread to finish with shorter timeout
            if self.ws_thread and self.ws_thread.is_alive():
                logger.debug("Waiting for WebSocket thread to stop...")
                self.ws_thread.join(timeout=3)
                
                # If thread is still alive, it's probably stuck
                if self.ws_thread and self.ws_thread.is_alive():
                    logger.warning("WebSocket thread didn't stop cleanly - it may be stuck")
                else:
                    logger.debug("WebSocket thread stopped successfully")
                
            self.connected = False
            self.subscribed_symbols.clear()
            self.ws = None
            self.ws_thread = None
            logger.info("✅ WebSocket disconnected")
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting: {e}")
            # Force cleanup even if there was an error
            self.connected = False
            self.running = False
            self.ws = None
            self.ws_thread = None

    def subscribe_feed(self, symbol: str) -> bool:
        """
        Subscribe to real-time data feed for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "NIFTY", "INDIGO")
            
        Returns:
            bool: True if subscription successful, False otherwise
        """
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return False
            
        try:
            symbol = symbol.upper()
            message = {
                "action": "subscribe",
                "symbol": symbol
            }
            
            self.ws.send(json.dumps(message))
            self.subscribed_symbols.add(symbol)
            logger.info(f"📡 Subscribed to {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Subscription failed for {symbol}: {e}")
            return False

    def subscribe_multiple(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Subscribe to real-time data feeds for multiple symbols.
        Can be called before connection - subscriptions will be queued.
        
        Args:
            symbols: List of stock symbols (e.g., ["NIFTY", "INDIGO", "RELIANCE"])
            
        Returns:
            Dict[str, bool]: Dictionary mapping symbol to subscription success status
        """
        if not self.connected:
            # Queue subscriptions for when connection is established
            logger.info(f"📡 Queueing subscription for {len(symbols)} symbols (not connected yet)")
            for symbol in symbols:
                self.subscribed_symbols.add(symbol.upper())
            
            # Set up a callback to subscribe when connected
            original_on_connect = self.on_connect
            
            def on_connect_with_subscribe():
                # Call original callback first
                if original_on_connect:
                    try:
                        original_on_connect()
                    except Exception as e:
                        logger.error(f"Error in original connect callback: {e}")
                
                # Then subscribe to queued symbols
                if self.subscribed_symbols:
                    queued_symbols = list(self.subscribed_symbols)
                    self.subscribed_symbols.clear()  # Clear queue before subscribing
                    logger.info(f"📡 Subscribing to {len(queued_symbols)} queued symbols...")
                    self._subscribe_now(queued_symbols)
            
            self.on_connect = on_connect_with_subscribe
            return {symbol: True for symbol in symbols}  # Return success for queuing
            
        return self._subscribe_now(symbols)
    
    def _subscribe_now(self, symbols: List[str]) -> Dict[str, bool]:
        """Internal method to subscribe immediately (when connected)."""
        results = {}
        successful_subscriptions = []
        
        for symbol in symbols:
            try:
                symbol = symbol.upper()
                message = {
                    "action": "subscribe",
                    "symbol": symbol
                }
                
                self.ws.send(json.dumps(message))
                self.subscribed_symbols.add(symbol)
                results[symbol] = True
                successful_subscriptions.append(symbol)
                
                # Small delay between subscriptions to avoid overwhelming the server
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Subscription failed for {symbol}: {e}")
                results[symbol] = False
        
        if successful_subscriptions:
            logger.info(f"📡 Subscribed to {len(successful_subscriptions)} symbols: {', '.join(successful_subscriptions)}")
        
        return results

    def subscribe_batch(self, symbols: List[str], batch_size: int = 10) -> Dict[str, bool]:
        """
        Subscribe to multiple symbols in batches to avoid overwhelming the server.
        
        Args:
            symbols: List of symbols to subscribe to
            batch_size: Number of symbols to subscribe to at once
            
        Returns:
            Dict[str, bool]: Dictionary mapping symbol to subscription success status
        """
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return {symbol: False for symbol in symbols}
            
        all_results = {}
        
        # Process symbols in batches
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            batch_results = self.subscribe_multiple(batch)
            all_results.update(batch_results)
            
            # Pause between batches if not the last batch
            if i + batch_size < len(symbols):
                time.sleep(0.5)
                
        return all_results

    def unsubscribe_feed(self, symbol: Optional[str] = None) -> bool:
        """
        Unsubscribe from data feed.
        
        Args:
            symbol: Symbol to unsubscribe from (optional, unsubscribes from all if not provided)
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return False
            
        try:
            if symbol:
                # Unsubscribe from specific symbol
                symbol = symbol.upper()
                if symbol not in self.subscribed_symbols:
                    logger.warning(f"⚠️ Not subscribed to {symbol}")
                    return False
                    
                message = {
                    "action": "unsubscribe", 
                    "symbol": symbol
                }
                
                self.ws.send(json.dumps(message))
                self.subscribed_symbols.discard(symbol)
                logger.info(f"📡 Unsubscribed from {symbol}")
                return True
            else:
                # Unsubscribe from all symbols
                if not self.subscribed_symbols:
                    logger.warning("⚠️ No active subscriptions")
                    return False
                
                symbols_to_unsubscribe = list(self.subscribed_symbols)
                success = True
                
                for sym in symbols_to_unsubscribe:
                    try:
                        message = {
                            "action": "unsubscribe", 
                            "symbol": sym
                        }
                        self.ws.send(json.dumps(message))
                        time.sleep(0.1)  # Small delay between unsubscriptions
                    except Exception as e:
                        logger.error(f"❌ Failed to unsubscribe from {sym}: {e}")
                        success = False
                
                self.subscribed_symbols.clear()
                logger.info(f"📡 Unsubscribed from all symbols")
                return success
                
        except Exception as e:
            logger.error(f"❌ Unsubscription failed: {e}")
            return False

    def unsubscribe_multiple(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Unsubscribe from multiple symbols.
        
        Args:
            symbols: List of symbols to unsubscribe from
            
        Returns:
            Dict[str, bool]: Dictionary mapping symbol to unsubscription success status
        """
        if not self.connected:
            logger.error("❌ Not connected to WebSocket")
            return {symbol: False for symbol in symbols}
            
        results = {}
        successful_unsubscriptions = []
        
        for symbol in symbols:
            try:
                symbol = symbol.upper()
                if symbol not in self.subscribed_symbols:
                    logger.warning(f"⚠️ Not subscribed to {symbol}")
                    results[symbol] = False
                    continue
                    
                message = {
                    "action": "unsubscribe", 
                    "symbol": symbol
                }
                
                self.ws.send(json.dumps(message))
                self.subscribed_symbols.discard(symbol)
                results[symbol] = True
                successful_unsubscriptions.append(symbol)
                
                # Small delay between unsubscriptions
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Unsubscription failed for {symbol}: {e}")
                results[symbol] = False
        
        if successful_unsubscriptions:
            logger.info(f"📡 Unsubscribed from {len(successful_unsubscriptions)} symbols: {', '.join(successful_unsubscriptions)}")
        
        return results

    def place_order(self, symbol: str, side: str, order_type: str, quantity: int, 
                   price: Optional[float] = None, stop_price: Optional[float] = None) -> Optional[Dict]:
        """
        Place a stock order.
        
        Args:
            symbol: Stock symbol
            side: "buy" or "sell"  
            order_type: "market", "limit", or "stop_loss"
            quantity: Number of shares
            price: Price for limit orders (optional)
            stop_price: Stop price for stop-loss orders (optional)
            
        Returns:
            Dict: Order details if successful, None if failed
        """
        try:
            order_data = {
                "symbol": symbol.upper(),
                "side": side.lower(),
                "order_type": order_type.lower(),
                "quantity": quantity
            }
            
            if price is not None:
                order_data["price"] = price
            if stop_price is not None:
                order_data["stop_price"] = stop_price
                
            response = requests.post(
                f"{self.api_uri}/api/orders",
                headers=self.headers,
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    order = result.get("order")
                    logger.info(f"✅ Order placed: {order['id']} - {side.upper()} {quantity} {symbol}")
                    
                    # Trigger callback if set
                    if self.on_order_update and order:
                        try:
                            self.on_order_update(order)
                        except Exception as e:
                            logger.error(f"Error in order callback: {e}")
                    
                    return order
                else:
                    logger.error(f"❌ Order failed: {result.get('message')}")
                    return None
            else:
                logger.error(f"❌ Order request failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Order placement error: {e}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order.
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.api_uri}/api/orders/{order_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"✅ Order cancelled: {order_id}")
                    
                    # Trigger callback if set
                    if self.on_order_update:
                        try:
                            self.on_order_update(result.get("order"))
                        except Exception as e:
                            logger.error(f"Error in order callback: {e}")
                    
                    return True
                else:
                    logger.error(f"❌ Cancel failed: {result.get('message')}")
                    return False
            else:
                logger.error(f"❌ Cancel request failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Order cancellation error: {e}")
            return False

    def get_orders(self, symbol: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """
        Get user's orders.
        
        Args:
            symbol: Filter by symbol (optional)
            status: Filter by status (optional)
            
        Returns:
            List[Dict]: List of orders
        """
        try:
            params = {}
            if symbol:
                params['symbol'] = symbol.upper()
            if status:
                params['status'] = status.lower()
                
            response = requests.get(
                f"{self.api_uri}/api/orders",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("orders", [])
                    
            logger.error(f"❌ Failed to get orders: {response.status_code}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting orders: {e}")
            return []

    def get_order(self, order_id: str) -> Optional[Dict]:
        """
        Get specific order details.
        
        Args:
            order_id: Order ID
            
        Returns:
            Dict: Order details if found, None otherwise
        """
        try:
            response = requests.get(
                f"{self.api_uri}/api/orders/{order_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("order")
                    
            logger.error(f"❌ Failed to get order: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting order: {e}")
            return None

    def health_check(self) -> bool:
        """
        Check API server health.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.api_uri}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    # Historical Data API Methods
    def get_historical_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get summary of all available symbols and their record counts.
        
        Returns:
            Dict: Summary with symbols, counts, and totals, or None if failed
            
        Raises:
            HistoricalDataError: If request fails or authentication required
        """
        try:
            response = requests.get(
                f"{self.api_uri}/api/historical",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"📊 Historical data summary: {result.get('total_symbols', 0)} symbols, "
                              f"{result.get('total_records', 0)} total records")
                    return result
                else:
                    raise HistoricalDataError(f"Failed to get historical summary: {result.get('message', 'Unknown error')}")
            elif response.status_code == 401:
                raise AuthenticationError("Authentication required for historical data access")
            else:
                raise HistoricalDataError(f"Failed to get historical summary: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise HistoricalDataError(f"Request failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (HistoricalDataError, AuthenticationError)):
                raise
            raise HistoricalDataError(f"Unexpected error: {str(e)}")

    
    def get_historical_data(
        self,
        symbol: str,
        limit: Optional[int] = None,
        from_date: Optional[Union[str, date]] = None,
        to_date: Optional[Union[str, date]] = None,
        time_period: Optional[str] = None,
        validate_datetime: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get historical data with clean format - essential fields including datetime.
        
        Args:
            symbol: Symbol to get data for (e.g., "NIFTY", "RELIANCE")
            limit: Maximum number of records to return
            from_date: Start date filter (YYYY-MM-DD format or date object)
            to_date: End date filter (YYYY-MM-DD format or date object)
            time_period: Time period filtering - "minutes"/"min"/"m", "hour"/"hours"/"h", "day"/"days"/"d"
            validate_datetime: Whether to validate datetime format (default: True)
        
        Returns:
            List[Dict]: Clean list with [datetime, open, high, low, close, volume] fields
        
        Examples:
            # Get last 100 records with clean format including datetime
            data = client.get_historical_data("NIFTY", limit=100)
            # Returns: [{"datetime": "2025-06-21 09:15:00", "open": 21500.0, "high": 21650.0, "low": 21480.0, "close": 21620.0, "volume": 1500000}, ...]
        """
        try:
            # Convert date objects to strings if needed
            if isinstance(from_date, date):
                from_date = from_date.strftime("%Y-%m-%d")
            if isinstance(to_date, date):
                to_date = to_date.strftime("%Y-%m-%d")
            
            # Build query parameters
            params = {}
            if limit is not None:
                params['limit'] = limit
            if from_date:
                params['from_date'] = from_date
            if to_date:
                params['to_date'] = to_date
            if time_period:
                params['time_period'] = time_period
            
            response = requests.get(
                f"{self.api_uri}/api/historical/{symbol}",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    # Extract and clean the data - keep essential fields including datetime
                    clean_data = []
                    for record in result.get("data", []):
                        clean_record = {
                            "datetime": record.get("datetime"),
                            "open": record.get("open"),
                            "high": record.get("high"), 
                            "low": record.get("low"),
                            "close": record.get("close"),
                            "volume": record.get("volume")
                        }
                        
                        # Validate datetime format if requested
                        if validate_datetime and clean_record["datetime"]:
                            try:
                                # Validate YYYY-MM-DD HH:MM:SS format
                                datetime.strptime(clean_record["datetime"], "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                logger.warning(f"Invalid datetime format: {clean_record['datetime']}")
                        
                        clean_data.append(clean_record)
                    
                    logger.info(f"📊 Retrieved {len(clean_data)} clean records for {symbol}")
                    
                    # Log date range if available
                    if clean_data:
                        first_dt = clean_data[0]["datetime"]
                        last_dt = clean_data[-1]["datetime"]
                        logger.info(f"📅 Date range: {first_dt} to {last_dt}")
                    
                    return clean_data
                else:
                    logger.error(f"❌ Failed to get historical data for {symbol}: {result.get('message', 'Unknown error')}")
                    return []
            elif response.status_code == 401:
                raise AuthenticationError("Authentication required for historical data access")
            elif response.status_code == 404:
                logger.error(f"❌ Symbol {symbol} not found")
                return []
            else:
                logger.error(f"❌ Failed to get historical data for {symbol}: HTTP {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {str(e)}")
            return []
        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise
            logger.error(f"❌ Unexpected error: {str(e)}")
            return []

    def get_historical_data_multiple(self, symbols: List[str], **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get historical data for multiple symbols efficiently.
        
        Args:
            symbols: List of symbols to get data for
            **kwargs: Additional parameters passed to get_historical_data()
        
        Returns:
            Dict mapping symbol to historical data list
        """
        results = {}
        
        for symbol in symbols:
            try:
                logger.info(f"📊 Fetching historical data for {symbol}...")
                data = self.get_historical_data(symbol, **kwargs)
                results[symbol] = data
                
                if data:
                    logger.info(f"✅ Got {len(data)} records for {symbol}")
                else:
                    logger.warning(f"⚠️ No data for {symbol}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to get data for {symbol}: {e}")
                results[symbol] = []
        
        total_records = sum(len(data) for data in results.values())
        logger.info(f"📊 Total: {total_records} records across {len(symbols)} symbols")
        
        return results

    def validate_symbol_availability(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Check which symbols are available on the server.
        
        Args:
            symbols: List of symbols to check
            
        Returns:
            Dict mapping symbol to availability status
        """
        try:
            available_symbols = self.get_available_symbols()
            
            results = {}
            for symbol in symbols:
                symbol_upper = symbol.upper()
                is_available = symbol_upper in available_symbols
                results[symbol] = is_available
                
                if is_available:
                    logger.info(f"✅ {symbol} is available")
                else:
                    logger.warning(f"⚠️ {symbol} is not available")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to validate symbols: {e}")
            return {symbol: False for symbol in symbols}

    def get_datetime_range_for_symbol(self, symbol: str) -> Optional[Dict[str, str]]:
        """
        Get the datetime range available for a specific symbol.
        
        Args:
            symbol: Symbol to check
            
        Returns:
            Dict with 'start' and 'end' datetime strings, or None if failed
        """
        try:
            # Get first and last record to determine range
            first_record = self.get_historical_data(symbol, limit=1)
            
            if not first_record:
                return None
                
            # Get summary to find total records, then get last record
            summary = self.get_historical_summary()
            if not summary or symbol.upper() not in summary.get("symbol_counts", {}):
                return None
                
            # Get a large limit to get the last records
            all_data = self.get_historical_data(symbol, limit=10000)
            
            if all_data:
                return {
                    "start": first_record[0]["datetime"],
                    "end": all_data[-1]["datetime"],
                    "total_records": len(all_data)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get datetime range for {symbol}: {e}")
            return None

    def show_available_symbols_info(self) -> None:
        """
        Display detailed information about available symbols.
        """
        try:
            logger.info("📊 Getting symbol information...")
            summary = self.get_historical_summary()
            
            if not summary:
                logger.error("❌ Failed to get symbol summary")
                return
                
            symbols = summary.get("symbols", [])
            symbol_counts = summary.get("symbol_counts", {})
            
            logger.info(f"📈 Available Symbols ({len(symbols)} total):")
            logger.info("=" * 50)
            
            for symbol in sorted(symbols):
                count = symbol_counts.get(symbol, 0)
                logger.info(f"  📊 {symbol}: {count:,} records")
                
                # Get datetime range for each symbol
                try:
                    range_info = self.get_datetime_range_for_symbol(symbol)
                    if range_info:
                        logger.info(f"      📅 Range: {range_info['start']} to {range_info['end']}")
                    else:
                        logger.info(f"      📅 Range: Unable to determine")
                except:
                    logger.info(f"      📅 Range: Error getting range")
            
            logger.info("=" * 50)
            logger.info(f"📊 Total records across all symbols: {summary.get('total_records', 0):,}")
            
        except Exception as e:
            logger.error(f"❌ Failed to show symbol info: {e}")

    # WebSocket event handlers
    def _on_ws_open(self, ws):
        """Handle WebSocket connection open."""
        self.connected = True
        self.last_pong_time = time.time()
        logger.info("🔌 WebSocket connection opened")
        
        if self.on_connect:
            try:
                self.on_connect()
            except Exception as e:
                logger.error(f"Error in connect callback: {e}")

    def _on_ws_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            
            # Handle subscription responses
            if "status" in data:
                status = data.get("status")
                symbol = data.get("symbol")
                msg = data.get("message", "")
                
                if status == "success":
                    logger.info(f"✅ {msg} - Symbol: {symbol}")
                else:
                    logger.error(f"❌ {msg} - Symbol: {symbol}")
            
            # Handle market data
            elif "symbol" in data and "data" in data:
                tick_data = {
                    "symbol": data["symbol"],
                    "data": data["data"],
                    "timestamp": data.get("timestamp", ""),
                    "received_at": datetime.now()
                }
                
                if self.on_ticks:
                    try:
                        self.on_ticks(tick_data)
                    except Exception as e:
                        logger.error(f"Error in ticks callback: {str(e)}")
            
            # Handle batch data
            elif "ticks" in data:
                for tick in data["ticks"]:
                    tick_data = {
                        "symbol": tick["symbol"],
                        "data": tick["data"], 
                        "timestamp": tick.get("timestamp", ""),
                        "received_at": datetime.now()
                    }
                    
                    if self.on_ticks:
                        try:
                            self.on_ticks(tick_data)
                        except Exception as e:
                            logger.error(f"Error in ticks callback: {str(e)}")
            
            else:
                logger.debug(f"Received message: {message}")
                
        except json.JSONDecodeError:
            logger.error(f"Failed to parse message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def _on_ws_error(self, ws, error):
        """Handle WebSocket errors."""
        logger.error(f"❌ WebSocket error: {error}")
        
        if self.on_error:
            try:
                self.on_error(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    def _on_ws_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close."""
        self.connected = False
        logger.info("🔌 WebSocket connection closed")
        
        if self.on_disconnect:
            try:
                self.on_disconnect()
            except Exception as e:
                logger.error(f"Error in disconnect callback: {e}")
        
        # Auto-reconnect if enabled
        if self.auto_reconnect and self.running:
            self._attempt_reconnect()

    def _on_ws_ping(self, ws, data):
        """Handle incoming ping from server."""
        logger.debug("💓 Received ping from server")
        # Pong response is handled automatically by websocket-client

    def _on_ws_pong(self, ws, data):
        """Handle incoming pong from server."""
        logger.debug("💓 Received pong from server")
        self.last_pong_time = time.time()

    def _start_heartbeat(self):
        """Start the heartbeat thread."""
        # With the new implementation, heartbeat is handled by websocket-client
        # This method is kept for backward compatibility but doesn't start a separate thread
        if self.heartbeat_enabled:
            logger.info(f"💓 Using built-in websocket heartbeat (interval: {self.heartbeat_interval}s)")

    def _stop_heartbeat(self):
        """Stop the heartbeat thread."""
        # With the new implementation, heartbeat is handled by websocket-client
        # This method is kept for backward compatibility
        if self.heartbeat_enabled:
            logger.info("💓 Heartbeat will stop with connection")

    def _heartbeat_worker(self):
        """
        Legacy heartbeat worker - no longer used.
        Heartbeat is now handled by websocket-client's built-in ping functionality.
        """
        # This method is kept for backward compatibility but is no longer used
        pass

    def _attempt_reconnect(self):
        """Attempt to reconnect to WebSocket."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"❌ Max reconnect attempts ({self.max_reconnect_attempts}) reached")
            self._stop_event.set()  # Signal to stop the run loop
            return
            
        self.reconnect_attempts += 1
        logger.info(f"🔄 Attempting to reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        time.sleep(self.reconnect_interval)
        
        if self.ws_connect():
            # Re-subscribe to current symbols if any
            if self.subscribed_symbols:
                symbols_to_resubscribe = list(self.subscribed_symbols)
                self.subscribed_symbols.clear()  # Clear before re-subscribing
                self.subscribe_multiple(symbols_to_resubscribe)

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected

    def get_subscribed_symbols(self) -> Set[str]:
        """Get set of currently subscribed symbols."""
        return self.subscribed_symbols.copy()

    def get_current_symbol(self) -> Optional[str]:
        """Get currently subscribed symbol (for backward compatibility)."""
        # Return the first symbol if any are subscribed, None otherwise
        return next(iter(self.subscribed_symbols)) if self.subscribed_symbols else None

    def is_subscribed(self, symbol: str) -> bool:
        """Check if subscribed to a specific symbol."""
        return symbol.upper() in self.subscribed_symbols

    def get_subscription_count(self) -> int:
        """Get the number of active subscriptions."""
        return len(self.subscribed_symbols)

    def set_log_level(self, level: str):
        """Set logging level."""
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        if level.upper() in log_levels:
            logger.setLevel(log_levels[level.upper()])

    def add_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Add new symbols to existing subscriptions.
        
        Args:
            symbols: List of new symbols to add
            
        Returns:
            Dict[str, bool]: Dictionary mapping symbol to subscription success status
        """
        # Filter out already subscribed symbols
        new_symbols = [s for s in symbols if s.upper() not in self.subscribed_symbols]
        
        if not new_symbols:
            logger.info("ℹ️ All symbols already subscribed")
            return {symbol: True for symbol in symbols}
            
        return self.subscribe_multiple(new_symbols)

    def remove_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Remove symbols from current subscriptions.
        
        Args:
            symbols: List of symbols to remove
            
        Returns:
            Dict[str, bool]: Dictionary mapping symbol to unsubscription success status
        """
        return self.unsubscribe_multiple(symbols)

    def replace_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Replace all current subscriptions with new symbols.
        
        Args:
            symbols: List of symbols to subscribe to (replaces all current)
            
        Returns:
            Dict[str, bool]: Dictionary mapping symbol to subscription success status
        """
        # Unsubscribe from all current symbols
        if self.subscribed_symbols:
            self.unsubscribe_feed()  # Unsubscribe from all
            
        # Subscribe to new symbols
        return self.subscribe_multiple(symbols)

    def get_heartbeat_status(self) -> Dict[str, Any]:
        """
        Get heartbeat status information.
        
        Returns:
            Dict containing heartbeat configuration and status
        """
        return {
            "enabled": self.heartbeat_enabled,
            "interval": self.heartbeat_interval,
            "timeout": self.ping_timeout,
            "last_pong": self.last_pong_time,
            "implementation": "built-in websocket-client ping/pong",
            "connected": self.connected
        }

    def set_heartbeat_config(self, enabled: bool = True, interval: int = 25, timeout: int = 10):
        """
        Configure heartbeat settings.
        
        Args:
            enabled: Whether to enable heartbeat/ping
            interval: Seconds between ping messages (default 25s, server expects within 30s)
            timeout: Seconds to wait for pong response before considering connection dead
        """
        self.heartbeat_enabled = enabled
        self.heartbeat_interval = interval
        self.ping_timeout = timeout
        logger.info(f"💓 Heartbeat configured: enabled={enabled}, interval={interval}s, timeout={timeout}s")

    def _run_websocket_with_ping(self):
        """Run WebSocket with ping/pong in an interruptible way."""
        try:
            # Check if we should stop before even starting
            while self.running and not self._stop_event.is_set():
                try:
                    # Run with a shorter timeout so we can check stop event more often
                    self.ws.run_forever(
                        ping_interval=self.heartbeat_interval,
                        ping_timeout=self.ping_timeout,
                        ping_payload="ping"
                    )
                    break  # If run_forever exits normally, break the loop
                except Exception as e:
                    if self._stop_event.is_set() or not self.running:
                        break  # Exit if stop was requested
                    logger.error(f"WebSocket error, retrying: {e}")
                    if self.auto_reconnect:
                        time.sleep(1)
                    else:
                        break
        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"WebSocket thread error: {e}")
        finally:
            logger.debug("WebSocket thread with ping exiting")

    def _run_websocket_simple(self):
        """Run WebSocket without ping in an interruptible way."""
        try:
            # Check if we should stop before even starting
            while self.running and not self._stop_event.is_set():
                try:
                    self.ws.run_forever()
                    break  # If run_forever exits normally, break the loop
                except Exception as e:
                    if self._stop_event.is_set() or not self.running:
                        break  # Exit if stop was requested
                    logger.error(f"WebSocket error, retrying: {e}")
                    if self.auto_reconnect:
                        time.sleep(1)
                    else:
                        break
        except Exception as e:
            if not self._stop_event.is_set():
                logger.error(f"WebSocket thread error: {e}")
        finally:
            logger.debug("WebSocket thread exiting")

    def _create_interruptible_dispatcher(self):
        """Create a dispatcher that can be interrupted by the stop event."""
        # This approach doesn't work well with websocket-client library
        # Let's use the WebSocket's built-in close mechanism instead
        pass

    def force_shutdown(self):
        """Force immediate shutdown of all components."""
        logger.info("🚨 Force shutdown initiated...")
        
        # Set all stop flags immediately
        self._stop_event.set()
        self.running = False
        self.auto_reconnect = False
        self.connected = False
        
        # Force close WebSocket without waiting
        if self.ws:
            try:
                self.ws.close()
                self.ws.keep_running = False  # Force websocket-client to stop
            except:
                pass  # Ignore any errors during force close
        
        # Don't wait for thread - just mark it as done
        self.ws = None
        self.ws_thread = None
        self.subscribed_symbols.clear()
        
        logger.info("🚨 Force shutdown completed")

    def authenticate(self, username: str) -> bool:
        """
        Authenticate the client using a username.
        
        Args:
            username: Username for authentication
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            token = self.get_token(username)
            return token is not None
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def keep_alive(self, timeout: Optional[float] = None):
        """
        Keep the program alive to receive WebSocket data.
        Call this after ws_connect() and subscribe to keep receiving data.
        
        Args:
            timeout: Maximum time to keep alive in seconds (None = indefinitely)
            
        Example:
            client.on_ticks = handle_data
            client.ws_connect()
            client.subscribe_multiple(["NIFTY", "RELIANCE"])
            client.keep_alive()  # Keeps program alive to receive data
        """
        if not self.connected:
            logger.error("❌ Not connected. Call ws_connect() first")
            return
            
        logger.info("🚀 Keeping program alive to receive data... Press Ctrl+C to stop")
        
        try:
            if timeout:
                self._stop_event.wait(timeout)
            else:
                # Run until stop event is set
                self._stop_event.wait()
                
        except KeyboardInterrupt:
            logger.info("🛑 Interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"❌ Error while keeping alive: {e}")
            self.stop()


# Convenience function for quick setup
def create_client(ws_uri: str = "ws://localhost:8080", 
                 api_uri: str = "http://localhost:3000",
                 token: Optional[str] = None,
                 username: Optional[str] = None) -> NSEClient:
    """
    Create NSE client with default settings.
    
    Args:
        ws_uri: WebSocket URI
        api_uri: REST API URI  
        token: JWT token (will try to load from file if not provided)
        username: Username for authentication (optional, used if no token provided)
        
    Returns:
        NSEClient: Configured client instance
    """
    if not token:
        # Try to load token from file
        try:
            with open("test_tokens.json", "r") as f:
                tokens = json.load(f)
                token = list(tokens.values())[0]
                print(f"🔑 Loaded token for user: {list(tokens.keys())[0]}")
        except:
            # Use hardcoded token as fallback
            token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImp0aSI6ImMzOWY4NzgzLWFmZTYtNDk5Zi1hNTg1LWRjYTkxNjk1ZjFhZCIsImV4cCI6MTc0ODk2OTYyNiwiaWF0IjoxNzQ4OTYyNDI2LCJ1c2VyX2lkIjoiYWRtaW4iLCJwZXJtaXNzaW9ucyI6WyJyZWFkX2RhdGEiLCJ3ZWJzb2NrZXRfY29ubmVjdCIsImFkbWluIl19.PTCECjo-wCdr9Tgp6bRYR2bcrBtv7uZzr6N4z7L-TkU"
            print("🔑 Using default token")
    
    client = NSEClient(ws_uri, api_uri, token)
    
    # Authenticate if username provided and no token
    if not token and username:
        if not client.authenticate(username):
            raise AuthenticationError(f"Failed to authenticate user: {username}")
    
    return client


if __name__ == "__main__":
    # Example usage
    print("NSE Socket Client Library")
    print("=" * 40)
    
    # Create client
    client = create_client()
    
    # Configure event handlers
    def handle_market_data(data):
        symbol = data["symbol"]
        price_data = data["data"]
        print(f"{symbol}: Price=${price_data['close']:.2f}, Volume={price_data['volume']:,}")
    
    def handle_connection():
        print("Market data connection established")
    
    def handle_disconnection():
        print("Market data connection lost")
    
    def handle_order_update(order):
        print(f"Order {order['id']}: {order['status']}")
    
    # Assign event handlers
    client.on_ticks = handle_market_data
    client.on_connect = handle_connection
    client.on_disconnect = handle_disconnection
    client.on_order_update = handle_order_update
    
    # Method 1: Connect and subscribe in one call, then run
    symbols = ["NIFTY", "INDIGO", "RELIANCE", "TCS", "HDFC"]
    if client.connect_and_subscribe(symbols):
        print("🚀 Streaming data for multiple symbols... Press Ctrl+C to stop")
        client.run()  # This blocks until stopped
    else:
        print("❌ Failed to connect and subscribe") 