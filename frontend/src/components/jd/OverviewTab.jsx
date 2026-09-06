import { motion } from "framer-motion";
import {
  Target,
  Wrench,
  Cpu,
  Briefcase,
  GraduationCap,
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";

const SCORE_LABELS = {
  overall_match_score: { label: "Overall Match", icon: Target, color: "#7BC4BE" },
  skill_match_score: { label: "Skills", icon: Wrench, color: "#10b981" },
  technology_match_score: { label: "Technology", icon: Cpu, color: "#8b5cf6" },
  experience_match_score: { label: "Experience", icon: Briefcase, color: "#f59e0b" },
  education_match_score: { label: "Education", icon: GraduationCap, color: "#3b82f6" },
  certification_match_score: { label: "Certifications", icon: Shield, color: "#ef4444" },
  keyword_match_score: { label: "ATS Keywords", icon: TrendingUp, color: "#06b6d4" },
};

function ScoreRing({ score, size = 80, strokeWidth = 6, color }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  const getScoreColor = (s) => {
    if (s >= 80) return "#10b981";
    if (s >= 60) return "#f59e0b";
    if (s >= 40) return "#f97316";
    return "#ef4444";
  };

  const displayColor = color || getScoreColor(score);

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={displayColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-lg font-bold text-white">
          {Math.round(score)}%
        </span>
      </div>
    </div>
  );
}

function ScoreCard({ scoreKey, scoreValue, index }) {
  const config = SCORE_LABELS[scoreKey];
  if (!config || scoreValue == null) return null;

  const getScoreLevel = (s) => {
    if (s >= 80) return { label: "Strong", icon: CheckCircle, color: "text-emerald-400" };
    if (s >= 60) return { label: "Good", icon: TrendingUp, color: "text-amber-400" };
    if (s >= 40) return { label: "Fair", icon: AlertTriangle, color: "text-orange-400" };
    return { label: "Needs Work", icon: AlertTriangle, color: "text-rose-400" };
  };

  const level = getScoreLevel(scoreValue);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="bg-white/5 border border-white/10 rounded-2xl p-5 flex flex-col items-center"
    >
      <ScoreRing score={scoreValue} color={config.color} />
      <p className="text-sm font-bold text-white mt-3">{config.label}</p>
      <div className="flex items-center gap-1 mt-1">
        <level.icon size={10} className={level.color} />
        <span className={`text-[10px] font-semibold ${level.color}`}>
          {level.label}
        </span>
      </div>
    </motion.div>
  );
}

export default function OverviewTab({ scores, gaps }) {
  if (!scores) {
    return (
      <div className="text-center py-12">
        <Target size={32} className="mx-auto text-gray-600 mb-3" />
        <p className="text-sm text-gray-400">No match scores available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="bg-gradient-to-r from-[#7BC4BE]/10 to-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-2xl p-6">
        <div className="flex items-center gap-4">
          <ScoreRing
            score={scores.overall_match_score || 0}
            size={100}
            strokeWidth={8}
          />
          <div>
            <h4 className="text-lg font-bold text-white">Overall Match</h4>
            <p className="text-sm text-gray-400 mt-1">
              {(scores.overall_match_score || 0) >= 80
                ? "Your resume is well-aligned with this job description."
                : (scores.overall_match_score || 0) >= 60
                ? "Your resume has good potential with some improvements needed."
                : "Your resume needs significant tailoring for this role."}
            </p>
          </div>
        </div>
      </div>

      {/* Score Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {Object.entries(scores)
          .filter(([key]) => key !== "overall_match_score" && scores[key] != null)
          .map(([key, value], index) => (
            <ScoreCard key={key} scoreKey={key} scoreValue={value} index={index} />
          ))}
      </div>

      {/* Missing Items Summary */}
      {gaps && gaps.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
          <h4 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <AlertTriangle size={14} className="text-amber-400" />
            Key Gaps Identified
          </h4>
          <div className="space-y-2">
            {gaps.slice(0, 5).map((gap, i) => (
              <div
                key={i}
                className="flex items-center justify-between p-3 bg-white/[0.03] rounded-xl border border-white/5"
              >
                <span className="text-xs font-semibold text-gray-300 capitalize">
                  {gap.category}
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    (gap.match_score || 0) >= 70
                      ? "bg-emerald-500/15 text-emerald-400"
                      : (gap.match_score || 0) >= 40
                      ? "bg-amber-500/15 text-amber-400"
                      : "bg-rose-500/15 text-rose-400"
                  }`}
                >
                  {Math.round(gap.match_score || 0)}% match
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
