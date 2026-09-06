const TEMPLATES = [
  {
    id: "meridian",
    templateName: "Meridian",
    style: "modern",
    accent: "#7BC4BE",
    headerBg: "linear-gradient(135deg, #4A9E98, #7BC4BE)",
    personName: "Alexandra Chen",
    role: "Senior Product Designer",
    location: "San Francisco, CA",
    sections: [
      { label: "Experience", lines: [0.95, 0.75, 0.85, 0.55] },
      { label: "Skills", tags: ["Figma", "React", "UX Research", "Prototyping", "Design Systems"] },
      { label: "Education", lines: [0.9, 0.6] },
    ],
  },
  {
    id: "ashford",
    templateName: "Ashford",
    style: "executive",
    accent: "#4A5568",
    headerBg: "linear-gradient(135deg, #2D3748, #4A5568)",
    personName: "James Mitchell",
    role: "VP of Engineering",
    location: "New York, NY",
    sections: [
      { label: "Experience", lines: [0.92, 0.7, 0.88] },
      { label: "Leadership", tags: ["Team Building", "Strategy", "Agile", "Cloud Architecture"] },
      { label: "Education", lines: [0.85, 0.55] },
    ],
  },
  {
    id: "luma",
    templateName: "Luma",
    style: "minimal",
    accent: "#2D7A74",
    headerBg: "linear-gradient(135deg, #1A2B2A, #2D7A74)",
    personName: "Sarah Park",
    role: "Data Scientist",
    location: "Seattle, WA",
    sections: [
      { label: "Experience", lines: [0.88, 0.65, 0.8] },
      { label: "Expertise", tags: ["Python", "ML/AI", "TensorFlow", "SQL", "NLP"] },
      { label: "Publications", lines: [0.92, 0.5] },
    ],
  },
  {
    id: "pulse",
    templateName: "Pulse",
    style: "developer",
    accent: "#1E3A8A",
    headerBg: "linear-gradient(135deg, #1E3A8A, #3B82F6)",
    personName: "Marcus Rivera",
    role: "Full-Stack Engineer",
    location: "Austin, TX",
    sections: [
      { label: "Experience", lines: [0.9, 0.72, 0.85, 0.6] },
      { label: "Tech Stack", tags: ["TypeScript", "Node.js", "React", "AWS", "PostgreSQL"] },
      { label: "Open Source", lines: [0.88, 0.45] },
    ],
  },
  {
    id: "cascade",
    templateName: "Cascade",
    style: "creative",
    accent: "#9333EA",
    headerBg: "linear-gradient(135deg, #7C3AED, #A855F7)",
    personName: "Elena Vasquez",
    role: "Creative Director",
    location: "Los Angeles, CA",
    sections: [
      { label: "Experience", lines: [0.94, 0.68, 0.82] },
      { label: "Capabilities", tags: ["Branding", "Motion Design", "Art Direction", "Figma"] },
      { label: "Awards", lines: [0.87, 0.52] },
    ],
  },
  {
    id: "atlas",
    templateName: "Atlas",
    style: "corporate",
    accent: "#0F766E",
    headerBg: "linear-gradient(135deg, #0F766E, #14B8A6)",
    personName: "David Okafor",
    role: "Management Consultant",
    location: "Chicago, IL",
    sections: [
      { label: "Experience", lines: [0.91, 0.74, 0.86] },
      { label: "Competencies", tags: ["Strategy", "M&A", "Due Diligence", "Financial Modeling"] },
      { label: "Education", lines: [0.88, 0.58] },
    ],
  },
  {
    id: "nova",
    templateName: "Nova",
    style: "startup",
    accent: "#EA580C",
    headerBg: "linear-gradient(135deg, #EA580C, #F97316)",
    personName: "Priya Sharma",
    role: "Product Manager",
    location: "San Jose, CA",
    sections: [
      { label: "Experience", lines: [0.89, 0.71, 0.83, 0.56] },
      { label: "Skills", tags: ["Roadmapping", "Analytics", "A/B Testing", "SQL", "Jira"] },
      { label: "Education", lines: [0.86, 0.48] },
    ],
  },
  {
    id: "zenith",
    templateName: "Zenith",
    style: "elegant",
    accent: "#B45309",
    headerBg: "linear-gradient(135deg, #92400E, #D97706)",
    personName: "Thomas Laurent",
    role: "Investment Analyst",
    location: "Boston, MA",
    sections: [
      { label: "Experience", lines: [0.93, 0.69, 0.87] },
      { label: "Skills", tags: ["DCF Valuation", "Excel", "Bloomberg", "Financial Analysis"] },
      { label: "Education", lines: [0.9, 0.54] },
    ],
  },
];

function TemplatePreview({ template }) {
  return (
    <div className="rc-inner">
      <div className="rc-header" style={{ background: template.headerBg }}>
        <div className="rc-name">{template.personName}</div>
        <div className="rc-role">{template.role}</div>
        <div className="rc-location">{template.location}</div>
      </div>
      <div className="rc-body">
        {template.sections.map((section, i) => (
          <div key={i} className="rc-section">
            <div className="rc-section-label">{section.label}</div>
            {section.lines && section.lines.map((w, j) => (
              <div key={j} className="rc-line" style={{ width: `${w * 100}%` }} />
            ))}
            {section.tags && (
              <div className="rc-tags">
                {section.tags.map((tag, k) => (
                  <span
                    key={k}
                    className="rc-tag"
                    style={{
                      borderColor: `${template.accent}30`,
                      background: `${template.accent}10`,
                      color: template.accent,
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ResumeCard({ templateIndex = 0, size = "portrait" }) {
  const template = TEMPLATES[templateIndex % TEMPLATES.length];

  return (
    <div className={`gallery-card gallery-card--${size}`}>
      <TemplatePreview template={template} />
      <div className="rc-footer">
        <span
          className="rc-badge"
          style={{ background: `${template.accent}12`, color: template.accent }}
        >
          {template.templateName}
        </span>
        <span className="rc-style">{template.style}</span>
      </div>
    </div>
  );
}

export function FeaturedCard({ templateIndex = 0 }) {
  const template = TEMPLATES[templateIndex % TEMPLATES.length];

  return (
    <div className="featured-card">
      <div className="featured-card-glow" style={{ background: `${template.accent}12` }} />
      <div className="featured-card-label">
        <span className="featured-card-dot" style={{ background: template.accent }} />
        Featured Template
      </div>
      <div className="featured-card-inner">
        <TemplatePreview template={template} />
        <div className="rc-footer">
          <span
            className="rc-badge"
            style={{ background: `${template.accent}12`, color: template.accent }}
          >
            {template.templateName}
          </span>
          <span className="rc-style">{template.style}</span>
        </div>
      </div>
    </div>
  );
}

export { TEMPLATES };
