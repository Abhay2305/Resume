import { useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  FileText,
  Upload,
  ClipboardPaste,
  Sparkles,
  ArrowRight,
  Loader2,
} from "lucide-react";

export default function JDInputStep({ onNext, loading }) {
  const [jdText, setJdText] = useState("");
  const [inputMode, setInputMode] = useState("paste");
  const fileInputRef = useRef(null);

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      setJdText(ev.target.result);
    };
    reader.readAsText(file);
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setJdText(text);
    } catch {
      // Clipboard API may fail in some browsers
    }
  };

  const handleSubmit = () => {
    if (jdText.trim()) {
      onNext(jdText.trim());
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
        <div className="w-16 h-16 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <FileText className="text-[#7BC4BE]" size={28} />
        </div>
        <h3 className="text-xl font-bold text-white">Paste the Job Description</h3>
        <p className="text-sm text-gray-400 mt-2 max-w-md mx-auto">
          Copy and paste the job description you want to tailor your resume for, or upload a text file.
        </p>
      </div>

      {/* Input Mode Toggle */}
      <div className="flex justify-center gap-2">
        <button
          onClick={() => setInputMode("paste")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            inputMode === "paste"
              ? "bg-[#7BC4BE] text-[#1A2B2A]"
              : "bg-white/5 text-gray-400 hover:bg-white/10"
          }`}
        >
          <ClipboardPaste size={14} />
          Paste Text
        </button>
        <button
          onClick={() => setInputMode("upload")}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
            inputMode === "upload"
              ? "bg-[#7BC4BE] text-[#1A2B2A]"
              : "bg-white/5 text-gray-400 hover:bg-white/10"
          }`}
        >
          <Upload size={14} />
          Upload File
        </button>
      </div>

      {/* Input Area */}
      <div className="relative">
        {inputMode === "paste" ? (
          <div className="relative">
            <textarea
              rows={12}
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the full job description here...

Example:
We are looking for a Senior Software Engineer to join our team.

Requirements:
- 5+ years of experience in backend development
- Proficiency in Python, Go, or Java
- Experience with AWS, Docker, and Kubernetes
- Strong understanding of microservices architecture
- Excellent communication skills

Benefits:
- Competitive salary and equity
- Health, dental, and vision insurance
- Flexible work arrangements"
              className="w-full bg-white/5 border border-white/10 rounded-xl py-4 px-4 text-white text-sm focus:outline-none focus:border-[#7BC4BE] transition-colors resize-none"
            />
            <button
              onClick={handlePaste}
              className="absolute top-3 right-3 px-3 py-1.5 bg-white/10 hover:bg-white/15 rounded-lg text-[10px] text-gray-400 hover:text-white font-semibold transition-all"
            >
              Paste
            </button>
          </div>
        ) : (
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-white/10 hover:border-[#7BC4BE]/50 rounded-xl p-12 text-center cursor-pointer transition-colors"
          >
            <Upload size={32} className="mx-auto text-gray-500 mb-3" />
            <p className="text-sm text-gray-400">
              {jdText ? "File loaded — click to replace" : "Click to upload a .txt or .pdf file"}
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.pdf,.doc,.docx"
              onChange={handleFileUpload}
              className="hidden"
            />
            {jdText && (
              <p className="text-xs text-[#7BC4BE] mt-2">
                {jdText.length.toLocaleString()} characters loaded
              </p>
            )}
          </div>
        )}
      </div>

      {/* Character Count */}
      {jdText && (
        <div className="flex items-center justify-between text-[10px] text-gray-500">
          <span>{jdText.length.toLocaleString()} characters</span>
          <span className="flex items-center gap-1">
            <Sparkles size={10} className="text-[#7BC4BE]" />
            {jdText.split(/\s+/).filter(Boolean).length} words
          </span>
        </div>
      )}

      {/* Submit */}
      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={!jdText.trim() || loading}
          className="flex items-center gap-2 px-6 py-3 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 size={14} className="animate-spin" />
              Processing...
            </>
          ) : (
            <>
              Continue
              <ArrowRight size={14} />
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}
