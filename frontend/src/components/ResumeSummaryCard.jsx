import { FileText } from "lucide-react";

export default function ResumeSummaryCard({ knowledge, parsedData }) {
  const summary = knowledge?.summary || parsedData?.summary;

  if (!summary) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
          <FileText size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Professional Summary</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            Parsed career overview
          </p>
        </div>
      </div>

      <div className="bg-white/5 rounded-xl p-4 border border-white/5">
        <p className="text-xs text-gray-300 leading-relaxed whitespace-pre-line">
          {summary}
        </p>
      </div>
    </div>
  );
}
