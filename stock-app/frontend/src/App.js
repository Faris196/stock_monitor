import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Home from './pages/Home';
import Watchlist from './pages/Watchlist';
import Analysis from './pages/Analysis';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-root">
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
  );
}

export default App;