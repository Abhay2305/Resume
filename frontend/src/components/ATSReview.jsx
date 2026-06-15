import React, { useState, useEffect } from "react";
import { COLORS } from "../utils/constants";
import { Check, AlertTriangle, Sparkles, ChevronRight, RefreshCw, Star, Info } from "lucide-react";
import { api } from "../services/api";
import ResumePreview from "./ResumePreview";

export default function ATSReview({ data, template, resumeId, onChange, onBack, onNext }) {
  const [score, setScore] = useState(0);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isFixing, setIsFixing] = useState(false);
  const [fixed, setFixed] = useState(false);

  const runAnalysis = async () => {
    try {
      setLoading(true);
      const res = await api.analyzeATS(resumeId);
      setAnalysis(res);
      setScore(res.score);
    } catch (err) {
      console.error("Failed to run ATS analysis:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      runAnalysis();
    }
  }, [resumeId]);

  const categories = analysis ? [
    { label: "Section Completeness", val: Math.round((analysis.details.completeness?.score / 15) * 100) || 0 },
    { label: "Action Verbs Usage", val: Math.round((analysis.details.action_verbs?.score / 20) * 100) || 0 },
    { label: "Keyword Density", val: Math.round((analysis.details.keywords?.score / 20) * 100) || 0 },
    { label: "Readability & Length", val: Math.round((analysis.details.length?.score / 15) * 100) || 0 },
  ] : [
    { label: "Keyword Matching", val: 50 },
    { label: "Formatting & Style", val: 50 },
    { label: "Section Structure", val: 50 },
    { label: "Readability & Flow", val: 50 }
  ];

  const suggestions = analysis ? analysis.recommendations.map((rec, i) => ({
    id: `rec-${i}`,
    title: rec,
    desc: "Adhering to this recommendation will enhance your ATS compatibility.",
    resolved: false
  })) : [];

  // Simulates AI optimization
  const handleAutoFix = async () => {
    setIsFixing(true);
    try {
      // Improve the professional summary via AI autofix
      const summaryText = data.summary || "";
      const res = await api.improveText(summaryText, "autofix", "summary");
      
      // Update parent data
      const updated = {
        ...data,
        summary: res.improved_text
      };
      
      // Save changes to backend
      const payload = Object.keys(updated).map((key, idx) => ({
        section_type: key,
        content: updated[key],
        position: idx
      }));
      await api.saveResumeSections(resumeId, payload);
      onChange(updated);
      
      // Re-run analysis
      const newAnalysis = await api.analyzeATS(resumeId);
      setAnalysis(newAnalysis);
      setScore(newAnalysis.score);
      setFixed(true);
    } catch (err) {
      alert("Autofix failed: " + err.message);
    } finally {
      setIsFixing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 flex flex-col items-center justify-center gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={36} />
        <p className="text-gray-500 text-xs">Evaluating document structures and keyword density...</p>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col bg-gray-50">
      
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden h-[calc(100vh-120px)]">
        
        {/* Left Panel: ATS Review Scorecard (Col span 5) */}
        <div className="col-span-1 lg:col-span-5 flex flex-col bg-white border-r h-full overflow-y-auto p-6" style={{ borderColor: COLORS.border }}>
          
          {/* Header */}
          <div className="flex items-center justify-between border-b pb-4 mb-6" style={{ borderColor: COLORS.border }}>
            <div className="flex flex-col gap-1">
              <h2 className="serif text-xl text-gray-900 leading-tight">ATS Compatibility Audit</h2>
              <p className="text-xs text-gray-500 font-light">Real-time resume assessment for recruiter tracking systems.</p>
            </div>
            <div className="p-2 rounded-lg bg-green-50 border border-green-100 flex items-center justify-center">
              <Check size={18} className="text-green-500" />
            </div>
          </div>

          {/* Overall score gauge card */}
          <div className="bg-gray-50 rounded-2xl border p-5 flex items-center justify-around gap-6 mb-6" style={{ borderColor: COLORS.border }}>
            {/* Circle Score Gauge */}
            <div className="relative w-28 h-28 flex items-center justify-center">
              {/* Outer SVG ring */}
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="56"
                  cy="56"
                  r="48"
                  stroke={COLORS.ivory}
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="56"
                  cy="56"
                  r="48"
                  stroke={score > 85 ? COLORS.tealDeep : score > 70 ? COLORS.teal : COLORS.amber}
                  strokeWidth="8"
                  fill="transparent"
                  strokeDasharray="301.6"
                  strokeDashoffset={301.6 - (301.6 * score) / 100}
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center">
                <span className="serif text-3xl font-bold text-gray-900 leading-none">{score}</span>
                <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider mt-0.5">SCORE</span>
              </div>
            </div>

            {/* Score Text Description */}
            <div className="flex flex-col gap-1.5 flex-1">
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">VERDICT</span>
              <span className="text-sm font-semibold text-gray-900">
                {score > 90 ? "🚀 Outstanding Readiness" : score > 75 ? "📈 Good Compatibility" : "⚠️ Needs Improvement"}
              </span>
              <p className="text-xs text-gray-500 font-light leading-relaxed">
                {score > 90
                  ? "Your resume matches standard ATS criteria and is optimized for recruiters."
                  : "Making minor changes will double your chances of passing automated screens."}
              </p>
            </div>
          </div>

          {/* AI Optimization Assist Strip */}
          {!fixed && (
            <div className="bg-gradient-to-r from-amber-50 to-orange-50 border rounded-2xl p-4 mb-6 flex flex-col gap-3.5 relative overflow-hidden" style={{ borderColor: "rgba(246, 178, 51, 0.3)" }}>
              <div className="flex items-start gap-2.5">
                <div className="p-1.5 rounded-lg bg-[#FAD07A] text-[#D4920F] shrink-0">
                  <Sparkles size={16} />
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-semibold text-gray-800 flex items-center gap-1">
                    <span>AI Resume Optimizer</span>
                    <span className="text-[9px] bg-amber-200 text-amber-800 font-bold px-1.5 py-0.5 rounded-full">PRO</span>
                  </span>
                  <p className="text-[11px] text-gray-600 font-light leading-relaxed">
                    Auto-apply industry keywords and quantify achievements instantly to maximize your score.
                  </p>
                </div>
              </div>

              <button
                onClick={handleAutoFix}
                disabled={isFixing}
                className="w-full py-2 bg-gradient-to-r from-[#F6B233] to-[#D4920F] hover:from-[#D4920F] hover:to-[#F6B233] text-white rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 cursor-pointer shadow-sm select-none"
              >
                {isFixing ? (
                  <>
                    <RefreshCw size={12} className="animate-spin" />
                    <span>Applying Keywords & Metrics...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={12} />
                    <span>Auto-Optimize with AI (+15 points)</span>
                  </>
                )}
              </button>
            </div>
          )}

          {fixed && (
            <div className="bg-[#7BC4BE]/10 border rounded-2xl p-4 mb-6 flex items-start gap-3 border-[#7BC4BE]/40 animate-[checkPop_0.4s_ease-out]">
              <div className="p-1.5 rounded-lg bg-[#7BC4BE] text-white shrink-0">
                <Star size={16} fill="white" />
              </div>
              <div className="flex flex-col gap-0.5">
                <span className="text-xs font-semibold text-[#2D7A74]">✓ Optimized successfully</span>
                <p className="text-[11px] text-gray-600 font-light leading-relaxed">
                  Measurable metrics and structural tags successfully injected! Score boosted.
                </p>
              </div>
            </div>
          )}

          {/* Breakdown Categories */}
          <div className="flex flex-col gap-3 mb-6">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Breakdown Categories</span>
            <div className="grid grid-cols-2 gap-4">
              {categories.map((cat, idx) => (
                <div key={idx} className="flex flex-col gap-1">
                  <div className="flex justify-between items-center text-[11px]">
                    <span className="text-gray-600 font-medium">{cat.label}</span>
                    <span className="font-semibold text-gray-900">{cat.val}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-1000 ease-out"
                      style={{
                        width: `${cat.val}%`,
                        backgroundColor: cat.val > 90 ? COLORS.tealDeep : COLORS.teal
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Detailed Suggestions Checkbox List */}
          <div className="flex flex-col gap-3">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Audit Checklist</span>
            <div className="flex flex-col gap-3">
              {suggestions.map((s) => (
                <div
                  key={s.id}
                  className={`p-3 border-2 rounded-xl flex items-start gap-2.5 transition-all duration-300 ${
                    s.resolved ? "bg-green-50/20 border-green-100" : "bg-white border-gray-100"
                  }`}
                >
                  <div className="mt-0.5">
                    {s.resolved ? (
                      <div className="w-4 h-4 rounded-full bg-green-500 flex items-center justify-center text-white">
                        <Check size={10} strokeWidth={4} />
                      </div>
                    ) : (
                      <AlertTriangle size={14} className="text-amber-500" />
                    )}
                  </div>
                  <div className="flex flex-col gap-0.5">
                    <span className={`text-xs font-semibold ${s.resolved ? "text-green-800 line-through" : "text-gray-800"}`}>
                      {s.title}
                    </span>
                    <span className="text-[10px] text-gray-500 font-light leading-relaxed">
                      {s.desc}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Panel: Resume live preview (Col span 7) */}
        <div className="col-span-1 lg:col-span-7 bg-[#FFFDF8]/40 overflow-y-auto p-8 lg:p-12 flex justify-center items-start h-full">
          <div className="w-full max-w-[760px] sticky top-4">
            <ResumePreview data={data} template={template} />
          </div>
        </div>

      </div>

      {/* Editor Footer / Control Bar */}
      <footer className="h-14 bg-white border-t px-6 flex items-center justify-between shrink-0" style={{ borderColor: COLORS.border }}>
        <button
          onClick={onBack}
          className="flex items-center gap-1 text-xs font-semibold hover:opacity-80 transition-opacity"
          style={{ color: COLORS.textMid }}
        >
          <span>← Back to Editor</span>
        </button>

        <button
          onClick={onNext}
          className="btn-hero py-2 px-5 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold transition-all duration-300 cursor-pointer shadow-md select-none"
          style={{
            background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`,
            boxShadow: "0 4px 12px rgba(75, 158, 152, 0.25)",
            color: "white"
          }}
        >
          <span>Continue to Export</span>
          <ChevronRight size={14} />
        </button>
      </footer>

    </div>
  );
}
