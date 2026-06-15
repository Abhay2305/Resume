import React from "react";
import { Mail, Phone, MapPin, Globe, Award, Briefcase, GraduationCap, Code, FolderGit } from "lucide-react";

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

// Metadata specifications for all 24 templates as a fallback catalog
const TEMPLATES_CATALOG = {
  // ATS Category
  harvard: {
    color: { primary: "#000000", secondary: "#4A4A4A", text: "#1A1A1A", accent: "#A51C30", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.75in", headerStyle: "centered", section_order: ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"] }
  },
  stanford: {
    color: { primary: "#8C1515", secondary: "#4D4F53", text: "#2E2D29", accent: "#8C1515", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "sans-serif", margins: "0.75in", headerStyle: "left", section_order: ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"] }
  },
  mit: {
    color: { primary: "#A31F34", secondary: "#8A8B8C", text: "#111111", accent: "#A31F34", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "monospace", margins: "0.5in", headerStyle: "left", section_order: ["education", "skills", "experience", "projects", "certifications", "achievements"] }
  },
  columbia: {
    color: { primary: "#003087", secondary: "#6CACE4", text: "#1D252D", accent: "#003087", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.8in", headerStyle: "centered", section_order: ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"] }
  },
  yale: {
    color: { primary: "#00356B", secondary: "#28619E", text: "#0F0F0F", accent: "#00356B", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.75in", headerStyle: "centered", section_order: ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"] }
  },
  princeton: {
    color: { primary: "#EE7F2D", secondary: "#222222", text: "#1C1C1C", accent: "#EE7F2D", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.75in", headerStyle: "left", section_order: ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"] }
  },
  // Corporate Category
  executive: {
    color: { primary: "#0F172A", secondary: "#475569", text: "#1E293B", accent: "#B45309", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.75in", headerStyle: "centered", section_order: ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"] }
  },
  consultant: {
    color: { primary: "#1E293B", secondary: "#64748B", text: "#334155", accent: "#0F766E", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "sans-serif", margins: "0.7in", headerStyle: "left", section_order: ["summary", "experience", "projects", "education", "skills", "certifications", "achievements"] }
  },
  finance: {
    color: { primary: "#064E3B", secondary: "#115E59", text: "#0F172A", accent: "#0D9488", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.75in", headerStyle: "centered", section_order: ["summary", "experience", "education", "skills", "certifications", "achievements"] }
  },
  product_manager: {
    color: { primary: "#4F46E5", secondary: "#475569", text: "#1E293B", accent: "#4F46E5", background: "#FFFFFF" },
    layout: { structure: "two-column-right", fontFamily: "sans-serif", margins: "0.6in", headerStyle: "left", section_order: ["summary", "experience", "projects"], sidebarSections: ["education", "skills", "certifications", "achievements"] }
  },
  operations: {
    color: { primary: "#334155", secondary: "#475569", text: "#0F172A", accent: "#2563EB", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "sans-serif", margins: "0.75in", headerStyle: "left", section_order: ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"] }
  },
  management: {
    color: { primary: "#881337", secondary: "#4C0519", text: "#1F2937", accent: "#9F1239", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.75in", headerStyle: "centered", section_order: ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"] }
  },
  // Technology Category
  software_engineer: {
    color: { primary: "#0F766E", secondary: "#334155", text: "#0F172A", accent: "#0D9488", background: "#FFFFFF" },
    layout: { structure: "two-column-left", fontFamily: "sans-serif", margins: "0.6in", headerStyle: "left", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education", "certifications", "achievements"] }
  },
  data_scientist: {
    color: { primary: "#1E3A8A", secondary: "#475569", text: "#1E293B", accent: "#3B82F6", background: "#FFFFFF" },
    layout: { structure: "two-column-left", fontFamily: "sans-serif", margins: "0.6in", headerStyle: "left", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education", "certifications"] }
  },
  ai_engineer: {
    color: { primary: "#312E81", secondary: "#4F46E5", text: "#111827", accent: "#F59E0B", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "monospace", margins: "0.6in", headerStyle: "left", section_order: ["summary", "skills", "experience", "projects", "education", "certifications"] }
  },
  devops: {
    color: { primary: "#4C1D95", secondary: "#6D28D9", text: "#1F2937", accent: "#8B5CF6", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "monospace", margins: "0.6in", headerStyle: "left", section_order: ["summary", "skills", "experience", "projects", "education"] }
  },
  cloud_engineer: {
    color: { primary: "#0369A1", secondary: "#0284C7", text: "#0F172A", accent: "#0EA5E9", background: "#FFFFFF" },
    layout: { structure: "two-column-left", fontFamily: "sans-serif", margins: "0.6in", headerStyle: "left", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education", "certifications"] }
  },
  cybersecurity: {
    color: { primary: "#065F46", secondary: "#047857", text: "#111827", accent: "#10B981", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "monospace", margins: "0.65in", headerStyle: "left", section_order: ["summary", "skills", "experience", "projects", "education", "certifications"] }
  },
  // Creative Category
  ui_ux: {
    color: { primary: "#6B21A8", secondary: "#DB2777", text: "#1F2937", accent: "#F472B6", background: "#FFFFFF" },
    layout: { structure: "two-column-left", fontFamily: "sans-serif", margins: "0.5in", headerStyle: "banner", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education", "achievements"] }
  },
  graphic_designer: {
    color: { primary: "#C2410C", secondary: "#1E293B", text: "#0F172A", accent: "#EA580C", background: "#FFFFFF" },
    layout: { structure: "single-column", fontFamily: "sans-serif", margins: "0.6in", headerStyle: "left", section_order: ["summary", "projects", "experience", "education", "skills"] }
  },
  marketing: {
    color: { primary: "#BE185D", secondary: "#475569", text: "#1E293B", accent: "#F43F5E", background: "#FFFFFF" },
    layout: { structure: "two-column-right", fontFamily: "sans-serif", margins: "0.6in", headerStyle: "left", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education", "certifications"] }
  },
  content_creator: {
    color: { primary: "#1D4ED8", secondary: "#2563EB", text: "#1E293B", accent: "#F59E0B", background: "#FFFFFF" },
    layout: { structure: "two-column-left", fontFamily: "sans-serif", margins: "0.55in", headerStyle: "left", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education"] }
  },
  photographer: {
    color: { primary: "#1F2937", secondary: "#4B5563", text: "#111827", accent: "#78350F", background: "#FCFBF7" },
    layout: { structure: "single-column", fontFamily: "serif", margins: "0.8in", headerStyle: "centered", section_order: ["summary", "projects", "experience", "education"] }
  },
  creative_director: {
    color: { primary: "#000000", secondary: "#111827", text: "#222222", accent: "#FBBF24", background: "#FFFFFF" },
    layout: { structure: "two-column-right", fontFamily: "sans-serif", margins: "0.5in", headerStyle: "banner", section_order: ["summary", "experience", "projects"], sidebarSections: ["skills", "education", "achievements"] }
  }
};

export default function ResumePreview({ data, template = "harvard" }) {
  if (!data) return <div className="p-8 text-center text-gray-400">No content available</div>;

  // Retrieve template specs from catalog or fallback to standard harvard
  const templateId = template.toLowerCase();
  const spec = TEMPLATES_CATALOG[templateId] || TEMPLATES_CATALOG["harvard"];
  
  const colors = spec.color;
  const layout = {
    ...spec.layout,
    section_order: data.section_order || spec.layout.section_order,
    sidebarSections: data.sidebarSections || spec.layout.sidebarSections
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
    switch (type) {
      case "summary":
        if (!summary) return null;
        return (
          <div key="summary" className="mb-4">
            <h3 className="text-xs font-bold uppercase tracking-wider mb-1.5 flex items-center gap-2" style={{ color: colors.primary }}>
              <span>Summary</span>
              <span className="flex-grow h-[1px]" style={{ backgroundColor: `${colors.primary}20` }} />
            </h3>
            <p className="text-[12px] leading-relaxed" style={{ color: colors.text }}>{summary}</p>
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
              {experience.map((exp, idx) => (
                <div key={idx} className="text-[11px]">
                  <div className="flex justify-between items-baseline font-bold" style={{ color: colors.primary }}>
                    <span>{exp.role}</span>
                    <span className="text-[10px] font-normal" style={{ color: colors.secondary }}>{exp.duration}</span>
                  </div>
                  <div className="text-[10.5px] font-semibold mb-1" style={{ color: colors.accent }}>{exp.company}</div>
                  <p className="text-[11px] whitespace-pre-line leading-relaxed" style={{ color: colors.text }}>
                    {exp.description}
                  </p>
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
              {education.map((edu, idx) => (
                <div key={idx} className="text-[11px]">
                  <div className="flex justify-between items-baseline font-semibold">
                    <span style={{ color: colors.primary }}>{edu.degree}</span>
                    <span className="text-[10px] font-normal" style={{ color: colors.secondary }}>{edu.duration}</span>
                  </div>
                  <div className="text-[10.5px]" style={{ color: colors.secondary }}>{edu.institution}</div>
                  {edu.description && <p className="text-[10px] italic mt-0.5" style={{ color: colors.text }}>{edu.description}</p>}
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
              {skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded text-[10px] font-semibold border"
                  style={{
                    backgroundColor: `${colors.primary}08`,
                    borderColor: `${colors.primary}25`,
                    color: colors.primary
                  }}
                >
                  {skill}
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
              {projects.map((proj, idx) => (
                <div key={idx} className="text-[11px]">
                  <div className="font-bold" style={{ color: colors.primary }}>{proj.name}</div>
                  <p className="text-[10.5px] leading-relaxed" style={{ color: colors.text }}>{proj.description}</p>
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
              {certifications.map((cert, idx) => (
                <li key={idx}>{cert}</li>
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
              {achievements.map((ach, idx) => (
                <li key={idx}>{ach}</li>
              ))}
            </ul>
          </div>
        );

      default:
        return null;
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
