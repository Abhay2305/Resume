const sourceConfig = {
  Harvard: {
    label: "Harvard",
    color: "bg-rose-500/15 text-rose-400 border-rose-500/20",
    dot: "bg-rose-400",
  },
  MIT: {
    label: "MIT",
    color: "bg-red-500/15 text-red-400 border-red-500/20",
    dot: "bg-red-400",
  },
  Yale: {
    label: "Yale",
    color: "bg-blue-500/15 text-blue-400 border-blue-500/20",
    dot: "bg-blue-400",
  },
  ATS: {
    label: "ATS Guide",
    color: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
    dot: "bg-emerald-400",
  },
  Internal: {
    label: "AI Engine",
    color: "bg-[#7BC4BE]/15 text-[#7BC4BE] border-[#7BC4BE]/20",
    dot: "bg-[#7BC4BE]",
  },
};

function getSourceConfig(source) {
  if (!source) return { label: source || "Unknown", color: "bg-white/10 text-gray-400 border-white/10", dot: "bg-gray-400" };
  const key = Object.keys(sourceConfig).find((k) =>
    source.toLowerCase().includes(k.toLowerCase())
  );
  return sourceConfig[key] || { label: source, color: "bg-white/10 text-gray-400 border-white/10", dot: "bg-gray-400" };
}

export default function SourceChip({ source, showDot = true, size = "sm" }) {
  const config = getSourceConfig(source);

  if (size === "lg") {
    return (
      <span
        className={`inline-flex items-center gap-2 text-xs font-bold px-3 py-1 rounded-full border ${config.color}`}
      >
        {showDot && (
          <span className={`w-2 h-2 rounded-full ${config.dot}`} />
        )}
        {config.label}
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-[10px] font-bold px-2 py-0.5 rounded-full border ${config.color}`}
    >
      {showDot && (
        <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      )}
      {config.label}
    </span>
  );
}
