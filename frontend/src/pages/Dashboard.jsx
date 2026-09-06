import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FileText, Mail, Layout, User, CreditCard, LogOut, 
  Plus, Trash2, Edit3, Download, RefreshCw, 
  Briefcase, MapPin, Phone, Globe, ExternalLink,
  Lock, Sparkles, ArrowRight
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import ResumePreview from "../components/ResumePreview";
import TemplatePreviewModal from "../components/TemplatePreviewModal";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("profile"); // profile, resumes, letters, templates, jd, account
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState({});
  const [resumes, setResumes] = useState([]);
  const [letters, setLetters] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [sub, setSub] = useState({ plan_type: "free", status: "active" });
  const [payments, setPayments] = useState([]);
  const [, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [previewTemplateId, setPreviewTemplateId] = useState(
    () => sessionStorage.getItem("lastPreviewTemplate") || "harvard"
  );

  const navigate = useNavigate();
  const { logout } = useAuth();

  // Load user details & database records
  const loadData = async () => {
    try {
      setLoading(true);

      // Auth check — if this fails, user is not logged in
      let me;
      try {
        me = await api.auth.getMe();
        setUser(me);
      } catch (authErr) {
        console.error("Auth check failed, redirecting to login:", authErr);
        logout();
        navigate("/login");
        return;
      }

      // Profile — non-critical, default to empty
      try {
        const prof = await api.user.getProfile();
        setProfile(prof);
      } catch (err) {
        console.error("Failed to load profile:", err);
      }

      // Resumes — non-critical, default to empty
      try {
        const resList = await api.resumes.list();
        setResumes(resList);
      } catch (err) {
        console.error("Failed to load resumes:", err);
      }

      // Cover letters — non-critical, default to empty
      try {
        const lettersList = await api.coverLetters.list();
        setLetters(lettersList);
      } catch (err) {
        console.error("Failed to load cover letters:", err);
      }

      // Templates — non-critical, default to empty
      try {
        const tempsRes = await api.templates.getPublished();
        setTemplates(Array.isArray(tempsRes) ? tempsRes : tempsRes.items || []);
      } catch (err) {
        console.error("Failed to load templates:", err);
      }

      // Subscription — non-critical, default to free
      try {
        const subscription = await api.user.getSubscription();
        setSub(subscription);
      } catch (err) {
        console.error("Failed to load subscription:", err);
      }

      // Billing — non-critical, default to empty
      try {
        const billing = await api.user.getBillingHistory();
        setPayments(billing);
      } catch (err) {
        console.error("Failed to load billing history:", err);
      }

      // Activity log — non-critical, default to empty
      try {
        const acts = await api.user.getActivityLog();
        setActivity(acts);
      } catch (err) {
        console.error("Failed to load activity log:", err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // Resume operations
  const handleCreateResume = async () => {
    navigate("/resume/create-flow");
  };

  const handleDeleteResume = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    try {
      await api.resumes.delete(id);
      setResumes(resumes.filter(r => r.id !== id));
    } catch (err) {
      alert("Delete failed: " + err.message);
    }
  };

  // Cover letter operations
  const [showLetterModal, setShowLetterModal] = useState(false);
  const [letterForm, setLetterForm] = useState({ jobRole: "", companyName: "", experienceSummary: "" });
  const [letterSubmitting, setLetterSubmitting] = useState(false);

  const handleCreateCoverLetter = () => {
    // Pre-fill experience context from profile
    const experienceContext = [
      profile.job_title ? `Current role: ${profile.job_title}` : "",
      profile.company ? `Company: ${profile.company}` : "",
      profile.summary ? `Summary: ${profile.summary.substring(0, 200)}...` : "",
    ].filter(Boolean).join("\n");
    
    setLetterForm({ 
      jobRole: "", 
      companyName: "", 
      experienceSummary: experienceContext 
    });
    setShowLetterModal(true);
  };

  const submitCoverLetter = async (e) => {
    e.preventDefault();
    const { jobRole, companyName, experienceSummary } = letterForm;
    if (!jobRole.trim() || !companyName.trim()) {
      alert("Job role and company name are required.");
      return;
    }
    try {
      setLetterSubmitting(true);
      const letter = await api.coverLetters.generate(
        `Cover Letter - ${companyName}`,
        jobRole,
        companyName,
        experienceSummary
      );
      setLetters((prev) => [letter, ...prev]);
      setShowLetterModal(false);
      setActiveTab("letters");
    } catch (err) {
      alert("Generation failed: " + err.message);
    } finally {
      setLetterSubmitting(false);
    }
  };

  const handleDeleteLetter = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this cover letter?")) return;
    try {
      await api.coverLetters.delete(id);
      setLetters(letters.filter(l => l.id !== id));
    } catch (err) {
      alert("Delete failed: " + err.message);
    }
  };

  // Selections
  const handleOpenPreview = (templateId) => {
    setPreviewTemplateId(templateId);
    sessionStorage.setItem("lastPreviewTemplate", templateId);
    setShowPreviewModal(true);
  };

  const handleUseTemplateFromPreview = async (templateId, resumeName) => {
    try {
      const res = await api.resumes.create(resumeName, templateId);

      // Auto-fill from expanded profile if available
      if (profile) {
        const parseJson = (val) => {
          if (!val) return [];
          try { const p = JSON.parse(val); return Array.isArray(p) ? p : []; } catch { return []; }
        };
        const sections = [
          {
            section_type: "personalInfo",
            content: {
              fullName: user?.full_name || "",
              jobTitle: profile.job_title || "",
              email: user?.email || "",
              phone: profile.phone || "",
              location: profile.location || "",
              website: profile.website || "",
              linkedin: profile.linkedin || "",
            },
            position: 0,
          },
          {
            section_type: "summary",
            content: profile.summary || "",
            position: 1,
          },
          {
            section_type: "experience",
            content: parseJson(profile.experience_json),
            position: 2,
          },
          {
            section_type: "education",
            content: parseJson(profile.education_json),
            position: 3,
          },
          {
            section_type: "skills",
            content: parseJson(profile.skills_json),
            position: 4,
          },
          {
            section_type: "projects",
            content: parseJson(profile.projects_json),
            position: 5,
          },
          {
            section_type: "certifications",
            content: parseJson(profile.certifications_json),
            position: 6,
          },
          {
            section_type: "achievements",
            content: parseJson(profile.achievements_json),
            position: 7,
          },
        ];
        await api.resumes.saveSections(res.id, sections);
      }

      setShowPreviewModal(false);
      navigate(`/resume/edit/${res.id}`);
    } catch (err) {
      alert("Failed to create resume: " + err.message);
    }
  };

  // Save profile changes
  const handleSaveProfile = async (e) => {
    e.preventDefault();
    try {
      const updated = await api.user.updateProfile({
        phone: profile.phone || null,
        location: profile.location || null,
        job_title: profile.job_title || null,
        company: profile.company || null,
        industry: profile.industry || null,
        years_of_experience: profile.years_of_experience ? parseInt(profile.years_of_experience) : null,
        education_level: profile.education_level || null,
        summary: profile.summary || null,
        linkedin: profile.linkedin || null,
        github: profile.github || null,
        website: profile.website || null,
        portfolio: profile.portfolio || null,
        professional_headline: profile.professional_headline || null,
        date_of_birth: profile.date_of_birth || null,
      });
      setProfile(updated);
      alert("Profile updated successfully!");
    } catch (err) {
      alert("Failed to save profile: " + err.message);
    }
  };

  // Trigger Playwright PDF download direct from dashboard
  const handleDownloadPDF = async (resume, e) => {
    e.stopPropagation();
    try {
      alert("Compiling PDF with Playwright... download will begin shortly.");
      // Render resume HTML on client
      const el = document.createElement("div");
      el.style.position = "absolute";
      el.style.left = "-9999px";
      document.body.appendChild(el);
      
      // Let's create a minimal container with tailwind loaded to pass to playwright
      const resumeHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <script src="https://cdn.tailwindcss.com"></script>
          <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&family=Fira+Code&family=Lora:ital,wght@0,400;0,700;1,400&family=Outfit:wght@400;500;700&family=Roboto+Mono&display=swap" rel="stylesheet">
          <style>
            body { font-family: 'DM Sans', sans-serif; background: white; color: #1f2937; }
            .serif { font-family: 'DM Serif Display', 'Lora', serif; }
            .mono { font-family: 'Fira Code', 'Roboto Mono', monospace; }
          </style>
        </head>
        <body class="p-8">
          <div style="width: 794px; min-height: 1123px; margin: auto;">
            ${document.getElementById(`res-preview-hidden-${resume.id}`)?.innerHTML || "No preview data found"}
          </div>
        </body>
        </html>
      `;
      
      const blob = await api.pdf.export(resumeHtml, `${resume.title.replace(/\s+/g, "_")}.pdf`);
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `${resume.title}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      alert("Failed to export PDF: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col items-center justify-center gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={40} />
        <p className="text-gray-400 text-sm">Synchronizing career profile data...</p>
      </div>
    );
  }

  const sidebarItems = [
    { id: "profile", label: "Profile", icon: User },
    { id: "resumes", label: "My Resume", icon: FileText },
    { id: "letters", label: "My Cover Letter", icon: Mail },
    { id: "templates", label: "My Templates", icon: Layout },
    { id: "jd", label: "JD Based", icon: Briefcase },
    { id: "account", label: "Account", icon: CreditCard },
  ];

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white flex overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white/5 border-r border-white/10 flex flex-col justify-between shrink-0">
        <div>
          <div className="p-6 border-b border-white/5">
            <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
              <span className="text-[#7BC4BE]">✦</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
            </span>
            <div className="mt-2 text-[10px] uppercase font-bold tracking-widest text-[#7BC4BE] bg-[#7BC4BE]/15 px-2 py-0.5 rounded inline-block">
              {(sub.plan_type || "free").toUpperCase()} PLAN
            </div>
          </div>
          <nav className="p-4 space-y-1">
            {sidebarItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    if (item.id === "jd") {
                      navigate("/jd-based");
                    } else {
                      setActiveTab(item.id);
                    }
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-semibold transition-all ${
                    isActive 
                      ? "bg-[#7BC4BE] text-[#1A2B2A] shadow-md shadow-[#7BC4BE]/15" 
                      : "text-gray-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <Icon size={16} />
                  {item.label}
                </button>
              );
            })}
          </nav>
        </div>
        
        <div className="p-4 border-t border-white/5 space-y-2">
          <div className="flex items-center gap-2 px-4 py-2">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#7BC4BE] to-[#4A9E98] text-[#1A2B2A] flex items-center justify-center font-bold text-sm">
              {user?.full_name ? user.full_name[0].toUpperCase() : "U"}
            </div>
            <div className="truncate">
              <div className="text-xs font-semibold truncate">{user?.full_name || "User Account"}</div>
              <div className="text-[10px] text-gray-500 truncate">{user?.email}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-xs font-semibold text-rose-400 hover:bg-rose-500/10 transition-all"
          >
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Panel Content Area */}
      <main className="flex-1 overflow-y-auto p-8 relative">
        {/* Hidden Preview Container for Playwright HTML parsing */}
        <div className="hidden">
          {resumes.map(r => {
            const sections = r.sections || [];
            const getSectionContent = (type, fallback) => {
              const content = sections.find(s => s.section_type === type)?.content;
              if (content == null) return fallback;
              if (typeof content === "object" && !Array.isArray(content) && Object.keys(content).length === 0) return fallback;
              return content;
            };
            const getStringContent = (type, fallback) => {
              const content = getSectionContent(type, fallback);
              return typeof content === "string" ? content : fallback;
            };
            const getArrayContent = (type, fallback) => {
              const content = getSectionContent(type, fallback);
              return Array.isArray(content) ? content : fallback;
            };
            const piContent = getSectionContent("personalInfo", null);
            return (
            <div key={r.id} id={`res-preview-hidden-${r.id}`}>
              <ResumePreview 
                data={{
                  personalInfo: {
                    fullName: (piContent?.fullName) || user?.full_name || "Applicant Name",
                    jobTitle: (piContent?.jobTitle) || profile.job_title || "Professional",
                    email: (piContent?.email) || user?.email || "",
                    phone: (piContent?.phone) || profile.phone || "",
                    location: (piContent?.location) || profile.location || "",
                    website: (piContent?.website) || profile.website || "",
                    linkedin: (piContent?.linkedin) || profile.linkedin || ""
                  },
                  summary: getStringContent("summary", "") || profile.summary || "",
                  experience: getArrayContent("experience", []),
                  education: getArrayContent("education", []),
                  skills: getArrayContent("skills", []),
                  projects: getArrayContent("projects", []),
                  certifications: getArrayContent("certifications", []),
                  achievements: getArrayContent("achievements", [])
                }} 
                template={r.template_id || "harvard"} 
              />
            </div>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          {/* TAB: MY RESUMES */}
          {activeTab === "resumes" && (
            <motion.div
              key="resumes"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">My Resume</h1>
                  <p className="text-gray-400 text-xs mt-1">Manage and edit your saved drafts</p>
                </div>
                <button
                  onClick={handleCreateResume}
                  className="px-4 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                >
                  <Plus size={14} /> Create Resume
                </button>
              </div>

              {resumes.length === 0 ? (
                <div className="bg-white/5 border border-white/10 rounded-2xl p-16 text-center text-gray-400 text-xs">
                  <FileText className="mx-auto text-gray-600 mb-3" size={36} />
                  No resumes in database. Create your first resume using the manual builder or AI assistant.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {resumes.map(res => (
                    <div
                      key={res.id}
                      onClick={() => navigate(`/resume/edit/${res.id}`)}
                      className="bg-white/5 border border-white/10 hover:border-[#7BC4BE]/40 rounded-2xl p-6 cursor-pointer hover:shadow-xl transition-all duration-300 relative group flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex justify-between items-start mb-3">
                          <h3 className="text-sm font-bold text-white group-hover:text-[#7BC4BE] transition-colors">{res.title}</h3>
                          <div className="text-[10px] bg-[#7BC4BE]/15 text-[#7BC4BE] px-2 py-0.5 rounded font-bold uppercase">
                            {res.template_id || "Harvard"}
                          </div>
                        </div>
                        <p className="text-[10px] text-gray-400 mb-6">
                          Updated: {new Date(res.updated_at).toLocaleDateString()}
                        </p>
                      </div>

                      <div className="flex justify-between items-center pt-4 border-t border-white/5">
                        <div className="flex gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/resume/edit/${res.id}`);
                            }}
                            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-gray-300 hover:text-white transition-all"
                            title="Edit Resume"
                          >
                            <Edit3 size={12} />
                          </button>
                          <button
                            onClick={(e) => handleDownloadPDF(res, e)}
                            className="p-2 bg-white/5 hover:bg-white/10 rounded-lg text-[#7BC4BE] transition-all"
                            title="Download PDF"
                          >
                            <Download size={12} />
                          </button>
                        </div>
                        <button
                          onClick={(e) => handleDeleteResume(res.id, e)}
                          className="p-2 bg-white/5 hover:bg-rose-500/15 rounded-lg text-rose-400 transition-all"
                          title="Delete Resume"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* TAB: COVER LETTERS */}
          {activeTab === "letters" && (
            <motion.div
              key="letters"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div className="flex justify-between items-center">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">My Cover Letter</h1>
                  <p className="text-gray-400 text-xs mt-1">Generate targeted applications for active roles</p>
                </div>
                <button
                  onClick={handleCreateCoverLetter}
                  className="px-4 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                >
                  <Plus size={14} /> New Cover Letter
                </button>
              </div>

              {letters.length === 0 ? (
                <div className="bg-white/5 border border-white/10 rounded-2xl p-16 text-center text-gray-400 text-xs">
                  <Mail className="mx-auto text-gray-600 mb-3" size={36} />
                  No cover letters in database. Click "New Cover Letter" to query the AI assistant.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {letters.map(letter => (
                    <div
                      key={letter.id}
                      className="bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex justify-between items-start mb-2">
                          <h3 className="text-xs font-bold text-white">{letter.title}</h3>
                          <button
                            onClick={(e) => handleDeleteLetter(letter.id, e)}
                            className="text-gray-500 hover:text-rose-400 transition-all"
                          >
                            <Trash2 size={12} />
                          </button>
                        </div>
                        <div className="text-[10px] text-gray-500 mb-4">
                          Role: {letter.job_role} • Company: {letter.company_name}
                        </div>
                        <p className="text-gray-300 text-[11px] leading-relaxed line-clamp-4 whitespace-pre-wrap">
                          {letter.content}
                        </p>
                      </div>
                      <div className="mt-4 pt-4 border-t border-white/5 text-right">
                        <button
                          onClick={() => {
                            // Copy letter text to clipboard
                            navigator.clipboard.writeText(letter.content);
                            alert("Cover letter text copied to clipboard!");
                          }}
                          className="px-3 py-1.5 bg-white/10 hover:bg-white/15 rounded-lg text-[10px] font-semibold transition-all"
                        >
                          Copy Plain Text
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {/* TAB: TEMPLATES HUB */}
          {activeTab === "templates" && (
            <motion.div
              key="templates"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold tracking-tight">My Templates</h1>
                <p className="text-gray-400 text-xs mt-1">Browse our 24 professional database-driven visual styles</p>
              </div>

              {["ATS", "Corporate", "Technology", "Creative"].map(category => {
                const categoryTemplates = templates.filter(t => t.category === category);
                return (
                  <div key={category} className="space-y-3 pt-4">
                    <h3 className="text-xs font-bold uppercase tracking-widest text-[#7BC4BE] border-b border-[#7BC4BE]/20 pb-1.5">
                      {category} Templates ({categoryTemplates.length})
                    </h3>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                      {categoryTemplates.map(t => (
                        <div 
                          key={t.id} 
                          onClick={() => handleOpenPreview(t.id)}
                          className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-[#7BC4BE]/30 transition-all flex flex-col justify-between cursor-pointer group"
                        >
                          <div>
                            <h4 className="text-xs font-bold text-white mb-1 group-hover:text-[#7BC4BE] transition-colors">{t.name}</h4>
                            <div className="flex items-center gap-1.5 mt-2">
                              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: typeof t.color_scheme?.primary === "string" ? t.color_scheme.primary : "#888" }} />
                              <span className="text-[10px] text-gray-400 font-medium">Primary accent</span>
                            </div>
                            <div className="text-[10px] text-gray-500 mt-1 uppercase font-semibold">
                              Layout: {typeof t.layout_schema?.structure === "string" ? t.layout_schema.structure : "N/A"} • Font: {typeof t.layout_schema?.fontFamily === "string" ? t.layout_schema.fontFamily : "N/A"}
                            </div>
                          </div>
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenPreview(t.id);
                            }}
                            className="w-full mt-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg text-[10px] font-semibold border border-white/5 transition-all text-center"
                          >
                            Preview & Use →
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </motion.div>
          )}

          {/* TAB: PROFILE (Master User Profile) */}
          {activeTab === "profile" && (
            <motion.div
              key="profile"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              {/* Build My Resume Hero Card */}
              <div className="bg-gradient-to-r from-[#7BC4BE]/20 to-[#4A9E98]/20 border border-[#7BC4BE]/30 rounded-2xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center gap-2">
                      <Sparkles size={20} className="text-[#7BC4BE]" />
                      Build My Resume
                    </h2>
                    <p className="text-xs text-gray-300 mt-1">
                      Create a new resume using AI or manual builder. Your profile will auto-fill the basics.
                    </p>
                  </div>
                  <button
                    onClick={handleCreateResume}
                    className="px-6 py-3 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-lg shadow-[#7BC4BE]/20"
                  >
                    <Plus size={16} />
                    Start Building
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>

              <div>
                <h1 className="text-2xl font-bold tracking-tight">My Profile</h1>
                <p className="text-gray-400 text-xs mt-1">Master profile — auto-fills all resumes and cover letters</p>
              </div>

              <form onSubmit={handleSaveProfile} className="space-y-6">
                {/* Basic Info */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#7BC4BE] mb-4 flex items-center gap-1.5">
                    <User size={14} /> Basic Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Full Name</label>
                      <input type="text" value={user?.full_name || ""} disabled className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs opacity-60 cursor-not-allowed" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Email</label>
                      <input type="email" value={user?.email || ""} disabled className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs opacity-60 cursor-not-allowed" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Phone</label>
                      <div className="relative">
                        <Phone size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input type="text" value={profile.phone || ""} onChange={(e) => setProfile({ ...profile, phone: e.target.value })} placeholder="+1 (555) 019-2834" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Location</label>
                      <div className="relative">
                        <MapPin size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input type="text" value={profile.location || ""} onChange={(e) => setProfile({ ...profile, location: e.target.value })} placeholder="San Francisco, CA" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">LinkedIn</label>
                      <div className="relative">
                        <ExternalLink size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input type="text" value={profile.linkedin || ""} onChange={(e) => setProfile({ ...profile, linkedin: e.target.value })} placeholder="linkedin.com/in/username" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">GitHub</label>
                      <div className="relative">
                        <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input type="text" value={profile.github || ""} onChange={(e) => setProfile({ ...profile, github: e.target.value })} placeholder="github.com/username" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                      </div>
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Portfolio</label>
                      <div className="relative">
                        <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                        <input type="text" value={profile.website || ""} onChange={(e) => setProfile({ ...profile, website: e.target.value })} placeholder="yoursite.com" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Professional Info */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#7BC4BE] mb-4 flex items-center gap-1.5">
                    <Briefcase size={14} /> Professional Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Job Title</label>
                      <input type="text" value={profile.job_title || ""} onChange={(e) => setProfile({ ...profile, job_title: e.target.value })} placeholder="Senior Software Engineer" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Industry</label>
                      <input type="text" value={profile.industry || ""} onChange={(e) => setProfile({ ...profile, industry: e.target.value })} placeholder="Technology" className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Professional Summary</label>
                    <textarea rows={4} value={profile.summary || ""} onChange={(e) => setProfile({ ...profile, summary: e.target.value })} placeholder="Experienced software engineer with expertise in building scalable distributed systems..." className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]" />
                  </div>
                </div>

                {/* Links & Resume Sections Info */}
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#7BC4BE] mb-4 flex items-center gap-1.5">
                    <ExternalLink size={14} /> Resume Sections
                  </h3>
                  <p className="text-xs text-gray-400 mb-4">
                    Edit your full profile including Education, Experience, Projects, Skills, and more from the Profile Setup page.
                  </p>
                  <button
                    type="button"
                    onClick={() => navigate("/profile/setup")}
                    className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-xl text-xs font-semibold transition-all"
                  >
                    Edit Full Profile →
                  </button>
                </div>

                <button
                  type="submit"
                  className="px-6 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all"
                >
                  Save Profile
                </button>
              </form>
            </motion.div>
          )}

          {/* TAB: ACCOUNT */}
          {activeTab === "account" && (
            <motion.div
              key="account"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Account</h1>
                <p className="text-gray-400 text-xs mt-1">Manage your subscription and account settings</p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center bg-gradient-to-r from-white/5 to-[#7BC4BE]/5">
                <div>
                  <div className="text-[10px] text-[#7BC4BE] font-bold uppercase tracking-widest mb-1">Active Plan</div>
                  <h3 className="text-2xl font-bold text-white flex items-center gap-1.5">
                    {(sub.plan_type || "free").toUpperCase()} PLAN
                  </h3>
                  <p className="text-gray-400 text-xs mt-1">
                    Status: <span className="text-emerald-400 font-semibold">{(sub.status || "active").toUpperCase()}</span>
                  </p>
                </div>
                {sub.plan_type === "free" && (
                  <Link
                    to="/pricing"
                    className="px-5 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all shadow-md"
                  >
                    Upgrade Tier
                  </Link>
                )}
              </div>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300 mb-4 border-b border-white/5 pb-2">
                  Account Settings
                </h3>
                <div className="space-y-3">
                  <Link
                    to="/settings/auth"
                    className="flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-xl transition-all text-xs text-gray-300 hover:text-white"
                  >
                    <Lock size={14} className="text-[#7BC4BE]" />
                    Security & Password Settings
                  </Link>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300 mb-4 border-b border-white/5 pb-2">
                  Invoice History
                </h3>
                {payments.length === 0 ? (
                  <div className="text-center py-10 text-gray-500 text-xs">
                    No transactions recorded on this account.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {payments.map(pay => (
                      <div key={pay.id} className="flex justify-between items-center text-xs">
                        <div>
                          <div className="font-semibold text-white">Upgrade Subscription</div>
                          <div className="text-[10px] text-gray-500">{new Date(pay.payment_date).toLocaleDateString()}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-[#7BC4BE]">+${pay.amount} USD</div>
                          <div className="text-[9px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded inline-block uppercase font-bold">
                            {pay.status}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* TAB: JD BASED - Redirects to /jd-based */}
        </AnimatePresence>
      </main>

      {/* Cover Letter Creation Modal */}
      {showLetterModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-md bg-[#16302F] border border-white/10 rounded-2xl p-6 shadow-2xl">
            <div className="flex justify-between items-start mb-5">
              <div>
                <h3 className="text-base font-bold text-white">New Cover Letter</h3>
                <p className="text-[11px] text-gray-400 mt-0.5">The AI advisor will draft a targeted letter.</p>
              </div>
              <button
                onClick={() => setShowLetterModal(false)}
                className="text-gray-500 hover:text-white text-lg leading-none"
              >
                ✕
              </button>
            </div>

            <form onSubmit={submitCoverLetter} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Target Job Role</label>
                <input
                  type="text"
                  value={letterForm.jobRole}
                  onChange={(e) => setLetterForm({ ...letterForm, jobRole: e.target.value })}
                  placeholder="e.g. Senior Software Engineer"
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Company Name</label>
                <input
                  type="text"
                  value={letterForm.companyName}
                  onChange={(e) => setLetterForm({ ...letterForm, companyName: e.target.value })}
                  placeholder="e.g. Stripe"
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                />
              </div>
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Experience Context</label>
                <textarea
                  rows={4}
                  value={letterForm.experienceSummary}
                  onChange={(e) => setLetterForm({ ...letterForm, experienceSummary: e.target.value })}
                  placeholder="Briefly summarize your relevant experience and strengths..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                />
              </div>

              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowLetterModal(false)}
                  className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 rounded-xl text-xs font-semibold transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={letterSubmitting}
                  className="flex-1 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 disabled:opacity-60"
                >
                  {letterSubmitting ? (
                    <>
                      <RefreshCw size={12} className="animate-spin" /> Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles size={12} /> Generate Letter
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Template Preview Modal */}
      <TemplatePreviewModal
        isOpen={showPreviewModal}
        onClose={() => setShowPreviewModal(false)}
        templates={templates}
        initialTemplateId={previewTemplateId}
        user={user}
        profile={profile}
        onUseTemplate={handleUseTemplateFromPreview}
        onTemplateChange={(id) => sessionStorage.setItem("lastPreviewTemplate", id)}
      />
    </div>
  );
}
