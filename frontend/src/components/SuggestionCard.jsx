import { motion } from "framer-motion";
import {
  Lightbulb,
  ArrowRight,
  Sparkles,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import SourceChip from "./SourceChip";
import ConfidenceBadge from "./ConfidenceBadge";

const sectionLabels = {
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

const sectionColors = {
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

function getSectionKey(rule) {
  if (rule.section_name) {
    const normalized = rule.section_name.toLowerCase().replace(/\s+/g, "_");
    const match = Object.keys(sectionLabels).find(
      (k) => k === normalized || normalized.includes(k)
    );
    if (match) return match;
  }
  if (rule.category) {
    const normalized = rule.category.toLowerCase().replace(/\s+/g, "_");
    const match = Object.keys(sectionLabels).find(
      (k) => k === normalized || normalized.includes(k)
    );
    if (match) return match;
  }
  return "other";
}

export default function SuggestionCard({ rule, compact = false }) {
  const [expanded, setExpanded] = useState(false);
  const sectionKey = getSectionKey(rule);
  const sectionLabel = sectionLabels[sectionKey] || rule.section_name || rule.category || "General";
  const sectionColor = sectionColors[sectionKey] || "text-gray-400";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/[0.03] border border-white/5 rounded-xl overflow-hidden hover:border-white/10 transition-colors"
    >
      {/* Main content */}
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
                <SourceChip source={rule.source} size="sm" />
                <ConfidenceBadge confidence={rule.confidence} />
              </div>
              <p className="text-xs text-white leading-relaxed">
                {rule.instruction}
              </p>
            </div>
          </div>
          <div className="p-1 rounded-lg bg-white/5 text-gray-400 shrink-0">
            {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </div>
        </div>
      </div>

      {/* Expanded details */}
      {expanded && !compact && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <div className="px-4 pb-4 pt-0 ml-[38px] space-y-3">
            {rule.reason && (
              <div className="flex items-start gap-2">
                <ArrowRight size={10} className="text-gray-500 shrink-0 mt-1" />
                <div>
                  <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-0.5">
                    Why this matters
                  </p>
                  <p className="text-[11px] text-gray-400 leading-relaxed">
                    {rule.reason}
                  </p>
                </div>
              </div>
            )}

            {rule.examples && (
              <div className="bg-white/[0.03] rounded-lg px-3 py-2.5 border border-white/5">
                <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1 flex items-center gap-1">
                  <Sparkles size={9} className="text-[#7BC4BE]" />
                  Example improvement
                </p>
                <p className="text-[11px] text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {rule.examples}
                </p>
              </div>
            )}

            {rule.priority && (
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-gray-500">Priority:</span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    rule.priority === "high"
                      ? "bg-amber-500/15 text-amber-400"
                      : rule.priority === "medium"
                      ? "bg-[#7BC4BE]/15 text-[#7BC4BE]"
                      : "bg-white/10 text-gray-400"
                  }`}
                >
                  {rule.priority}
                </span>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
