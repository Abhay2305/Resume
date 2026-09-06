
import { AlertTriangle, RefreshCw } from "lucide-react";

export default function KnowledgeErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-4">
        <AlertTriangle size={28} className="text-rose-400" />
      </div>
      <h3 className="text-sm font-bold text-white mb-1">Something went wrong</h3>
      <p className="text-xs text-gray-500 max-w-sm leading-relaxed mb-4">
        {message || "An unexpected error occurred while fetching data."}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white rounded-xl text-xs font-semibold transition-all flex items-center gap-2"
        >
          <RefreshCw size={14} />
          Retry
        </button>
      )}
    </div>
  );
}
