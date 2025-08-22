import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

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
    <div className="loading-container">
      <div className="loading-spinner"></div>
      {retryCount > 0 && (
        <p style={{ marginTop: '1rem', color: '#666' }}>
          Attempting retry {retryCount}... (this may take a while)
        </p>
      )}
      <p style={{ marginTop: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
        Analyzing {symbol}... This can take up to a minute.
      </p>
    </div>
  );
  
  if (error) return (
    <div className="card error-message">
      <h3>Error Loading Analysis</h3>
      <p>{error}</p>
      <button 
        onClick={handleRetry}
        className="btn btn-primary"
        style={{ marginTop: '1rem' }}
      >
        Try Again
      </button>
      <button 
        onClick={() => navigate(-1)}
        className="btn btn-outline"
        style={{ marginTop: '0.5rem', marginLeft: '0.5rem' }}
      >
        ← Go Back
      </button>
    </div>
  );

  return (
    <div>
      <div className="stock-header">
        <button 
          onClick={() => navigate(-1)}
          className="btn btn-outline"
        >
          ← Back to Watchlist
        </button>
        <h1>{data.fundamentals?.name || symbol}</h1>
      </div>
      
      {data.chart && (
        <div className="stock-chart">
          <img 
            src={`data:image/png;base64,${data.chart}`} 
            alt="Price chart" 
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        </div>
      )}
      
      <div className="analysis-section">
        <h2>Analysis</h2>
        <ReactMarkdown>
          {data.analysis || 'No analysis available'}
        </ReactMarkdown>
      </div>
    </div>
  );
}