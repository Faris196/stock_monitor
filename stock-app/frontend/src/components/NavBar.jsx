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
          <FaHome className="nav-icon" />
          <span className="nav-text">Home</span>
        </Link>
        <Link 
          to="/watchlist" 
          className={`nav-link ${location.pathname === '/watchlist' ? 'active' : ''}`}
        >
          <FaChartLine className="nav-icon" />
          <span className="nav-text">Watchlist</span>
        </Link>
      </div>
    </nav>
  );
}