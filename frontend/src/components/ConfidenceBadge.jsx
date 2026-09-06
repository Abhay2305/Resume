export default function ConfidenceBadge({ confidence, size = "sm" }) {
  const pct = Math.round((confidence || 0) * 100);

  let colorClass = "bg-gray-500/15 text-gray-400 border-gray-500/20";
  if (pct >= 80) colorClass = "bg-emerald-500/15 text-emerald-400 border-emerald-500/20";
  else if (pct >= 60) colorClass = "bg-[#7BC4BE]/15 text-[#7BC4BE] border-[#7BC4BE]/20";
  else if (pct >= 40) colorClass = "bg-amber-500/15 text-amber-400 border-amber-500/20";

  if (size === "lg") {
    return (
      <div className="flex items-center gap-2">
        <div className="h-2 flex-1 max-w-[140px] bg-white/5 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${pct}%`,
              background: pct >= 80
                ? "linear-gradient(90deg, #34d399, #10b981)"
                : pct >= 60
                ? "linear-gradient(90deg, #7BC4BE, #4A9E98)"
                : "linear-gradient(90deg, #F6B233, #D4920F)",
            }}
          />
        </div>
        <span className="text-xs font-bold text-white">{pct}%</span>
      </div>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${colorClass}`}
    >
      {pct}%
    </span>
  );
}
