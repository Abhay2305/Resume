import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="footer-logo">
              <div className="footer-logo-mark">PR</div>
              Prompt Resume
            </div>
            <p className="footer-desc">
              AI-powered resume builder that helps you land your dream job. Build ATS-optimized resumes in seconds.
            </p>
          </div>
          
          <div>
            <div className="footer-col-title">Product</div>
            <div className="footer-links">
              <a href="#features">Features</a>
              <a href="#templates">Templates</a>
              <Link to="/pricing">Pricing</Link>
              <a href="#faq">FAQ</a>
            </div>
          </div>
          
          <div>
            <div className="footer-col-title">Resources</div>
            <div className="footer-links">
              <Link to="/about">About</Link>
              <Link to="/contact">Contact</Link>
            </div>
          </div>
          
          <div>
            <div className="footer-col-title">Company</div>
            <div className="footer-links">
              <Link to="/about">About</Link>
              <Link to="/contact">Contact</Link>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="footer-copy">© 2024 Prompt Resume. All rights reserved.</div>
          <div className="footer-badge">
            <div className="footer-badge-dot" />
            AI-powered · Built with ♥
          </div>
        </div>
      </div>
    </footer>
  );
}
