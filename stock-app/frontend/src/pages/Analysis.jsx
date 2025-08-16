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

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await axios.post('http://localhost:5000/api/analyze', {
          symbol: symbol
        });
        
        const analysisText = typeof response.data.analysis === 'string' 
          ? response.data.analysis 
          : JSON.stringify(response.data.analysis);
        
        setData({
          fundamentals: response.data.fundamentals || {},
          chart: response.data.chart || null,
          analysis: analysisText
        });
      } catch (err) {
        setError(err.message);
        console.error('Analysis error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [symbol]);

  if (loading) return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
    </div>
  );
  
  if (error) return (
    <div className="card error-message">
      Error: {error}
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