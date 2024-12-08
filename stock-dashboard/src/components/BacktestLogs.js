import React from 'react';
import './Backtest.css';

const BacktestLogs = ({ logs }) => {
  return (
    <div className="logs-container">
      <h2>Historical Backtest Logs</h2>
      <table className="logs-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Annual Return (%)</th>
            <th>Number of Trades</th>
            <th>Profit Factor</th>
            <th>Sharpe Ratio</th>
            <th>Total Return (%)</th>
            <th>Win Rate (%)</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr key={log.id}>
              <td>{log.id}</td>
              <td>{log.annual_return}</td>
              <td>{log.number_of_trades}</td>
              <td>{log.profit_factor}</td>
              <td>{log.sharpe_ratio}</td>
              <td>{log.total_return}</td>
              <td>{log.win_rate}</td>
              <td>{new Date(log.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default BacktestLogs;
