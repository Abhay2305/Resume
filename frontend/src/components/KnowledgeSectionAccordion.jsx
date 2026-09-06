import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronRight, Hash } from "lucide-react";

export default function KnowledgeSectionAccordion({ section, children }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-white/5 rounded-xl overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-3 bg-white/[0.03] hover:bg-white/[0.05] transition-colors"
      >
        <div className="flex items-center gap-3">
          <Hash size={12} className="text-[#7BC4BE]" />
          <span className="text-xs font-semibold text-white">
            {section.name || section.category}
          </span>
          {section.rule_count != null && (
            <span className="text-[10px] text-gray-500 bg-white/5 px-2 py-0.5 rounded-full">
              {section.rule_count} rules
            </span>
          )}
        </div>
        <div className="text-gray-400">
          {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        </div>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 py-3 space-y-2">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
