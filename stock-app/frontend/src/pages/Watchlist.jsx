// src/pages/Watchlist.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaPlus, FaSearch, FaExchangeAlt } from 'react-icons/fa';

export default function Watchlist() {
  const [exchange, setExchange] = useState('NSE');
  const [watchlist, setWatchlist] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [availableStocks, setAvailableStocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStocks = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/api/stocks?exchange=${exchange}`);
        const formattedStocks = response.data[exchange].map(stock => ({
          value: stock,
          label: stock
        }));
        setAvailableStocks(formattedStocks);
      } catch (err) {
        setError('Failed to fetch stocks. Please try again.');
        console.error('Error fetching stocks:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, [exchange]);

  const addToWatchlist = () => {
    if (selectedStock && !watchlist.includes(selectedStock.value)) {
      setWatchlist([...watchlist, selectedStock.value]);
      setSelectedStock(null);
      setSearchQuery('');
    }
  };

  const removeFromWatchlist = (stockToRemove) => {
    setWatchlist(watchlist.filter(stock => stock !== stockToRemove));
  };

  const filteredStocks = availableStocks.filter(stock => 
    stock.label.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="watchlist-page">
      <div className="page-header">
        <h1>My Watchlist</h1>
        <p>Track and analyze your favorite stocks</p>
      </div>
      
      <div className="card watchlist-card">
        <div className="card-header">
          <h2>Add Stocks</h2>
        </div>
        
        <div className="exchange-selector">
          <div className="selector-label">
            <FaExchangeAlt />
            <span>Select Exchange</span>
          </div>
          <div className="exchange-buttons">
            <button 
              className={`exchange-btn ${exchange === 'NSE' ? 'active' : ''}`}
              onClick={() => setExchange('NSE')}
            >
              NSE
            </button>
            <button 
              className={`exchange-btn ${exchange === 'BSE' ? 'active' : ''}`}
              onClick={() => setExchange('BSE')}
            >
              BSE
            </button>
          </div>
        </div>

        <div className="stock-selector">
          <div className="search-box">
            <FaSearch className="search-icon" />
            <input
              type="text"
              placeholder="Search stocks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
          
          <div className="stock-options">
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <span>Loading stocks...</span>
              </div>
            ) : error ? (
              <div className="error-message">{error}</div>
            ) : (
              <div className="options-list">
                {filteredStocks.slice(0, 5).map(stock => (
                  <div 
                    key={stock.value}
                    className={`stock-option ${selectedStock?.value === stock.value ? 'selected' : ''}`}
                    onClick={() => setSelectedStock(stock)}
                  >
                    {stock.label}
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <button 
            onClick={addToWatchlist}
            disabled={!selectedStock}
            className="add-button"
          >
            <FaPlus />
            Add to Watchlist
          </button>
        </div>
      </div>

      <div className="card watchlist-card">
        <div className="card-header">
          <h2>Your Watchlist</h2>
          <span className="count-badge">{watchlist.length} stocks</span>
        </div>
        
        {watchlist.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h3>No stocks added yet</h3>
            <p>Add stocks to your watchlist to start tracking them</p>
          </div>
        ) : (
          <div className="watchlist-grid">
            {watchlist.map(stock => (
              <div key={stock} className="watchlist-item">
                <div className="stock-info">
                  <div className="stock-symbol">{stock}</div>
                  <div className="stock-exchange">{exchange}</div>
                </div>
                <div className="stock-actions">
                  <button 
                    onClick={() => navigate(`/analysis/${stock}`)}
                    className="analyze-btn"
                  >
                    Analyze
                  </button>
                  <button 
                    onClick={() => removeFromWatchlist(stock)}
                    className="remove-btn"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}