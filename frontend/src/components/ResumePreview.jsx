import { Mail, Phone, MapPin, Globe } from "lucide-react";
import { useTemplateCatalog } from "../hooks/useTemplateCatalog";

/**
 * Strip leading/trailing literal double or single quotes from text.
 * Only removes quotes that wrap the entire string, not internal quotes.
 */
function stripQuotes(text) {
  if (typeof text !== "string") return String(text ?? "");
  return text.replace(/^["'\s]+|["'\s]+$/g, "").trim();
}

/**
 * Normalize experience/project descriptions into an array of bullet strings.
 * Handles: arrays, multi-line strings, bullet markers (-, *, numbered), and quote wrapping.
 * Does not invent content — only restructures existing text.
 */
function normalizeBullets(input) {
  if (Array.isArray(input)) {
    return input.map((item) => stripQuotes(String(item).trim())).filter(Boolean);
  }
  if (typeof input === "string" && input.trim()) {
    // Split on newlines with optional bullet markers
    let bullets = input.split(/\n\s*(?:[-*•]\s+)?/);
    // Also split on numbered patterns like "1." "2."
    bullets = bullets.flatMap((b) => b.split(/\n\s*\d+\.\s+/));
    return bullets.map((b) => stripQuotes(b.trim())).filter(Boolean);
  }
  if (input != null && typeof input === "object") {
    // Object value — convert to readable string, not JSON
    return [stripQuotes(String(input))];
  }
  return [];
}

// Inline LinkedIn brand icon
const Linkedin = ({ size = 12, className, ...props }) => (
  <svg
    viewBox="0 0 24 24"
    width={size}
    height={size}
    stroke="currentColor"
    strokeWidth="2"
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    {...props}
  >
    <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
    <rect x="2" y="9" width="4" height="12" />
    <circle cx="4" cy="4" r="2" />
  </svg>
);

export default function ResumePreview({ data, template = "harvard" }) {
  const { catalog } = useTemplateCatalog();

  if (!data) return <div className="p-8 text-center text-gray-400">No content available</div>;

  const templateId = template.toLowerCase();
  const spec = catalog[templateId] || catalog["harvard"];
  
  const colors = spec?.color || {};
  const layout = {
    ...(spec?.layout || {}),
    section_order: data.section_order || spec?.layout?.section_order || [],
    sidebarSections: data.sidebarSections || spec?.layout?.sidebarSections
  };

  // Map fonts
  const getFontClass = () => {
    if (layout.fontFamily === "serif") return "font-serif";
    if (layout.fontFamily === "monospace") return "font-mono";
    return "font-sans";
  };

  const {
    personalInfo = {},
    summary = "",
    experience = [],
    education = [],
    skills = [],
    projects = [],
    certifications = [],
    achievements = [],
  } = data;

  // Render individual section blocks helper
  const renderSection = (type) => {
    const safeStr = (val) => {
      if (val == null) return "";
      if (typeof val === "string") return stripQuotes(val);
      if (typeof val === "object") {
        // Avoid raw JSON output — render as key-value pairs or stringified without wrapping quotes
        if (Array.isArray(val)) return val.map((v) => stripQuotes(String(v))).join(", ");
        return Object.values(val)
          .filter((v) => v != null && v !== "")
          .map((v) => stripQuotes(String(v)))
          .join(", ");
      }
      return String(val);
    };
    const safeArr = (val) => Array.isArray(val) ? val : [];

    switch (type) {
      case "summary":
        if (!summary) return null;
        return (
          <div key="summary" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Summary</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <p className="text-[12px] leading-relaxed" style={{ color: colors.text }}>{safeStr(summary)}</p>
          </div>
        );

      case "experience":
        if (experience.length === 0) return null;
        return (
          <div key="experience" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-2 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Experience</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <div className="flex flex-col gap-3">
              {safeArr(experience).map((exp, idx) => (
                <div key={idx} className="text-[11px]">
                  <div className="flex justify-between items-baseline font-bold" style={{ color: colors.primary }}>
                    <span>{safeStr(exp.role)}</span>
                    <span className="text-[10px] font-normal" style={{ color: colors.secondary }}>{safeStr(exp.duration)}</span>
                  </div>
                  <div className="text-[10.5px] font-semibold mb-1" style={{ color: colors.accent }}>{safeStr(exp.company)}</div>
                  <ul className="list-disc list-inside text-[11px] leading-relaxed" style={{ color: colors.text }}>
                    {normalizeBullets(exp.description).map((bullet, bIdx) => (
                      <li key={bIdx}>{bullet}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        );

      case "education":
        if (education.length === 0) return null;
        return (
          <div key="education" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-2 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Education</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <div className="flex flex-col gap-2">
              {safeArr(education).map((edu, idx) => (
                <div key={idx} className="text-[11px]">
                  <div className="flex justify-between items-baseline font-semibold">
                    <span style={{ color: colors.primary }}>{safeStr(edu.degree)}</span>
                    <span className="text-[10px] font-normal" style={{ color: colors.secondary }}>{safeStr(edu.duration)}</span>
                  </div>
                  <div className="text-[10.5px]" style={{ color: colors.secondary }}>{safeStr(edu.institution)}</div>
                  {edu.description && <p className="text-[10px] italic mt-0.5" style={{ color: colors.text }}>{safeStr(edu.description)}</p>}
                </div>
              ))}
            </div>
          </div>
        );

      case "skills":
        if (skills.length === 0) return null;
        return (
          <div key="skills" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-2 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Skills</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {safeArr(skills).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded text-[10px] font-semibold border"
                  style={{
                    backgroundColor: `${colors.primary}08`,
                    borderColor: `${colors.primary}25`,
                    color: colors.primary
                  }}
                >
                  {safeStr(skill)}
                </span>
              ))}
            </div>
          </div>
        );

      case "projects":
        if (projects.length === 0) return null;
        return (
          <div key="projects" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-2 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Projects</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <div className="flex flex-col gap-2.5">
              {safeArr(projects).map((proj, idx) => (
                <div key={idx} className="text-[11px]">
                  <div className="font-bold" style={{ color: colors.primary }}>{safeStr(proj.name)}</div>
                  <ul className="list-disc list-inside text-[10.5px] leading-relaxed" style={{ color: colors.text }}>
                    {normalizeBullets(proj.description).map((bullet, bIdx) => (
                      <li key={bIdx}>{bullet}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        );

      case "certifications":
        if (certifications.length === 0) return null;
        return (
          <div key="certifications" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Certifications</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <ul className="list-disc list-inside text-[11px] leading-relaxed" style={{ color: colors.text }}>
              {safeArr(certifications).map((cert, idx) => (
                <li key={idx}>{safeStr(cert)}</li>
              ))}
            </ul>
          </div>
        );

      case "achievements":
        if (achievements.length === 0) return null;
        return (
          <div key="achievements" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Achievements</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <ul className="list-disc list-inside text-[11px] leading-relaxed" style={{ color: colors.text }}>
              {safeArr(achievements).map((ach, idx) => (
                <li key={idx}>{safeStr(ach)}</li>
              ))}
            </ul>
          </div>
        );

      default: {
        // GenericSection: render unknown/custom section types dynamically
        // Look for matching data in data[type] or data[type + "s"]
        const sectionData = data[type] || data[type + "s"];
        if (!sectionData) return null;
        const items = Array.isArray(sectionData) ? sectionData : [sectionData];
        if (items.length === 0) return null;
        return (
          <div key={type} className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>{type.replace(/_/g, " ")}</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <div className="flex flex-col gap-1.5">
              {items.map((item, idx) => (
                <div key={idx} className="text-[11px] leading-relaxed" style={{ color: colors.text }}>
                  {typeof item === "string" ? safeStr(item) : (
                    <div className="flex flex-col gap-0.5">
                      {Object.entries(item).filter(([, v]) => v != null && v !== "").map(([k, v]) => (
                        <div key={k}>
                          {k !== "title" && k !== "name" && <span className="font-semibold text-[10px] uppercase tracking-wide" style={{ color: colors.secondary }}>{k.replace(/_/g, " ")}: </span>}
                          <span>{typeof v === "object"
                            ? (Array.isArray(v) ? v.map((i) => stripQuotes(String(i))).join(", ") : Object.values(v).filter((x) => x != null).map((x) => stripQuotes(String(x))).join(", "))
                            : String(v)
                          }</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      }
    }
  };

  // Header styles
  const renderHeader = () => {
    const isCentered = layout.headerStyle === "centered";
    const isBanner = layout.headerStyle === "banner";

    return (
      <div 
        className={`mb-6 border-b pb-4 ${isCentered ? "text-center" : "text-left"} ${isBanner ? "p-6 -mx-6 -mt-6 text-white" : ""}`}
        style={{ 
          borderColor: isBanner ? "transparent" : `${colors.primary}30`,
          background: isBanner ? `linear-gradient(135deg, ${colors.primary}, ${colors.accent || colors.secondary})` : "transparent"
        }}
      >
        <h1 className="text-2xl font-bold tracking-tight mb-1" style={{ color: isBanner ? "#FFFFFF" : colors.primary }}>
          {personalInfo.fullName || "Your Full Name"}
        </h1>
        <p className="text-sm font-semibold tracking-wider uppercase mb-3" style={{ color: isBanner ? "#FFFFFFee" : colors.accent }}>
          {personalInfo.jobTitle || "Job Title Focus"}
        </p>
        
        <div className={`flex flex-wrap gap-x-4 gap-y-1.5 text-[10.5px] ${isCentered ? "justify-center" : "justify-start"}`} style={{ color: isBanner ? "#FFFFFFcc" : colors.secondary }}>
          {personalInfo.email && (
            <span className="flex items-center gap-1">
              <Mail size={11} /> {personalInfo.email}
            </span>
          )}
          {personalInfo.phone && (
            <span className="flex items-center gap-1">
              <Phone size={11} /> {personalInfo.phone}
            </span>
          )}
          {personalInfo.location && (
            <span className="flex items-center gap-1">
              <MapPin size={11} /> {personalInfo.location}
            </span>
          )}
          {personalInfo.website && (
            <span className="flex items-center gap-1">
              <Globe size={11} /> {personalInfo.website}
            </span>
          )}
          {personalInfo.linkedin && (
            <span className="flex items-center gap-1">
              <Linkedin size={11} /> {personalInfo.linkedin}
            </span>
          )}
        </div>
      </div>
    );
  };

  // Core layout assembly
  const renderLayoutContent = () => {
    if (layout.structure === "two-column-left") {
      return (
        <div className="grid grid-cols-12 gap-6 items-start">
          {/* Left Sidebar Column */}
          <div className="col-span-4 flex flex-col gap-4 border-r pr-5" style={{ borderColor: `${colors.primary}15` }}>
            {layout.sidebarSections?.map(sec => renderSection(sec))}
          </div>
          {/* Main Column */}
          <div className="col-span-8 flex flex-col gap-4">
            {layout.section_order.map(sec => renderSection(sec))}
          </div>
        </div>
      );
    }

    if (layout.structure === "two-column-right") {
      return (
        <div className="grid grid-cols-12 gap-6 items-start">
          {/* Main Column */}
          <div className="col-span-8 flex flex-col gap-4">
            {layout.section_order.map(sec => renderSection(sec))}
          </div>
          {/* Right Sidebar Column */}
          <div className="col-span-4 flex flex-col gap-4 border-l pl-5" style={{ borderColor: `${colors.primary}15` }}>
            {layout.sidebarSections?.map(sec => renderSection(sec))}
          </div>
        </div>
      );
    }

    // Default structure: single-column
    return (
      <div className="flex flex-col gap-4">
        {layout.section_order.map(sec => renderSection(sec))}
      </div>
    );
  };

  return (
    <div
      className={`w-full shadow-2xl rounded-sm border p-8 sm:p-12 mx-auto relative overflow-hidden transition-all duration-300 ${getFontClass()}`}
      style={{
        aspectRatio: "1 / 1.414", // A4 Ratio
        backgroundColor: colors.background || "#FFFFFF",
        borderColor: "rgba(0,0,0,0.06)",
        color: colors.text
      }}
    >
      {renderHeader()}
      {renderLayoutContent()}
    </div>
  );
}
