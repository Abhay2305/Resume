import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Lightbulb,
  ArrowRight,
  ChevronDown,
  ChevronRight,
  Sparkles,
  BookOpen,
} from "lucide-react";

const SECTION_LABELS = {
  summary: "Professional Summary",
  experience: "Work Experience",
  skills: "Technical Skills",
  education: "Education",
  projects: "Projects",
  certifications: "Certifications",
  achievements: "Achievements",
  cover_letter: "Cover Letter",
  ats: "ATS Optimization",
  formatting: "Formatting",
};

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

const PRIORITY_STYLES = {
  high: "bg-amber-500/15 text-amber-400",
  medium: "bg-[#7BC4BE]/15 text-[#7BC4BE]",
  low: "bg-white/10 text-gray-400",
};

function SuggestionCard({ recommendation, index }) {
  const [expanded, setExpanded] = useState(false);
  const sectionKey = (recommendation.category || "").toLowerCase().replace(/\s+/g, "_");
  const sectionLabel =
    SECTION_LABELS[sectionKey] || recommendation.category || "General";
  const sectionColor = SECTION_COLORS[sectionKey] || "text-gray-400";

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
          <div className="flex items-start gap-2.5 flex-1 min-w-0">
            <div className="w-7 h-7 rounded-lg bg-amber-500/15 flex items-center justify-center shrink-0 mt-0.5">
              <Lightbulb size={13} className="text-amber-400" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className={`text-[10px] font-bold ${sectionColor}`}>
                  {sectionLabel}
                </span>
                {recommendation.priority && (
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      PRIORITY_STYLES[recommendation.priority] || "bg-white/10 text-gray-400"
                    }`}
                  >
                    {recommendation.priority}
                  </span>
                )}
              </div>
              <p className="text-xs text-white leading-relaxed">
                {recommendation.description || recommendation.action}
              </p>
            </div>
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
            <div className="px-4 pb-4 pt-0 ml-[38px] space-y-3">
              {/* Why this matters */}
              {recommendation.description && recommendation.action && (
                <div className="flex items-start gap-2">
                  <ArrowRight size={10} className="text-gray-500 shrink-0 mt-1" />
                  <div>
                    <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-0.5">
                      Action
                    </p>
                    <p className="text-[11px] text-gray-300 leading-relaxed">
                      {recommendation.action}
                    </p>
                  </div>
                </div>
              )}

              {/* Target */}
              {recommendation.target_item && (
                <div className="flex items-start gap-2">
                  <ArrowRight size={10} className="text-gray-500 shrink-0 mt-1" />
                  <div>
                    <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-0.5">
                      Target
                    </p>
                    <p className="text-[11px] text-gray-300 leading-relaxed">
                      {recommendation.target_item}
                    </p>
                  </div>
                </div>
              )}

              {/* Apply Button (Future) */}
              <button
                disabled
                className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-semibold text-gray-500 cursor-not-allowed"
              >
                <Sparkles size={10} />
                Apply (Coming Soon)
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function SuggestionsTab({ recommendations, knowledgeContext }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="text-center py-12">
        <Lightbulb size={32} className="mx-auto text-gray-600 mb-3" />
        <p className="text-sm text-gray-400">No suggestions available</p>
        <p className="text-xs text-gray-500 mt-1">
          Suggestions will appear here once the analysis is complete.
        </p>
      </div>
    );
  }

  // Group by category
  const grouped = recommendations.reduce((acc, rec) => {
    const category = rec.category || "general";
    if (!acc[category]) acc[category] = [];
    acc[category].push(rec);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Knowledge Sources */}
      {knowledgeContext && knowledgeContext.citations && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-4">
          <h4 className="text-xs font-bold text-white mb-2 flex items-center gap-2">
            <BookOpen size={12} className="text-[#7BC4BE]" />
            Writing Standards Applied
          </h4>
          <div className="flex flex-wrap gap-2">
            {(Array.isArray(knowledgeContext.citations)
              ? knowledgeContext.citations
              : [knowledgeContext.citations]
            ).map((cite, i) => (
              <span
                key={i}
                className="text-[10px] text-gray-400 bg-white/[0.03] px-2.5 py-1 rounded-lg border border-white/5"
              >
                {cite}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations by Category */}
      {Object.entries(grouped).map(([category, recs]) => (
        <div key={category}>
          <h4 className="text-xs font-bold text-white mb-3 capitalize flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${
                SECTION_COLORS[category.toLowerCase().replace(/\s+/g, "_")]
                  ? "bg-current"
                  : "bg-gray-500"
              }`}
            />
            <span
              className={
                SECTION_COLORS[category.toLowerCase().replace(/\s+/g, "_")] ||
                "text-gray-400"
              }
            >
              {category.replace(/_/g, " ")}
            </span>
            <span className="text-[10px] text-gray-500 font-normal">
              ({recs.length} suggestion{recs.length !== 1 ? "s" : ""})
            </span>
          </h4>
          <div className="space-y-2">
            {recs.map((rec, i) => (
              <SuggestionCard key={rec.id || i} recommendation={rec} index={i} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
