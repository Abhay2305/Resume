import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  User, ExternalLink, Briefcase,
  GraduationCap, ArrowRight, ArrowLeft,
  Save, RefreshCw, Check, Sparkles, Plus, Trash2, Award,
  BookOpen, Code, Languages, Heart, Star, Users, Activity,
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

const STEPS = [
  { id: "basics", label: "Basic Info", icon: User },
  { id: "links", label: "Links", icon: ExternalLink },
  { id: "education", label: "Education", icon: GraduationCap },
  { id: "experience", label: "Experience", icon: Briefcase },
  { id: "projects", label: "Projects", icon: Code },
  { id: "skills", label: "Skills", icon: Star },
  { id: "extras", label: "Extras", icon: Award },
  { id: "complete", label: "Done", icon: Check },
];

const EDUCATION_LEVELS = [
  "High School", "Associate's Degree", "Bachelor's Degree",
  "Master's Degree", "Doctorate (PhD)", "Professional Degree (MD, JD, etc.)",
  "Self-Taught", "Other",
];

const PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Native", "Fluent"];

const slideVariants = {
  enter: (d) => ({ x: d > 0 ? 80 : -80, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (d) => ({ x: d < 0 ? 80 : -80, opacity: 0 }),
};

const emptyEducation = () => ({ degree: "", university: "", field: "", cgpa: "", graduation_year: "" });
const emptyExperience = () => ({ company: "", role: "", duration: "", description: "", bullets: [""] });
const emptyProject = () => ({ name: "", technologies: "", description: "", links: "" });
const emptyCert = () => ({ name: "", issuer: "", date: "" });
const emptyLanguage = () => ({ language: "", proficiency: "Intermediate" });
const emptyPublication = () => ({ title: "", publisher: "", date: "", url: "" });
const emptyVolunteer = () => ({ organization: "", role: "", duration: "", description: "" });
const emptyExtracurricular = () => ({ activity: "", description: "", duration: "" });

function parseJson(value) {
  if (!value) return [];
  try { const p = JSON.parse(value); return Array.isArray(p) ? p : []; } catch { return []; }
}

export default function ProfileSetup() {
  const navigate = useNavigate();
  const { user, refreshUser } = useAuth();
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState({
    full_name: "", email: "", phone: "", location: "", date_of_birth: "",
    job_title: "", professional_headline: "", company: "", industry: "",
    years_of_experience: "", education_level: "", summary: "",
    linkedin: "", github: "", website: "", portfolio: "",
  });

  const [education, setEducation] = useState([]);
  const [experience, setExperience] = useState([]);
  const [projects, setProjects] = useState([]);
  const [skills, setSkills] = useState([""]);
  const [certifications, setCertifications] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [awards, setAwards] = useState([]);
  const [publications, setPublications] = useState([]);
  const [volunteer, setVolunteer] = useState([]);
  const [extracurricular, setExtracurricular] = useState([]);

  useEffect(() => {
    (async () => {
      if (user) {
        setProfile(prev => ({ ...prev, full_name: user.full_name || "", email: user.email || "" }));
      }
      try {
        setLoading(true);
        const prof = await api.user.getProfile();
        if (prof) {
          setProfile(prev => ({
            ...prev,
            phone: prof.phone || "", location: prof.location || "",
            job_title: prof.job_title || "", professional_headline: prof.professional_headline || "",
            company: prof.company || "", industry: prof.industry || "",
            years_of_experience: prof.years_of_experience || "",
            education_level: prof.education_level || "", summary: prof.summary || "",
            linkedin: prof.linkedin || "", github: prof.github || "",
            website: prof.website || "", portfolio: prof.portfolio || "",
            date_of_birth: prof.date_of_birth || "",
          }));
          setEducation(parseJson(prof.education_json));
          setExperience(parseJson(prof.experience_json));
          setProjects(parseJson(prof.projects_json));
          const sk = parseJson(prof.skills_json);
          setSkills(sk.length > 0 ? sk : [""]);
          setCertifications(parseJson(prof.certifications_json));
          setAchievements(parseJson(prof.achievements_json));
          setLanguages(parseJson(prof.languages_json));
          setAwards(parseJson(prof.awards_json));
          setPublications(parseJson(prof.publications_json));
          setVolunteer(parseJson(prof.volunteer_json));
          setExtracurricular(parseJson(prof.extracurricular_json));
        }
      } catch (err) {
        console.error("Failed to load profile:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, [user]);

  const update = (field, value) => setProfile(prev => ({ ...prev, [field]: value }));
  const goNext = () => { if (step < STEPS.length - 1) { setDirection(1); setStep(step + 1); } };
  const goBack = () => { if (step > 0) { setDirection(-1); setStep(step - 1); } };

  const canProceed = () => {
    if (step === 0) return (profile.full_name || "").trim().length > 0 && (profile.phone || "").trim().length > 0;
    return true;
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.user.updateProfile({
        phone: profile.phone || null,
        location: profile.location || null,
        date_of_birth: profile.date_of_birth || null,
        job_title: profile.job_title || null,
        professional_headline: profile.professional_headline || null,
        company: profile.company || null,
        industry: profile.industry || null,
        years_of_experience: profile.years_of_experience ? parseInt(profile.years_of_experience) : null,
        education_level: profile.education_level || null,
        summary: profile.summary || null,
        linkedin: profile.linkedin || null,
        github: profile.github || null,
        website: profile.website || null,
        portfolio: profile.portfolio || null,
        education_json: JSON.stringify(education.filter(e => e.degree || e.university)),
        experience_json: JSON.stringify(experience.filter(e => e.company || e.role)),
        projects_json: JSON.stringify(projects.filter(p => p.name)),
        skills_json: JSON.stringify(skills.filter(s => s.trim())),
        certifications_json: JSON.stringify(certifications.filter(c => c.name)),
        achievements_json: JSON.stringify(achievements.filter(a => a.title)),
        languages_json: JSON.stringify(languages.filter(l => l.language)),
        awards_json: JSON.stringify(awards.filter(a => a.name)),
        publications_json: JSON.stringify(publications.filter(p => p.title)),
        volunteer_json: JSON.stringify(volunteer.filter(v => v.organization)),
        extracurricular_json: JSON.stringify(extracurricular.filter(e => e.activity)),
        profile_completed: true,
      });
      await refreshUser();
      localStorage.setItem("profile_setup_complete", "true");
      navigate("/dashboard");
    } catch (err) {
      alert("Failed to save profile: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  // Helper: add/remove items in array fields
  const addToList = (setter, emptyFn) => setter(prev => [...prev, emptyFn()]);
  const removeFromList = (setter, idx) => setter(prev => prev.filter((_, i) => i !== idx));
  const updateListItem = (setter, idx, field, value) => {
    setter(prev => prev.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  };

  const inputCls = "w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE] transition-colors";
  const labelCls = "block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5";

  const renderStep = () => {
    switch (step) {
      case 0: // Basic Info
        return (
          <motion.div key="basics" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <User className="text-[#7BC4BE]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Basic Information</h3>
              <p className="text-xs text-gray-400 mt-1">Mandatory fields for your profile</p>
            </div>
            <div>
              <label className={labelCls}>Full Name *</label>
              <input type="text" value={profile.full_name} onChange={e => update("full_name", e.target.value)} placeholder="John Doe" className={inputCls} />
            </div>
            <div>
              <label className={labelCls}>Email</label>
              <input type="email" value={profile.email} disabled className={`${inputCls} opacity-60 cursor-not-allowed`} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Phone *</label>
                <input type="text" value={profile.phone} onChange={e => update("phone", e.target.value)} placeholder="+1 (555) 012-3456" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Location</label>
                <input type="text" value={profile.location} onChange={e => update("location", e.target.value)} placeholder="San Francisco, CA" className={inputCls} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Job Title</label>
                <input type="text" value={profile.job_title} onChange={e => update("job_title", e.target.value)} placeholder="Senior Software Engineer" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Professional Headline</label>
                <input type="text" value={profile.professional_headline} onChange={e => update("professional_headline", e.target.value)} placeholder="Full Stack Developer | React & Node.js" className={inputCls} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Company</label>
                <input type="text" value={profile.company} onChange={e => update("company", e.target.value)} placeholder="Google" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Industry</label>
                <input type="text" value={profile.industry} onChange={e => update("industry", e.target.value)} placeholder="Technology" className={inputCls} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Years of Experience</label>
                <input type="number" value={profile.years_of_experience} onChange={e => update("years_of_experience", e.target.value)} placeholder="5" min="0" max="50" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Education Level</label>
                <select value={profile.education_level} onChange={e => update("education_level", e.target.value)} className={inputCls}>
                  <option value="" className="bg-[#1A2B2A]">Select level</option>
                  {EDUCATION_LEVELS.map(l => <option key={l} value={l} className="bg-[#1A2B2A]">{l}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className={labelCls}>Professional Summary</label>
              <textarea rows={3} value={profile.summary} onChange={e => update("summary", e.target.value)} placeholder="Experienced software engineer with expertise in..." className={`${inputCls} resize-none`} />
            </div>
          </motion.div>
        );

      case 1: // Links
        return (
          <motion.div key="links" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#FAD07A]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <ExternalLink className="text-[#FAD07A]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Professional Links</h3>
              <p className="text-xs text-gray-400 mt-1">All optional — add what you have</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>LinkedIn</label>
                <input type="text" value={profile.linkedin} onChange={e => update("linkedin", e.target.value)} placeholder="linkedin.com/in/username" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>GitHub</label>
                <input type="text" value={profile.github} onChange={e => update("github", e.target.value)} placeholder="github.com/username" className={inputCls} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className={labelCls}>Portfolio</label>
                <input type="text" value={profile.portfolio} onChange={e => update("portfolio", e.target.value)} placeholder="portfolio.example.com" className={inputCls} />
              </div>
              <div>
                <label className={labelCls}>Personal Website</label>
                <input type="text" value={profile.website} onChange={e => update("website", e.target.value)} placeholder="yoursite.com" className={inputCls} />
              </div>
            </div>
          </motion.div>
        );

      case 2: // Education
        return (
          <motion.div key="education" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <GraduationCap className="text-[#7BC4BE]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Education</h3>
              <p className="text-xs text-gray-400 mt-1">Add your educational background</p>
            </div>
            {education.map((edu, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2 relative">
                <button onClick={() => removeFromList(setEducation, i)} className="absolute top-2 right-2 text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                <div className="grid grid-cols-2 gap-2">
                  <input value={edu.degree} onChange={e => updateListItem(setEducation, i, "degree", e.target.value)} placeholder="Degree (e.g. B.S. Computer Science)" className={inputCls} />
                  <input value={edu.university} onChange={e => updateListItem(setEducation, i, "university", e.target.value)} placeholder="University" className={inputCls} />
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <input value={edu.field} onChange={e => updateListItem(setEducation, i, "field", e.target.value)} placeholder="Field of Study" className={inputCls} />
                  <input value={edu.cgpa} onChange={e => updateListItem(setEducation, i, "cgpa", e.target.value)} placeholder="CGPA / GPA" className={inputCls} />
                  <input value={edu.graduation_year} onChange={e => updateListItem(setEducation, i, "graduation_year", e.target.value)} placeholder="Graduation Year" className={inputCls} />
                </div>
              </div>
            ))}
            <button onClick={() => addToList(setEducation, emptyEducation)} className="w-full py-2 border border-dashed border-white/20 rounded-xl text-xs text-gray-400 hover:text-[#7BC4BE] hover:border-[#7BC4BE]/30 transition-all flex items-center justify-center gap-1">
              <Plus size={12} /> Add Education
            </button>
          </motion.div>
        );

      case 3: // Experience
        return (
          <motion.div key="experience" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#FAD07A]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <Briefcase className="text-[#FAD07A]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Work Experience</h3>
              <p className="text-xs text-gray-400 mt-1">Add your professional experience</p>
            </div>
            {experience.map((exp, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2 relative">
                <button onClick={() => removeFromList(setExperience, i)} className="absolute top-2 right-2 text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                <div className="grid grid-cols-2 gap-2">
                  <input value={exp.company} onChange={e => updateListItem(setExperience, i, "company", e.target.value)} placeholder="Company" className={inputCls} />
                  <input value={exp.role} onChange={e => updateListItem(setExperience, i, "role", e.target.value)} placeholder="Role / Title" className={inputCls} />
                </div>
                <input value={exp.duration} onChange={e => updateListItem(setExperience, i, "duration", e.target.value)} placeholder="Duration (e.g. Jan 2020 - Present)" className={inputCls} />
                <textarea rows={2} value={exp.description} onChange={e => updateListItem(setExperience, i, "description", e.target.value)} placeholder="Description of your role and responsibilities..." className={`${inputCls} resize-none`} />
              </div>
            ))}
            <button onClick={() => addToList(setExperience, emptyExperience)} className="w-full py-2 border border-dashed border-white/20 rounded-xl text-xs text-gray-400 hover:text-[#7BC4BE] hover:border-[#7BC4BE]/30 transition-all flex items-center justify-center gap-1">
              <Plus size={12} /> Add Experience
            </button>
          </motion.div>
        );

      case 4: // Projects
        return (
          <motion.div key="projects" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <Code className="text-[#7BC4BE]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Projects</h3>
              <p className="text-xs text-gray-400 mt-1">Showcase your best work</p>
            </div>
            {projects.map((proj, i) => (
              <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2 relative">
                <button onClick={() => removeFromList(setProjects, i)} className="absolute top-2 right-2 text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                <input value={proj.name} onChange={e => updateListItem(setProjects, i, "name", e.target.value)} placeholder="Project Name" className={inputCls} />
                <input value={proj.technologies} onChange={e => updateListItem(setProjects, i, "technologies", e.target.value)} placeholder="Technologies (e.g. React, Node.js, PostgreSQL)" className={inputCls} />
                <textarea rows={2} value={proj.description} onChange={e => updateListItem(setProjects, i, "description", e.target.value)} placeholder="Brief description..." className={`${inputCls} resize-none`} />
                <input value={proj.links} onChange={e => updateListItem(setProjects, i, "links", e.target.value)} placeholder="Links (GitHub, Live Demo)" className={inputCls} />
              </div>
            ))}
            <button onClick={() => addToList(setProjects, emptyProject)} className="w-full py-2 border border-dashed border-white/20 rounded-xl text-xs text-gray-400 hover:text-[#7BC4BE] hover:border-[#7BC4BE]/30 transition-all flex items-center justify-center gap-1">
              <Plus size={12} /> Add Project
            </button>
          </motion.div>
        );

      case 5: // Skills
        return (
          <motion.div key="skills" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#FAD07A]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <Star className="text-[#FAD07A]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Skills</h3>
              <p className="text-xs text-gray-400 mt-1">Add your technical and soft skills</p>
            </div>
            {skills.map((skill, i) => (
              <div key={i} className="flex gap-2">
                <input value={skill} onChange={e => { const s = [...skills]; s[i] = e.target.value; setSkills(s); }} placeholder={`Skill ${i + 1} (e.g. JavaScript, Python, Project Management)`} className={inputCls} />
                {skills.length > 1 && <button onClick={() => setSkills(skills.filter((_, j) => j !== i))} className="text-gray-500 hover:text-rose-400 px-2"><Trash2 size={12} /></button>}
              </div>
            ))}
            <button onClick={() => setSkills([...skills, ""])} className="w-full py-2 border border-dashed border-white/20 rounded-xl text-xs text-gray-400 hover:text-[#7BC4BE] hover:border-[#7BC4BE]/30 transition-all flex items-center justify-center gap-1">
              <Plus size={12} /> Add Skill
            </button>
          </motion.div>
        );

      case 6: // Extras (Certifications, Achievements, Languages, Awards, Volunteer, Extracurricular)
        return (
          <motion.div key="extras" className="space-y-5">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-3">
                <Award className="text-[#7BC4BE]" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Additional Sections</h3>
              <p className="text-xs text-gray-400 mt-1">All optional — enhance your resume</p>
            </div>

            {/* Certifications */}
            <div>
              <h4 className="text-xs font-bold text-[#7BC4BE] mb-2 flex items-center gap-1"><BookOpen size={12} /> Certifications</h4>
              {certifications.map((cert, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <input value={cert.name} onChange={e => updateListItem(setCertifications, i, "name", e.target.value)} placeholder="Certification name" className={inputCls} />
                  <input value={cert.issuer} onChange={e => updateListItem(setCertifications, i, "issuer", e.target.value)} placeholder="Issuer" className={inputCls} style={{ maxWidth: 120 }} />
                  <button onClick={() => removeFromList(setCertifications, i)} className="text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                </div>
              ))}
              <button onClick={() => addToList(setCertifications, emptyCert)} className="text-[10px] text-gray-500 hover:text-[#7BC4BE] flex items-center gap-1"><Plus size={10} /> Add</button>
            </div>

            {/* Languages */}
            <div>
              <h4 className="text-xs font-bold text-[#7BC4BE] mb-2 flex items-center gap-1"><Languages size={12} /> Languages</h4>
              {languages.map((lang, i) => (
                <div key={i} className="flex gap-2 mb-2">
                  <input value={lang.language} onChange={e => updateListItem(setLanguages, i, "language", e.target.value)} placeholder="Language" className={inputCls} />
                  <select value={lang.proficiency} onChange={e => updateListItem(setLanguages, i, "proficiency", e.target.value)} className={`${inputCls}`} style={{ maxWidth: 130 }}>
                    {PROFICIENCY_LEVELS.map(p => <option key={p} value={p} className="bg-[#1A2B2A]">{p}</option>)}
                  </select>
                  <button onClick={() => removeFromList(setLanguages, i)} className="text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                </div>
              ))}
              <button onClick={() => addToList(setLanguages, emptyLanguage)} className="text-[10px] text-gray-500 hover:text-[#7BC4BE] flex items-center gap-1"><Plus size={10} /> Add</button>
            </div>

            {/* Publications */}
            <div>
              <h4 className="text-xs font-bold text-[#7BC4BE] mb-2 flex items-center gap-1"><BookOpen size={12} /> Publications</h4>
              {publications.map((pub, i) => (
                <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2 relative">
                  <button onClick={() => removeFromList(setPublications, i)} className="absolute top-2 right-2 text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                  <input value={pub.title} onChange={e => updateListItem(setPublications, i, "title", e.target.value)} placeholder="Publication title" className={inputCls} />
                  <div className="grid grid-cols-2 gap-2">
                    <input value={pub.publisher} onChange={e => updateListItem(setPublications, i, "publisher", e.target.value)} placeholder="Publisher / Journal" className={inputCls} />
                    <input value={pub.date} onChange={e => updateListItem(setPublications, i, "date", e.target.value)} placeholder="Date (e.g. 2023)" className={inputCls} />
                  </div>
                  <input value={pub.url} onChange={e => updateListItem(setPublications, i, "url", e.target.value)} placeholder="URL (optional)" className={inputCls} />
                </div>
              ))}
              <button onClick={() => addToList(setPublications, emptyPublication)} className="text-[10px] text-gray-500 hover:text-[#7BC4BE] flex items-center gap-1"><Plus size={10} /> Add Publication</button>
            </div>

            {/* Interests */}
            <div>
              <h4 className="text-xs font-bold text-[#7BC4BE] mb-2 flex items-center gap-1"><Heart size={12} /> Interests</h4>
              <textarea rows={2} value={profile.interests || ""} onChange={e => update("interests", e.target.value)} placeholder="Comma-separated (e.g. Open Source, Machine Learning, hiking)" className={`${inputCls} resize-none`} />
            </div>

            {/* Volunteer Experience */}
            <div>
              <h4 className="text-xs font-bold text-[#7BC4BE] mb-2 flex items-center gap-1"><Users size={12} /> Volunteer Experience</h4>
              {volunteer.map((vol, i) => (
                <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2 relative">
                  <button onClick={() => removeFromList(setVolunteer, i)} className="absolute top-2 right-2 text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                  <div className="grid grid-cols-2 gap-2">
                    <input value={vol.organization} onChange={e => updateListItem(setVolunteer, i, "organization", e.target.value)} placeholder="Organization" className={inputCls} />
                    <input value={vol.role} onChange={e => updateListItem(setVolunteer, i, "role", e.target.value)} placeholder="Role" className={inputCls} />
                  </div>
                  <input value={vol.duration} onChange={e => updateListItem(setVolunteer, i, "duration", e.target.value)} placeholder="Duration (e.g. Jan 2020 - Present)" className={inputCls} />
                  <textarea rows={2} value={vol.description} onChange={e => updateListItem(setVolunteer, i, "description", e.target.value)} placeholder="Description of your volunteer work..." className={`${inputCls} resize-none`} />
                </div>
              ))}
              <button onClick={() => addToList(setVolunteer, emptyVolunteer)} className="text-[10px] text-gray-500 hover:text-[#7BC4BE] flex items-center gap-1"><Plus size={10} /> Add Volunteer Experience</button>
            </div>

            {/* Extracurricular Activities */}
            <div>
              <h4 className="text-xs font-bold text-[#7BC4BE] mb-2 flex items-center gap-1"><Activity size={12} /> Extracurricular Activities</h4>
              {extracurricular.map((extra, i) => (
                <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3 space-y-2 relative">
                  <button onClick={() => removeFromList(setExtracurricular, i)} className="absolute top-2 right-2 text-gray-500 hover:text-rose-400"><Trash2 size={12} /></button>
                  <input value={extra.activity} onChange={e => updateListItem(setExtracurricular, i, "activity", e.target.value)} placeholder="Activity name" className={inputCls} />
                  <div className="grid grid-cols-2 gap-2">
                    <textarea rows={2} value={extra.description} onChange={e => updateListItem(setExtracurricular, i, "description", e.target.value)} placeholder="Description" className={`${inputCls} resize-none`} />
                    <input value={extra.duration} onChange={e => updateListItem(setExtracurricular, i, "duration", e.target.value)} placeholder="Duration" className={inputCls} />
                  </div>
                </div>
              ))}
              <button onClick={() => addToList(setExtracurricular, emptyExtracurricular)} className="text-[10px] text-gray-500 hover:text-[#7BC4BE] flex items-center gap-1"><Plus size={10} /> Add Activity</button>
            </div>
          </motion.div>
        );

      case 7: // Complete
        return (
          <motion.div key="complete" className="space-y-4">
            <div className="text-center mb-4">
              <div className="w-14 h-14 bg-gradient-to-br from-[#7BC4BE] to-[#4A9E98] rounded-2xl flex items-center justify-center mx-auto mb-3">
                <Check className="text-white" size={24} />
              </div>
              <h3 className="text-lg font-bold text-white">Profile Complete!</h3>
              <p className="text-xs text-gray-400 mt-1">Review and finish setup</p>
            </div>
            <div className="bg-white/5 rounded-xl p-3 space-y-2 text-xs">
              <div className="flex justify-between"><span className="text-gray-400">Name</span><span className="text-white">{profile.full_name || "—"}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Title</span><span className="text-white">{profile.job_title || "—"}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Location</span><span className="text-white">{profile.location || "—"}</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Education</span><span className="text-white">{education.length} entry(ies)</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Experience</span><span className="text-white">{experience.length} entry(ies)</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Projects</span><span className="text-white">{projects.length} entry(ies)</span></div>
              <div className="flex justify-between"><span className="text-gray-400">Skills</span><span className="text-white">{skills.filter(s => s.trim()).length} skill(s)</span></div>
            </div>
            <div className="bg-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-xl p-3 flex items-start gap-2">
              <Sparkles size={14} className="text-[#7BC4BE] mt-0.5" />
              <p className="text-[11px] text-gray-300">This profile will auto-fill all future resumes. You can edit it anytime from Dashboard → Profile.</p>
            </div>
          </motion.div>
        );

      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col items-center justify-center gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={40} />
        <p className="text-gray-400 text-sm">Loading your profile...</p>
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
        className="w-full max-w-lg bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl shadow-2xl relative overflow-hidden max-h-[90vh] overflow-y-auto"
      >
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

        <div className="text-center mb-4">
          <span className="text-xl font-bold tracking-tight text-white flex items-center justify-center gap-1.5 mb-1">
            <span className="text-[#7BC4BE]">&#10022;</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
          </span>
          <h2 className="text-base font-medium text-white/90">Complete Your Profile</h2>
          <p className="text-[10px] text-gray-400 mt-0.5">Auto-fills all your resumes</p>
        </div>

        {/* Step Indicator */}
        <div className="flex flex-wrap justify-center gap-1 mb-5">
          {STEPS.map((s, i) => {
            const Icon = s.icon;
            const done = i < step;
            const cur = i === step;
            return (
              <button key={s.id} onClick={() => { if (i < step) { setDirection(-1); setStep(i); } }}
                className={`flex items-center gap-1 px-2 py-1 rounded-full text-[9px] font-semibold transition-all ${
                  cur ? "bg-[#7BC4BE] text-[#1A2B2A]" : done ? "bg-[#7BC4BE]/20 text-[#7BC4BE] cursor-pointer" : "bg-white/5 text-gray-500"
                }`}>
                {done ? <Check size={10} /> : <Icon size={10} />}
                {s.label}
              </button>
            );
          })}
        </div>

        <div className="min-h-[280px]">
          <AnimatePresence mode="wait" custom={direction}>
            <motion.div key={step} custom={direction} variants={slideVariants} initial="enter" animate="center" exit="exit" transition={{ duration: 0.2, ease: "easeInOut" }}>
              {renderStep()}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="flex justify-between items-center mt-5 pt-4 border-t border-white/10">
          {step > 0 ? (
            <button onClick={goBack} className="flex items-center gap-1 px-3 py-1.5 text-gray-400 hover:text-white text-xs font-semibold transition-all">
              <ArrowLeft size={12} /> Back
            </button>
          ) : <div />}
          {step < STEPS.length - 1 ? (
            <button onClick={goNext} disabled={!canProceed()} className="flex items-center gap-1 px-5 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed">
              Next <ArrowRight size={12} />
            </button>
          ) : (
            <button onClick={handleSave} disabled={saving} className="flex items-center gap-1 px-5 py-2 bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all shadow-lg shadow-[#7BC4BE]/10 disabled:opacity-50">
              {saving ? <><RefreshCw size={12} className="animate-spin" /> Saving...</> : <><Save size={12} /> Finish Setup</>}
            </button>
          )}
        </div>

        <div className="text-center mt-3">
          <button onClick={() => navigate("/dashboard")} className="text-[10px] text-gray-500 hover:text-gray-300 transition-colors">
            Skip for now →
          </button>
        </div>
      </motion.div>
    </div>
  );
}
