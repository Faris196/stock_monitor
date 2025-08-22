// src/components/Header.jsx
import { useLocation, Link } from 'react-router-dom';
import { LogoWithText } from './Logo'; // Import the logo

export default function Header() {
  const location = useLocation();
  
  const getTitle = () => {
    if (location.pathname === '/') return 'Dashboard';
    if (location.pathname === '/watchlist') return 'My Watchlist';
    if (location.pathname.includes('/analysis')) return 'Stock Analysis';
    return 'Stock Health Monitor';
  };

  return (
    <header className="app-header">
      <div className="header-content">
        <Link to="/" className="logo">
          <LogoWithText /> {/* logo */}
        </Link>
        <h1 className="page-title">{getTitle()}</h1>
        <div className="header-actions">
          <button className="theme-toggle" aria-label="Toggle theme">
            <span className="theme-icon">🌙</span>
          </button>
        </div>
      </div>
    </header>
  );
}