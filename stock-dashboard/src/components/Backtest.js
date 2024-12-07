import React, { useState } from 'react';

const Backtest = () => {
  const [form, setForm] = useState({
    symbol: '',
    start_date: '',
    end_date: '',
    window: 20,
    num_std: 2.0,
    initial_capital: 100000.0,
  });

  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResults(null);

    try {
      const response = await fetch('http://localhost:4000/api/backtest', {
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
    <div>
      <h1>Bollinger Bands Backtest</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Symbol:
          <input type="text" name="symbol" value={form.symbol} onChange={handleChange} required />
        </label>
        <label>
          Start Date:
          <input type="date" name="start_date" value={form.start_date} onChange={handleChange} required />
        </label>
        <label>
          End Date:
          <input type="date" name="end_date" value={form.end_date} onChange={handleChange} required />
        </label>
        <label>
          Window:
          <input type="number" name="window" value={form.window} onChange={handleChange} />
        </label>
        <label>
          Num Std:
          <input type="number" step="0.1" name="num_std" value={form.num_std} onChange={handleChange} />
        </label>
        <label>
          Initial Capital:
          <input type="number" name="initial_capital" value={form.initial_capital} onChange={handleChange} />
        </label>
        <button type="submit">Run Backtest</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {results && (
        <div>
          <h2>Results</h2>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default Backtest;
