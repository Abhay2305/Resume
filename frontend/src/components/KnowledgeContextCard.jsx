import { motion } from "framer-motion";
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
  Clock,
  Link2,
} from "lucide-react";

const sectionConfig = [
  { key: "summary_rules", label: "Summary Rules", icon: FileText, color: "text-[#7BC4BE]" },
  { key: "experience_rules", label: "Experience Rules", icon: Briefcase, color: "text-amber-400" },
  { key: "skills_rules", label: "Skills Rules", icon: Wrench, color: "text-emerald-400" },
  { key: "education_rules", label: "Education Rules", icon: GraduationCap, color: "text-blue-400" },
  { key: "projects_rules", label: "Projects Rules", icon: FolderGit2, color: "text-purple-400" },
  { key: "certifications_rules", label: "Certifications Rules", icon: Award, color: "text-rose-400" },
  { key: "ats_rules", label: "ATS Rules", icon: Shield, color: "text-emerald-400" },
  { key: "formatting_rules", label: "Formatting Rules", icon: Paintbrush, color: "text-orange-400" },
  { key: "cover_letter_rules", label: "Cover Letter Rules", icon: Mail, color: "text-cyan-400" },
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

export default function KnowledgeContextCard({ context, retrieval }) {
  if (!context) return null;

  const citations = parseCitations(context.citations);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Retrieval info */}
      {retrieval && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-6">
              <div>
                <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
                  Total Rules
                </p>
                <p className="text-lg font-bold text-white">
                  {context.total_rules || retrieval.total_rules_retrieved}
                </p>
              </div>
              <div>
                <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
                  Strategy
                </p>
                <p className="text-xs text-gray-300">
                  {retrieval.retrieval_strategy}
                </p>
              </div>
              {retrieval.processing_time_ms && (
                <div>
                  <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
                    Processing Time
                  </p>
                  <p className="text-xs text-gray-300 flex items-center gap-1">
                    <Clock size={10} />
                    {retrieval.processing_time_ms}ms
                  </p>
                </div>
              )}
            </div>
            <div className="text-[10px] text-gray-500">
              ID: <span className="font-mono text-gray-400">{context.id}</span>
            </div>
          </div>
        </div>
      )}

      {/* Section rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sectionConfig.map(({ key, label, icon: Icon, color }) => {
          const rules = context[key];
          if (!rules) return null;

          return (
            <div
              key={key}
              className="bg-white/5 border border-white/10 rounded-2xl p-5"
            >
              <div className="flex items-center gap-2 mb-3">
                <Icon size={14} className={color} />
                <h4 className="text-xs font-bold text-white">{label}</h4>
              </div>
              <div className="text-[11px] text-gray-300 leading-relaxed whitespace-pre-wrap bg-white/[0.03] rounded-xl p-3 border border-white/5 max-h-48 overflow-y-auto">
                {rules}
              </div>
            </div>
          );
        })}
      </div>

      {/* Citations */}
      {citations.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Link2 size={14} className="text-[#7BC4BE]" />
            <h4 className="text-xs font-bold text-white">Citations</h4>
          </div>
          <div className="space-y-1.5">
            {citations.map((cite, i) => (
              <div
                key={i}
                className="text-[11px] text-gray-400 bg-white/[0.03] rounded-lg px-3 py-2 border border-white/5 font-mono"
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
