import requests
import psycopg2
from datetime import datetime, timedelta

# Alpaca API credentials
API_KEY = os.getenv('APCA_API_KEY_ID')
API_SECRET = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = "https://data.alpaca.markets/v2"

# PostgreSQL connection details
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "alpaca_data"
DB_USER = "postgres"
DB_PASSWORD = "secretpass"

# Function to fetch trading data
def fetch_trading_data(symbol, start_date, end_date):
    url = f"{BASE_URL}/stocks/{symbol}/bars"
    params = {
        "start": f"{start_date}T09:00:00Z",
        "end": f"{end_date}T16:00:00Z",
        "timeframe": "1Min",
    }
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("bars", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Function to insert data into PostgreSQL
def insert_into_postgres(data, symbol):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        for record in data:
            timestamp = datetime.strptime(record["t"], "%Y-%m-%dT%H:%M:%SZ")
            open_price = record["o"]
            high_price = record["h"]
            low_price = record["l"]
            close_price = record["c"]
            number_of_trades = record["n"]
            volume = record["v"]
            volume_weighted_average_price = record["vw"]
            
            cursor.execute(
                """
                INSERT INTO trading_info (
                    symbol, timestamp, open_price, high_price, low_price, close_price,
                    number_of_trades, volume, volume_weighted_average_price
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    symbol, timestamp, open_price, high_price, low_price, close_price,
                    number_of_trades, volume, volume_weighted_average_price
                )
            )
        conn.commit()
        cursor.close()
        conn.close()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Database error: {e}")

# Main function
def main():
    symbol = "AAPL"
    start_date = "2023-01-01"  # Replace with your start date
    end_date = "2024-01-01"    # Replace with your end date
    
    print(f"Fetching trading data for {symbol} from {start_date} to {end_date}...")
    data = fetch_trading_data(symbol, start_date, end_date)
    if data:
        print(f"Inserting data into PostgreSQL for {symbol}...")
        insert_into_postgres(data, symbol)
    else:
        print("No data retrieved.")

if __name__ == "__main__":
    main()
