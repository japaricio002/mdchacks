import alpaca_trade_api as tradeapi
import psycopg2
from psycopg2 import sql

API_KEY = os.getenv('APCA_API_KEY_ID')
SECRET_KEY = os.getenv('APCA_API_SECRET_KEY')
BASE_URL = "https://paper-api.alpaca.markets"  # Use this for the paper trading environment

# PostgreSQL credentials
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "alpaca_data"
DB_USER = "postgres"
DB_PASSWORD = "secretpass"

# Initialize the Alpaca API
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def get_all_stocks():
    """Fetch all tradable stocks from Alpaca API."""
    try:
        # Get all available assets
        assets = api.list_assets()

        # Filter for stocks that are tradable
        tradable_stocks = [
            {"symbol": asset.symbol, "name": asset.name, "exchange": asset.exchange}
            for asset in assets if asset.tradable
        ]
        print(f"Total tradable stocks found: {len(tradable_stocks)}")
        return tradable_stocks
    except Exception as e:
        print(f"An error occurred while fetching stocks: {e}")
        return []

def insert_stocks_into_db(stocks):
    """Insert stock data into PostgreSQL table."""
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS available_stock (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            name TEXT NOT NULL,
            exchange VARCHAR(20) NOT NULL
        );
        """
        cursor.execute(create_table_query)
        conn.commit()

        # Insert stock data with duplicate check
        insert_query = """
        INSERT INTO available_stock (symbol, name, exchange)
        VALUES (%s, %s, %s)
        ON CONFLICT (symbol) DO NOTHING; -- Use symbol as a unique identifier
        """
        for stock in stocks:
            cursor.execute(insert_query, (stock["symbol"], stock["name"], stock["exchange"]))

        # Commit the changes and close the connection
        conn.commit()
        print(f"Inserted {len(stocks)} stocks into the database.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred while inserting stocks into the database: {e}")


if __name__ == "__main__":
    # Fetch stocks and insert into the database
    stocks = get_all_stocks()
    if stocks:
        insert_stocks_into_db(stocks)
