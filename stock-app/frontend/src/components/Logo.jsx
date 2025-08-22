// src/components/Logo.jsx
export const Logo = ({ width = 40, height = 40, className = "" }) => (
  <svg 
    width={width} 
    height={height} 
    viewBox="0 0 100 100" 
    className={className}
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#4361ee" />
        <stop offset="100%" stopColor="#3a0ca3" />
      </linearGradient>
    </defs>
    <rect x="10" y="40" width="15" height="40" fill="url(#gradient)" rx="2" />
    <rect x="35" y="25" width="15" height="55" fill="url(#gradient)" rx="2" />
    <rect x="60" y="35" width="15" height="45" fill="url(#gradient)" rx="2" />
    <rect x="85" y="10" width="15" height="70" fill="url(#gradient)" rx="2" />
    <path d="M10,40 L25,40 L35,25 L50,25 L60,35 L75,35 L85,10 L100,10" 
          stroke="#4361ee" strokeWidth="3" fill="none" strokeLinejoin="round" />
  </svg>
);

export const LogoWithText = ({ width = 160, className = "" }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }} className={className}>
    <Logo width={40} height={40} />
    <span style={{ 
      fontSize: '24px', 
      fontWeight: '800', 
      background: 'linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text'
    }}>
      StockHealth
    </span>
  </div>
);