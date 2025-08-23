// components/NavBar.jsx - Updated with new design
import { Link, useLocation } from 'react-router-dom';
import { FaHome, FaChartLine } from 'react-icons/fa';

export default function NavBar() {
  const location = useLocation();
  
  if (location.pathname.includes('/analysis')) {
    return null;
  }

  return (
    <nav className="bottom-nav">
      <div className="nav-container">
        <Link 
          to="/" 
          className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
        >
          <div className="nav-icon-container">
            <FaHome className="nav-icon" />
          </div>
          <span className="nav-text">Home</span>
        </Link>
        <Link 
          to="/watchlist" 
          className={`nav-link ${location.pathname === '/watchlist' ? 'active' : ''}`}
        >
          <div className="nav-icon-container">
            <FaChartLine className="nav-icon" />
          </div>
          <span className="nav-text">Watchlist</span>
        </Link>
        <div className="nav-indicator"></div>
      </div>
    </nav>
  );
}