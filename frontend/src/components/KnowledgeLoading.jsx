import { RefreshCw } from "lucide-react";

export default function KnowledgeLoading({ variant = "cards", count = 3 }) {
  if (variant === "spinner") {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={32} />
        <p className="text-gray-400 text-xs">Analyzing your resume...</p>
      </div>
    );
  }

  if (variant === "rules") {
    return (
      <div className="space-y-3">
        {Array.from({ length: count }).map((_, i) => (
          <div
            key={i}
            className="bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3"
          >
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 bg-amber-500/15 rounded-lg animate-pulse" />
              <div className="h-4 w-24 bg-white/10 rounded animate-pulse" />
              <div className="h-5 w-14 bg-white/10 rounded-full animate-pulse" />
              <div className="h-5 w-10 bg-white/10 rounded-full animate-pulse" />
            </div>
            <div className="h-4 w-3/4 bg-white/10 rounded animate-pulse" />
            <div className="h-3 w-full bg-white/10 rounded animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-white/5 border border-white/10 rounded-2xl p-6 space-y-4"
        >
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-[#7BC4BE]/15 rounded-xl animate-pulse shrink-0" />
            <div className="space-y-2 flex-1">
              <div className="h-5 w-40 bg-white/10 rounded animate-pulse" />
              <div className="flex gap-2">
                <div className="h-5 w-16 bg-white/10 rounded-full animate-pulse" />
                <div className="h-5 w-12 bg-white/10 rounded-full animate-pulse" />
              </div>
            </div>
          </div>
          <div className="flex gap-4 ml-13">
            <div className="h-3 w-20 bg-white/10 rounded animate-pulse" />
            <div className="h-3 w-24 bg-white/10 rounded animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );
}
