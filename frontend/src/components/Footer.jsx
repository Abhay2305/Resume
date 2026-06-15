export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-grid">
          <div className="footer-brand">
            <div className="footer-logo">
              <div className="footer-logo-mark">R</div>
              ResumeAI
            </div>
            <p className="footer-desc">
              The AI-powered resume builder built for modern job seekers. Professional, fast, and ATS-ready.
            </p>
          </div>
          
          <div>
            <div className="footer-col-title">Product</div>
            <div className="footer-links">
              <a href="#">AI Resume Mode</a>
              <a href="#">Manual Builder</a>
              <a href="#">Templates</a>
              {/* <a href="#">ATS Checker</a> */}
              <a href="#pricing">Pricing</a>
            </div>
          </div>
          
          {/* <div>
            <div className="footer-col-title">Company</div>
            <div className="footer-links">
              <a href="#">About</a>
              <a href="#">Blog</a>
              <a href="#">Careers</a>
              <a href="#">Press</a>
              <a href="#">Contact</a>
            </div>
          </div> */}
          
          <div>
            <div className="footer-col-title">Legal</div>
            <div className="footer-links">
              {/* <a href="#">Privacy Policy</a> */}
              <a href="#">Terms of Service</a>
              <a href="#">Cookie Policy</a>
              <a href="#">GDPR</a>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <div className="footer-copy">© 2026 ResumeAI. All rights reserved.</div>
          <div className="footer-badge">
            <div className="footer-badge-dot" />
            {/* All systems operational */}
          </div>
        </div>
      </div>
    </footer>
  );
}