// pages/Home.jsx - Completely redesigned
import { Link } from 'react-router-dom';
import { FaArrowRight, FaChartLine, FaBell, FaRocket } from 'react-icons/fa';

export default function Home() {
  const features = [
    {
      icon: <FaChartLine />,
      title: "Real-time Analysis",
      description: "Get detailed technical and fundamental analysis for any stock"
    },
    {
      icon: <FaBell />,
      title: "Smart Alerts",
      description: "Set up notifications for price movements and important events"
    },
    {
      icon: <FaRocket />,
      title: "Performance Tracking",
      description: "Monitor your portfolio performance with advanced analytics"
    }
  ];

  return (
    <div className="home-container">
      <div className="hero-section">
        <div className="hero-content">
          <h1>Smart Stock Analysis <span className="gradient-text">Made Simple</span></h1>
          <p className="hero-subtitle">Powerful insights, beautiful visualizations, and actionable recommendations for smarter investing</p>
          <Link to="/watchlist" className="cta-button">
            Get Started <FaArrowRight />
          </Link>
        </div>
        <div className="hero-visual">
          <div className="chart-placeholder">
            <div className="chart-line"></div>
            <div className="chart-line"></div>
            <div className="chart-line"></div>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2>Why Choose StockHealth?</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="stats-section">
        <div className="stat-item">
          <div className="stat-value">10K+</div>
          <div className="stat-label">Stocks Analyzed</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">98%</div>
          <div className="stat-label">Accuracy Rate</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">24/7</div>
          <div className="stat-label">Real-time Updates</div>
        </div>
      </div>
    </div>
  );
}