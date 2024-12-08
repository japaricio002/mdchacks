import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Portfolio from "./components/Portfolio";
import Backtest from "./components/Backtest";

import {
  FaTachometerAlt,
  FaCogs,
  FaChartLine,
  FaHistory,
  FaDatabase,
  FaUser,
} from "react-icons/fa";

const Dashboard = () => <div className="p-4">Dashboard Content</div>;
const Strategy = () => <div className="p-4">Strategy Content</div>;
const DataManagement = () => <div className="p-4">Data Management Content</div>;
const Settings = () => <div className="p-4">Settings Content</div>;

const App = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleNavbar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const navItems = [
    { name: "Dashboard", path: "/", icon: <FaTachometerAlt /> },
    { name: "Strategy", path: "/strategy", icon: <FaChartLine /> },
    { name: "Backtest", path: "/backtest", icon: <FaHistory /> },
    { name: "Portfolio", path: "/portfolio", icon: <FaUser /> },
    { name: "Data Management", path: "/data-management", icon: <FaDatabase /> },
    { name: "Settings", path: "/settings", icon: <FaCogs /> },
  ];

  return (
    <Router>
      <div className="flex h-screen">
        {/* Collapsible Sidebar */}
        <nav
          className={`${
            isCollapsed ? "w-16" : "w-64"
          } bg-gray-800 text-white flex flex-col transition-width duration-300`}
        >
          {/* Burger Button */}
          <button
            onClick={toggleNavbar}
            className="p-4 focus:outline-none hover:bg-gray-700"
          >
            <div className="space-y-1">
              <div
                className={`h-1 w-6 bg-white transition-transform duration-300 ${
                  isCollapsed ? "rotate-45 translate-y-2" : ""
                }`}
              ></div>
              <div
                className={`h-1 w-6 bg-white transition-opacity duration-300 ${
                  isCollapsed ? "opacity-0" : ""
                }`}
              ></div>
              <div
                className={`h-1 w-6 bg-white transition-transform duration-300 ${
                  isCollapsed ? "-rotate-45 -translate-y-2" : ""
                }`}
              ></div>
            </div>
          </button>
          <ul className="flex-1">
            {navItems.map((item) => (
              <li key={item.name} className="mb-4">
                <NavLink
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center p-2 hover:bg-gray-700 ${
                      isActive ? "bg-gray-700" : ""
                    }`
                  }
                >
                  <span className="text-lg">{item.icon}</span>
                  {!isCollapsed && <span className="ml-4">{item.name}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Main Content */}
        <main className="flex-1 bg-gray-100 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/strategy" element={<Strategy />} />
            <Route path="/backtest" element={<Backtest />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/data-management" element={<DataManagement />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
