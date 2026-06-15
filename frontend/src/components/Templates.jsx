import { COLORS } from "../utils/constants";

const TEMPLATES = [
  { name: "Meridian", tag: "Modern",    hue: COLORS.teal,    lines: [0.9,0.6,0.85,0.5,0.75,0.4,0.8] },
  { name: "Ashford", tag: "Executive",  hue: "#4A5568",      lines: [0.85,0.55,0.8,0.65,0.7,0.5,0.75] },
  { name: "Luma",    tag: "Minimal",    hue: COLORS.tealDark, lines: [0.9,0.5,0.7,0.6,0.8,0.45,0.65] },
  { name: "Pulse",   tag: "Developer",  hue: "#1E3A8A",      lines: [0.8,0.7,0.9,0.55,0.75,0.6,0.85] },
];

export default function Templates({ onBuildResume }) {
  return (
    <div className="templates-section" id="templates">
      <div className="templates-inner">
        <div className="text-centered">
          <div className="section-tag reveal" style={{ display: "inline-flex" }}>◧ Resume Templates</div>
          <h2 className="section-headline reveal delay-1">Professional templates<br />that get noticed</h2>
          <p className="section-sub centered reveal delay-2">
            Every template is ATS-safe, recruiter-approved, and designed by professional resume writers and product designers.
          </p>
        </div>
        <div className="template-grid">
          {TEMPLATES.map((t, i) => (
            <div className={`template-card reveal delay-${i + 2}`} key={i} onClick={() => onBuildResume(t.name)}>
              <div className="template-preview">
                <div className="template-preview-header" style={{ background: t.hue }}>
                  <div className="template-preview-name-line" />
                  <div className="template-preview-role-line" />
                </div>
                <div className="template-preview-body">
                  {t.lines.map((w, j) => (
                    <div key={j} className="template-line" style={{ width: `${w * 100}%` }} />
                  ))}
                </div>
              </div>
              <div className="template-info">
                <span className="template-name">{t.name}</span>
                <span className="template-tag">{t.tag}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}