import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);

  const handleSignUp = (e) => {
    e.preventDefault();
    if (isAuthenticated) {
      navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };

  return (
    <nav className={`nav${scrolled ? " scrolled" : ""}`}>
      <Link to="/" className="nav-logo">
        <img src="/prompt_logo.png" alt="Prompt Resume" className="nav-logo-img" />
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
        <Link to="/register" className="btn-ghost" style={{ display: "inline-flex", alignItems: "center" }} onClick={handleSignUp}>
          Sign Up
        </Link>
      </div>
    </nav>
  );
}
