import {
  FileText,
  Clock,
  Cpu,
  CalendarDays,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Archive,
} from "lucide-react";

const STATUS_CONFIG = {
  parsed: {
    label: "Parsed",
    icon: CheckCircle2,
    color: "text-emerald-400",
    bg: "bg-emerald-400/10",
    border: "border-emerald-400/20",
  },
  parsing: {
    label: "Parsing",
    icon: Loader2,
    color: "text-amber-400",
    bg: "bg-amber-400/10",
    border: "border-amber-400/20",
    animate: true,
  },
  pending: {
    label: "Pending",
    icon: Clock,
    color: "text-gray-400",
    bg: "bg-white/5",
    border: "border-white/10",
  },
  failed: {
    label: "Failed",
    icon: AlertCircle,
    color: "text-rose-400",
    bg: "bg-rose-400/10",
    border: "border-rose-400/20",
  },
  archived: {
    label: "Archived",
    icon: Archive,
    color: "text-gray-500",
    bg: "bg-white/5",
    border: "border-white/10",
  },
};

export default function ResumeOverviewCard({ profile }) {
  const status = STATUS_CONFIG[profile?.status] || STATUS_CONFIG.pending;
  const StatusIcon = status.icon;

  const formatDate = (dateStr) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatMs = (ms) => {
    if (ms == null) return "—";
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center">
            <FileText size={20} className="text-[#7BC4BE]" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              {profile?.title || "Untitled Resume"}
            </h3>
            <p className="text-[11px] text-gray-500 mt-0.5">
              Resume Overview
            </p>
          </div>
        </div>

        <div
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold ${status.color} ${status.bg} border ${status.border}`}
        >
          <StatusIcon
            size={12}
            className={status.animate ? "animate-spin" : ""}
          />
          {status.label}
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-1.5 mb-1">
            <CalendarDays size={12} className="text-gray-500" />
            <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Created
            </span>
          </div>
          <p className="text-xs text-white font-medium">
            {formatDate(profile?.created_at)}
          </p>
        </div>

        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-1.5 mb-1">
            <Clock size={12} className="text-gray-500" />
            <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Last Updated
            </span>
          </div>
          <p className="text-xs text-white font-medium">
            {formatDate(profile?.updated_at)}
          </p>
        </div>

        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-1.5 mb-1">
            <Cpu size={12} className="text-gray-500" />
            <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Parser Version
            </span>
          </div>
          <p className="text-xs text-white font-medium">
            {profile?.parser_version || "—"}
          </p>
        </div>

        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
          <div className="flex items-center gap-1.5 mb-1">
            <Clock size={12} className="text-gray-500" />
            <span className="text-[10px] text-gray-500 uppercase font-bold tracking-wider">
              Processing Time
            </span>
          </div>
          <p className="text-xs text-white font-medium">
            {formatMs(profile?.processing_time_ms)}
          </p>
        </div>
      </div>
    </div>
  );
}
