import { Sparkles, ArrowLeft, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function KnowledgeHeader({ onRefresh, loading }) {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate("/dashboard")}
          className="p-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <ArrowLeft size={16} />
        </button>
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#7BC4BE] to-[#4A9E98] flex items-center justify-center">
              <Sparkles size={16} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              AI Resume Insights
            </h1>
          </div>
          <p className="text-gray-400 text-xs mt-1">
            Personalized writing recommendations backed by Harvard, MIT, Yale, and ATS standards.
          </p>
        </div>
      </div>
      <button
        onClick={onRefresh}
        disabled={loading}
        className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white border border-white/10 rounded-xl text-xs font-semibold transition-all flex items-center gap-2 disabled:opacity-50"
      >
        <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
        Refresh
      </button>
    </div>
  );
}
