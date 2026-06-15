import { COLORS } from "../utils/constants";

export default function FinalCTA({ onBuildResume }) {
  return (
    <div className="final-cta">
      <div className="cta-bg-circle" style={{ width: 500, height: 500, top: "-20%", right: "-10%" }} />
      <div className="cta-bg-circle" style={{ width: 300, height: 300, bottom: "-15%", left: "-5%" }} />
      <div className="final-cta-inner">
        <h2 className="final-cta-headline reveal">
          Your next interview<br />
          <em style={{ fontStyle: "italic", color: COLORS.amberLight }}>starts with one resume</em>
        </h2>
        <p className="final-cta-sub reveal delay-2">
          Join 240,000+ job seekers who built their career-winning resume on ResumeAI. Free to start, results in 60 seconds.
        </p>
        <div className="final-cta-btns reveal delay-3">
          <button className="btn-cta-white" onClick={onBuildResume}>Build my resume — it's free</button>
          <button className="btn-cta-outline" onClick={() => document.getElementById("templates")?.scrollIntoView({ behavior: "smooth" })}>Explore templates</button>
        </div>
        <p className="final-cta-note reveal delay-4">No credit card · No setup · Instant export</p>
      </div>
    </div>
  );
}