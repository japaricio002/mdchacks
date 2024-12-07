import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict

class BollingerBandsBacktest:
    def __init__(self, 
                 db_params: Dict[str, str],
                 symbol: str,
                 start_date: str,
                 end_date: str,
                 window: int = 20,
                 num_std: float = 2.0,
                 initial_capital: float = 100000.0):
        """
        Initialize the Bollinger Bands backtest strategy
        
        Args:
            db_params: Database connection parameters
            symbol: Trading symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            window: Moving average window
            num_std: Number of standard deviations for bands
            initial_capital: Starting capital for backtest
        """
        self.db_params = db_params
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.window = window
        self.num_std = num_std
        self.initial_capital = initial_capital
        self.positions = 0
        self.capital = initial_capital
        self.trades: List[Dict] = []
        
    def fetch_data(self) -> pd.DataFrame:
        """Fetch data from PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_params)
            query = """
                SELECT timestamp, close_price, volume
                FROM trading_info
                WHERE symbol = %s
                AND timestamp BETWEEN %s AND %s
                ORDER BY timestamp ASC
            """
            
            df = pd.read_sql_query(
                query,
                conn,
                params=(self.symbol, self.start_date, self.end_date)
            )
            conn.close()
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands indicators"""
        df['SMA'] = df['close_price'].rolling(window=self.window).mean()
        df['STD'] = df['close_price'].rolling(window=self.window).std()
        df['Upper_Band'] = df['SMA'] + (df['STD'] * self.num_std)
        df['Lower_Band'] = df['SMA'] - (df['STD'] * self.num_std)
        df['Position'] = 0  # Initialize position column
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on Bollinger Bands"""
        # Buy signal: price crosses below lower band
        df.loc[df['close_price'] < df['Lower_Band'], 'Position'] = 1
        
        # Sell signal: price crosses above upper band
        df.loc[df['close_price'] > df['Upper_Band'], 'Position'] = -1
        
        return df
    
    def execute_backtest(self) -> Tuple[pd.DataFrame, Dict]:
        """Execute the backtest and return results"""
        # Fetch and prepare data
        df = self.fetch_data()
        if df.empty:
            raise ValueError("No data available for backtest")
        
        # Calculate indicators and signals
        df = self.calculate_indicators(df)
        df = self.generate_signals(df)
        
        # Initialize results tracking
        df['Returns'] = df['close_price'].pct_change()
        df['Strategy_Returns'] = 0.0
        df['Capital'] = self.initial_capital
        
        # Execute trades
        current_position = 0
        
        for i in range(1, len(df)):
            if df['Position'].iloc[i] != 0 and df['Position'].iloc[i] != current_position:
                # Close existing position if any
                if current_position != 0:
                    returns = (df['close_price'].iloc[i] - entry_price) / entry_price
                    self.capital *= (1 + returns * current_position)
                    self.trades.append({
                        'exit_date': df['timestamp'].iloc[i],
                        'exit_price': df['close_price'].iloc[i],
                        'returns': returns,
                        'type': 'sell' if current_position > 0 else 'buy'
                    })
                
                # Open new position
                current_position = df['Position'].iloc[i]
                entry_price = df['close_price'].iloc[i]
                self.trades.append({
                    'entry_date': df['timestamp'].iloc[i],
                    'entry_price': entry_price,
                    'type': 'buy' if current_position > 0 else 'sell'
                })
            
            df.loc[df.index[i], 'Capital'] = self.capital
            if current_position != 0:
                df.loc[df.index[i], 'Strategy_Returns'] = df['Returns'].iloc[i] * current_position
        
        # Calculate strategy performance metrics
        results = self.calculate_performance_metrics(df)
        
        return df, results
    
    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate strategy performance metrics"""
        total_return = (self.capital - self.initial_capital) / self.initial_capital
        strategy_returns = df['Strategy_Returns'].dropna()
        
        results = {
            'Total Return (%)': round(total_return * 100, 2),
            'Annual Return (%)': round(total_return / (len(df) / 252) * 100, 2),
            'Sharpe Ratio': round(np.sqrt(252) * strategy_returns.mean() / strategy_returns.std(), 2),
            'Max Drawdown (%)': round(self.calculate_max_drawdown(df) * 100, 2),
            'Number of Trades': len(self.trades),
            'Win Rate (%)': self.calculate_win_rate(),
            'Profit Factor': self.calculate_profit_factor()
        }
        
        return results
    
    def calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        rolling_max = df['Capital'].expanding().max()
        drawdowns = df['Capital'] / rolling_max - 1
        return abs(drawdowns.min())
    
    def calculate_win_rate(self) -> float:
        """Calculate win rate of trades"""
        if not self.trades:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trades if 
                           'returns' in trade and trade['returns'] > 0)
        return round(winning_trades / (len(self.trades) / 2) * 100, 2)
    
    def calculate_profit_factor(self) -> float:
        """Calculate profit factor"""
        profits = sum(trade['returns'] for trade in self.trades if 
                     'returns' in trade and trade['returns'] > 0)
        losses = sum(abs(trade['returns']) for trade in self.trades if 
                    'returns' in trade and trade['returns'] < 0)
        
        return round(profits / losses if losses != 0 else float('inf'), 2)
    
    def plot_results(self, df: pd.DataFrame) -> None:
        """Plot backtest results including price, Bollinger Bands, and capital"""
        plt.figure(figsize=(15, 10))
        
        # Plot price and Bollinger Bands
        plt.subplot(2, 1, 1)
        plt.plot(df['timestamp'], df['close_price'], label='Price')
        plt.plot(df['timestamp'], df['Upper_Band'], 'r--', label='Upper Band')
        plt.plot(df['timestamp'], df['Lower_Band'], 'g--', label='Lower Band')
        plt.plot(df['timestamp'], df['SMA'], 'y-', label='SMA')
        plt.fill_between(df['timestamp'], df['Upper_Band'], df['Lower_Band'], alpha=0.1)
        plt.title(f'Bollinger Bands Strategy - {self.symbol}')
        plt.legend()
        
        # Plot capital
        plt.subplot(2, 1, 2)
        plt.plot(df['timestamp'], df['Capital'], label='Portfolio Value')
        plt.title('Portfolio Value Over Time')
        plt.legend()
        
        plt.tight_layout()
        plt.show()

def main():
    # Database connection parameters
    db_params = {
        "host": "localhost",
        "port": 5432,
        "database": "alpaca_data",
        "user": "postgres",
        "password": "secretpass"
    }
    
    # Backtest parameters
    symbol = "AAPL"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    # Initialize and run backtest
    backtest = BollingerBandsBacktest(
        db_params=db_params,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        window=20,
        num_std=2.0,
        initial_capital=100000.0
    )
    
    try:
        df, results = backtest.execute_backtest()
        
        # Print results
        print("\nBacktest Results:")
        print("=" * 40)
        for metric, value in results.items():
            print(f"{metric}: {value}")
        
        # Plot results
        backtest.plot_results(df)
        
    except Exception as e:
        print(f"Error during backtest: {e}")

if __name__ == "__main__":
    main()