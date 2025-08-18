import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Select from 'react-select';

export default function Watchlist() {
  const [exchange, setExchange] = useState('NSE');
  const [watchlist, setWatchlist] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [availableStocks, setAvailableStocks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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
    }
  };

  return (
    <div>
      <h1>Stock Watchlist</h1>
      
      <div className="card">
        <div className="exchange-selector">
          <label>
            <input 
              type="radio" 
              className="exchange-radio"
              checked={exchange === 'NSE'} 
              onChange={() => setExchange('NSE')} 
            />
            <span className="exchange-label">NSE</span>
          </label>
          <label>
            <input 
              type="radio" 
              className="exchange-radio"
              checked={exchange === 'BSE'} 
              onChange={() => setExchange('BSE')} 
            />
            <span className="exchange-label">BSE</span>
          </label>
        </div>

        <div className="stock-selector-container">
          <div style={{ flex: 1 }}>
            {loading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
              </div>
            ) : error ? (
              <div className="error-message">{error}</div>
            ) : (
              <Select
                value={selectedStock}
                onChange={setSelectedStock}
                options={availableStocks}
                placeholder="Search or select stock..."
                isSearchable
              />
            )}
          </div>
          <button 
            onClick={addToWatchlist}
            disabled={!selectedStock}
            className="btn btn-primary"
          >
            Add to Watchlist
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Your Watchlist</h2>
        {watchlist.length === 0 ? (
          <p>No stocks added yet</p>
        ) : (
          <ul className="watchlist-items">
            {watchlist.map(stock => (
              <li key={stock} className="watchlist-item">
                <span className="stock-symbol">{stock}</span>
                <button 
                  onClick={() => navigate(`/analysis/${stock}`)}
                  className="btn btn-secondary btn-sm"
                >
                  Analyze
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
