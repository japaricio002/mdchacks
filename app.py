from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from bollinger_bands_backtest import BollingerBandsBacktest
from moving_average_crossover import MACrossoverBacktest


import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:secretpass@localhost/alpaca_data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the trading_info table
class TradingInfo(db.Model):
    __tablename__ = 'trading_info'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    number_of_trades = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Float, nullable=False)
    volume_weighted_average_price = db.Column(db.Float, nullable=False)

class BacktestLog(db.Model):
    __tablename__ = 'backtest_log'
    id = db.Column(db.Integer, primary_key=True)
    annual_return = db.Column(db.Numeric(10, 2), nullable=False)
    number_of_trades = db.Column(db.Integer, nullable=False)
    profit_factor = db.Column(db.Numeric(10, 2), nullable=False)
    sharpe_ratio = db.Column(db.Numeric(6, 3), nullable=False)
    total_return = db.Column(db.Numeric(10, 2), nullable=False)
    win_rate = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/api/stocks', methods=['GET'])
def get_stock_data():
    symbol = request.args.get('symbol')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not symbol or not start_date or not end_date:
        return jsonify({"error": "Missing query parameters"}), 400
    
    data = TradingInfo.query.filter(
        TradingInfo.symbol == symbol,
        TradingInfo.timestamp >= start_date,
        TradingInfo.timestamp <= end_date
    ).all()
    
    result = [
        {
            "timestamp": item.timestamp,
            "open_price": item.open_price,
            "high_price": item.high_price,
            "low_price": item.low_price,
            "close_price": item.close_price,
            "number_of_trades": item.number_of_trades,
            "volume": item.volume,
            "volume_weighted_average_price": item.volume_weighted_average_price
        }
        for item in data
    ]
    
    return jsonify(result)
@app.route('/api/backtest/bollinger', methods=['POST'])
def bollinger_backtest():
    try:
        data = request.json
        db_params = {
            "host": "localhost",
            "port": 5432,
            "database": "alpaca_data",
            "user": "postgres",
            "password": "secretpass"
        }
        
        backtest = BollingerBandsBacktest(
            db_params=db_params,
            symbol=data.get('symbol'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            window=int(data.get('window', 20)),
            num_std=float(data.get('num_std', 2.0)),
            initial_capital=float(data.get('initial_capital', 100000.0))
        )
        
        df, results = backtest.execute_backtest()

        # Log the results into the database
        log = BacktestLog(
            annual_return=results.get('Annual Return (%)', 0),
            number_of_trades=results.get('Number of Trades', 0),
            profit_factor=results.get('Profit Factor', 0),
            sharpe_ratio=results.get('Sharpe Ratio', 0),
            total_return=results.get('Total Return (%)', 0),
            win_rate=results.get('Win Rate (%)', 0),
        )
        db.session.add(log)
        db.session.commit()

        return jsonify({
            "success": True,
            "results": results,
            "trades": backtest.trades
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backtest/logs', methods=['GET'])
def get_backtest_logs():
    logs = BacktestLog.query.order_by(BacktestLog.created_at.desc()).all()
    log_list = [
        {
            "id": log.id,
            "annual_return": float(log.annual_return) if log.annual_return is not None else 0.0,
            "number_of_trades": log.number_of_trades if log.number_of_trades is not None else 0,
            "profit_factor": float(log.profit_factor) if log.profit_factor is not None else 0.0,
            "sharpe_ratio": float(log.sharpe_ratio) if log.sharpe_ratio is not None else 0.0,
            "total_return": float(log.total_return) if log.total_return is not None else 0.0,
            "win_rate": float(log.win_rate) if log.win_rate is not None else 0.0,
            "created_at": log.created_at
        }
        for log in logs
    ]
    return jsonify(log_list)


@app.route('/api/backtest/moving_average', methods=['POST'])
def moving_average_backtest():
    try:
        data = request.json
        db_params = {
            "host": "localhost",
            "port": 5432,
            "database": "alpaca_data",
            "user": "postgres",
            "password": "secretpass"
        }
        
        backtest = MACrossoverBacktest(
            db_params=db_params,
            symbol=data.get('symbol'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            fast_window=int(data.get('fast_window', 10)),
            slow_window=int(data.get('slow_window', 30)),
            initial_capital=float(data.get('initial_capital', 100000.0))
        )
        
        df, results = backtest.execute_backtest()

        # Log the results into the database
        log = BacktestLog(
            annual_return=results.get('Annual Return (%)', 0),
            number_of_trades=results.get('Number of Trades', 0),
            profit_factor=results.get('Profit Factor', 0),
            sharpe_ratio=results.get('Sharpe Ratio', 0),
            total_return=results.get('Total Return (%)', 0),
            win_rate=results.get('Win Rate (%)', 0),
        )
        db.session.add(log)
        db.session.commit()
        return jsonify({
            "success": True,
            "results": results,
            "trades": backtest.trades
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

class AvailableStock(db.Model):
    __tablename__ = 'available_stock'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String, nullable=False)

@app.route('/api/stocks/symbols', methods=['GET'])
def get_stock_symbols():
    symbols = db.session.query(AvailableStock.symbol).distinct().all()
    symbol_list = [symbol[0] for symbol in symbols]
    return jsonify(symbol_list)



if __name__ == '__main__':
    app.run(port=4000)
