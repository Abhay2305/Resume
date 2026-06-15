import { useState, useEffect, useRef } from "react";
import { COLORS } from "../utils/constants";

function ATSCriteria() {
  const [animated, setAnimated] = useState(false);
  const ref = useRef();
  
  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setAnimated(true); },
      { threshold: 0.3 }
    );
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  
  const criteria = [
    { label: "Keyword Density", pct: 94 },
    { label: "Formatting Standards", pct: 98 },
    { label: "Section Structure", pct: 91 },
    { label: "Readability Score", pct: 97 },
    { label: "Length Optimization", pct: 89 },
  ];
  
  return (
    <div className="ats-meter-card" ref={ref}>
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: "0.7rem", color: "rgba(255,255,255,0.6)", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>ATS Analysis Score</div>
        <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: "3rem", color: "white", lineHeight: 1, display: "flex", alignItems: "baseline", gap: 4 }}>
          94 <span style={{ fontSize: "1rem", fontFamily: "'DM Sans', sans-serif", color: "rgba(255,255,255,0.55)" }}>/100</span>
        </div>
      </div>
      <div className="ats-criteria">
        {criteria.map((c, i) => (
          <div className="ats-crit-row" key={i}>
            <div className="ats-crit-top">
              <span className="ats-crit-label">{c.label}</span>
              <span className="ats-crit-pct">{c.pct}%</span>
            </div>
            <div className="ats-crit-track">
              <div className="ats-crit-fill" style={{ width: animated ? `${c.pct}%` : "0%", transitionDelay: `${i * 0.15}s` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ATSSection() {
  return (
    <div className="ats-section">
      <div style={{ position: "absolute", top: "10%", right: "5%", width: 300, height: 300 }} className="ats-bg-circle anim-floatSlow" />
      <div style={{ position: "absolute", bottom: "5%", left: "3%", width: 200, height: 200 }} className="ats-bg-circle anim-float" />
      <div className="ats-section-inner">
        <div>
          <div className="section-tag reveal">◎ ATS Optimization</div>
          <h2 className="section-headline reveal delay-1">Pass every ATS<br />filter, every time</h2>
          <p className="section-sub reveal delay-2">
            Over 99% of Fortune 500 companies use ATS software. Our real-time analyzer ensures your resume is always optimized for both human recruiters and automated systems.
          </p>
        </div>
        <div className="reveal-right delay-3">
          <ATSCriteria />
        </div>
      </div>
    </div>
  );
}