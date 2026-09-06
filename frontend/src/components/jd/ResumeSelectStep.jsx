import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Upload,
  ChevronRight,
  ArrowLeft,
  ArrowRight,
  Loader2,
  RefreshCw,
  Check,
  ClipboardPaste,
} from "lucide-react";
import { api } from "../../services/api";

export default function ResumeSelectStep({ onNext, onBack, loading }) {
  const [mode, setMode] = useState("existing");
  const [resumes, setResumes] = useState([]);
  const [resumesLoading, setResumesLoading] = useState(true);
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [resumeText, setResumeText] = useState("");
  const [resumeTextLoading, setResumeTextLoading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    (async () => {
      setResumesLoading(true);
      try {
        const res = await api.resumes.list();
        setResumes(Array.isArray(res) ? res : []);
      } catch (err) {
        console.error("Failed to load resumes:", err);
      } finally {
        setResumesLoading(false);
      }
    })();
  }, []);

  const handleSelectResume = async (resumeId) => {
    setSelectedResumeId(resumeId);
    setResumeTextLoading(true);
    try {
      const resume = await api.resumes.get(resumeId);
      // Combine sections into plain text
      const sections = resume?.sections || [];
      const text = sections
        .map((s) => {
          if (typeof s.content === "string") return s.content;
          if (Array.isArray(s.content)) {
            return s.content
              .map((item) => {
                if (typeof item === "string") return item;
                if (typeof item === "object") {
                  return Object.values(item).filter(Boolean).join(" ");
                }
                return "";
              })
              .join("\n");
          }
          if (typeof s.content === "object") {
            return JSON.stringify(s.content, null, 2);
          }
          return "";
        })
        .filter(Boolean)
        .join("\n\n");
      setResumeText(text || "");
    } catch (err) {
      console.error("Failed to load resume:", err);
    } finally {
      setResumeTextLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setResumeText(ev.target.result);
    };
    reader.readAsText(file);
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setResumeText(text);
    } catch {
      // Clipboard API may fail
    }
  };

  const handleSubmit = () => {
    if (resumeText.trim()) {
      onNext(resumeText.trim(), selectedResumeId);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-16 h-16 bg-[#FAD07A]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileText className="text-[#FAD07A]" size={28} />
        </div>
        <h3 className="text-xl font-bold text-white">Select Your Resume</h3>
        <p className="text-sm text-gray-400 mt-2 max-w-md mx-auto">
          Choose an existing resume to tailor, or upload/paste a new one.
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="flex justify-center gap-2">
        <button
          onClick={() => setMode("existing")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            mode === "existing"
              ? "bg-[#7BC4BE] text-[#1A2B2A]"
              : "bg-white/5 text-gray-400 hover:bg-white/10"
          }`}
        >
          <FileText size={14} />
          Existing Resume
        </button>
        <button
          onClick={() => setMode("upload")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            mode === "upload"
              ? "bg-[#7BC4BE] text-[#1A2B2A]"
              : "bg-white/5 text-gray-400 hover:bg-white/10"
          }`}
        >
          <Upload size={14} />
          Upload / Paste
        </button>
      </div>

      {/* Existing Resumes */}
      {mode === "existing" && (
        <div className="space-y-3">
          {resumesLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="animate-spin text-[#7BC4BE]" size={24} />
            </div>
          ) : resumes.length === 0 ? (
            <div className="text-center py-12 bg-white/5 rounded-xl border border-white/10">
              <FileText size={32} className="mx-auto text-gray-600 mb-3" />
              <p className="text-sm text-gray-400">No resumes found</p>
              <p className="text-xs text-gray-500 mt-1">
                Create a resume first, or upload one below.
              </p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
              {resumes.map((resume) => (
                <button
                  key={resume.id}
                  onClick={() => handleSelectResume(resume.id)}
                  className={`w-full flex items-center justify-between p-4 rounded-xl border transition-all text-left ${
                    selectedResumeId === resume.id
                      ? "bg-[#7BC4BE]/10 border-[#7BC4BE]/30"
                      : "bg-white/5 border-white/10 hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                        selectedResumeId === resume.id
                          ? "bg-[#7BC4BE]/20"
                          : "bg-white/10"
                      }`}
                    >
                      <FileText
                        size={14}
                        className={
                          selectedResumeId === resume.id
                            ? "text-[#7BC4BE]"
                            : "text-gray-400"
                        }
                      />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-white truncate">
                        {resume.title || "Untitled Resume"}
                      </p>
                      <p className="text-[10px] text-gray-500">
                        {resume.updated_at
                          ? new Date(resume.updated_at).toLocaleDateString()
                          : "No date"}
                      </p>
                    </div>
                  </div>
                  {selectedResumeId === resume.id ? (
                    <Check size={14} className="text-[#7BC4BE] shrink-0" />
                  ) : (
                    <ChevronRight size={14} className="text-gray-500 shrink-0" />
                  )}
                </button>
              ))}
            </div>
          )}

          {/* Show resume text preview if selected */}
          {selectedResumeId && resumeText && (
            <div className="bg-white/5 rounded-xl border border-white/10 p-4">
              <p className="text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-2">
                Resume Preview
              </p>
              <div className="text-xs text-gray-300 max-h-[150px] overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {resumeText.substring(0, 500)}
                {resumeText.length > 500 && "..."}
              </div>
            </div>
          )}

          {resumeTextLoading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="animate-spin text-[#7BC4BE]" size={18} />
              <span className="text-xs text-gray-400 ml-2">Loading resume content...</span>
            </div>
          )}
        </div>
      )}

      {/* Upload / Paste */}
      {mode === "upload" && (
        <div className="space-y-4">
          <div className="relative">
            <textarea
              rows={10}
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume content here...

Example:
John Doe
Software Engineer | john@email.com | (555) 123-4567

Experience:
Senior Software Engineer | Google | 2020-Present
- Led development of microservices architecture
- Improved system performance by 40%

Education:
B.S. Computer Science | Stanford University | 2018"
              className="w-full bg-white/5 border border-white/10 rounded-xl py-4 px-4 text-white text-sm focus:outline-none focus:border-[#7BC4BE] transition-colors resize-none"
            />
            <button
              onClick={handlePaste}
              className="absolute top-3 right-3 px-3 py-1.5 bg-white/10 hover:bg-white/15 rounded-lg text-[10px] text-gray-400 hover:text-white font-semibold transition-all"
            >
              <ClipboardPaste size={12} className="inline mr-1" />
              Paste
            </button>
          </div>

          {/* File Upload */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-white/10 hover:border-[#7BC4BE]/50 rounded-xl p-6 text-center cursor-pointer transition-colors"
          >
            <Upload size={24} className="mx-auto text-gray-500 mb-2" />
            <p className="text-xs text-gray-400">
              {resumeText ? "File loaded — click to replace" : "Or click to upload a .txt file"}
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf,.doc,.docx"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>

          {resumeText && (
            <p className="text-[10px] text-gray-500 text-right">
              {resumeText.length.toLocaleString()} characters
            </p>
          )}
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center pt-4 border-t border-white/10">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 px-4 py-2 text-gray-400 hover:text-white text-xs font-semibold transition-all"
        >
          <ArrowLeft size={14} />
          Back
        </button>
        <button
          onClick={handleSubmit}
          disabled={!resumeText.trim() || loading}
          className="flex items-center gap-2 px-6 py-3 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              Processing...
            </>
          ) : (
            <>
              Analyze Resume
              <ArrowRight size={14} />
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}
