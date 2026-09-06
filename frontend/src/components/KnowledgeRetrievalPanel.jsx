import { useState } from "react";
import { Zap, Loader2, CheckCircle, AlertTriangle, Sparkles } from "lucide-react";

export default function KnowledgeRetrievalPanel({ onRetrieve, loading, result, error }) {
  const [gapAnalysisId, setGapAnalysisId] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (gapAnalysisId.trim()) {
      onRetrieve(gapAnalysisId.trim());
    }
  };

  return (
    <div className="space-y-4">
      {/* Input form */}
      <form
        onSubmit={handleSubmit}
        className="bg-gradient-to-r from-[#7BC4BE]/10 to-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 rounded-xl bg-[#7BC4BE]/20 flex items-center justify-center">
            <Sparkles size={18} className="text-[#7BC4BE]" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              Get AI Resume Recommendations
            </h3>
            <p className="text-[11px] text-gray-400">
              Enter your Gap Analysis ID to receive personalized writing suggestions.
            </p>
          </div>
        </div>

        <div className="flex gap-3 mt-4">
          <input
            type="text"
            value={gapAnalysisId}
            onChange={(e) => setGapAnalysisId(e.target.value)}
            placeholder="Paste your Gap Analysis ID here..."
            className="flex-1 bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] transition-colors"
          />
          <button
            type="submit"
            disabled={!gapAnalysisId.trim() || loading}
            className="px-5 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 size={14} className="animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Zap size={14} />
                Get Recommendations
              </>
            )}
          </button>
        </div>
      </form>

      {/* Result */}
      {result && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle size={16} className="text-emerald-400" />
            <span className="text-xs font-bold text-emerald-400">
              Recommendations Generated
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-3">
            <div>
              <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
                Writing Rules Matched
              </p>
              <p className="text-lg font-bold text-white">
                {result.total_rules}
              </p>
            </div>
            <div>
              <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
                Analysis ID
              </p>
              <p className="text-xs text-gray-300 truncate">
                {result.retrieval_id}
              </p>
            </div>
          </div>
          {result.message && (
            <p className="text-[11px] text-gray-400 mt-3">{result.message}</p>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle size={16} className="text-rose-400" />
            <span className="text-xs font-bold text-rose-400">
              Analysis Failed
            </span>
          </div>
          <p className="text-[11px] text-gray-400">{error}</p>
        </div>
      )}
    </div>
  );
}
