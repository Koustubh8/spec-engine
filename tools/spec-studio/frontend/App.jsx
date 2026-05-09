import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './Dashboard';
import NodeBrowser from './NodeBrowser';
import NodeDetail from './NodeDetail';

function NavLink({ to, children }) {
  const loc = useLocation();
  const active = loc.pathname === to || (to !== '/' && loc.pathname.startsWith(to));
  return (
    <Link to={to} className={`nav-link ${active ? 'active' : ''}`}>
      {children}
    </Link>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <nav className="sidebar">
          <div className="sidebar-header">
            <h1 className="logo">Spec Studio</h1>
            <span className="logo-sub">graph dashboard</span>
          </div>
          <div className="nav-links">
            <NavLink to="/">Dashboard</NavLink>
            <NavLink to="/nodes">Nodes</NavLink>
          </div>
          <div className="sidebar-footer">
            <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">API Docs</a>
          </div>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/nodes" element={<NodeBrowser />} />
            <Route path="/nodes/:slug" element={<NodeDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
