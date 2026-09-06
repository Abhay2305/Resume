import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Shield,
  AlertTriangle,
  CheckCircle,
  FileText,
} from "lucide-react";


const SECTION_COLORS = {
  summary: "text-[#7BC4BE]",
  experience: "text-amber-400",
  skills: "text-emerald-400",
  education: "text-blue-400",
  projects: "text-purple-400",
  certifications: "text-rose-400",
  achievements: "text-orange-400",
  cover_letter: "text-cyan-400",
  ats: "text-emerald-400",
  formatting: "text-orange-400",
};

const RISK_COLORS = {
  low: "bg-emerald-500/15 text-emerald-400",
  medium: "bg-amber-500/15 text-amber-400",
  high: "bg-orange-500/15 text-orange-400",
  critical: "bg-rose-500/15 text-rose-400",
};

function ChangeCard({ change, index }) {
  const [expanded, setExpanded] = useState(false);
  const sectionColor = SECTION_COLORS[change.section] || "text-gray-400";
  const riskColor = RISK_COLORS[change.risk_level] || "bg-white/10 text-gray-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className="bg-white/[0.03] border border-white/5 rounded-xl overflow-hidden hover:border-white/10 transition-colors"
    >
      <div
        className="p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className={`text-[10px] font-bold uppercase ${sectionColor}`}>
                {change.section || "General"}
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${riskColor}`}>
                {change.risk_level || "low"} risk
              </span>
              {change.confidence != null && (
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  change.confidence >= 0.8
                    ? "bg-green-500/15 text-green-400"
                    : change.confidence >= 0.5
                    ? "bg-amber-500/15 text-amber-400"
                    : "bg-rose-500/15 text-rose-400"
                }`}>
                  {Math.round(change.confidence * 100)}% confidence
                </span>
              )}
            </div>
            <p className="text-xs text-gray-400 leading-relaxed">
              {change.description}
            </p>
          </div>
          <div className="p-1 rounded-lg bg-white/5 text-gray-400 shrink-0">
            {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-0 space-y-3">
              {/* Before / After */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-white/[0.03] rounded-xl p-3 border border-white/5">
                  <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-gray-500" />
                    Before
                  </p>
                  <p className="text-[11px] text-gray-300 leading-relaxed whitespace-pre-wrap">
                    {change.original_value || "—"}
                  </p>
                </div>
                <div className="bg-[#7BC4BE]/5 rounded-xl p-3 border border-[#7BC4BE]/10">
                  <p className="text-[10px] font-bold text-[#7BC4BE] uppercase tracking-wider mb-1.5 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#7BC4BE]" />
                    After
                  </p>
                  <p className="text-[11px] text-white leading-relaxed whitespace-pre-wrap">
                    {change.new_value || "—"}
                  </p>
                </div>
              </div>

              {/* Improvement Arrow */}
              <div className="flex items-center justify-center gap-2 text-[10px] text-gray-500">
                <ArrowRight size={12} className="text-[#7BC4BE]" />
                <span>{change.change_type || "modified"}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function ChangesTab({ changes, validation }) {
  if (!changes || changes.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText size={32} className="mx-auto text-gray-600 mb-3" />
        <p className="text-sm text-gray-400">No changes detected</p>
        <p className="text-xs text-gray-500 mt-1">
          The AI analysis will appear here once generated.
        </p>
      </div>
    );
  }

  // Group changes by section
  const grouped = changes.reduce((acc, change) => {
    const section = change.section || "general";
    if (!acc[section]) acc[section] = [];
    acc[section].push(change);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Validation Summary */}
      {validation && (
        <div className="bg-gradient-to-r from-[#7BC4BE]/10 to-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-2xl p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <Shield size={18} className="text-[#7BC4BE]" />
              <h4 className="text-sm font-bold text-white">Validation Summary</h4>
            </div>
            {validation.approved != null && (
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                  validation.approved
                    ? "bg-green-500/15 text-green-400"
                    : "bg-amber-500/15 text-amber-400"
                }`}
              >
                {validation.approved ? "APPROVED" : "PENDING"}
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="flex items-center gap-2">
              {validation.schema_valid ? (
                <CheckCircle size={12} className="text-emerald-400" />
              ) : (
                <AlertTriangle size={12} className="text-rose-400" />
              )}
              <span className="text-[11px] text-gray-300">Schema</span>
            </div>
            <div className="flex items-center gap-2">
              {validation.truth_valid ? (
                <CheckCircle size={12} className="text-emerald-400" />
              ) : (
                <AlertTriangle size={12} className="text-rose-400" />
              )}
              <span className="text-[11px] text-gray-300">Accuracy</span>
            </div>
            <div className="flex items-center gap-2">
              {validation.knowledge_valid ? (
                <CheckCircle size={12} className="text-emerald-400" />
              ) : (
                <AlertTriangle size={12} className="text-rose-400" />
              )}
              <span className="text-[11px] text-gray-300">Best Practices</span>
            </div>
            <div className="flex items-center gap-2">
              {validation.gap_valid ? (
                <CheckCircle size={12} className="text-emerald-400" />
              ) : (
                <AlertTriangle size={12} className="text-rose-400" />
              )}
              <span className="text-[11px] text-gray-300">Gap Coverage</span>
            </div>
          </div>
          {validation.overall_confidence != null && (
            <div className="mt-3 flex items-center gap-2">
              <Sparkles size={12} className="text-[#7BC4BE]" />
              <span className="text-[11px] text-gray-300">
                Overall Confidence:{" "}
                <span className="font-bold text-white">
                  {Math.round(validation.overall_confidence * 100)}%
                </span>
              </span>
            </div>
          )}
          {/* Warnings */}
          {validation.warnings && validation.warnings.length > 0 && (
            <div className="mt-3 space-y-1">
              {validation.warnings.map((warning, i) => (
                <div key={i} className="flex items-start gap-2 text-[11px] text-amber-400">
                  <AlertTriangle size={10} className="shrink-0 mt-0.5" />
                  <span>{warning}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Changes by Section */}
      {Object.entries(grouped).map(([section, sectionChanges]) => (
        <div key={section}>
          <h4 className="text-xs font-bold text-white mb-3 capitalize flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                SECTION_COLORS[section] ? "bg-current" : "bg-gray-500"
              }`}
              style={{
                color: SECTION_COLORS[section]
                  ? undefined
                  : undefined,
              }}
            />
            <span className={SECTION_COLORS[section] || "text-gray-400"}>
              {section.replace(/_/g, " ")}
            </span>
            <span className="text-[10px] text-gray-500 font-normal">
              ({sectionChanges.length} change{sectionChanges.length !== 1 ? "s" : ""})
            </span>
          </h4>
          <div className="space-y-2">
            {sectionChanges.map((change, i) => (
              <ChangeCard key={change.id || i} change={change} index={i} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
