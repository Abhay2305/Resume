import { useState, useEffect, useRef } from "react";
import { COLORS } from "../utils/constants";

function CoverLetterVisual() {
  const [typingIndex, setTypingIndex] = useState(0);
  const lines = [
    "Dear Hiring Manager,",
    "I am writing to express my strong interest in the Senior",
    "Frontend role at Stripe. With over 5 years of experience",
    "building scalable React applications, I have...",
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setTypingIndex((prev) => (prev < lines.length ? prev + 1 : 0));
    }, 1500);
    return () => clearInterval(timer);
  }, [lines.length]);

  return (
    <div className="ats-meter-card" style={{ padding: "32px", position: "relative", overflow: "hidden" }}>
      {/* Subtle background glow */}
      <div style={{ position: "absolute", top: -50, right: -50, width: 150, height: 150, background: COLORS.amber, opacity: 0.15, filter: "blur(40px)", borderRadius: "50%" }} />
      
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
        <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(255,255,255,0.1)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem" }}>
          ✉️
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.6)", fontWeight: 600, letterSpacing: "0.08em", textTransform: "uppercase" }}>AI Generator Active</div>
          <div style={{ fontSize: "0.9rem", color: "white", fontWeight: 500 }}>Stripe_CoverLetter.pdf</div>
        </div>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12, minHeight: 120 }}>
        {lines.map((line, i) => (
          <div 
            key={i} 
            style={{ 
              fontSize: "0.85rem", 
              color: "rgba(255,255,255,0.85)", 
              lineHeight: 1.6,
              opacity: i < typingIndex ? 1 : 0,
              transform: i < typingIndex ? "translateY(0)" : "translateY(10px)",
              transition: "all 0.4s ease-out"
            }}
          >
            {line}
            {i === typingIndex - 1 && (
              <span className="cursor-blink" style={{ background: COLORS.amberLight, display: "inline-block", width: 2, height: 14, marginLeft: 4, verticalAlign: "middle" }} />
            )}
          </div>
        ))}
      </div>

      <div style={{ marginTop: 24, paddingTop: 16, borderTop: "1px solid rgba(255,255,255,0.1)", display: "flex", alignItems: "center", gap: 8 }}>
        {/* <span style={{ fontSize: "0.75rem", color: COLORS.amberLight, fontWeight: 500 }}>✓ Tone matched to resume</span> */}
      </div>
    </div>
  );
}

export default function CoverLetterSection() {
  return (
    <div className="ats-section">
      {/* Using the same dark aesthetic class from the original ATS section to keep the page rhythm */}
      <div style={{ position: "absolute", top: "10%", right: "5%", width: 300, height: 300 }} className="ats-bg-circle anim-floatSlow" />
      <div style={{ position: "absolute", bottom: "5%", left: "3%", width: 200, height: 200 }} className="ats-bg-circle anim-float" />
      
      <div className="ats-section-inner">
        <div>
          <div className="section-tag reveal">◎ 1-Click Cover Letters</div>
          <h2 className="section-headline reveal delay-1">Perfectly matched.<br />Instantly written.</h2>
          <p className="section-sub reveal delay-2">
            Don't let a generic cover letter ruin a great resume. Our AI analyzes your newly built resume alongside the target job description to generate a highly personalized, persuasive cover letter in seconds.
          </p>
          <div className="reveal delay-3" style={{ marginTop: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
            {[
              "Automatically matches your resume's tone and style", 
              "Highlights your most relevant experience for the specific role", 
              "Bypasses the 'blank page' anxiety entirely", 
              "Exports seamlessly to PDF and DOCX"
            ].map((item, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontSize: "0.88rem", color: "rgba(255,255,255,0.8)" }}>
                <div style={{ width: 20, height: 20, borderRadius: 6, background: "rgba(255,255,255,0.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.7rem", flexShrink: 0, color: COLORS.amberLight }}>✓</div>
                {item}
              </div>
            ))}
          </div>
        </div>
        
        <div className="reveal-right delay-3">
          <CoverLetterVisual />
        </div>
      </div>
    </div>
  );
}