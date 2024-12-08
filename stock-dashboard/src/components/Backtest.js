import React, { useState } from 'react';
import './Backtest.css';

const Backtest = () => {
  const [strategy, setStrategy] = useState("Bollinger Bands");
  const [form, setForm] = useState({
    symbol: '',
    start_date: '',
    end_date: '',
    window: 20,
    num_std: 2.0,
    fast_window: 10,
    slow_window: 30,
    initial_capital: 100000.0,
  });

  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleStrategyChange = (e) => {
    setStrategy(e.target.value);
    setResults(null); // Clear results on strategy change
    setError(null);   // Clear error on strategy change
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResults(null);

    let endpoint;
    if (strategy === "Bollinger Bands") {
      endpoint = 'http://localhost:4000/api/backtest/bollinger';
    } else if (strategy === "Moving Average Crossover") {
      endpoint = 'http://localhost:4000/api/backtest/moving_average';
    }

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const data = await response.json();
      if (data.success) {
        setResults(data.results);
      } else {
        setError(data.error);
      }
    } catch (err) {
      setError('Error connecting to the server');
    }
  };

  return (
    <div className="backtest-container">
      <h1 className="title">Trading Strategy Backtest</h1>
      <form className="backtest-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Strategy:</label>
          <select value={strategy} onChange={handleStrategyChange}>
            <option value="Bollinger Bands">Bollinger Bands</option>
            <option value="Moving Average Crossover">Moving Average Crossover</option>
          </select>
        </div>
        <div className="form-group">
          <label>Symbol:</label>
          <input
            type="text"
            name="symbol"
            value={form.symbol}
            onChange={handleChange}
            placeholder="Enter a trading symbol"
            required
          />
        </div>
        <div className="form-group">
          <label>Start Date:</label>
          <input
            type="date"
            name="start_date"
            value={form.start_date}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>End Date:</label>
          <input
            type="date"
            name="end_date"
            value={form.end_date}
            onChange={handleChange}
            required
          />
        </div>
        {strategy === "Bollinger Bands" && (
          <>
            <div className="form-group">
              <label>Window:</label>
              <input
                type="number"
                name="window"
                value={form.window}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Num Std:</label>
              <input
                type="number"
                step="0.1"
                name="num_std"
                value={form.num_std}
                onChange={handleChange}
              />
            </div>
          </>
        )}
        {strategy === "Moving Average Crossover" && (
          <>
            <div className="form-group">
              <label>Fast Window:</label>
              <input
                type="number"
                name="fast_window"
                value={form.fast_window}
                onChange={handleChange}
              />
            </div>
            <div className="form-group">
              <label>Slow Window:</label>
              <input
                type="number"
                name="slow_window"
                value={form.slow_window}
                onChange={handleChange}
              />
            </div>
          </>
        )}
        <div className="form-group">
          <label>Initial Capital:</label>
          <input
            type="number"
            name="initial_capital"
            value={form.initial_capital}
            onChange={handleChange}
          />
        </div>
        <button type="submit" className="submit-button">Run Backtest</button>
      </form>
      {error && <p className="error-message">{error}</p>}
      {results && (
        <div className="results">
          <h2>Results</h2>
          <div className="results-grid">
            {Object.entries(results).map(([key, value]) => (
              <div key={key} className="result-item">
                <strong>{key}:</strong> {value}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Backtest;
