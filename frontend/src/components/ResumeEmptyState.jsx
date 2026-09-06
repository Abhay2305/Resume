import { FileText, Upload, AlertCircle } from "lucide-react";

const icons = {
  profiles: FileText,
  detail: AlertCircle,
  default: Upload,
};

const messages = {
  profiles: {
    title: "No Resumes Analyzed Yet",
    description:
      "Upload or paste your resume text to let the AI engine parse and extract structured intelligence from it.",
  },
  detail: {
    title: "Resume Not Found",
    description:
      "This resume profile doesn't exist or has been removed. Go back to the dashboard to try again.",
  },
  parse: {
    title: "Not Parsed Yet",
    description:
      "This resume hasn't been through the parsing pipeline yet. Click 'Parse Resume' to extract structured data.",
  },
  knowledge: {
    title: "Knowledge Not Built",
    description:
      "Resume knowledge hasn't been built yet. Parse the resume first to generate the canonical knowledge representation.",
  },
  entities: {
    title: "No Entities Extracted",
    description:
      "No skills, technologies, or other entities have been extracted yet. Parse the resume to extract entities.",
  },
  default: {
    title: "Nothing to show yet",
    description: "Parse your resume to see the extracted intelligence.",
  },
};

export default function ResumeEmptyState({ type = "default" }) {
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
