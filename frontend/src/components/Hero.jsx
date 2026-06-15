import { COLORS } from "../utils/constants";

const PIXELS = [
  { top: "15%", left: "8%",  delay: "0s",   dur: "3.5s", size: 3, color: COLORS.teal },
  { top: "25%", left: "92%", delay: "0.5s", dur: "4s",   size: 4, color: COLORS.amber },
  { top: "60%", left: "5%",  delay: "1s",   dur: "3s",   size: 3, color: COLORS.tealLight },
  { top: "70%", left: "95%", delay: "0.3s", dur: "5s",   size: 4, color: COLORS.teal },
  { top: "40%", left: "3%",  delay: "1.5s", dur: "4.5s", size: 3, color: COLORS.amberLight },
  { top: "80%", left: "88%", delay: "0.8s", dur: "3.8s", size: 3, color: COLORS.tealDark },
];

export default function Hero({ onBuildResume }) {
  return (
    <section style={{ position: "relative" }}>
      {/* HERO BG */}
      <div className="hero-bg">
        <div className="hero-bg-blob1" />
        <div className="hero-bg-blob2" />
        <div className="hero-bg-grid" />
        {PIXELS.map((p, i) => (
          <div key={i} className="pixel-particle" style={{
            top: p.top, left: p.left,
            animationDelay: p.delay, animationDuration: p.dur,
            width: p.size, height: p.size, background: p.color,
          }} />
        ))}
      </div>

      <div className="hero">
        {/* HERO LEFT: TEXT & CTAs */}
        <div>
          <div className="hero-badge anim-fadeUp delay-1">
            <div className="hero-badge-dot" />
            AI-Powered · ATS-Optimized · Interview-Ready
          </div>
          <h1 className="hero-headline anim-fadeUp delay-2">
            Build resumes that<br />
            <em>actually get you</em><br />
            hired
          </h1>
          <p className="hero-sub anim-fadeUp delay-3">
            Describe yourself in plain English — our AI builds a polished, ATS-friendly resume in under 60 seconds. Or take full manual control. Your resume, your way.
          </p>
          <div className="hero-modes anim-fadeUp delay-4">
            <div className="hero-mode-chip">
              <div className="hero-mode-chip-dot" />
              AI Prompt Mode — instant generation
            </div>
            <div className="hero-mode-chip">
              <div className="hero-mode-chip-dot amber" />
              Manual Mode — full editing control
            </div>
          </div>
          <div className="hero-ctas anim-fadeUp delay-5">
            <button className="btn-hero" onClick={onBuildResume}>
              Build my resume
              <span style={{ fontSize: "1.1rem" }}>→</span>
            </button>
            {/* <button className="btn-hero-sec">
              <span style={{ fontSize: "1rem" }}>▶</span>
              Watch demo
            </button> */}
          </div>
          <div className="anim-fadeUp delay-6" style={{ marginTop: "1.5rem", fontSize: "0.78rem", color: COLORS.textMuted, display: "flex", alignItems: "center", gap: "1rem" }}>
            {/* <span>✓ Free forever plan</span> */}
            {/* <span>✓ No credit card needed</span> */}
            <span>✓ Export in 60 seconds</span>
          </div>
        </div>

        {/* HERO RIGHT: INTERACTIVE VISUAL */}
        <div className="hero-visual anim-fadeIn delay-4">
          
          {/* Main resume card */}
          <div className="resume-card resume-main">
            <div className="resume-header">
              <div className="resume-name">Alexandra Chen</div>
              <div className="resume-role">Senior Product Designer · San Francisco, CA</div>
            </div>
            <div className="resume-body">
              <div className="resume-section-label">Experience</div>
              <div className="resume-line resume-line-full active" style={{ marginBottom: 6 }} />
              <div className="resume-line resume-line-med active" style={{ marginBottom: 6 }} />
              <div className="resume-line resume-line-short" style={{ marginBottom: 12 }} />
              
              <div className="resume-section-label">Skills</div>
              <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 12 }}>
                {["Figma", "React", "UX Research", "Prototyping"].map(s => (
                  <span key={s} style={{ background: "rgba(123,196,190,0.12)", border: "1px solid rgba(123,196,190,0.25)", borderRadius: 5, padding: "2px 7px", fontSize: "0.62rem", color: COLORS.tealDark, fontWeight: 500 }}>{s}</span>
                ))}
              </div>
              
              <div className="resume-section-label">Education</div>
              <div className="resume-line resume-line-full" />
              <div className="resume-line resume-line-med" style={{ marginTop: 4 }} />
            </div>
          </div>

          {/* ATS Badge */}
          <div className="ats-badge">
            <div className="ats-label">ATS Score</div>
            <div className="ats-score">94<span>/100</span></div>
            <div className="ats-bar-track"><div className="ats-bar-fill" /></div>
            <div style={{ fontSize: "0.6rem", color: COLORS.textMuted, marginTop: 5 }}>↑ Excellent — recruiter ready</div>
          </div>

          {/* Recruiter badge */}
          <div className="recruiter-badge">
            <div className="recruiter-badge-icon">👁</div>
            Recruiter<br />Reviewed ✓
          </div>

          {/* AI prompt card */}
          <div className="ai-prompt-card">
            <div className="ai-prompt-label">
              <span style={{ width: 6, height: 6, borderRadius: 1, background: COLORS.teal, display: "inline-block" }} />
              AI Prompt
            </div>
            <div className="ai-prompt-text">
              "5 years product design at startups, led design systems, shipped 3 mobile apps, Stanford CS grad..."
              <span className="cursor-blink" />
            </div>
            <button className="ai-prompt-btn" onClick={onBuildResume}>
              ✦ Generate resume →
            </button>
          </div>

          {/* Export chip */}
          <div className="export-chip">
            <div className="export-chip-dot" />
            PDF exported · 48 KB
          </div>

        </div>
      </div>
    </section>
  );
}