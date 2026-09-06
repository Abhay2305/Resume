import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mail,
  BarChart3,
  Sparkles,
  Target,
  X,
  Loader2,
  Copy,
  CheckCircle,
} from "lucide-react";
import { api } from "../../services/api";

const ACTIONS = [
  {
    id: "cover_letter",
    label: "Generate Cover Letter",
    icon: Mail,
    color: "text-[#7BC4BE]",
    bg: "bg-[#7BC4BE]/10",
    description: "Create a tailored cover letter for this job",
  },
  {
    id: "ats_optimize",
    label: "Optimize ATS Score",
    icon: BarChart3,
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    description: "Optimize your resume for applicant tracking systems",
  },
  {
    id: "bullets",
    label: "Improve Bullet Points",
    icon: Sparkles,
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    description: "Generate stronger achievement-focused bullet points",
  },
  {
    id: "tailor",
    label: "Tailor Resume",
    icon: Target,
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    description: "Fine-tune your resume for this specific role",
  },
];

function ActionModal({ action, jdText, resumeText, onClose }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [inputText, setInputText] = useState(
    action.id === "cover_letter" ? resumeText : ""
  );

  const handleExecute = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      let res;
      switch (action.id) {
        case "cover_letter":
          res = await api.career.generateCoverLetter({
            job_description: jdText,
            experience_summary: inputText || resumeText,
          });
          setResult(res?.data || res);
          break;
        case "ats_optimize":
          res = await api.career.optimizeForATS({
            content: inputText || resumeText,
            job_description: jdText,
          });
          setResult(res?.data || res);
          break;
        case "bullets":
          res = await api.career.generateBullets({
            responsibilities: jdText,
          });
          setResult(res?.data || res);
          break;
        case "tailor":
          res = await api.career.optimizeForATS({
            content: inputText || resumeText,
            job_description: jdText,
          });
          setResult(res?.data || res);
          break;
        default:
          break;
      }
    } catch (err) {
      setError(err.message || "Failed to execute action");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    const text = typeof result === "string" ? result : JSON.stringify(result, null, 2);
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API may fail
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-lg bg-[#16302F] border border-white/10 rounded-2xl p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start mb-5">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl ${action.bg} flex items-center justify-center`}>
              <action.icon size={18} className={action.color} />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">{action.label}</h3>
              <p className="text-[11px] text-gray-400 mt-0.5">{action.description}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-white p-1"
          >
            <X size={18} />
          </button>
        </div>

        {/* Input for certain actions */}
        {(action.id === "ats_optimize" || action.id === "bullets") && (
          <div className="mb-4">
            <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">
              {action.id === "ats_optimize" ? "Resume Content" : "Current Bullet Points (optional)"}
            </label>
            <textarea
              rows={4}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={
                action.id === "ats_optimize"
                  ? "Paste your resume content here..."
                  : "Paste your current bullet points..."
              }
              className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs focus:outline-none focus:border-[#7BC4BE]"
            />
          </div>
        )}

        {/* Execute Button */}
        {!result && (
          <button
            onClick={handleExecute}
            disabled={loading}
            className="w-full py-3 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles size={14} />
                Generate
              </>
            )}
          </button>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 bg-rose-500/10 border border-rose-500/20 rounded-xl p-4">
            <p className="text-xs text-rose-400">{error}</p>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-4 space-y-3">
            <div className="bg-white/5 border border-white/10 rounded-xl p-4 max-h-[300px] overflow-y-auto">
              <pre className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed">
                {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
              </pre>
            </div>
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-semibold text-gray-400 hover:text-white transition-all"
            >
              {copied ? (
                <>
                  <CheckCircle size={12} className="text-emerald-400" />
                  Copied
                </>
              ) : (
                <>
                  <Copy size={12} />
                  Copy to Clipboard
                </>
              )}
            </button>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}

export default function QuickActions({ jdText, resumeText }) {
  const [activeAction, setActiveAction] = useState(null);

  return (
    <>
      <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
        <h4 className="text-xs font-bold text-white mb-4 flex items-center gap-2">
          <Sparkles size={14} className="text-[#7BC4BE]" />
          Quick Actions
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {ACTIONS.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.id}
                onClick={() => setActiveAction(action)}
                className="flex flex-col items-center gap-2 p-4 bg-white/[0.03] border border-white/5 rounded-xl hover:bg-white/[0.06] hover:border-white/10 transition-all text-center"
              >
                <div className={`w-10 h-10 rounded-xl ${action.bg} flex items-center justify-center`}>
                  <Icon size={18} className={action.color} />
                </div>
                <span className="text-[11px] font-semibold text-gray-300">
                  {action.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <AnimatePresence>
        {activeAction && (
          <ActionModal
            action={activeAction}
            jdText={jdText}
            resumeText={resumeText}
            onClose={() => setActiveAction(null)}
          />
        )}
      </AnimatePresence>
    </>
  );
}
