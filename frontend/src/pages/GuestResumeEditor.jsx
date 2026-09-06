import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { RefreshCw, ArrowLeft, Download, Save } from "lucide-react";
import ResumeFlowHeader from "../components/ResumeFlowHeader";
import ResumeEditor from "../components/ResumeEditor";
import TemplateSelection from "../components/TemplateSelection";
import ATSReview from "../components/ATSReview";
import ExportDownload from "../components/ExportDownload";
import { useAuth } from "../hooks/useAuth";
import { getGuestSession, saveGuestSession, clearPendingDownload } from "../utils/guestSession";

export default function GuestResumeEditor() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [, setError] = useState("");
  const [step, setStep] = useState("editor"); // 'editor' | 'templates' | 'ats' | 'export'
  const [selectedTemplate, setSelectedTemplate] = useState("harvard");
  const [isGuest, setIsGuest] = useState(!user);
  
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

  // Trigger actual download (for authenticated users)
  const handleDownloadNow = async () => {
    try {
      alert("PDF generation will be triggered. Your resume data is ready.");
    } catch (err) {
      console.error("Download failed:", err);
      alert("Download failed. Please try again.");
    }
  };

  // Load resume from unified session on startup
  useEffect(() => {
    const loadGuestResume = () => {
      try {
        setLoading(true);
        
        // Check if we should start at templates (from AI generation)
        const initialStep = location.state?.step;
        if (initialStep) {
          setStep(initialStep);
        }
        
        // Load from unified guest session
        const session = getGuestSession();
        
        if (session.generatedResume) {
          setResumeData(session.generatedResume);
        } else {
          // Fallback to old localStorage key for backward compatibility
          const savedData = localStorage.getItem("guest_resume_data");
          if (savedData) {
            setResumeData(JSON.parse(savedData));
          }
        }
        
        if (session.selectedTemplate) {
          setSelectedTemplate(session.selectedTemplate);
        } else {
          // Fallback to old localStorage key
          const savedTemplate = localStorage.getItem("guest_resume_template");
          if (savedTemplate) {
            setSelectedTemplate(savedTemplate);
          }
        }
        
        // Check if user just logged in and there's a pending download
        if (user) {
          setIsGuest(false);
          if (session.pendingDownload) {
            clearPendingDownload();
            // Trigger download after a short delay
            setTimeout(() => {
              handleDownloadNow();
            }, 500);
          }
        }
      } catch (err) {
        setError(err.message || "Failed to load resume data.");
      } finally {
        setLoading(false);
      }
    };

    loadGuestResume();
  }, [user, location.state]);

  // Save to unified session whenever data changes
  useEffect(() => {
    if (!loading) {
      saveGuestSession({
        generatedResume: resumeData,
        selectedTemplate: selectedTemplate,
      });
    }
  }, [resumeData, selectedTemplate, loading]);

  // Synchronize changes from editor
  const handleDataChange = (updatedData) => {
    setResumeData(updatedData);
  };

  // Handle template change
  const handleTemplateChange = (templateId) => {
    setSelectedTemplate(templateId);
    saveGuestSession({ selectedTemplate: templateId });
  };

  // Handle download - prompt login for guests
  const handleDownload = () => {
    if (isGuest || !user) {
      // Store current state and mark pending download
      saveGuestSession({
        generatedResume: resumeData,
        selectedTemplate: selectedTemplate,
        pendingDownload: true,
      });
      
      // Redirect to login with return URL
      navigate("/login", { 
        state: { 
          returnUrl: "/resume/guest-edit",
          message: "Please sign in to download your resume. Your work has been saved." 
        } 
      });
    } else {
      // User is authenticated, trigger download directly
      handleDownloadNow();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col items-center justify-center gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={40} />
        <p className="text-gray-400 text-sm">Loading your resume...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white">
      {/* Header */}
      <div className="bg-white/5 border-b border-white/10 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(isGuest ? "/" : "/dashboard")}
            className="flex items-center gap-1.5 text-gray-400 hover:text-white text-xs font-semibold transition-all"
          >
            <ArrowLeft size={14} /> {isGuest ? "Home" : "Dashboard"}
          </button>
          <div className="h-5 w-px bg-white/10" />
          {isGuest ? (
            <span className="text-xs font-bold text-[#7BC4BE]">Guest Mode</span>
          ) : (
            <span className="text-xs font-bold text-emerald-400">Signed In</span>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          {isGuest ? (
            <button
              onClick={() => navigate("/login", { state: { returnUrl: "/resume/guest-edit" } })}
              className="px-3 py-1.5 bg-white/10 hover:bg-white/15 text-white rounded-lg text-xs font-semibold transition-all"
            >
              Sign In
            </button>
          ) : (
            <button
              onClick={() => {
                // Save to backend if authenticated
                alert("Resume saved to your account.");
              }}
              className="px-3 py-1.5 bg-white/10 hover:bg-white/15 text-white rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5"
            >
              <Save size={12} /> Save to Account
            </button>
          )}
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
          >
            <Download size={14} /> Download PDF
          </button>
        </div>
      </div>

      {/* Step Indicator */}
      <ResumeFlowHeader 
        step={step}
        onBack={() => {
          if (step === "export") setStep("ats");
          else if (step === "ats") setStep("editor");
          else if (step === "editor") setStep("templates");
          else if (step === "templates") navigate(isGuest ? "/" : "/dashboard");
        }}
        onExit={() => {
          if (window.confirm("Return to home? Your changes are saved locally.")) {
            navigate(isGuest ? "/" : "/dashboard");
          }
        }}
      />

      {/* Main Content */}
      <div className="flex h-[calc(100vh-120px)]">
        {step === "editor" && (
          <ResumeEditor
            data={resumeData}
            template={selectedTemplate}
            onChange={handleDataChange}
            onChangeTemplate={(templateId) => {
              setSelectedTemplate(templateId);
              saveGuestSession({ selectedTemplate: templateId });
            }}
            onBack={() => setStep("templates")}
            onNext={() => setStep("ats")}
          />
        )}
        
        {step === "templates" && (
          <TemplateSelection
            resumeData={resumeData}
            selectedTemplate={selectedTemplate}
            onSelect={(id) => {
              handleTemplateChange(id);
              setStep("editor");
            }}
            onBack={() => setStep("editor")}
          />
        )}
        
        {step === "ats" && (
          <ATSReview
            data={resumeData}
            template={selectedTemplate}
            onChange={(improvedData) => {
              setResumeData(improvedData);
              setStep("editor");
            }}
            onBack={() => setStep("editor")}
            onNext={() => setStep("export")}
          />
        )}
        
        {step === "export" && (
          <ExportDownload
            data={resumeData}
            template={selectedTemplate}
            onExit={() => setStep("editor")}
          />
        )}
      </div>

      {/* Guest Mode Banner */}
      {isGuest && (
        <div className="fixed bottom-0 left-0 right-0 bg-[#FAD07A]/10 border-t border-[#FAD07A]/30 px-6 py-3 flex items-center justify-between z-50">
          <div className="flex items-center gap-2">
            <Save size={14} className="text-[#FAD07A]" />
            <span className="text-xs text-[#FAD07A]">
              Your resume is saved locally. Sign in to download or save to your account.
            </span>
          </div>
          <button
            onClick={() => navigate("/login", { state: { returnUrl: "/resume/guest-edit" } })}
            className="px-4 py-1.5 bg-[#FAD07A] hover:bg-[#FAD07A]/80 text-[#1A2B2A] rounded-lg text-xs font-bold transition-all"
          >
            Sign In
          </button>
        </div>
      )}
    </div>
  );
}
