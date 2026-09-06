import { RefreshCw } from "lucide-react";

export default function ResumeLoading({ variant = "cards", count = 3 }) {
  if (variant === "spinner") {
    return (
      <div className="flex flex-col items-center justify-center py-16 gap-4">
        <RefreshCw className="animate-spin text-[#7BC4BE]" size={32} />
        <p className="text-gray-400 text-xs">Loading resume data...</p>
      </div>
    );
  }

  if (variant === "timeline") {
    return (
      <div className="space-y-6">
        {Array.from({ length: count }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div className="w-3 h-3 bg-white/10 rounded-full animate-pulse" />
              <div className="w-px h-full bg-white/10" />
            </div>
            <div className="flex-1 bg-white/5 border border-white/10 rounded-2xl p-5 space-y-3">
              <div className="h-4 w-32 bg-white/10 rounded animate-pulse" />
              <div className="h-3 w-24 bg-white/10 rounded animate-pulse" />
              <div className="h-3 w-full bg-white/10 rounded animate-pulse" />
              <div className="h-3 w-3/4 bg-white/10 rounded animate-pulse" />
            </div>
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
              <div className="h-3 w-24 bg-white/10 rounded animate-pulse" />
            </div>
          </div>
          <div className="space-y-2">
            <div className="h-3 w-full bg-white/10 rounded animate-pulse" />
            <div className="h-3 w-5/6 bg-white/10 rounded animate-pulse" />
          </div>
        </div>
      ))}
    </div>
  );
}
