import alpaca_trade_api as tradeapi
import os
# Alpaca API credentials
API_KEY = os.getenv('APCA_API_KEY_ID')
SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = "https://paper-api.alpaca.markets"  # Use this for paper trading; use https://api.alpaca.markets for live trading

# Initialize Alpaca API client
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL)

def get_latest_price(symbol):
    try:
        # Get the latest trade data for the symbol
        latest_trade = api.get_latest_trade(symbol)
        print(f"Symbol: {symbol}")
        print(f"Price: ${latest_trade.price}")
        print(f"Timestamp: {latest_trade.timestamp}")
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")

# Replace 'AAPL' with the stock symbol you want to check
get_latest_price("AAPL")
