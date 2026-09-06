import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  User,
  ArrowRight, ArrowLeft, RefreshCw, Sparkles, PenTool, Bot,
  Check,
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { saveGuestSession } from "../utils/guestSession";

const STEPS = [
  { id: "info", label: "Basic Info", icon: User },
  { id: "method", label: "Creation Method", icon: Sparkles },
];

const slideVariants = {
  enter: (d) => ({ x: d > 0 ? 80 : -80, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (d) => ({ x: d < 0 ? 80 : -80, opacity: 0 }),
};

export default function ResumeCreationFlow() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [isGuest, setIsGuest] = useState(!user);

  const [form, setForm] = useState({
    name: "", email: "", phone: "", location: "",
    linkedin: "", github: "", portfolio: "", website: "",
  });

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        
        // If no user (guest), try to load from unified session
        if (!user) {
          const { getGuestSession } = await import("../utils/guestSession");
          const session = getGuestSession();
          if (session.basicInfo && Object.keys(session.basicInfo).length > 0) {
            setForm(session.basicInfo);
          } else {
            // Fallback to old localStorage key for backward compatibility
            const savedForm = localStorage.getItem("guest_resume_form");
            if (savedForm) {
              setForm(JSON.parse(savedForm));
            }
          }
          setIsGuest(true);
          setLoading(false);
          return;
        }
        
        // Authenticated user - load from API
        setIsGuest(false);
        const me = await api.auth.getMe();
        const prof = await api.user.getProfile().catch(() => null);
        setForm({
          name: me.full_name || "",
          email: me.email || "",
          phone: prof?.phone || "",
          location: prof?.location || "",
          linkedin: prof?.linkedin || "",
          github: prof?.github || "",
          portfolio: prof?.portfolio || "",
          website: prof?.website || "",
        });
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [user]);

  const update = (field, value) => setForm(prev => ({ ...prev, [field]: value }));
  const goNext = () => { setDirection(1); setStep(step + 1); };
  const goBack = () => { setDirection(-1); setStep(step - 1); };

  const canProceed = () => {
    if (step === 0) return form.name.trim().length > 0 && form.email.trim().length > 0 && form.phone.trim().length > 0;
    return true;
  };

  const handleCreate = async (method) => {
    setCreating(true);
    try {
      // Save form data to localStorage for guests
      if (isGuest) {
        saveGuestSession({
          basicInfo: form,
        });
      } else {
        // Save profile data for authenticated users
        await api.user.updateProfile({
          phone: form.phone || null,
          location: form.location || null,
          linkedin: form.linkedin || null,
          github: form.github || null,
          portfolio: form.portfolio || null,
          website: form.website || null,
        }).catch(() => {});
      }

      if (method === "ai") {
        // Navigate to AI chat with pre-filled context
        navigate("/resume/create", { state: { prefill: form, isGuest } });
      } else {
        // For manual builder
        if (isGuest) {
          // Guests: Store initial resume data in unified session and go to guest editor
          const guestResumeData = {
            personalInfo: {
              fullName: form.name,
              email: form.email,
              phone: form.phone,
              location: form.location,
              website: form.website || form.portfolio,
              linkedin: form.linkedin,
            },
            summary: "",
            experience: [],
            education: [],
            skills: [],
            projects: [],
            certifications: [],
            achievements: [],
          };
          saveGuestSession({
            basicInfo: form,
            generatedResume: guestResumeData,
            selectedTemplate: "harvard",
          });
          navigate("/resume/guest-edit");
        } else {
          // Authenticated users: Create resume in backend
          const res = await api.resumes.create("My Professional Resume", "harvard");
          // Auto-fill from form data
          const sections = [
            {
              section_type: "personalInfo",
              content: {
                fullName: form.name,
                email: form.email,
                phone: form.phone,
                location: form.location,
                website: form.website || form.portfolio,
                linkedin: form.linkedin,
              },
              position: 0,
            },
            { section_type: "summary", content: "", position: 1 },
            { section_type: "experience", content: [], position: 2 },
            { section_type: "education", content: [], position: 3 },
            { section_type: "skills", content: [], position: 4 },
            { section_type: "projects", content: [], position: 5 },
            { section_type: "certifications", content: [], position: 6 },
            { section_type: "achievements", content: [], position: 7 },
          ];
          await api.resumes.saveSections(res.id, sections);
          navigate(`/resume/edit/${res.id}`);
        }
      }
    } catch (err) {
      alert("Failed to create resume: " + err.message);
    } finally {
      setCreating(false);
    }
  };

  const inputCls = "w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE] transition-colors";
  const labelCls = "block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5";

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col items-center justify-center gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={40} />
        <p className="text-gray-400 text-sm">Loading your information...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#7BC4BE]/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FAD07A]/5 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-lg bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

        <div className="text-center mb-6">
          <span className="text-xl font-bold tracking-tight text-white flex items-center justify-center gap-1.5 mb-2">
            <span className="text-[#7BC4BE]">&#10022;</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
          </span>
          <h2 className="text-lg font-medium text-white/90">Create New Resume</h2>
          <p className="text-xs text-gray-400 mt-1">Let's build something great together</p>
        </div>

        {/* Step Indicator */}
        <div className="flex justify-center gap-1.5 mb-8">
          {STEPS.map((s, i) => {
            const Icon = s.icon;
            const done = i < step;
            const cur = i === step;
            return (
              <button key={s.id} onClick={() => { if (i < step) { setDirection(-1); setStep(i); } }}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-semibold transition-all ${
                  cur ? "bg-[#7BC4BE] text-[#1A2B2A]" : done ? "bg-[#7BC4BE]/20 text-[#7BC4BE] cursor-pointer" : "bg-white/5 text-gray-500"
                }`}>
                {done ? <Check size={12} /> : <Icon size={12} />}
                {s.label}
              </button>
            );
          })}
        </div>

        <div className="min-h-[340px]">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div key={step} custom={direction} variants={slideVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.25, ease: "easeInOut" }}>
              {step === 0 ? (
                <motion.div key="info" className="space-y-4">
                  <div className="text-center mb-5">
                    <div className="w-14 h-14 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                      <User className="text-[#7BC4BE]" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-white">Basic Information</h3>
                    <p className="text-xs text-gray-400 mt-1">Review your details before creating</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className={labelCls}>Name *</label>
                      <input type="text" value={form.name} onChange={e => update("name", e.target.value)} placeholder="John Doe" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>Email *</label>
                      <input type="email" value={form.email} onChange={e => update("email", e.target.value)} placeholder="john@example.com" className={inputCls} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className={labelCls}>Phone *</label>
                      <input type="text" value={form.phone} onChange={e => update("phone", e.target.value)} placeholder="+1 (555) 012-3456" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>Location</label>
                      <input type="text" value={form.location} onChange={e => update("location", e.target.value)} placeholder="San Francisco, CA" className={inputCls} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className={labelCls}>LinkedIn</label>
                      <input type="text" value={form.linkedin} onChange={e => update("linkedin", e.target.value)} placeholder="linkedin.com/in/username" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>GitHub</label>
                      <input type="text" value={form.github} onChange={e => update("github", e.target.value)} placeholder="github.com/username" className={inputCls} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className={labelCls}>Portfolio</label>
                      <input type="text" value={form.portfolio} onChange={e => update("portfolio", e.target.value)} placeholder="portfolio.example.com" className={inputCls} />
                    </div>
                    <div>
                      <label className={labelCls}>Website</label>
                      <input type="text" value={form.website} onChange={e => update("website", e.target.value)} placeholder="yoursite.com" className={inputCls} />
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div key="method" className="space-y-4">
                  <div className="text-center mb-5">
                    <div className="w-14 h-14 bg-[#FAD07A]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                      <Sparkles className="text-[#FAD07A]" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-white">Choose Creation Method</h3>
                    <p className="text-xs text-gray-400 mt-1">How would you like to build your resume?</p>
                  </div>

                  <button
                    onClick={() => handleCreate("ai")}
                    disabled={creating}
                    className="w-full bg-white/5 hover:bg-[#7BC4BE]/10 border border-white/10 hover:border-[#7BC4BE]/30 rounded-2xl p-5 text-left transition-all group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-[#7BC4BE]/10 rounded-xl flex items-center justify-center shrink-0 group-hover:bg-[#7BC4BE]/20 transition-all">
                        <Bot className="text-[#7BC4BE]" size={24} />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-bold text-white group-hover:text-[#7BC4BE] transition-colors">AI Prompt Based</h4>
                        <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">
                          Chat with AI to build your resume. Describe your experience and let AI craft a professional resume for you.
                        </p>
                        <div className="flex items-center gap-1.5 mt-2 text-[10px] text-[#7BC4BE] font-semibold">
                          <span>Start AI Chat</span>
                          <ArrowRight size={10} />
                        </div>
                      </div>
                    </div>
                  </button>

                  <button
                    onClick={() => handleCreate("manual")}
                    disabled={creating}
                    className="w-full bg-white/5 hover:bg-[#FAD07A]/10 border border-white/10 hover:border-[#FAD07A]/30 rounded-2xl p-5 text-left transition-all group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 bg-[#FAD07A]/10 rounded-xl flex items-center justify-center shrink-0 group-hover:bg-[#FAD07A]/20 transition-all">
                        <PenTool className="text-[#FAD07A]" size={24} />
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-bold text-white group-hover:text-[#FAD07A] transition-colors">Classic Manual Builder</h4>
                        <p className="text-[11px] text-gray-400 mt-1 leading-relaxed">
                          Fill in each section yourself with full control. Edit, preview, and download your resume instantly.
                        </p>
                        <div className="flex items-center gap-1.5 mt-2 text-[10px] text-[#FAD07A] font-semibold">
                          <span>Open Manual Builder</span>
                          <ArrowRight size={10} />
                        </div>
                      </div>
                    </div>
                  </button>

                  {creating && (
                    <div className="flex items-center justify-center gap-2 py-3 text-xs text-gray-400">
                      <RefreshCw size={14} className="animate-spin" />
                      Creating your resume...
                    </div>
                  )}
                </motion.div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="flex justify-between items-center mt-6 pt-5 border-t border-white/10">
          {step > 0 ? (
            <button onClick={goBack} className="flex items-center gap-1.5 px-4 py-2 text-gray-400 hover:text-white text-xs font-semibold transition-all">
              <ArrowLeft size={14} /> Back
            </button>
          ) : (
            <button onClick={() => navigate(isGuest ? "/" : "/dashboard")} className="flex items-center gap-1.5 px-4 py-2 text-gray-400 hover:text-white text-xs font-semibold transition-all">
              <ArrowLeft size={14} /> {isGuest ? "Home" : "Dashboard"}
            </button>
          )}
          {step < STEPS.length - 1 && (
            <button onClick={goNext} disabled={!canProceed()} className="flex items-center gap-1.5 px-6 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed">
              Next <ArrowRight size={14} />
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}
