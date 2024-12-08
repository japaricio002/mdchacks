import websocket
import json
import os
# Replace with your Alpaca API credentials
API_KEY = os.getenv('APCA_API_KEY_ID')
SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')

# Updated WebSocket URL for crypto data
CRYPTO_STREAM_URL = "wss://stream.data.alpaca.markets/v1beta3/crypto/us"

def on_open(ws):
    print("WebSocket opened.")
    auth_message = {
        "action": "auth",
        "key": API_KEY,
        "secret": SECRET_KEY
    }
    ws.send(json.dumps(auth_message))

    # Subscribe to multiple crypto pairs
    subscribe_message = {
        "action": "subscribe",
        "trades": ["BTC/USD", "ETH/USD", "LTC/USD"],  # Add more pairs as needed
    }
    ws.send(json.dumps(subscribe_message))


def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")

def start_stream():
    ws = websocket.WebSocketApp(
        CRYPTO_STREAM_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

if __name__ == "__main__":
    start_stream()
