
import { motion } from "framer-motion";
import { Lightbulb, Tag, ArrowRight, BookOpen } from "lucide-react";

const priorityColors = {
  high: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  medium: "bg-[#7BC4BE]/15 text-[#7BC4BE] border-[#7BC4BE]/20",
  low: "bg-white/10 text-gray-400 border-white/10",
};

const stateColors = {
  ACTIVE: "bg-green-500/15 text-green-400 border-green-500/20",
  APPROVED: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  VERIFIED: "bg-yellow-500/15 text-yellow-400 border-yellow-500/20",
  DISCOVERED: "bg-gray-500/15 text-gray-400 border-gray-500/20",
  REJECTED: "bg-red-500/15 text-red-400 border-red-500/20",
};

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

export default function KnowledgeRuleCard({ rule, compact = false }) {
  const priorityKey = (rule.priority || "low").toLowerCase();
  const priorityClass = priorityColors[priorityKey] || priorityColors.low;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/[0.03] border border-white/5 rounded-xl p-4 hover:border-white/10 transition-colors"
    >
      {/* Badges row */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        {rule.state && (
          <span
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${stateColors[rule.state] || stateColors.DISCOVERED}`}
          >
            {rule.state}
          </span>
        )}
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${priorityClass}`}
        >
          {rule.priority || "low"}
        </span>
        <span
          className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getSourceBadgeClass(
            rule.source
          )}`}
        >
          {rule.source}
        </span>
        {rule.category && (
          <span className="text-[10px] text-gray-500 flex items-center gap-1">
            <Tag size={9} />
            {rule.category}
          </span>
        )}
        {rule.section_name && (
          <span className="text-[10px] text-gray-500 flex items-center gap-1">
            <BookOpen size={9} />
            {rule.section_name}
          </span>
        )}
        {rule.source_document && (
          <span className="text-[10px] text-gray-500">
            {rule.source_document}{rule.source_page ? ` p.${rule.source_page}` : ""}
          </span>
        )}
      </div>

      {/* Instruction */}
      <div className="flex items-start gap-2 mb-2">
        <Lightbulb size={12} className="text-amber-400 shrink-0 mt-0.5" />
        <p className="text-xs text-white leading-relaxed">{rule.instruction}</p>
      </div>

      {!compact && (
        <>
          {/* Reason */}
          {rule.reason && (
            <div className="flex items-start gap-2 mb-2 ml-5">
              <ArrowRight size={10} className="text-gray-500 shrink-0 mt-1" />
              <p className="text-[11px] text-gray-400 leading-relaxed">
                {rule.reason}
              </p>
            </div>
          )}

          {/* Examples */}
          {rule.examples && (
            <div className="ml-5 mt-2 bg-white/[0.03] rounded-lg px-3 py-2 border border-white/5">
              <p className="text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1">
                Examples
              </p>
              <p className="text-[11px] text-gray-300 leading-relaxed whitespace-pre-wrap">
                {rule.examples}
              </p>
            </div>
          )}
        </>
      )}

      {/* Confidence */}
      {rule.confidence != null && (
        <div className="flex items-center gap-2 mt-3 ml-5">
          <div className="h-1.5 flex-1 max-w-[120px] bg-white/5 rounded-full overflow-hidden">
            <div
              className="h-full bg-[#7BC4BE] rounded-full transition-all"
              style={{ width: `${Math.round(rule.confidence * 100)}%` }}
            />
          </div>
          <span className="text-[10px] text-gray-500">
            {Math.round(rule.confidence * 100)}%
          </span>
        </div>
      )}
    </motion.div>
  );
}
