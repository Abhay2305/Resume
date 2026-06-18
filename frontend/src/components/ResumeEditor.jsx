import React, { useState, useEffect } from "react";
import { COLORS } from "../utils/constants";
import { api } from "../services/api";
import {
  Sparkles,
  User,
  FileText,
  Briefcase,
  GraduationCap,
  Code,
  FolderGit,
  Award,
  Check,
  ChevronRight,
  Eye,
  Plus,
  Trash2,
  Settings,
  RefreshCw,
  TrendingUp,
  Layout
} from "lucide-react";
import ResumePreview from "./ResumePreview";

export default function ResumeEditor({ data, template, onChange, onChangeTemplate, onBack, onNext }) {
  const [activeTab, setActiveTab] = useState("personal");
  const [localData, setLocalData] = useState(data);
  const [selectedStyle, setSelectedStyle] = useState(template || "harvard");
  const [templateOptions, setTemplateOptions] = useState([]);
  const [isRewriting, setIsRewriting] = useState(null); // section ID being rewritten
  const [showMobilePreview, setShowMobilePreview] = useState(false);

  // Load the real seeded template catalog so the style switcher uses valid IDs.
  useEffect(() => {
    let active = true;
    api
      .listTemplates()
      .then((list) => {
        if (active) setTemplateOptions(list);
      })
      .catch((err) => console.error("Failed to load templates:", err));
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setLocalData(data);
  }, [data]);

  useEffect(() => {
    if (template) {
      setSelectedStyle(template);
    }
  }, [template]);

  const updateField = (section, field, value) => {
    // When field is null the section itself is a scalar value (e.g. summary),
    // so set it directly instead of spreading it into an object.
    const updated =
      field === null
        ? { ...localData, [section]: value }
        : {
            ...localData,
            [section]: {
              ...localData[section],
              [field]: value
            }
          };
    setLocalData(updated);
    onChange(updated);
  };

  const updateArrayField = (section, index, field, value) => {
    const updatedArr = [...localData[section]];
    updatedArr[index] = {
      ...updatedArr[index],
      [field]: value
    };
    const updated = {
      ...localData,
      [section]: updatedArr
    };
    setLocalData(updated);
    onChange(updated);
  };

  const addArrayItem = (section, emptyItem) => {
    const updated = {
      ...localData,
      [section]: [...localData[section], emptyItem]
    };
    setLocalData(updated);
    onChange(updated);
  };

  const removeArrayItem = (section, index) => {
    const updatedArr = localData[section].filter((_, i) => i !== index);
    const updated = {
      ...localData,
      [section]: updatedArr
    };
    setLocalData(updated);
    onChange(updated);
  };

  const updateSkills = (newSkillsString) => {
    const skillList = newSkillsString.split(",").map(s => s.trim()).filter(s => s !== "");
    const updated = {
      ...localData,
      skills: skillList
    };
    setLocalData(updated);
    onChange(updated);
  };

  const handleTemplateChange = (e) => {
    const newTemp = e.target.value;
    setSelectedStyle(newTemp);
    onChangeTemplate(newTemp);
  };

  // AI assistant runner targeting the FastAPI backend
  const handleAIAssist = async (section, index, type) => {
    const assistKey = index !== null ? `${section}-${index}-${type}` : `${section}-${type}`;
    setIsRewriting(assistKey);

    let originalText = "";
    if (section === "summary") {
      originalText = localData.summary || "";
    } else if (section === "experience") {
      originalText = localData.experience[index]?.description || "";
    } else if (section === "projects") {
      originalText = localData.projects[index]?.description || "";
    }

    try {
      const res = await api.improveText(originalText, type, section);
      const rewrittenText = res.improved_text;

      if (section === "summary") {
        updateField("summary", null, rewrittenText);
      } else if (section === "experience") {
        updateArrayField("experience", index, "description", rewrittenText);
      } else if (section === "projects") {
        updateArrayField("projects", index, "description", rewrittenText);
      }
    } catch (err) {
      console.error(err);
      alert("AI optimization request failed: " + err.message);
    } finally {
      setIsRewriting(null);
    }
  };

  const tabs = [
    { id: "personal", label: "Contact", icon: <User size={14} /> },
    { id: "summary", label: "Summary", icon: <FileText size={14} /> },
    { id: "experience", label: "Experience", icon: <Briefcase size={14} /> },
    { id: "education", label: "Education", icon: <GraduationCap size={14} /> },
    { id: "skills", label: "Skills", icon: <Code size={14} /> },
    { id: "projects", label: "Projects", icon: <FolderGit size={14} /> },
    { id: "other", label: "Credentials", icon: <Award size={14} /> },
    { id: "layout", label: "Reorder", icon: <Layout size={14} /> }
  ];

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col bg-gray-50">
      
      {/* Editor Main Content Area */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden h-[calc(100vh-120px)]">
        
        {/* Left Panel: Editor Forms (Col span 5 or 6 depending on screen) */}
        <div className={`col-span-1 lg:col-span-5 flex flex-col bg-white border-r h-full overflow-hidden ${showMobilePreview ? "hidden" : "flex"}`} style={{ borderColor: COLORS.border }}>
          
          {/* Section Selector Tab Bar */}
          <div className="flex overflow-x-auto border-b bg-gray-50/50 p-2 gap-1 shrink-0" style={{ borderColor: COLORS.border }}>
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                  activeTab === t.id
                    ? "bg-[#7BC4BE] text-white shadow-sm"
                    : "text-gray-500 hover:bg-gray-100"
                }`}
              >
                {t.icon}
                <span>{t.label}</span>
              </button>
            ))}
          </div>

          {/* Section editor scroll area */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
            
            {/* Quick Template Switcher & Info */}
            <div className="bg-gray-50 p-4 rounded-xl border flex flex-col gap-2 shrink-0" style={{ borderColor: COLORS.border }}>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                  <Layout size={14} className="text-[#4A9E98]" />
                  <span>Resume Style</span>
                </span>
                <span className="text-[10px] text-gray-400">Apply instantly</span>
              </div>
              <select
                value={selectedStyle}
                onChange={handleTemplateChange}
                className="w-full text-xs font-semibold p-2 bg-white border rounded-lg focus:outline-none"
                style={{ borderColor: COLORS.borderMid }}
              >
                {templateOptions.length === 0 ? (
                  <option value={selectedStyle}>{selectedStyle}</option>
                ) : (
                  templateOptions.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.name} ({t.category})
                    </option>
                  ))
                )}
              </select>
            </div>

            {/* TAB: Personal Info */}
            {activeTab === "personal" && (
              <div className="flex flex-col gap-4 animate-fadeIn">
                <h3 className="text-sm font-semibold text-gray-800 border-b pb-2">Personal Information</h3>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1 col-span-2">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Full Name</label>
                    <input
                      type="text"
                      value={localData.personalInfo.fullName || ""}
                      onChange={(e) => updateField("personalInfo", "fullName", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Job Title</label>
                    <input
                      type="text"
                      value={localData.personalInfo.jobTitle || ""}
                      onChange={(e) => updateField("personalInfo", "jobTitle", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Location</label>
                    <input
                      type="text"
                      value={localData.personalInfo.location || ""}
                      onChange={(e) => updateField("personalInfo", "location", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Email Address</label>
                    <input
                      type="email"
                      value={localData.personalInfo.email || ""}
                      onChange={(e) => updateField("personalInfo", "email", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Phone Number</label>
                    <input
                      type="text"
                      value={localData.personalInfo.phone || ""}
                      onChange={(e) => updateField("personalInfo", "phone", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">LinkedIn Profile</label>
                    <input
                      type="text"
                      value={localData.personalInfo.linkedin || ""}
                      onChange={(e) => updateField("personalInfo", "linkedin", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Website / Portfolio</label>
                    <input
                      type="text"
                      value={localData.personalInfo.website || ""}
                      onChange={(e) => updateField("personalInfo", "website", e.target.value)}
                      className="border rounded-lg p-2 text-sm focus:outline-none focus:border-[#7BC4BE]"
                      style={{ borderColor: COLORS.borderMid }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* TAB: Professional Summary */}
            {activeTab === "summary" && (
              <div className="flex flex-col gap-4 animate-fadeIn">
                <div className="flex justify-between items-center border-b pb-2">
                  <h3 className="text-sm font-semibold text-gray-800">Professional Summary</h3>
                  <div className="flex items-center gap-1 text-[10px] text-gray-400 font-medium bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    <Sparkles size={10} className="text-[#F6B233]" />
                    <span>AI Writing Assist Active</span>
                  </div>
                </div>

                <div className="flex flex-col gap-1 relative">
                  <textarea
                    value={localData.summary || ""}
                    onChange={(e) => updateField("summary", null, e.target.value)}
                    className="w-full h-48 border rounded-lg p-3 text-sm focus:outline-none focus:border-[#7BC4BE] leading-relaxed"
                    style={{ borderColor: COLORS.borderMid }}
                    placeholder="Enter professional summary"
                  />
                  
                  {isRewriting === "summary-improve" || isRewriting === "summary-shorten" || isRewriting === "summary-professional" ? (
                    <div className="absolute inset-0 bg-white/80 backdrop-blur-xs flex flex-col justify-center items-center rounded-lg border border-teal-200 gap-2">
                      <RefreshCw size={24} className="text-[#7BC4BE] animate-spin" />
                      <span className="text-xs font-semibold text-teal-800">AI Rewriting summary...</span>
                    </div>
                  ) : null}
                </div>

                {/* AI helper tools row */}
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">AI Quick Actions:</span>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => handleAIAssist("summary", null, "improve")}
                      className="px-2.5 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1 hover:bg-[#7BC4BE]/10 hover:border-[#7BC4BE] text-[#2D7A74] cursor-pointer"
                      style={{ borderColor: COLORS.borderMid }}
                    >
                      <Sparkles size={11} className="text-[#F6B233]" />
                      <span>Improve wording</span>
                    </button>
                    <button
                      onClick={() => handleAIAssist("summary", null, "shorten")}
                      className="px-2.5 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1 hover:bg-[#7BC4BE]/10 hover:border-[#7BC4BE] text-[#2D7A74] cursor-pointer"
                      style={{ borderColor: COLORS.borderMid }}
                    >
                      <span>Shorten</span>
                    </button>
                    <button
                      onClick={() => handleAIAssist("summary", null, "professional")}
                      className="px-2.5 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1 hover:bg-[#7BC4BE]/10 hover:border-[#7BC4BE] text-[#2D7A74] cursor-pointer"
                      style={{ borderColor: COLORS.borderMid }}
                    >
                      <span>Make Professional</span>
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: Work Experience */}
            {activeTab === "experience" && (
              <div className="flex flex-col gap-6 animate-fadeIn">
                <div className="flex justify-between items-center border-b pb-2">
                  <h3 className="text-sm font-semibold text-gray-800">Work Experience</h3>
                  <button
                    onClick={() => addArrayItem("experience", { company: "New Company", role: "Job Title", duration: "2026 - Present", description: "" })}
                    className="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded bg-teal-50 border border-[#7BC4BE] text-[#2D7A74] hover:bg-teal-100 cursor-pointer"
                  >
                    <Plus size={12} /> Add Job
                  </button>
                </div>

                <div className="flex flex-col gap-6">
                  {localData.experience.map((exp, idx) => (
                    <div key={idx} className="p-4 bg-gray-50/50 rounded-xl border border-gray-100 flex flex-col gap-4 relative group">
                      
                      {/* Delete job button */}
                      <button
                        onClick={() => removeArrayItem("experience", idx)}
                        className="absolute top-3 right-3 text-gray-300 hover:text-red-500 transition-colors p-1"
                        title="Delete Experience"
                      >
                        <Trash2 size={14} />
                      </button>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Job Title</label>
                          <input
                            type="text"
                            value={exp.role}
                            onChange={(e) => updateArrayField("experience", idx, "role", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Company Name</label>
                          <input
                            type="text"
                            value={exp.company}
                            onChange={(e) => updateArrayField("experience", idx, "company", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1 col-span-2">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Duration / Dates</label>
                          <input
                            type="text"
                            value={exp.duration}
                            onChange={(e) => updateArrayField("experience", idx, "duration", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1 col-span-2 relative">
                          <label className="text-[10px] font-bold text-gray-400 uppercase flex items-center justify-between">
                            <span>Job Description / Achievements</span>
                          </label>
                          <textarea
                            value={exp.description}
                            onChange={(e) => updateArrayField("experience", idx, "description", e.target.value)}
                            className="w-full h-32 border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE] leading-relaxed"
                            style={{ borderColor: COLORS.borderMid }}
                            placeholder="Describe your role and key accomplishments"
                          />

                          {isRewriting === `experience-${idx}-improve` || isRewriting === `experience-${idx}-shorten` || isRewriting === `experience-${idx}-professional` ? (
                            <div className="absolute inset-0 bg-white/80 backdrop-blur-xs flex flex-col justify-center items-center rounded-lg border border-teal-200 gap-1.5">
                              <RefreshCw size={18} className="text-[#7BC4BE] animate-spin" />
                              <span className="text-[10px] font-semibold text-teal-800">AI Rewriting experience...</span>
                            </div>
                          ) : null}
                        </div>
                      </div>

                      {/* AI assist triggers */}
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider mr-1">AI Assist:</span>
                        <button
                          onClick={() => handleAIAssist("experience", idx, "improve")}
                          className="px-2 py-1 bg-white border rounded text-[10px] font-semibold text-[#2D7A74] flex items-center gap-0.5 hover:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        >
                          <Sparkles size={9} className="text-[#F6B233]" />
                          <span>Optimize phrasing</span>
                        </button>
                        <button
                          onClick={() => handleAIAssist("experience", idx, "shorten")}
                          className="px-2 py-1 bg-white border rounded text-[10px] font-semibold text-[#2D7A74] hover:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        >
                          <span>Concise</span>
                        </button>
                        <button
                          onClick={() => handleAIAssist("experience", idx, "professional")}
                          className="px-2 py-1 bg-white border rounded text-[10px] font-semibold text-[#2D7A74] hover:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        >
                          <span>Formalize</span>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: Education */}
            {activeTab === "education" && (
              <div className="flex flex-col gap-6 animate-fadeIn">
                <div className="flex justify-between items-center border-b pb-2">
                  <h3 className="text-sm font-semibold text-gray-800">Education History</h3>
                  <button
                    onClick={() => addArrayItem("education", { institution: "New University", degree: "Degree, Major", duration: "2020 - 2024", description: "" })}
                    className="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded bg-teal-50 border border-[#7BC4BE] text-[#2D7A74] hover:bg-teal-100 cursor-pointer"
                  >
                    <Plus size={12} /> Add Education
                  </button>
                </div>

                <div className="flex flex-col gap-5">
                  {localData.education.map((edu, idx) => (
                    <div key={idx} className="p-4 bg-gray-50/50 rounded-xl border border-gray-100 flex flex-col gap-3 relative">
                      
                      {/* Delete button */}
                      <button
                        onClick={() => removeArrayItem("education", idx)}
                        className="absolute top-3 right-3 text-gray-300 hover:text-red-500 transition-colors p-1"
                      >
                        <Trash2 size={14} />
                      </button>

                      <div className="grid grid-cols-2 gap-3">
                        <div className="flex flex-col gap-1 col-span-2">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Degree & Major</label>
                          <input
                            type="text"
                            value={edu.degree}
                            onChange={(e) => updateArrayField("education", idx, "degree", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Institution / School</label>
                          <input
                            type="text"
                            value={edu.institution}
                            onChange={(e) => updateArrayField("education", idx, "institution", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Duration / Dates</label>
                          <input
                            type="text"
                            value={edu.duration}
                            onChange={(e) => updateArrayField("education", idx, "duration", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1 col-span-2">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Details (GPA, Honors, Coursework)</label>
                          <input
                            type="text"
                            value={edu.description || ""}
                            onChange={(e) => updateArrayField("education", idx, "description", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: Skills */}
            {activeTab === "skills" && (
              <div className="flex flex-col gap-4 animate-fadeIn">
                <h3 className="text-sm font-semibold text-gray-800 border-b pb-2">Professional Skills</h3>
                
                <div className="flex flex-col gap-2">
                  <label className="text-[11px] font-bold text-gray-500 uppercase">Skills List (Comma Separated)</label>
                  <textarea
                    value={localData.skills.join(", ")}
                    onChange={(e) => updateSkills(e.target.value)}
                    className="w-full h-36 border rounded-lg p-3 text-sm focus:outline-none focus:border-[#7BC4BE] leading-relaxed"
                    style={{ borderColor: COLORS.borderMid }}
                    placeholder="Enter skills separated by commas, e.g. Figma, React, User Research, Photoshop"
                  />
                </div>

                <div className="flex flex-col gap-2">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Current Active Skill Tags:</span>
                  <div className="flex flex-wrap gap-1.5 p-3 bg-gray-50 rounded-xl border border-gray-100">
                    {localData.skills.map((skill, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 bg-white border rounded text-xs font-medium text-gray-700 flex items-center gap-1 shadow-2xs"
                        style={{ borderColor: COLORS.borderMid }}
                      >
                        <span>{skill}</span>
                        <button
                          type="button"
                          onClick={() => {
                            const newSkills = localData.skills.filter((_, i) => i !== idx);
                            const updated = { ...localData, skills: newSkills };
                            setLocalData(updated);
                            onChange(updated);
                          }}
                          className="text-gray-400 hover:text-red-500 font-bold ml-1 text-[10px]"
                        >
                          ✕
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB: Projects */}
            {activeTab === "projects" && (
              <div className="flex flex-col gap-6 animate-fadeIn">
                <div className="flex justify-between items-center border-b pb-2">
                  <h3 className="text-sm font-semibold text-gray-800">Key Projects</h3>
                  <button
                    onClick={() => addArrayItem("projects", { name: "Project Name", description: "" })}
                    className="flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded bg-teal-50 border border-[#7BC4BE] text-[#2D7A74] hover:bg-teal-100 cursor-pointer"
                  >
                    <Plus size={12} /> Add Project
                  </button>
                </div>

                <div className="flex flex-col gap-5">
                  {localData.projects.map((proj, idx) => (
                    <div key={idx} className="p-4 bg-gray-50/50 rounded-xl border border-gray-100 flex flex-col gap-3 relative">
                      
                      {/* Delete project button */}
                      <button
                        onClick={() => removeArrayItem("projects", idx)}
                        className="absolute top-3 right-3 text-gray-300 hover:text-red-500 transition-colors p-1"
                      >
                        <Trash2 size={14} />
                      </button>

                      <div className="flex flex-col gap-3">
                        <div className="flex flex-col gap-1">
                          <label className="text-[10px] font-bold text-gray-400 uppercase">Project Name</label>
                          <input
                            type="text"
                            value={proj.name}
                            onChange={(e) => updateArrayField("projects", idx, "name", e.target.value)}
                            className="border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                            style={{ borderColor: COLORS.borderMid }}
                          />
                        </div>

                        <div className="flex flex-col gap-1 col-span-2 relative">
                          <label className="text-[10px] font-bold text-gray-400 uppercase flex items-center justify-between">
                            <span>Project Description</span>
                          </label>
                          <textarea
                            value={proj.description}
                            onChange={(e) => updateArrayField("projects", idx, "description", e.target.value)}
                            className="w-full h-24 border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE] leading-relaxed"
                            style={{ borderColor: COLORS.borderMid }}
                            placeholder="Describe project details, technology used, and results"
                          />

                          {isRewriting === `projects-${idx}-improve` || isRewriting === `projects-${idx}-shorten` || isRewriting === `projects-${idx}-professional` ? (
                            <div className="absolute inset-0 bg-white/80 backdrop-blur-xs flex flex-col justify-center items-center rounded-lg border border-teal-200 gap-1.5">
                              <RefreshCw size={18} className="text-[#7BC4BE] animate-spin" />
                              <span className="text-[10px] font-semibold text-teal-800">AI Rewriting project...</span>
                            </div>
                          ) : null}
                        </div>
                      </div>

                      {/* AI assist triggers */}
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider mr-1">AI Assist:</span>
                        <button
                          onClick={() => handleAIAssist("projects", idx, "improve")}
                          className="px-2 py-1 bg-white border rounded text-[10px] font-semibold text-[#2D7A74] flex items-center gap-0.5 hover:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        >
                          <Sparkles size={9} className="text-[#F6B233]" />
                          <span>Optimize description</span>
                        </button>
                        <button
                          onClick={() => handleAIAssist("projects", idx, "shorten")}
                          className="px-2 py-1 bg-white border rounded text-[10px] font-semibold text-[#2D7A74] hover:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        >
                          <span>Shorten</span>
                        </button>
                        <button
                          onClick={() => handleAIAssist("projects", idx, "professional")}
                          className="px-2 py-1 bg-white border rounded text-[10px] font-semibold text-[#2D7A74] hover:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        >
                          <span>Formal</span>
                        </button>
                      </div>

                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: Credentials (Certifications & Achievements) */}
            {activeTab === "other" && (
              <div className="flex flex-col gap-6 animate-fadeIn">
                <h3 className="text-sm font-semibold text-gray-800 border-b pb-2">Credentials & Accomplishments</h3>
                
                {/* Certifications list */}
                <div className="flex flex-col gap-3">
                  <div className="flex justify-between items-center">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Certifications</label>
                    <button
                      onClick={() => {
                        const updated = {
                          ...localData,
                          certifications: [...(localData.certifications || []), "New Certificate"]
                        };
                        setLocalData(updated);
                        onChange(updated);
                      }}
                      className="text-[10px] font-semibold text-[#2D7A74] flex items-center gap-0.5 hover:underline"
                    >
                      <Plus size={10} /> Add
                    </button>
                  </div>
                  <div className="flex flex-col gap-2">
                    {(localData.certifications || []).map((cert, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <input
                          type="text"
                          value={cert}
                          onChange={(e) => {
                            const updatedArr = [...localData.certifications];
                            updatedArr[idx] = e.target.value;
                            const updated = { ...localData, certifications: updatedArr };
                            setLocalData(updated);
                            onChange(updated);
                          }}
                          className="flex-1 border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        />
                        <button
                          onClick={() => {
                            const updatedArr = localData.certifications.filter((_, i) => i !== idx);
                            const updated = { ...localData, certifications: updatedArr };
                            setLocalData(updated);
                            onChange(updated);
                          }}
                          className="text-gray-300 hover:text-red-500 transition-colors p-1"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Achievements list */}
                <div className="flex flex-col gap-3 mt-2">
                  <div className="flex justify-between items-center">
                    <label className="text-[11px] font-bold text-gray-500 uppercase">Achievements & Awards</label>
                    <button
                      onClick={() => {
                        const updated = {
                          ...localData,
                          achievements: [...(localData.achievements || []), "Award details"]
                        };
                        setLocalData(updated);
                        onChange(updated);
                      }}
                      className="text-[10px] font-semibold text-[#2D7A74] flex items-center gap-0.5 hover:underline"
                    >
                      <Plus size={10} /> Add
                    </button>
                  </div>
                  <div className="flex flex-col gap-2">
                    {(localData.achievements || []).map((ach, idx) => (
                      <div key={idx} className="flex items-center gap-2">
                        <input
                          type="text"
                          value={ach}
                          onChange={(e) => {
                            const updatedArr = [...localData.achievements];
                            updatedArr[idx] = e.target.value;
                            const updated = { ...localData, achievements: updatedArr };
                            setLocalData(updated);
                            onChange(updated);
                          }}
                          className="flex-1 border bg-white rounded-lg p-2 text-xs focus:outline-none focus:border-[#7BC4BE]"
                          style={{ borderColor: COLORS.borderMid }}
                        />
                        <button
                          onClick={() => {
                            const updatedArr = localData.achievements.filter((_, i) => i !== idx);
                            const updated = { ...localData, achievements: updatedArr };
                            setLocalData(updated);
                            onChange(updated);
                          }}
                          className="text-gray-300 hover:text-red-500 transition-colors p-1"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

            {/* TAB: Section Reordering (Drag and Drop / Up Down) */}
            {activeTab === "layout" && (
              <div className="flex flex-col gap-5 animate-fadeIn">
                <div className="border-b pb-2">
                  <h3 className="text-sm font-semibold text-gray-800">Reorder Sections</h3>
                  <p className="text-[10px] text-gray-500 font-light mt-0.5">
                    Drag and drop or use arrow buttons to rearrange resume sections.
                  </p>
                </div>

                <div className="flex flex-col gap-2.5">
                  {(localData.section_order || ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]).map((sec, index, arr) => {
                    const labelMap = {
                      summary: "Summary Profile",
                      experience: "Work Experience",
                      education: "Education History",
                      projects: "Key Projects",
                      skills: "Core Skills",
                      certifications: "Certifications",
                      achievements: "Achievements"
                    };
                    
                    return (
                      <div
                        key={sec}
                        draggable
                        onDragStart={(e) => {
                          e.dataTransfer.setData("index", index);
                        }}
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) => {
                          const sourceIndex = parseInt(e.dataTransfer.getData("index"));
                          if (isNaN(sourceIndex) || sourceIndex === index) return;
                          const newOrder = [...arr];
                          const [removed] = newOrder.splice(sourceIndex, 1);
                          newOrder.splice(index, 0, removed);
                          const updated = {
                            ...localData,
                            section_order: newOrder
                          };
                          setLocalData(updated);
                          onChange(updated);
                        }}
                        className="flex justify-between items-center p-3 bg-gray-50 border border-gray-200 hover:border-[#7BC4BE] rounded-xl hover:shadow-xs cursor-grab active:cursor-grabbing transition-all select-none"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400 text-xs font-bold font-mono">::</span>
                          <span className="text-xs font-bold text-gray-700">{labelMap[sec] || sec}</span>
                        </div>
                        
                        <div className="flex items-center gap-1.5">
                          <button
                            type="button"
                            disabled={index === 0}
                            onClick={() => {
                              const newOrder = [...arr];
                              const temp = newOrder[index];
                              newOrder[index] = newOrder[index - 1];
                              newOrder[index - 1] = temp;
                              const updated = { ...localData, section_order: newOrder };
                              setLocalData(updated);
                              onChange(updated);
                            }}
                            className="p-1 hover:bg-gray-200 rounded text-gray-500 disabled:opacity-30 cursor-pointer"
                          >
                            ▲
                          </button>
                          <button
                            type="button"
                            disabled={index === arr.length - 1}
                            onClick={() => {
                              const newOrder = [...arr];
                              const temp = newOrder[index];
                              newOrder[index] = newOrder[index + 1];
                              newOrder[index + 1] = temp;
                              const updated = { ...localData, section_order: newOrder };
                              setLocalData(updated);
                              onChange(updated);
                            }}
                            className="p-1 hover:bg-gray-200 rounded text-gray-500 disabled:opacity-30 cursor-pointer"
                          >
                            ▼
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

          </div>
        </div>

        {/* Right Panel: A4 Live Preview (Col span 7) */}
        <div className={`col-span-1 lg:col-span-7 bg-[#FFFDF8]/40 overflow-y-auto p-8 lg:p-12 flex justify-center items-start h-full ${showMobilePreview ? "flex" : "hidden lg:flex"}`}>
          <div className="w-full max-w-[760px] sticky top-4">
            <ResumePreview data={localData} template={selectedStyle} />
          </div>
        </div>

      </div>

      {/* Editor Footer / Control Bar */}
      <footer className="h-14 bg-white border-t px-6 flex items-center justify-between shrink-0 z-10" style={{ borderColor: COLORS.border }}>
        
        {/* Toggle mobile view (visible only on mobile) */}
        <button
          onClick={() => setShowMobilePreview(!showMobilePreview)}
          className="lg:hidden flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border cursor-pointer"
          style={{ borderColor: COLORS.borderMid, color: COLORS.textMid }}
        >
          <Eye size={14} />
          <span>{showMobilePreview ? "Show Inputs" : "Show Preview"}</span>
        </button>

        <button
          onClick={onBack}
          className="hidden sm:flex items-center gap-1 text-xs font-semibold hover:opacity-80 transition-opacity"
          style={{ color: COLORS.textMid }}
        >
          <span>← Gallery</span>
        </button>

        {/* Empty placeholder to push CTA right on mobile */}
        <div className="sm:hidden" />

        <button
          onClick={onNext}
          className="btn-hero py-2 px-5 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold transition-all duration-300 cursor-pointer shadow-md select-none"
          style={{
            background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`,
            boxShadow: "0 4px 12px rgba(75, 158, 152, 0.25)",
            color: "white"
          }}
        >
          <span>Check ATS Score</span>
          <ChevronRight size={14} />
        </button>
      </footer>

    </div>
  );
}
