import { motion } from "framer-motion";
import {
  BookOpen,
  Shield,
  FileText,
  TrendingUp,
  ChevronDown,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import SourceChip from "./SourceChip";
import ConfidenceBadge from "./ConfidenceBadge";

export default function InsightCard({ document }) {
  const [expanded, setExpanded] = useState(false);
  const confidencePct = Math.round((document.confidence || 0) * 100);

  const sourceFriendlyNames = {
    "Harvard Business Review": "Harvard Resume Standards",
    "MIT Career Guidelines": "MIT Career Writing Guide",
    "Yale Career Services": "Yale Professional Writing",
    "ATS Optimization Guide": "ATS Compliance Standards",
    Internal: "AI Writing Engine",
  };

  const friendlyName =
    sourceFriendlyNames[document.name] || document.name;

  const typeLabels = {
    guide: "Writing Guide",
    examples: "Example Collection",
    ats_guide: "ATS Compliance",
    book: "Reference Book",
  };

  return (
    <motion.div
      layout
      className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden hover:border-white/15 transition-colors"
    >
      <div
        className="p-5 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center text-[#7BC4BE] shrink-0">
              <BookOpen size={18} />
            </div>
            <div className="min-w-0">
              <h3 className="text-sm font-bold text-white truncate">
                {friendlyName}
              </h3>
              <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                <SourceChip source={document.source} />
                {document.document_type && (
                  <span className="text-[10px] text-gray-500">
                    {typeLabels[document.document_type] || document.document_type}
                  </span>
                )}
                <ConfidenceBadge confidence={document.confidence} />
              </div>
            </div>
          </div>
          <div className="p-1.5 rounded-lg bg-white/5 text-gray-400 shrink-0">
            {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </div>
        </div>

        <div className="flex items-center gap-4 mt-3 ml-13">
          {document.total_rules != null && (
            <span className="text-[10px] text-gray-500 flex items-center gap-1">
              <FileText size={10} />
              {document.total_rules} writing rules
            </span>
          )}
          {document.total_sections != null && (
            <span className="text-[10px] text-gray-500">
              {document.total_sections} sections
            </span>
          )}
          <span
            className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
              document.is_active
                ? "bg-emerald-500/10 text-emerald-400"
                : "bg-gray-500/10 text-gray-500"
            }`}
          >
            {document.is_active ? "ACTIVE" : "INACTIVE"}
          </span>
        </div>
      </div>

      {expanded && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          transition={{ duration: 0.2 }}
          className="overflow-hidden"
        >
          <div className="px-5 pb-5 border-t border-white/5 pt-4">
            {document.description && (
              <p className="text-xs text-gray-400 mb-3 leading-relaxed">
                {document.description}
              </p>
            )}
            <div className="flex items-center gap-4 text-[10px] text-gray-500">
              <span className="flex items-center gap-1">
                <Shield size={10} />
                Confidence: {confidencePct}%
              </span>
              <span className="flex items-center gap-1">
                <TrendingUp size={10} />
                Version {document.version}
              </span>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
