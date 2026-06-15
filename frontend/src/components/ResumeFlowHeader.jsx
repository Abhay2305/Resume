import React from "react";
import { COLORS } from "../utils/constants";
import { ArrowLeft, Check, CloudLightning } from "lucide-react";

export default function ResumeFlowHeader({ step, onBack, onExit }) {
  const steps = [
    { id: "prompt", label: "Prompt" },
    { id: "templates", label: "Gallery" },
    { id: "editor", label: "Editor" },
    { id: "ats", label: "ATS Score" },
    { id: "export", label: "Export" },
  ];

  const getStepStatus = (stepId) => {
    const stepOrder = ["prompt", "generating", "templates", "editor", "ats", "export"];
    const currentIndex = stepOrder.indexOf(step === "generating" ? "prompt" : step);
    const targetIndex = stepOrder.indexOf(stepId);

    if (targetIndex < currentIndex) return "completed";
    if (targetIndex === currentIndex) return "active";
    return "pending";
  };

  return (
    <header
      className="w-full h-16 border-b flex items-center justify-between px-6 sticky top-0 z-50 transition-all duration-300"
      style={{
        background: "rgba(255, 253, 248, 0.92)",
        backdropFilter: "blur(12px)",
        borderColor: COLORS.border,
      }}
    >
      {/* Left side: Back or Logo */}
      <div className="flex items-center gap-4">
        {step !== "prompt" && step !== "generating" ? (
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-sm font-medium hover:opacity-80 transition-opacity"
            style={{ color: COLORS.textMid }}
          >
            <ArrowLeft size={16} />
            <span>Back</span>
          </button>
        ) : (
          <button
            onClick={onExit}
            className="flex items-center gap-2 text-sm font-medium hover:opacity-80 transition-opacity"
            style={{ color: COLORS.textMid }}
          >
            <ArrowLeft size={16} />
            <span>Exit</span>
          </button>
        )}

        <div className="h-6 w-[1px] bg-gray-200 hidden md:block" />

        {/* Logo */}
        <div className="flex items-center gap-2 cursor-pointer" onClick={onExit}>
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-xs"
            style={{
              background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`,
              boxShadow: "0 2px 6px rgba(75,158,152,0.25)",
            }}
          >
            PR
          </div>
          <span className="serif font-semibold text-lg" style={{ color: COLORS.text }}>
            Prompt Resume
          </span>
        </div>
      </div>

      {/* Middle: Stepper (Progress Tracker) */}
      {step !== "generating" && (
        <nav className="hidden md:flex items-center gap-1">
          {steps.map((s, index) => {
            const status = getStepStatus(s.id);
            return (
              <React.Fragment key={s.id}>
                {index > 0 && (
                  <div
                    className="w-8 h-[2px] transition-colors duration-300"
                    style={{
                      background: status === "completed" ? COLORS.teal : COLORS.border,
                    }}
                  />
                )}
                <div className="flex items-center gap-2 px-2 py-1">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold border transition-all duration-300 ${
                      status === "active"
                        ? "shadow-sm scale-110"
                        : ""
                    }`}
                    style={{
                      backgroundColor:
                        status === "completed"
                          ? COLORS.teal
                          : status === "active"
                          ? "white"
                          : COLORS.ivory,
                      borderColor:
                        status === "completed" || status === "active"
                          ? COLORS.teal
                          : COLORS.border,
                      color:
                        status === "completed"
                          ? "white"
                          : status === "active"
                          ? COLORS.tealDeep
                          : COLORS.textMuted,
                    }}
                  >
                    {status === "completed" ? <Check size={12} strokeWidth={3} /> : index + 1}
                  </div>
                  <span
                    className={`text-xs font-medium transition-all duration-300`}
                    style={{
                      color: status === "active" ? COLORS.text : COLORS.textMuted,
                      fontWeight: status === "active" ? 600 : 500,
                    }}
                  >
                    {s.label}
                  </span>
                </div>
              </React.Fragment>
            );
          })}
        </nav>
      )}

      {/* Right side: Save status / Exit */}
      <div className="flex items-center gap-4">
        {step !== "prompt" && step !== "generating" && (
          <div
            className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all duration-300"
            style={{
              backgroundColor: "rgba(123, 196, 190, 0.1)",
              color: COLORS.tealDeep,
            }}
          >
            <CloudLightning size={12} className="animate-pulse" />
            <span>Autosaved</span>
          </div>
        )}
        <button
          onClick={onExit}
          className="text-xs font-semibold px-3 py-1.5 rounded-lg border hover:bg-gray-50 transition-colors"
          style={{ borderColor: COLORS.borderMid, color: COLORS.textMid }}
        >
          Exit Builder
        </button>
      </div>
    </header>
  );
}
