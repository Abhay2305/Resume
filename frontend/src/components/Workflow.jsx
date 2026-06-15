const WORKFLOW_STEPS = [
  { num: "01", title: "Choose your mode", desc: "Pick AI-assisted generation for speed, or manual mode for full control." },
  { num: "02", title: "Enter your information", desc: "Describe yourself in natural language or fill structured sections." },
  { num: "03", title: "AI formats and optimizes", desc: "Our system structures content, applies professional formatting, and runs ATS analysis." },
  { num: "04", title: "Review and refine", desc: "See your live ATS score. Edit any section inline. Swap templates instantly." },
  { num: "05", title: "Export and apply", desc: "Download PDF, DOCX, or plain text. Your resume is ready." },
];

export default function Workflow() {
  return (
    <div className="workflow-section" id="how">
      <div className="workflow-inner">
        <div>
          <div className="section-tag reveal">⬡ How It Works</div>
          <h2 className="section-headline reveal delay-1">From blank page to<br />interview in 5 steps</h2>
        </div>
        <div className="workflow-steps">
          {WORKFLOW_STEPS.map((s, i) => (
            <div className={`workflow-step reveal delay-${i + 2}`} key={i}>
              <div className="workflow-step-num">{s.num}</div>
              <div className="workflow-step-content">
                <div className="workflow-step-title">{s.title}</div>
                <div className="workflow-step-desc">{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}