import alpaca_trade_api as tradeapi
import websocket
import json
import os

# Replace with your Alpaca API credentials
API_KEY = os.getenv('APCA_API_KEY_ID')
SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = "https://paper-api.alpaca.markets"  # For paper trading; use "https://api.alpaca.markets" for live trading
DATA_STREAM_URL = "wss://stream.data.alpaca.markets/v2/iex"  # Use IEX or SIP based on your subscription
print(API_KEY)
# Callback functions for WebSocket
def on_open(ws):
    print("WebSocket opened.")
    # Authenticate and subscribe to a stream
    auth_message = {
        "action": "auth",
        "key": API_KEY,
        "secret": SECRET_KEY
    }
    ws.send(json.dumps(auth_message))

    # Subscribe to trade updates for specific symbols
    subscribe_message = {
        "action": "subscribe",
        "trades": ["AAPL", "MSFT"],  # Replace with symbols you're interested in
    }
    ws.send(json.dumps(subscribe_message))

def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")

# Initialize WebSocket connection
def start_stream():
    ws = websocket.WebSocketApp(
        DATA_STREAM_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    start_stream()
