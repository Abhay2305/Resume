import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FileText,
  ChevronDown,
  ChevronRight,
  Trash2,
  Clock,
  Shield,
  BookOpen,
} from "lucide-react";

const sourceColors = {
  Harvard: "bg-rose-500/15 text-rose-400 border-rose-500/20",
  MIT: "bg-red-500/15 text-red-400 border-red-500/20",
  Yale: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  ATS: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  Internal: "bg-[#7BC4BE]/15 text-[#7BC4BE] border-[#7BC4BE]/20",
};

function getSourceBadgeClass(source) {
  if (!source) return "bg-white/10 text-gray-400 border-white/10";
  const key = Object.keys(sourceColors).find((k) =>
    source.toLowerCase().includes(k.toLowerCase())
  );
  return sourceColors[key] || "bg-white/10 text-gray-400 border-white/10";
}

export default function KnowledgeDocumentCard({ document, onDelete }) {
  const [expanded, setExpanded] = useState(false);

  const confidencePct = Math.round((document.confidence || 0) * 100);

  return (
    <motion.div
      layout
      className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <div
        className="p-5 cursor-pointer hover:bg-white/[0.02] transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center text-[#7BC4BE] shrink-0">
              <FileText size={18} />
            </div>
            <div className="min-w-0">
              <h3 className="text-sm font-bold text-white truncate">
                {document.name}
              </h3>
              <div className="flex items-center gap-2 mt-1 flex-wrap">
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getSourceBadgeClass(
                    document.source
                  )}`}
                >
                  {document.source}
                </span>
                <span className="text-[10px] text-gray-500 flex items-center gap-1">
                  <BookOpen size={10} />
                  v{document.version}
                </span>
                <span className="text-[10px] text-gray-500 flex items-center gap-1">
                  <Shield size={10} />
                  {confidencePct}%
                </span>
                {document.total_rules != null && (
                  <span className="text-[10px] text-gray-500">
                    {document.total_rules} rules
                  </span>
                )}
                {document.total_sections != null && (
                  <span className="text-[10px] text-gray-500">
                    {document.total_sections} sections
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(document.id);
                }}
                className="p-1.5 rounded-lg text-gray-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
                title="Delete document"
              >
                <Trash2 size={14} />
              </button>
            )}
            <div className="p-1.5 rounded-lg bg-white/5 text-gray-400">
              {expanded ? (
                <ChevronDown size={14} />
              ) : (
                <ChevronRight size={14} />
              )}
            </div>
          </div>
        </div>

        {/* Meta row */}
        <div className="flex items-center gap-4 mt-3 ml-13">
          <span className="text-[10px] text-gray-500 flex items-center gap-1">
            <Clock size={10} />
            {new Date(document.created_at).toLocaleDateString()}
          </span>
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

      {/* Expanded content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 border-t border-white/5 pt-4">
              {document.description && (
                <p className="text-xs text-gray-400 mb-4 leading-relaxed">
                  {document.description}
                </p>
              )}

              {document.document_type && (
                <div className="mb-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">
                    Type:{" "}
                  </span>
                  <span className="text-[10px] text-gray-300">
                    {document.document_type}
                  </span>
                </div>
              )}

              {/* Sections placeholder - sections are internal to backend */}
              <div className="bg-white/[0.03] rounded-xl p-4 border border-white/5">
                <p className="text-[10px] text-gray-500 text-center">
                  Document sections and rules are managed by the backend
                  intelligence engine. Use the Rules tab to browse all rules.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
