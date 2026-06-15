import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";

export default function Navbar({ onBuildResume }) {
  const [scrolled, setScrolled] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    setIsLoggedIn(api.isAuthenticated());
    return () => window.removeEventListener("scroll", fn);
  }, []);

  return (
    <nav className={`nav${scrolled ? " scrolled" : ""}`}>
      <Link to="/" className="nav-logo">
        <div className="nav-logo-mark">PR</div>
        Prompt Resume
      </Link>
      <ul className="nav-links">
        <li><a href="#features">Features</a></li>
        <li><a href="#templates">Templates</a></li>
        <li><a href="#how">How it works</a></li>
        <li><Link to="/pricing">Pricing</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
      <div className="nav-cta">
        {isLoggedIn ? (
          <Link to="/dashboard" className="btn-primary">Dashboard →</Link>
        ) : (
          <>
            <Link to="/login" className="btn-ghost" style={{ display: 'inline-flex', alignItems: 'center' }}>Log in</Link>
            <Link to="/register" className="btn-primary">Start free →</Link>
          </>
        )}
      </div>
    </nav>
  );
}