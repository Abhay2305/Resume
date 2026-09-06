import { Briefcase, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

function ExperienceEntry({ entry, index }) {
  const [expanded, setExpanded] = useState(true);

  const role = entry.role || entry.title || entry.position || "Role";
  const company = entry.company || entry.organization || "";
  const duration =
    entry.duration || entry.date_range || entry.period || "";
  const responsibilities =
    entry.responsibilities || entry.bullets || entry.description || [];
  const metrics = entry.metrics || entry.achievements || [];

  const hasResponsibilities = Array.isArray(responsibilities)
    ? responsibilities.length > 0
    : !!responsibilities;
  const hasMetrics = Array.isArray(metrics) ? metrics.length > 0 : !!metrics;

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className="w-3 h-3 bg-[#7BC4BE] rounded-full shrink-0 ring-4 ring-[#0F1E1E]" />
        {index < 20 && <div className="w-px flex-1 bg-white/10" />}
      </div>

      <div className="flex-1 pb-6">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full text-left flex items-start justify-between gap-3"
        >
          <div>
            <p className="text-sm font-bold text-white">{role}</p>
            {company && (
              <p className="text-xs text-[#7BC4BE] font-medium mt-0.5">
                {company}
              </p>
            )}
            {duration && (
              <p className="text-[11px] text-gray-500 mt-0.5">{duration}</p>
            )}
          </div>
          <div className="text-gray-500 mt-1 shrink-0">
            {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          </div>
        </button>

        {expanded && (
          <div className="mt-3 space-y-2">
            {hasResponsibilities && (
              <div>
                <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1.5">
                  Responsibilities
                </p>
                <ul className="space-y-1">
                  {(Array.isArray(responsibilities)
                    ? responsibilities
                    : [responsibilities]
                  ).map((item, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-xs text-gray-300"
                    >
                      <span className="text-[#7BC4BE] mt-1 shrink-0">•</span>
                      <span className="leading-relaxed">{String(item)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {hasMetrics && (
              <div>
                <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wider mb-1.5">
                  Key Metrics
                </p>
                <ul className="space-y-1">
                  {(Array.isArray(metrics) ? metrics : [metrics]).map(
                    (item, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2 text-xs text-gray-300"
                      >
                        <span className="text-amber-400 mt-1 shrink-0">★</span>
                        <span className="leading-relaxed">{String(item)}</span>
                      </li>
                    )
                  )}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ExperienceTimeline({ knowledge, parsedData }) {
  const entries =
    knowledge?.experience_summary ||
    parsedData?.experience_entries ||
    [];

  if (!entries || entries.length === 0) return null;

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
          <Briefcase size={20} className="text-[#7BC4BE]" />
        </div>
        <div>
          <h3 className="text-sm font-bold text-white">Experience</h3>
          <p className="text-[11px] text-gray-500 mt-0.5">
            {entries.length} position{entries.length !== 1 ? "s" : ""} found
          </p>
        </div>
      </div>

      <div>{entries.map((entry, i) => (
        <ExperienceEntry key={entry.id || i} entry={entry} index={i} />
      ))}</div>
    </div>
  );
}
