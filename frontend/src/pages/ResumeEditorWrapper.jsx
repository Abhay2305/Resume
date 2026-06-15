import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { RefreshCw, ArrowLeft, Save } from "lucide-react";
import { api } from "../services/api";
import ResumeFlowHeader from "../components/ResumeFlowHeader";
import ResumeEditor from "../components/ResumeEditor";
import TemplateSelection from "../components/TemplateSelection";
import ATSReview from "../components/ATSReview";
import ExportDownload from "../components/ExportDownload";

export default function ResumeEditorWrapper() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [step, setStep] = useState("editor"); // 'editor' | 'templates' | 'ats' | 'export'
  const [resumeTitle, setResumeTitle] = useState("My Resume");
  const [selectedTemplate, setSelectedTemplate] = useState("harvard");
  
  // Key-value resume structure matching editor expectations
  const [resumeData, setResumeData] = useState({
    personalInfo: { fullName: "", jobTitle: "", email: "", phone: "", location: "", website: "", linkedin: "" },
    summary: "",
    experience: [],
    education: [],
    skills: [],
    projects: [],
    certifications: [],
    achievements: []
  });

  const [saving, setSaving] = useState(false);
  const autosaveTimer = useRef(null);

  // Load resume on startup
  useEffect(() => {
    const loadResume = async () => {
      try {
        setLoading(true);
        const res = await api.getResume(id);
        setResumeTitle(res.title);
        setSelectedTemplate(res.template_id || "harvard");

        if (res.sections && res.sections.length > 0) {
          const formatted = {
            personalInfo: { fullName: "", jobTitle: "", email: "", phone: "", location: "", website: "", linkedin: "" },
            summary: "",
            experience: [],
            education: [],
            skills: [],
            projects: [],
            certifications: [],
            achievements: []
          };
          res.sections.forEach(s => {
            formatted[s.section_type] = s.content;
          });
          setResumeData(formatted);
        }
      } catch (err) {
        setError(err.message || "Failed to load resume details.");
      } finally {
        setLoading(false);
      }
    };

    loadResume();
  }, [id]);

  // Synchronize changes and run debounced autosave
  const triggerAutosave = (updatedData) => {
    setResumeData(updatedData);
    setSaving(true);

    if (autosaveTimer.current) {
      clearTimeout(autosaveTimer.current);
    }

    autosaveTimer.current = setTimeout(async () => {
      try {
        // Map key-value state to backend array format
        const payload = Object.keys(updatedData).map((key, idx) => ({
          section_type: key,
          content: updatedData[key],
          position: idx
        }));
        await api.saveResumeSections(id, payload);
      } catch (err) {
        console.error("Autosave failed:", err);
      } finally {
        setSaving(false);
      }
    }, 1500); // 1.5 seconds debounce
  };

  const handleTemplateSelect = async (templateId) => {
    setSelectedTemplate(templateId);
    try {
      await api.updateResume(id, resumeTitle, templateId);
    } catch (err) {
      console.error(err);
    }
    setStep("editor");
  };

  const handleTemplateChange = async (templateId) => {
    setSelectedTemplate(templateId);
    try {
      await api.updateResume(id, resumeTitle, templateId);
    } catch (err) {
      console.error(err);
    }
  };

  const handleBack = () => {
    if (step === "export") {
      setStep("ats");
    } else if (step === "ats") {
      setStep("editor");
    } else if (step === "editor") {
      setStep("templates");
    } else if (step === "templates") {
      navigate("/dashboard");
    }
  };

  const handleExit = () => {
    if (window.confirm("Return to Dashboard? Your changes are autosaved.")) {
      navigate("/dashboard");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col items-center justify-center gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={40} />
        <p className="text-gray-400 text-sm">Loading your resume canvas...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col items-center justify-center gap-4">
        <p className="text-rose-400 text-sm font-semibold">{error}</p>
        <button
          onClick={() => navigate("/dashboard")}
          className="px-4 py-2 bg-white/10 hover:bg-white/15 rounded-lg text-xs font-semibold flex items-center gap-1.5 border border-white/10"
        >
          <ArrowLeft size={14} /> Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50 text-gray-800">
      {/* Top Progress bar and Header */}
      <ResumeFlowHeader step={step} onBack={handleBack} onExit={handleExit} />
      
      {/* Autosave badge indicator */}
      <div className="bg-white border-b px-6 py-1 text-right text-[10px] text-gray-400 flex justify-end items-center gap-1.5 select-none border-gray-200">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
        <span>{saving ? "Saving Draft..." : "All changes autosaved to DB"}</span>
      </div>

      <main className="flex-1">
        {step === "templates" && (
          <TemplateSelection
            resumeData={resumeData}
            selectedTemplate={selectedTemplate}
            onSelect={handleTemplateSelect}
            onBack={handleBack}
          />
        )}
        
        {step === "editor" && (
          <ResumeEditor
            data={resumeData}
            template={selectedTemplate}
            onChange={triggerAutosave}
            onChangeTemplate={handleTemplateChange}
            onBack={handleBack}
            onNext={() => setStep("ats")}
          />
        )}

        {step === "ats" && (
          <ATSReview
            data={resumeData}
            template={selectedTemplate}
            onChange={triggerAutosave}
            onBack={handleBack}
            onNext={() => setStep("export")}
          />
        )}

        {step === "export" && (
          <ExportDownload
            data={resumeData}
            template={selectedTemplate}
            onBack={handleBack}
            onExit={() => navigate("/dashboard")}
          />
        )}
      </main>
    </div>
  );
}
