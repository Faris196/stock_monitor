// App.js - Updated with ThemeProvider
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Home from './pages/Home';
import Watchlist from './pages/Watchlist';
import Analysis from './pages/Analysis';
import Header from './components/Header';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="app-root">
          <Header />
          <div className="content-wrapper">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/watchlist" element={<Watchlist />} />
              <Route path="/analysis/:symbol" element={<Analysis />} />
            </Routes>
          </div>
          <NavBar />
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;