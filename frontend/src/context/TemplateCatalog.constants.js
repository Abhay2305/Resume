// Hardcoded fallback catalog for when API is unavailable
export const FALLBACK_CATALOG = {
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

/**
 * Converts a CMS template item into the catalog format used by ResumePreview.
 */
export function cmsTemplateToCatalog(t) {
  return {
    color: t.colors || t.color_scheme || {},
    layout: t.template_definition?.layout || t.layout_schema || {},
    thumbnail_url: t.thumbnail_url,
    preview_images: t.preview_images,
    category: t.category,
    description: t.description,
    status: t.status,
    version: t.version,
    author: t.author,
    tags: t.tags,
  };
}
