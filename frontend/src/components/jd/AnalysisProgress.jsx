import { motion } from "framer-motion";
import {
  Check,
  Loader2,
  FileText,
  BookOpen,
  Search,
  Key,
  Lightbulb,
  Sparkles,
  Shield,
  RotateCcw,
  AlertTriangle,
  XCircle,
  Minus,
} from "lucide-react";

const PIPELINE_STEPS = [
  {
    id: "understanding_jd",
    label: "Understanding Job Description",
    icon: FileText,
    description: "Extracting requirements and keywords",
  },
  {
    id: "reading_resume",
    label: "Reading Resume",
    icon: BookOpen,
    description: "Analyzing your experience and skills",
  },
  {
    id: "finding_gaps",
    label: "Finding Missing Skills",
    icon: Search,
    description: "Identifying areas for improvement",
  },
  {
    id: "matching_ats",
    label: "Matching ATS Keywords",
    icon: Key,
    description: "Optimizing for applicant tracking systems",
  },
  {
    id: "applying_best_practices",
    label: "Applying Resume Best Practices",
    icon: Lightbulb,
    description: "Applying approved writing standards",
  },
  {
    id: "generating_resume",
    label: "Generating Tailored Resume",
    icon: Sparkles,
    description: "Creating personalized content",
  },
  {
    id: "reviewing",
    label: "Reviewing Suggestions",
    icon: Shield,
    description: "Validating quality and accuracy",
  },
];

const NON_FATAL_STEP_IDS = new Set(["applying_best_practices", "reviewing"]);

export default function AnalysisProgress({
  currentStep,
  completedSteps,
  error,
  onRetry,
  stageTimings = {},
  stageErrors = {},
  stageStatuses = {},
}) {
  // Derive step status (backward compatible with old props)
  const getStepStatus = (stepId) => {
    if (stageStatuses[stepId]) return stageStatuses[stepId];
    if (completedSteps.includes(stepId)) return "completed";
    if (currentStep === stepId) return "running";
    return "pending";
  };

  // Compute total time from all stage timings
  const totalTime = Object.values(stageTimings).reduce((sum, t) => sum + (typeof t === "number" ? t : 0), 0);

  // Collect non-fatal warnings
  const nonFatalWarnings = [];
  for (const step of PIPELINE_STEPS) {
    if (NON_FATAL_STEP_IDS.has(step.id) && getStepStatus(step.id) === "failed") {
      nonFatalWarnings.push({ step: step.label, message: stageErrors[step.id] || "Stage failed" });
    }
  }

  // Determine overall pipeline status
  const failedSteps = PIPELINE_STEPS.filter((s) => getStepStatus(s.id) === "failed");
  const hasFatalFailure = failedSteps.some((s) => !NON_FATAL_STEP_IDS.has(s.id));
  const hasNonFatalFailure = failedSteps.some((s) => NON_FATAL_STEP_IDS.has(s.id));
  const allDone = PIPELINE_STEPS.every((s) => {
    const st = getStepStatus(s.id);
    return st === "completed" || st === "failed" || st === "skipped";
  });
  const isRunning = !allDone && !error;

  let pipelineStatusText = "";
  if (error && hasFatalFailure) {
    const fatalStep = failedSteps.find((s) => !NON_FATAL_STEP_IDS.has(s.id));
    pipelineStatusText = `Failed at "${fatalStep?.label || "unknown step"}"`;
  } else if (allDone && hasFatalFailure) {
    pipelineStatusText = "Failed";
  } else if (allDone && hasNonFatalFailure) {
    pipelineStatusText = `Completed with warnings in ${(totalTime / 1000).toFixed(1)}s`;
  } else if (allDone) {
    pipelineStatusText = `Completed in ${(totalTime / 1000).toFixed(1)}s`;
  } else if (isRunning) {
    pipelineStatusText = `${completedSteps.length} of ${PIPELINE_STEPS.length} steps completed`;
  }
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="text-center">
        <div className="w-16 h-16 bg-[#7BC4BE]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Sparkles className="text-[#7BC4BE] animate-pulse" size={28} />
        </div>
        <h3 className="text-xl font-bold text-white">Analyzing Your Resume</h3>
        <p className="text-sm text-gray-400 mt-2 max-w-md mx-auto">
          Our AI is tailoring your resume to match the job description. This may take a moment.
        </p>
      </div>

      {/* Progress Steps */}
      <div className="space-y-3">
        {PIPELINE_STEPS.map((step, index) => {
          const Icon = step.icon;
          const status = getStepStatus(step.id);
          const isCompleted = status === "completed";
          const isCurrent = status === "running";
          const isFailed = status === "failed";
          const isSkipped = status === "skipped";
          const timing = stageTimings[step.id];
          const stageError = stageErrors[step.id];
          const isNonFatal = NON_FATAL_STEP_IDS.has(step.id) && isFailed;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className={`flex items-center gap-4 p-4 rounded-xl border transition-all ${
                isCompleted
                  ? "bg-emerald-500/10 border-emerald-500/20"
                  : isCurrent
                  ? "bg-[#7BC4BE]/10 border-[#7BC4BE]/30"
                  : isFailed
                  ? isNonFatal
                    ? "bg-amber-500/10 border-amber-500/20"
                    : "bg-rose-500/10 border-rose-500/20"
                  : isSkipped
                  ? "bg-white/5 border-white/10 opacity-60"
                  : "bg-white/5 border-white/10"
              }`}
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
                  isCompleted
                    ? "bg-emerald-500/20"
                    : isCurrent
                    ? "bg-[#7BC4BE]/20"
                    : isFailed
                    ? isNonFatal
                      ? "bg-amber-500/20"
                      : "bg-rose-500/20"
                    : "bg-white/10"
                }`}
              >
                {isCompleted ? (
                  <Check size={18} className="text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 size={18} className="text-[#7BC4BE] animate-spin" />
                ) : isFailed ? (
                  isNonFatal ? (
                    <AlertTriangle size={18} className="text-amber-400" />
                  ) : (
                    <XCircle size={18} className="text-rose-400" />
                  )
                ) : isSkipped ? (
                  <Minus size={18} className="text-gray-500" />
                ) : (
                  <Icon size={18} className="text-gray-500" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p
                  className={`text-sm font-semibold ${
                    isCompleted
                      ? "text-emerald-400"
                      : isCurrent
                      ? "text-white"
                      : isFailed
                      ? isNonFatal
                        ? "text-amber-400"
                        : "text-rose-400"
                      : "text-gray-500"
                  }`}
                >
                  {step.label}
                </p>
                <p
                  className={`text-[11px] mt-0.5 ${
                    isCompleted
                      ? "text-emerald-400/70"
                      : isCurrent
                      ? "text-gray-400"
                      : isFailed
                      ? "text-gray-400"
                      : "text-gray-600"
                  }`}
                >
                  {isFailed && stageError ? stageError : step.description}
                </p>
              </div>
              <div className="flex items-center gap-3 shrink-0">
                {timing != null && (
                  <span className="text-[10px] text-gray-500 tabular-nums">
                    {(timing / 1000).toFixed(1)}s
                  </span>
                )}
                {isCompleted && (
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                    Done
                  </span>
                )}
                {isCurrent && (
                  <span className="text-[10px] font-bold text-[#7BC4BE] uppercase tracking-wider">
                    Processing
                  </span>
                )}
                {isFailed && isNonFatal && (
                  <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider">
                    Warning
                  </span>
                )}
                {isFailed && !isNonFatal && (
                  <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">
                    Failed
                  </span>
                )}
                {isSkipped && (
                  <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">
                    Skipped
                  </span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Non-Fatal Warning Banner */}
      {nonFatalWarnings.length > 0 && !error && (
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
          <p className="text-xs font-bold text-amber-400 mb-1">Pipeline completed with warnings</p>
          {nonFatalWarnings.map((w) => (
            <p key={w.step} className="text-[11px] text-gray-400">
              {w.step}: {w.message}
            </p>
          ))}
        </div>
      )}

      {/* Error State (fatal failures) */}
      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-4">
          <p className="text-xs font-bold text-rose-400 mb-1">Analysis Failed</p>
          <p className="text-[11px] text-gray-400 mb-3">{error}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 rounded-lg text-[11px] font-semibold transition-all"
            >
              <RotateCcw size={12} />
              Retry
            </button>
          )}
        </div>
      )}

      {/* Progress Bar */}
      <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${
            hasFatalFailure
              ? "bg-gradient-to-r from-rose-500 to-rose-400"
              : "bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98]"
          }`}
          initial={{ width: "0%" }}
          animate={{
            width: `${((completedSteps.length + (currentStep ? 1 : 0)) / PIPELINE_STEPS.length) * 100}%`,
          }}
          transition={{ duration: 0.5 }}
        />
      </div>

      <p className="text-center text-[11px] text-gray-500">
        {pipelineStatusText}
      </p>
    </motion.div>
  );
}
