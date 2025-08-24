// src/components/Header.jsx
import { useLocation, Link } from 'react-router-dom';
import { LogoWithText } from './Logo';
import { useTheme } from '../contexts/ThemeContext';
import { FaMoon, FaSun } from 'react-icons/fa';

export default function Header() {
  const location = useLocation();
  const { toggleTheme, isDark } = useTheme(); // Remove unused 'theme'
  
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
          <LogoWithText />
        </Link>
        <h1 className="page-title">{getTitle()}</h1>
        <div className="header-actions">
          <button 
            className="theme-toggle" 
            onClick={toggleTheme}
            aria-label="Toggle theme"
          >
            {isDark ? (
              <FaSun className="theme-icon" />
            ) : (
              <FaMoon className="theme-icon" />
            )}
          </button>
        </div>
      </div>
    </header>
  );
}