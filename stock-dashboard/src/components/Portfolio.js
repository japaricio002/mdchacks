import React, { useState, useEffect } from "react";
import axios from "axios";

const App = () => {
  const [symbols, setSymbols] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredSymbols, setFilteredSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");

  // Fetch symbols from the backend
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
    setSearchTerm(symbol);
    setFilteredSymbols([]); // Clear suggestions after selection
  };

  const handleBlur = () => {
    // Delay clearing the suggestions to allow click event to register
    setTimeout(() => setFilteredSymbols([]), 100);
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
                key={symbol}
                onClick={() => handleSymbolClick(symbol)}
                className="p-2 cursor-pointer hover:bg-gray-200"
              >
                {symbol}
              </li>
            ))}
          </ul>
        )}
        {selectedSymbol && (
          <p className="mt-4 text-center">
            Selected Symbol: <strong>{selectedSymbol}</strong>
          </p>
        )}
      </div>
    </div>
  );
};

export default App;
