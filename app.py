from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from bollinger_bands_backtest import BollingerBandsBacktest
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
@app.route('/api/backtest', methods=['POST'])
def backtest():
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
        return jsonify({
            "success": True,
            "results": results,
            "trades": backtest.trades
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=4000)
