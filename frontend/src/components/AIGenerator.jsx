import React, { useEffect, useState } from "react";
import { COLORS } from "../utils/constants";
import { Loader2, CheckCircle2, ChevronRight, HelpCircle } from "lucide-react";

export default function AIGenerator({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps = [
    { label: "Reading your background", desc: "Parsing experience, contact info, and skills." },
    { label: "Structuring resume sections", desc: "Grouping data into standard professional structures." },
    { label: "Optimizing wording", desc: "Applying strong action verbs and professional style." },
    { label: "Applying ATS-friendly formatting", desc: "Verifying layout keywords and metadata readability." },
    { label: "Preparing template-ready content", desc: "Injecting compiled data into the document engine." }
  ];

  const logs = [
    "Analyzing prompt structure...",
    "Extracted personal details successfully.",
    "Categorized 3 previous roles and responsibilities.",
    "Extracted key technical competencies.",
    "Formulating professional summary statement...",
    "Applying recruiter-grade phrasing models...",
    "Validating ATS keyword density...",
    "Aligning sections with optimal parsing order...",
    "Formatting content blocks for template injection...",
    "Complete! Building editor preview."
  ];

  const [activeLogs, setActiveLogs] = useState([]);

  useEffect(() => {
    // Step progression timer
    const stepInterval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1;
        }
        clearInterval(stepInterval);
        return prev;
      });
    }, 850);

    // Progress bar timer (0 to 100 over 4.2 seconds)
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev < 100) {
          return prev + 1;
        }
        clearInterval(progressInterval);
        return prev;
      });
    }, 42);

    // Log messages simulation timer
    const logInterval = setInterval(() => {
      setActiveLogs((prev) => {
        if (prev.length < logs.length) {
          return [...prev, logs[prev.length]];
        }
        clearInterval(logInterval);
        return prev;
      });
    }, 420);

    return () => {
      clearInterval(stepInterval);
      clearInterval(progressInterval);
      clearInterval(logInterval);
    };
  }, []);

  // When progress hits 100, trigger callback with a slight delay
  useEffect(() => {
    if (progress === 100) {
      const delay = setTimeout(() => {
        onComplete();
      }, 500);
      return () => clearTimeout(delay);
    }
  }, [progress, onComplete]);

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col justify-center items-center px-4" style={{ backgroundColor: COLORS.cream }}>
      <div className="w-full max-w-lg bg-white rounded-2xl border p-8 shadow-xl flex flex-col gap-6 relative overflow-hidden" style={{ borderColor: COLORS.border }}>
        {/* Shimmer accent line at top */}
        <div className="absolute top-0 left-0 right-0 h-1" style={{ background: `linear-gradient(90deg, ${COLORS.teal}, ${COLORS.amber}, ${COLORS.tealDark})`, backgroundSize: "200% auto", animation: "shimmer 3s linear infinite" }} />
        
        {/* Title */}
        <div className="text-center flex flex-col gap-1">
          <span className="text-xs font-bold uppercase tracking-widest text-[#4A9E98]">Prompt Resume AI</span>
          <h2 className="serif text-2xl text-gray-900">Structuring your resume</h2>
          <p className="text-xs text-gray-500 font-light">Please wait while our models format your information.</p>
        </div>

        {/* Progress Bar & Ring */}
        <div className="flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs font-semibold" style={{ color: COLORS.textMid }}>
            <span>Progress</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full h-2 rounded-full overflow-hidden" style={{ backgroundColor: COLORS.ivory }}>
            <div
              className="h-full rounded-full transition-all duration-300 ease-out"
              style={{
                width: `${progress}%`,
                background: `linear-gradient(90deg, ${COLORS.teal}, ${COLORS.tealDark})`
              }}
            />
          </div>
        </div>

        {/* Steps Status Checkmarks list */}
        <div className="flex flex-col gap-3.5 mt-2">
          {steps.map((s, index) => {
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;

            return (
              <div
                key={index}
                className="flex items-start gap-3 transition-all duration-300"
                style={{ opacity: isCompleted || isActive ? 1 : 0.35 }}
              >
                <div className="mt-0.5">
                  {isCompleted ? (
                    <CheckCircle2 size={16} className="text-[#7BC4BE] animate-[checkPop_0.4s_ease-out]" />
                  ) : isActive ? (
                    <Loader2 size={16} className="text-[#F6B233] animate-spin" />
                  ) : (
                    <div className="w-4 h-4 rounded-full border border-gray-300" />
                  )}
                </div>
                <div className="flex flex-col gap-0.5">
                  <span className={`text-xs font-semibold ${isActive ? "text-[#1A2B2A]" : "text-gray-600"}`}>
                    {s.label}
                  </span>
                  {isActive && (
                    <span className="text-[10px] text-gray-400 font-light animate-fadeIn">
                      {s.desc}
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Simulated logs panel */}
        <div className="bg-[#1A2B2A] rounded-xl p-4 font-mono text-[10px] text-green-400 h-28 overflow-y-auto flex flex-col gap-1 border border-black shadow-inner">
          <div className="text-gray-500 border-b border-gray-800 pb-1 mb-1 flex items-center justify-between">
            <span>AI ENGINE OUTPUT logs</span>
            <span className="animate-pulse flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-green-400" /> ACTIVE</span>
          </div>
          {activeLogs.map((log, idx) => (
            <div key={idx} className="flex gap-1.5 animate-fadeIn">
              <span className="text-gray-600 select-none">&gt;</span>
              <span>{log}</span>
            </div>
          ))}
          {progress < 100 && (
            <div className="flex items-center gap-1 text-gray-400">
              <span className="text-gray-600 select-none">&gt;</span>
              <span className="inline-block w-1.5 h-3 bg-green-400 animate-[blink_0.8s_step-end_infinite]" />
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
