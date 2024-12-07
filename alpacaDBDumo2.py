import requests
import psycopg2
from datetime import datetime, timedelta
import time

# Alpaca API credentials
API_KEY = ""
API_SECRET = ""
BASE_URL = "https://data.alpaca.markets/v2"

# PostgreSQL connection details
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "alpaca_data"
DB_USER = "postgres"
DB_PASSWORD = "secretpass"

def get_last_id():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM trading_info")
        last_id = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return last_id if last_id is not None else 0
    except Exception as e:
        print(f"Error getting last ID: {e}")
        return 0

def fetch_trading_data(symbol, start_date, end_date, page_token=None):
    url = f"{BASE_URL}/stocks/{symbol}/bars"
    params = {
        "start": f"{start_date}T09:00:00Z",
        "end": f"{end_date}T16:00:00Z",
        "timeframe": "1Min",
        "limit": 10000  # Maximum allowed by Alpaca
    }
    if page_token:
        params["page_token"] = page_token
        
    headers = {
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET,
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def insert_into_postgres(data, symbol, start_id):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        current_id = start_id
        for record in data:
            current_id += 1
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
                    id, symbol, timestamp, open_price, high_price, low_price, close_price,
                    number_of_trades, volume, volume_weighted_average_price
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    current_id, symbol, timestamp, open_price, high_price, low_price,
                    close_price, number_of_trades, volume, volume_weighted_average_price
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return current_id
    except Exception as e:
        print(f"Database error: {e}")
        return start_id

def main():
    symbol = "AAPL"
    start_date = "2023-01-01"  # Replace with your start date
    end_date = "2024-01-01"    # Replace with your end date
    
    print(f"Fetching trading data for {symbol} from {start_date} to {end_date}...")
    
    # Get the last ID from the database
    last_id = get_last_id()
    current_id = last_id
    
    page_token = None
    total_records = 0
    
    while True:
        # Add delay to respect rate limits
        time.sleep(0.5)
        
        # Fetch data with pagination
        response = fetch_trading_data(symbol, start_date, end_date, page_token)
        
        if not response or not response.get("bars"):
            break
            
        data = response["bars"]
        total_records += len(data)
        print(f"Processing {len(data)} records...")
        
        # Insert data and get the last used ID
        current_id = insert_into_postgres(data, symbol, current_id)
        
        # Check if there's more data to fetch
        page_token = response.get("next_page_token")
        if not page_token:
            break
    
    print(f"Completed! Total records processed: {total_records}")

if __name__ == "__main__":
    main()