import React, { useState, useEffect } from "react";
import axios from "axios";

const AddToPortfolio = ({ symbol, onClose }) => {
  const [entryPrice, setEntryPrice] = useState("");

  const handleAddToPortfolio = async () => {
    if (!entryPrice) {
      alert("Please enter the entry price.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:4000/api/portfolio/add", {
        symbol,
        entry: parseFloat(entryPrice),
      });

      if (response.data.success) {
        alert("Stock added to portfolio successfully!");
        onClose(); // Remove delay, directly close the popup
      } else {
        alert(`Failed to add stock: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Error adding to portfolio:", error);
      alert("An error occurred while adding the stock.");
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex justify-center items-center">
      <div className="bg-white p-6 rounded shadow-lg">
        <h2 className="text-xl font-bold mb-4">Add {symbol} to Portfolio</h2>
        <input
          type="number"
          value={entryPrice}
          onChange={(e) => setEntryPrice(e.target.value)}
          placeholder="Enter Price"
          className="p-2 border rounded w-full mb-4"
        />
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 mr-2 bg-gray-300 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            onClick={handleAddToPortfolio}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
};

const CurrentPortfolio = () => {
  const [portfolio, setPortfolio] = useState([]);

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get("http://localhost:4000/api/portfolio");
      setPortfolio(response.data);
    } catch (error) {
      console.error("Error fetching portfolio data:", error);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  return (
    <div className="mt-8">
      <h2 className="text-xl font-bold mb-4">Current Portfolio</h2>
      {portfolio.length > 0 ? (
        <table className="w-full border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-200">
              <th className="border border-gray-300 px-4 py-2">Symbol</th>
              <th className="border border-gray-300 px-4 py-2">Entry Price</th>
              <th className="border border-gray-300 px-4 py-2">Current Value</th>
              <th className="border border-gray-300 px-4 py-2">Profit/Loss</th>
              <th className="border border-gray-300 px-4 py-2">P/L %</th>
            </tr>
          </thead>
          <tbody>
            {portfolio.map((position) => (
              <tr key={position.id}> {/* Ensure unique key */}
                <td className="border border-gray-300 px-4 py-2">{position.symbol}</td>
                <td className="border border-gray-300 px-4 py-2">{position.entry.toFixed(2)}</td>
                <td className="border border-gray-300 px-4 py-2">{position.current_value.toFixed(2)}</td>
                <td
                  className={`border border-gray-300 px-4 py-2 ${
                    position.profit_loss >= 0 ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {position.profit_loss.toFixed(2)}
                </td>
                <td
                  className={`border border-gray-300 px-4 py-2 ${
                    position.pl_percent >= 0 ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {position.pl_percent.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No stocks in the portfolio yet.</p>
      )}
    </div>
  );
};

const App = () => {
  const [symbols, setSymbols] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredSymbols, setFilteredSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [isAddingToPortfolio, setIsAddingToPortfolio] = useState(false);

  const fetchSymbols = async () => {
    try {
      const response = await axios.get("http://localhost:4000/api/stocks/symbols");
      setSymbols(response.data);
    } catch (error) {
      console.error("Error fetching stock symbols:", error);
    }
  };

  useEffect(() => {
    fetchSymbols();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      setFilteredSymbols(
        symbols.filter((symbol) =>
          symbol.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    } else {
      setFilteredSymbols([]);
    }
  }, [searchTerm, symbols]);

  const handleSymbolClick = (symbol) => {
    setSelectedSymbol(symbol);
    setIsAddingToPortfolio(true);
  };

  const closePortfolioPopup = () => {
    setIsAddingToPortfolio(false); // Immediate state update without delay
    setSelectedSymbol("");
  };

  const handleBlur = () => {
    setFilteredSymbols([]); // Directly clear on blur
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold text-center">Search Stock Symbols</h1>
      <div className="flex flex-col items-center my-4">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onBlur={handleBlur}
          placeholder="Search for a stock symbol"
          className="p-2 border rounded w-64"
        />
        {filteredSymbols.length > 0 && (
          <ul className="border rounded w-64 max-h-48 overflow-y-auto mt-2">
            {filteredSymbols.map((symbol) => (
              <li
                key={symbol} // Ensure unique key
                onMouseDown={() => handleSymbolClick(symbol)}
                className="p-2 cursor-pointer hover:bg-gray-200"
              >
                {symbol}
              </li>
            ))}
          </ul>
        )}
        {isAddingToPortfolio && (
          <AddToPortfolio
            symbol={selectedSymbol}
            onClose={closePortfolioPopup}
          />
        )}
      </div>
      <CurrentPortfolio />
    </div>
  );
};

export default App;
