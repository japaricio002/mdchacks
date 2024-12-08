import pandas as pd
import numpy as np
import psycopg2
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
from datetime import datetime

class MACrossoverBacktest:
    def __init__(self,
                 db_params: Dict[str, str],
                 symbol: str,
                 start_date: str,
                 end_date: str,
                 fast_window: int = 10,
                 slow_window: int = 30,
                 initial_capital: float = 100000.0):
        """
        Initialize the Moving Average Crossover backtest strategy
        
        Args:
            db_params: Database connection parameters
            symbol: Trading symbol
            start_date: Start date for backtest
            end_date: End date for backtest
            fast_window: Fast moving average period
            slow_window: Slow moving average period
            initial_capital: Starting capital for backtest
        """
        self.db_params = db_params
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.initial_capital = initial_capital
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
        """Calculate moving averages"""
        df['Fast_MA'] = df['close_price'].rolling(window=self.fast_window).mean()
        df['Slow_MA'] = df['close_price'].rolling(window=self.slow_window).mean()
        df['Position'] = 0
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on MA crossover"""
        # Buy signal: fast MA crosses above slow MA
        df['Signal'] = np.where(df['Fast_MA'] > df['Slow_MA'], 1, -1)
        
        # Only generate signal on crossover
        df['Position'] = df['Signal'].diff()
        
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
        position = 0
        entry_price = 0
        
        for i in range(1, len(df)):
            if df['Position'].iloc[i] != 0:
                if df['Position'].iloc[i] > 0:  # Buy signal
                    if position == 0:
                        position = 1
                        entry_price = df['close_price'].iloc[i]
                        self.trades.append({
                            'entry_date': df['timestamp'].iloc[i],
                            'entry_price': entry_price,
                            'type': 'buy'
                        })
                elif df['Position'].iloc[i] < 0:  # Sell signal
                    if position == 1:
                        position = 0
                        exit_price = df['close_price'].iloc[i]
                        returns = (exit_price - entry_price) / entry_price
                        self.capital *= (1 + returns)
                        self.trades.append({
                            'exit_date': df['timestamp'].iloc[i],
                            'exit_price': exit_price,
                            'returns': returns,
                            'type': 'sell'
                        })
            
            df.loc[df.index[i], 'Capital'] = self.capital
            if position == 1:
                df.loc[df.index[i], 'Strategy_Returns'] = df['Returns'].iloc[i]
        
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
            'Number of Trades': len(self.trades) // 2,
            'Win Rate (%)': self.calculate_win_rate(),
            'Average Trade Duration': self.calculate_avg_trade_duration(),
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
    
    def calculate_avg_trade_duration(self) -> str:
        """Calculate average trade duration"""
        durations = []
        for i in range(0, len(self.trades) - 1, 2):
            entry_date = pd.to_datetime(self.trades[i]['entry_date'])
            exit_date = pd.to_datetime(self.trades[i + 1]['exit_date'])
            duration = exit_date - entry_date
            durations.append(duration)
        
        if durations:
            avg_duration = sum(durations, pd.Timedelta(0)) / len(durations)
            return str(avg_duration)
        return "N/A"
    
    def plot_results(self, df: pd.DataFrame) -> None:
        """Plot backtest results"""
        plt.figure(figsize=(15, 10))
        
        # Plot price and moving averages
        plt.subplot(2, 1, 1)
        plt.plot(df['timestamp'], df['close_price'], label='Price')
        plt.plot(df['timestamp'], df['Fast_MA'], 'r--', label=f'{self.fast_window}-day MA')
        plt.plot(df['timestamp'], df['Slow_MA'], 'g--', label=f'{self.slow_window}-day MA')
        
        # Plot buy and sell signals
        buy_signals = df[df['Position'] > 0]
        sell_signals = df[df['Position'] < 0]
        plt.scatter(buy_signals['timestamp'], buy_signals['close_price'], 
                   marker='^', color='g', label='Buy Signal')
        plt.scatter(sell_signals['timestamp'], sell_signals['close_price'], 
                   marker='v', color='r', label='Sell Signal')
        
        plt.title(f'Moving Average Crossover Strategy - {self.symbol}')
        plt.legend()
        
        # Plot portfolio value
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
    backtest = MACrossoverBacktest(
        db_params=db_params,
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        fast_window=10,
        slow_window=30,
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