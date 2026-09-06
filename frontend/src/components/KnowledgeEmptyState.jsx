import { BookOpen, FileText, Search, Sparkles } from "lucide-react";

const icons = {
  documents: BookOpen,
  rules: FileText,
  search: Search,
  default: Sparkles,
};

const messages = {
  documents: {
    title: "No Knowledge Sources Yet",
    description:
      "The AI engine hasn't ingested any writing standards yet. Knowledge sources include guidelines from Harvard, MIT, Yale, and ATS optimization guides.",
  },
  rules: {
    title: "No Recommendations Found",
    description:
      "No recommendations match your current filters. Try adjusting your search or browse all suggestions.",
  },
  search: {
    title: "No Results Found",
    description: "No recommendations match your search. Try different keywords.",
  },
  context: {
    title: "No Recommendations Yet",
    description:
      "Run a gap analysis first, then load your personalized recommendations to see AI-powered suggestions for your resume.",
  },
  retrieval: {
    title: "Get Your Recommendations",
    description:
      "Enter a Gap Analysis ID to receive personalized writing recommendations tailored to your target role.",
  },
  default: {
    title: "Nothing to show yet",
    description: "Start by loading your knowledge sources or running a gap analysis.",
  },
};

export default function KnowledgeEmptyState({ type = "default" }) {
  const Icon = icons[type] || icons.default;
  const msg = messages[type] || messages.default;

  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mb-4">
        <Icon size={28} className="text-gray-500" />
      </div>
      <h3 className="text-sm font-bold text-white mb-1">{msg.title}</h3>
      <p className="text-xs text-gray-500 max-w-sm leading-relaxed">
        {msg.description}
      </p>
    </div>
  );
}
