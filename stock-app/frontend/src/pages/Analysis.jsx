// pages/Analysis.jsx - Completely redesigned
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { FaArrowLeft, FaRedo, FaChartLine, FaInfoCircle, FaExclamationTriangle } from 'react-icons/fa';

export default function Analysis() {
  const { symbol } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState({
    fundamentals: null,
    chart: null,
    analysis: ''
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [activeTab, setActiveTab] = useState('analysis');

  // Retry function with exponential backoff
  const fetchAnalysisWithRetry = async (symbol, retries = 3) => {
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/analyze`, {
        symbol: symbol
      }, {
        timeout: 45000, // 45 second timeout
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const analysisText = typeof response.data.analysis === 'string' 
        ? response.data.analysis 
        : JSON.stringify(response.data.analysis);
      
      setData({
        fundamentals: response.data.fundamentals || {},
        chart: response.data.chart || null,
        analysis: analysisText
      });
      setError(null);
      return true;
      
    } catch (err) {
      console.error('Analysis error:', err);
      
      // Check if we should retry
      if (retries > 0 && (
        err.code === 'ECONNABORTED' || // Timeout
        err.response?.status === 429 || // Rate limit
        err.response?.status === 500 || // Server error
        err.response?.status === 502 || // Bad gateway
        err.response?.status === 503 || // Service unavailable
        err.response?.status === 504    // Gateway timeout
      )) {
        const delay = Math.pow(2, 4 - retries) * 1000; // Exponential backoff: 2s, 4s, 8s
        console.log(`Retrying in ${delay/1000}s... (${retries} attempts left)`);
        
        await new Promise(resolve => setTimeout(resolve, delay));
        setRetryCount(prev => prev + 1);
        return fetchAnalysisWithRetry(symbol, retries - 1);
      }
      
      // Final error after all retries
      throw err;
    }
  };

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const success = await fetchAnalysisWithRetry(symbol, 3);
        
        if (!success) {
          setError('Failed to fetch analysis after multiple attempts. Please try again later.');
        }
      } catch (err) {
        let errorMessage = err.message;
        
        // User-friendly error messages
        if (err.code === 'ECONNABORTED') {
          errorMessage = 'Request timeout. The analysis is taking longer than expected.';
        } else if (err.response?.status === 429) {
          errorMessage = 'Rate limited. Please wait a moment and try again.';
        } else if (err.response?.status >= 500) {
          errorMessage = 'Server error. Please try again in a few moments.';
        } else if (!err.response) {
          errorMessage = 'Network error. Please check your connection.';
        }
        
        setError(errorMessage);
        console.error('Final analysis error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [symbol]);

  const handleRetry = () => {
    setLoading(true);
    setError(null);
    setRetryCount(0);
    // useEffect will trigger again because loading state changes
  };

  if (loading) return (
    <div className="analysis-page">
      <div className="loading-container">
        <div className="loading-spinner-large"></div>
        {retryCount > 0 && (
          <p className="retry-message">
            Attempting retry {retryCount}... (this may take a while)
          </p>
        )}
        <div className="loading-content">
          <h2>Analyzing {symbol}</h2>
          <p>This can take up to a minute as we gather comprehensive data</p>
          <div className="loading-steps">
            <div className="loading-step active">
              <div className="step-icon">1</div>
              <div className="step-text">Fetching market data</div>
            </div>
            <div className="loading-step">
              <div className="step-icon">2</div>
              <div className="step-text">Analyzing fundamentals</div>
            </div>
            <div className="loading-step">
              <div className="step-icon">3</div>
              <div className="step-text">Generating insights</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  
  if (error) return (
    <div className="analysis-page">
      <div className="card error-card">
        <div className="error-icon">
          <FaExclamationTriangle />
        </div>
        <h3>Error Loading Analysis</h3>
        <p>{error}</p>
        <div className="error-actions">
          <button 
            onClick={handleRetry}
            className="btn btn-primary"
          >
            <FaRedo /> Try Again
          </button>
          <button 
            onClick={() => navigate(-1)}
            className="btn btn-outline"
          >
            <FaArrowLeft /> Go Back
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="analysis-page">
      <div className="stock-header">
        <button 
          onClick={() => navigate(-1)}
          className="btn btn-outline back-btn"
        >
          <FaArrowLeft /> Back
        </button>
        <div className="stock-title">
          <h1>{data.fundamentals?.name || symbol}</h1>
          <span className="stock-symbol">{symbol}</span>
        </div>
        <div className="header-actions">
          <button 
            onClick={handleRetry}
            className="btn btn-outline"
            title="Refresh analysis"
          >
            <FaRedo />
          </button>
        </div>
      </div>
      
      {data.chart && (
        <div className="card chart-card">
          <div className="card-header">
            <h2>Price Chart</h2>
          </div>
          <div className="stock-chart">
            <img 
              src={`data:image/png;base64,${data.chart}`} 
              alt={`${symbol} price chart`} 
            />
          </div>
        </div>
      )}
      
      <div className="analysis-tabs">
        <button 
          className={`tab-btn ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          <FaChartLine /> Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'fundamentals' ? 'active' : ''}`}
          onClick={() => setActiveTab('fundamentals')}
        >
          <FaInfoCircle /> Fundamentals
        </button>
      </div>
      
      {activeTab === 'analysis' ? (
        <div className="card analysis-card">
          <div className="card-header">
            <h2>AI Analysis</h2>
          </div>
          <div className="analysis-content">
            <ReactMarkdown>
              {data.analysis || 'No analysis available for this stock.'}
            </ReactMarkdown>
          </div>
        </div>
      ) : (
        <div className="card fundamentals-card">
          <div className="card-header">
            <h2>Fundamental Data</h2>
          </div>
          <div className="fundamentals-content">
            {data.fundamentals && Object.keys(data.fundamentals).length > 0 ? (
              <div className="fundamentals-grid">
                {Object.entries(data.fundamentals).map(([key, value]) => (
                  <div key={key} className="fundamental-item">
                    <span className="fundamental-label">{key.replace(/_/g, ' ')}</span>
                    <span className="fundamental-value">{value}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p>No fundamental data available.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}