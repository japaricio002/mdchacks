import React, { useState, useEffect } from "react";
import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend } from "chart.js";
import { Line } from "react-chartjs-2";
import axios from "axios";

// Register required Chart.js components
ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

const App = () => {
  const [stock, setStock] = useState("AAPL");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [chartData, setChartData] = useState(null);

  const fetchStockData = async () => {
    try {
      const response = await axios.get("http://localhost:4000/api/stocks", {
        params: { symbol: stock, start_date: startDate, end_date: endDate },
      });
      const data = response.data;
      setChartData({
        labels: data.map((item) => new Date(item.timestamp).toLocaleDateString()),
        datasets: [
          {
            label: "Close Price",
            data: data.map((item) => item.close_price),
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            fill: false,
          },
        ],
      });
    } catch (error) {
      console.error("Error fetching stock data:", error);
    }
  };

  useEffect(() => {
    if (startDate && endDate) fetchStockData();
  }, [stock, startDate, endDate]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold text-center">Stock Data Viewer</h1>
      <div className="flex justify-center my-4">
        <select
          value={stock}
          onChange={(e) => setStock(e.target.value)}
          className="p-2 border rounded"
        >
          <option value="AAPL">Apple (AAPL)</option>
        </select>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="ml-4 p-2 border rounded"
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="ml-4 p-2 border rounded"
        />
      </div>
      <div>
        {chartData ? (
          <Line data={chartData} />
        ) : (
          <p className="text-center">Select a date range to view the data.</p>
        )}
      </div>
    </div>
  );
};

export default App;
