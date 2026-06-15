export default function StatsStrip() {
  return (
    <div className="stats-strip">
      <div className="stats-inner">
        {[
          { num: "240", suffix: "K+", label: "Resumes created" },
          { num: "94", suffix: "%", label: "ATS pass rate" },
          { num: "3x", suffix: "", label: "More interviews" },
          { num: "60", suffix: "s", label: "AI generation time" },
        ].map((s, i) => (
          <div key={i} className="stat-item reveal" style={{ transitionDelay: `${i * 0.1}s` }}>
            <div className="stat-number">
              {s.num}<sub>{s.suffix}</sub>
            </div>
            <div className="stat-label">{s.label}</div>
          </div>
        ))}
        <div className="stat-divider" />
        <div className="company-logos reveal delay-5">
          <span className="company-logo">Google</span>
          <span className="company-logo">Meta</span>
          <span className="company-logo">Stripe</span>
          <span className="company-logo">Figma</span>
          <span className="company-logo">Notion</span>
        </div>
      </div>
    </div>
  );
}