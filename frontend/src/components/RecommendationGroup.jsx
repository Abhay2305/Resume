import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  Briefcase,
  GraduationCap,
  Wrench,
  FolderGit2,
  Award,
  Shield,
  Paintbrush,
  Mail,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import { useState } from "react";

const sectionConfig = [
  { key: "summary_rules", label: "Professional Summary", icon: FileText, color: "text-[#7BC4BE]", bg: "bg-[#7BC4BE]/15" },
  { key: "experience_rules", label: "Work Experience", icon: Briefcase, color: "text-amber-400", bg: "bg-amber-500/15" },
  { key: "skills_rules", label: "Technical Skills", icon: Wrench, color: "text-emerald-400", bg: "bg-emerald-500/15" },
  { key: "education_rules", label: "Education", icon: GraduationCap, color: "text-blue-400", bg: "bg-blue-500/15" },
  { key: "projects_rules", label: "Projects", icon: FolderGit2, color: "text-purple-400", bg: "bg-purple-500/15" },
  { key: "certifications_rules", label: "Certifications", icon: Award, color: "text-rose-400", bg: "bg-rose-500/15" },
  { key: "ats_rules", label: "ATS Optimization", icon: Shield, color: "text-emerald-400", bg: "bg-emerald-500/15" },
  { key: "formatting_rules", label: "Formatting", icon: Paintbrush, color: "text-orange-400", bg: "bg-orange-500/15" },
  { key: "cover_letter_rules", label: "Cover Letter", icon: Mail, color: "text-cyan-400", bg: "bg-cyan-500/15" },
];

function parseCitations(citations) {
  if (!citations) return [];
  if (Array.isArray(citations)) return citations;
  try {
    const parsed = JSON.parse(citations);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [citations];
  }
}

function countRecommendations(context) {
  let count = 0;
  sectionConfig.forEach(({ key }) => {
    if (context[key]) count++;
  });
  return count;
}

export default function RecommendationGroup({ context, retrieval }) {
  const [expandedSections, setExpandedSections] = useState({});

  if (!context) return null;

  const citations = parseCitations(context.citations);
  const sectionCount = countRecommendations(context);
  const totalRules = context.total_rules || retrieval?.total_rules_retrieved || 0;

  const toggleSection = (key) => {
    setExpandedSections((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Summary header */}
      <div className="bg-gradient-to-r from-[#7BC4BE]/10 to-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-2xl p-5">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 rounded-xl bg-[#7BC4BE]/20 flex items-center justify-center">
            <Sparkles size={18} className="text-[#7BC4BE]" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              Your AI Resume Recommendations
            </h3>
            <p className="text-[11px] text-gray-400">
              {totalRules} personalized recommendations across {sectionCount} resume sections
            </p>
          </div>
        </div>

        {retrieval && (
          <div className="flex items-center gap-4 text-[10px] text-gray-500">
            {retrieval.processing_time_ms && (
              <span>Analyzed in {retrieval.processing_time_ms}ms</span>
            )}
            <span>Strategy: {retrieval.retrieval_strategy}</span>
          </div>
        )}
      </div>

      {/* Section groups */}
      <div className="space-y-3">
        {sectionConfig.map(({ key, label, icon: Icon, color, bg }) => {
          const rules = context[key];
          if (!rules) return null;

          const isExpanded = expandedSections[key];
          const rulePreview = rules.length > 120 ? rules.substring(0, 120) + "..." : rules;
          const ruleLines = rules.split("\n").filter((l) => l.trim());

          return (
            <motion.div
              key={key}
              layout
              className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden"
            >
              <button
                onClick={() => toggleSection(key)}
                className="w-full flex items-center justify-between p-5 hover:bg-white/[0.02] transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center`}>
                    <Icon size={15} className={color} />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">{label}</h4>
                    <p className="text-[10px] text-gray-500 mt-0.5">
                      {ruleLines.length} recommendation{ruleLines.length !== 1 ? "s" : ""}
                    </p>
                  </div>
                </div>
                <div className="text-gray-400">
                  {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                </div>
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 pb-5 pt-0">
                      <div className="text-[11px] text-gray-300 leading-relaxed whitespace-pre-wrap bg-white/[0.03] rounded-xl p-4 border border-white/5 max-h-64 overflow-y-auto">
                        {rules}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {!isExpanded && (
                <div className="px-5 pb-4 -mt-1">
                  <p className="text-[10px] text-gray-500 leading-relaxed line-clamp-2">
                    {rulePreview}
                  </p>
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Citations */}
      {citations.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
          <h4 className="text-xs font-bold text-white mb-3 flex items-center gap-2">
            <span className="w-5 h-5 rounded bg-[#7BC4BE]/15 flex items-center justify-center">
              <span className="text-[10px] text-[#7BC4BE] font-bold">
                {citations.length}
              </span>
            </span>
            Knowledge Sources Referenced
          </h4>
          <div className="space-y-1.5">
            {citations.map((cite, i) => (
              <div
                key={i}
                className="text-[11px] text-gray-400 bg-white/[0.03] rounded-lg px-3 py-2 border border-white/5"
              >
                {cite}
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
