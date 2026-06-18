import React, { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Home, FileText, Mail, Layout, MessageSquare, User, CreditCard, LogOut, 
  Plus, Sparkles, Trash2, Edit3, Download, RefreshCw, Award, Send, 
  CheckCircle, ShieldAlert, ArrowUpRight, Check 
} from "lucide-react";
import { api } from "../services/api";
import ResumePreview from "../components/ResumePreview";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("home"); // home, resumes, letters, templates, ai, profile, billing
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState({});
  const [resumes, setResumes] = useState([]);
  const [letters, setLetters] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [sub, setSub] = useState({ plan_type: "free", status: "active" });
  const [payments, setPayments] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // AI assistant states
  const [aiMessage, setAiMessage] = useState("");
  const [aiChat, setAiChat] = useState([
    { sender: "ai", text: "Hello! I am your Harvard-trained career advisor. Ask me to write, shorten, or review any resume bullet points or cover letters." }
  ]);
  const [aiLoading, setAiLoading] = useState(false);

  const navigate = useNavigate();

  // Load user details & database records
  const loadData = async () => {
    try {
      setLoading(true);
      const me = await api.getMe();
      setUser(me);
      
      const prof = await api.getProfile();
      setProfile(prof);
      
      const resList = await api.listResumes();
      setResumes(resList);
      
      const lettersList = await api.listCoverLetters();
      setLetters(lettersList);
      
      const tempsList = await api.listTemplates();
      setTemplates(tempsList);
      
      const subscription = await api.getSubscription();
      setSub(subscription);
      
      const billing = await api.getBillingHistory();
      setPayments(billing);

      try {
        const acts = await api.getActivityLog();
        setActivity(acts);
      } catch (actErr) {
        console.error("Failed to load activity log:", actErr);
      }
    } catch (err) {
      console.error("Failed to load dashboard data, redirecting to login:", err);
      api.logout();
      navigate("/login");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!api.isAuthenticated()) {
      navigate("/login");
      return;
    }
    loadData();
  }, []);

  const handleLogout = () => {
    api.logout();
    navigate("/");
  };

  // Resume operations
  const handleCreateResume = async () => {
    try {
      const title = prompt("Enter resume title:", "My Professional Resume");
      if (!title) return;
      const res = await api.createResume(title, "harvard");
      navigate(`/resume/edit/${res.id}`);
    } catch (err) {
      alert("Failed to create resume: " + err.message);
    }
  };

  const handleGenerateResumeAI = () => {
    navigate("/resume/create"); // Navigate to the AI prompt workflow page
  };

  const handleDeleteResume = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    try {
      await api.deleteResume(id);
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
    setLetterForm({ jobRole: "", companyName: "", experienceSummary: "" });
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
      const letter = await api.generateCoverLetter(
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
      await api.deleteCoverLetter(id);
      setLetters(letters.filter(l => l.id !== id));
    } catch (err) {
      alert("Delete failed: " + err.message);
    }
  };

  // Selections
  const handleUseTemplate = async (templateId) => {
    try {
      const title = prompt("Enter resume title:");
      if (!title) return;
      const res = await api.createResume(title, templateId);
      navigate(`/resume/edit/${res.id}`);
    } catch (err) {
      alert("Failed: " + err.message);
    }
  };

  // Save profile changes
  const handleSaveProfile = async (e) => {
    e.preventDefault();
    try {
      const updated = await api.updateProfile(profile);
      setProfile(updated);
      alert("Profile updated successfully!");
    } catch (err) {
      alert("Failed to save profile: " + err.message);
    }
  };

  // Send message to AI assistant
  const handleSendAiMessage = async (e) => {
    e.preventDefault();
    if (!aiMessage.trim()) return;
    
    const userMsg = { sender: "user", text: aiMessage };
    setAiChat(prev => [...prev, userMsg]);
    setAiMessage("");
    setAiLoading(true);

    try {
      const res = await api.improveText(aiMessage, "improve", "summary");
      setAiChat(prev => [...prev, { sender: "ai", text: res.improved_text }]);
    } catch (err) {
      setAiChat(prev => [...prev, { sender: "ai", text: "I apologize, but I encountered an issue optimizing your prompt. Please check your network connection." }]);
    } finally {
      setAiLoading(false);
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
      
      const blob = await api.exportPDF(resumeHtml, `${resume.title.replace(/\s+/g, "_")}.pdf`);
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
    { id: "home", label: "Home Workspace", icon: Home },
    { id: "resumes", label: "My Resumes", icon: FileText },
    { id: "letters", label: "Cover Letters", icon: Mail },
    { id: "templates", label: "Templates Hub", icon: Layout },
    { id: "ai", label: "AI Advisor Chat", icon: MessageSquare },
    { id: "profile", label: "Advisor Profile", icon: User },
    { id: "billing", label: "Billing & Plans", icon: CreditCard },
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
              {sub.plan_type.toUpperCase()} PLAN
            </div>
          </div>
          <nav className="p-4 space-y-1">
            {sidebarItems.map(item => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
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
          {resumes.map(r => (
            <div key={r.id} id={`res-preview-hidden-${r.id}`}>
              <ResumePreview 
                data={{
                  personalInfo: {
                    fullName: r.sections.find(s => s.section_type === "personalInfo")?.content?.fullName || user?.full_name || "Applicant Name",
                    jobTitle: r.sections.find(s => s.section_type === "personalInfo")?.content?.jobTitle || profile.job_title || "Professional",
                    email: r.sections.find(s => s.section_type === "personalInfo")?.content?.email || user?.email || "",
                    phone: r.sections.find(s => s.section_type === "personalInfo")?.content?.phone || profile.phone || "",
                    location: r.sections.find(s => s.section_type === "personalInfo")?.content?.location || profile.location || "",
                    website: r.sections.find(s => s.section_type === "personalInfo")?.content?.website || profile.website || "",
                    linkedin: r.sections.find(s => s.section_type === "personalInfo")?.content?.linkedin || profile.linkedin || ""
                  },
                  summary: r.sections.find(s => s.section_type === "summary")?.content || profile.summary || "",
                  experience: r.sections.find(s => s.section_type === "experience")?.content || [],
                  education: r.sections.find(s => s.section_type === "education")?.content || [],
                  skills: r.sections.find(s => s.section_type === "skills")?.content || [],
                  projects: r.sections.find(s => s.section_type === "projects")?.content || [],
                  certifications: r.sections.find(s => s.section_type === "certifications")?.content || [],
                  achievements: r.sections.find(s => s.section_type === "achievements")?.content || []
                }} 
                template={r.template_id || "harvard"} 
              />
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* TAB: HOME WORKSPACE */}
          {activeTab === "home" && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-8"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-2xl font-bold tracking-tight">Welcome, {user?.full_name || "Career Professional"}</h1>
                  <p className="text-gray-400 text-xs mt-1">Design, analyze, and optimize your executive assets.</p>
                </div>
                <div className="flex gap-3">
                  <button 
                    onClick={handleCreateResume}
                    className="px-4 py-2.5 bg-white/10 hover:bg-white/15 text-white border border-white/10 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5"
                  >
                    <Plus size={14} /> New Manual Resume
                  </button>
                  <button
                    onClick={handleGenerateResumeAI}
                    className="px-4 py-2.5 bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-[#7BC4BE]/10"
                  >
                    <Sparkles size={14} /> Create with AI Advisor
                  </button>
                </div>
              </div>

              {/* Quick Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                  <div className="text-gray-400 text-[10px] font-bold uppercase tracking-wider mb-2">Total Resumes</div>
                  <div className="text-3xl font-bold mb-1">{resumes.length}</div>
                  <p className="text-gray-500 text-[10px] leading-relaxed">Saved drafts in your database</p>
                  <FileText className="absolute right-4 bottom-4 text-white/5" size={48} />
                </div>
                
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6 relative overflow-hidden">
                  <div className="text-gray-400 text-[10px] font-bold uppercase tracking-wider mb-2">Cover Letters</div>
                  <div className="text-3xl font-bold mb-1">{letters.length}</div>
                  <p className="text-gray-500 text-[10px]">Generated target documents</p>
                  <Mail className="absolute right-4 bottom-4 text-white/5" size={48} />
                </div>

                <div className="bg-white/5 border border-[#7BC4BE]/20 rounded-2xl p-6 relative overflow-hidden bg-gradient-to-br from-white/5 to-[#7BC4BE]/5">
                  <div className="text-[#7BC4BE] text-[10px] font-bold uppercase tracking-wider mb-2">Plan Tier</div>
                  <div className="text-3xl font-bold mb-1 flex items-baseline gap-1">
                    {sub.plan_type.toUpperCase()}
                  </div>
                  <Link to="/pricing" className="text-xs text-[#7BC4BE] hover:underline flex items-center gap-1 mt-1 font-semibold">
                    Manage Subscriptions <ArrowUpRight size={12} />
                  </Link>
                </div>
              </div>

              {/* Recent Resumes List */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 mb-4">Recent Resumes</h3>
                {resumes.length === 0 ? (
                  <div className="text-center py-12 text-gray-500 text-xs">
                    No resumes created yet. Click "Create with AI Advisor" to launch.
                  </div>
                ) : (
                  <div className="divide-y divide-white/5">
                    {resumes.slice(0, 3).map(res => (
                      <div key={res.id} className="flex justify-between items-center py-3.5 hover:bg-white/5 transition-all rounded-lg px-2">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-[#7BC4BE]/15 flex items-center justify-center text-[#7BC4BE]">
                            <FileText size={18} />
                          </div>
                          <div>
                            <div className="text-xs font-bold text-white">{res.title}</div>
                            <div className="text-[10px] text-gray-500">Template: {res.template_id || "Harvard"} • Updated: {new Date(res.updated_at).toLocaleDateString()}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <button
                            onClick={() => navigate(`/resume/edit/${res.id}`)}
                            className="px-3 py-1.5 bg-white/10 hover:bg-white/15 rounded-lg text-[10px] font-semibold transition-all"
                          >
                            Open Editor
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recent Activity */}
              <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                <h3 className="text-sm font-bold uppercase tracking-wider text-gray-300 mb-4">Recent Activity</h3>
                {activity.length === 0 ? (
                  <div className="text-center py-8 text-gray-500 text-xs">
                    No recent activity yet. Your actions will appear here.
                  </div>
                ) : (
                  <div className="divide-y divide-white/5">
                    {activity.slice(0, 6).map(act => (
                      <div key={act.id} className="flex items-center gap-3 py-3 px-2">
                        <div className="w-8 h-8 rounded-lg bg-[#7BC4BE]/15 flex items-center justify-center text-[#7BC4BE] shrink-0">
                          <Check size={14} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-semibold text-white truncate">{act.description || act.activity_type}</div>
                          <div className="text-[10px] text-gray-500">{new Date(act.created_at).toLocaleString()}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

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
                  <h1 className="text-2xl font-bold tracking-tight">My Resumes</h1>
                  <p className="text-gray-400 text-xs mt-1">Manage and edit your saved drafts</p>
                </div>
                <button
                  onClick={handleCreateResume}
                  className="px-4 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                >
                  <Plus size={14} /> New Resume
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
                  <h1 className="text-2xl font-bold tracking-tight">Cover Letters</h1>
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
                <h1 className="text-2xl font-bold tracking-tight">Templates Hub</h1>
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
                          className="bg-white/5 border border-white/10 rounded-xl p-4 hover:border-[#7BC4BE]/30 transition-all flex flex-col justify-between"
                        >
                          <div>
                            <h4 className="text-xs font-bold text-white mb-1">{t.name}</h4>
                            <div className="flex items-center gap-1.5 mt-2">
                              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: t.color_scheme.primary }} />
                              <span className="text-[10px] text-gray-400 font-medium">Primary accent</span>
                            </div>
                            <div className="text-[10px] text-gray-500 mt-1 uppercase font-semibold">
                              Layout: {t.layout_schema.structure} • Font: {t.layout_schema.fontFamily}
                            </div>
                          </div>
                          
                          <button
                            onClick={() => handleUseTemplate(t.id)}
                            className="w-full mt-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-lg text-[10px] font-semibold border border-white/5 transition-all text-center"
                          >
                            Use Style →
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </motion.div>
          )}

          {/* TAB: AI ASSISTANT */}
          {activeTab === "ai" && (
            <motion.div
              key="ai"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4 h-[calc(100vh-100px)] flex flex-col justify-between"
            >
              <div>
                <h1 className="text-2xl font-bold tracking-tight">AI Advisor</h1>
                <p className="text-gray-400 text-xs mt-1">Review resume content against Harvard resume principles</p>
              </div>

              {/* Chat Window */}
              <div className="flex-1 bg-white/5 border border-white/10 rounded-2xl p-6 overflow-y-auto space-y-4 flex flex-col justify-end">
                <div className="space-y-4 overflow-y-auto max-h-[400px]">
                  {aiChat.map((msg, index) => (
                    <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                      <div className={`max-w-[70%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                        msg.sender === "user" 
                          ? "bg-[#7BC4BE] text-[#1A2B2A] rounded-tr-none" 
                          : "bg-white/10 text-white rounded-tl-none border border-white/5"
                      }`}>
                        {msg.text}
                      </div>
                    </div>
                  ))}
                  {aiLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white/10 text-white rounded-2xl rounded-tl-none p-3.5 border border-white/5 text-xs flex items-center gap-2">
                        <RefreshCw className="animate-spin text-[#7BC4BE]" size={12} /> Improving writing copy...
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Prompt Input */}
              <form onSubmit={handleSendAiMessage} className="flex gap-2">
                <input
                  type="text"
                  value={aiMessage}
                  onChange={(e) => setAiMessage(e.target.value)}
                  placeholder="e.g. Worked as an intern at Oracle. Managed SQL database. Make it professional."
                  className="flex-1 bg-white/5 border border-white/10 rounded-xl py-3 px-4 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE]"
                />
                <button
                  type="submit"
                  className="px-6 py-3 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-md shadow-[#7BC4BE]/15"
                >
                  Ask <Send size={12} />
                </button>
              </form>
            </motion.div>
          )}

          {/* TAB: PROFILE */}
          {activeTab === "profile" && (
            <motion.div
              key="profile"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Advisor Profile</h1>
                <p className="text-gray-400 text-xs mt-1">Manage global default values for your resumes</p>
              </div>

              <form onSubmit={handleSaveProfile} className="bg-white/5 border border-white/10 rounded-2xl p-8 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Target Job Title</label>
                    <input
                      type="text"
                      value={profile.job_title || ""}
                      onChange={(e) => setProfile({ ...profile, job_title: e.target.value })}
                      placeholder="e.g. Senior Software Engineer"
                      className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Contact Phone</label>
                    <input
                      type="text"
                      value={profile.phone || ""}
                      onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                      placeholder="+1 (555) 019-2834"
                      className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Location</label>
                    <input
                      type="text"
                      value={profile.location || ""}
                      onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                      placeholder="San Francisco, CA"
                      className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Personal Website</label>
                    <input
                      type="text"
                      value={profile.website || ""}
                      onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                      placeholder="portfolio.dev"
                      className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">LinkedIn Handle</label>
                  <input
                    type="text"
                    value={profile.linkedin || ""}
                    onChange={(e) => setProfile({ ...profile, linkedin: e.target.value })}
                    placeholder="linkedin.com/in/username"
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Professional Summary</label>
                  <textarea
                    rows={4}
                    value={profile.summary || ""}
                    onChange={(e) => setProfile({ ...profile, summary: e.target.value })}
                    placeholder="Brief objective summary statement..."
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
                  />
                </div>

                <button
                  type="submit"
                  className="px-6 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all"
                >
                  Save Workspace Defaults
                </button>
              </form>
            </motion.div>
          )}

          {/* TAB: BILLING */}
          {activeTab === "billing" && (
            <motion.div
              key="billing"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-6"
            >
              <div>
                <h1 className="text-2xl font-bold tracking-tight">Billing & Plans</h1>
                <p className="text-gray-400 text-xs mt-1">Review active plan, subscription state, and historical invoices</p>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center bg-gradient-to-r from-white/5 to-[#7BC4BE]/5">
                <div>
                  <div className="text-[10px] text-[#7BC4BE] font-bold uppercase tracking-widest mb-1">Active Plan</div>
                  <h3 className="text-2xl font-bold text-white flex items-center gap-1.5">
                    {sub.plan_type.toUpperCase()} PLAN
                  </h3>
                  <p className="text-gray-400 text-xs mt-1">
                    Status: <span className="text-emerald-400 font-semibold">{sub.status.toUpperCase()}</span>
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
    </div>
  );
}
