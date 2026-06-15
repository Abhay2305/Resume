import React, { useState } from "react";
import { COLORS } from "../utils/constants";
import { ChevronRight, ArrowLeft, Check, Eye } from "lucide-react";
import ResumePreview from "./ResumePreview";

export default function TemplateSelection({ resumeData, selectedTemplate, onSelect, onBack }) {
  const [activeTemplate, setActiveTemplate] = useState(selectedTemplate || "Meridian");

  const templates = [
    {
      name: "Meridian",
      tag: "Modern / Creative",
      desc: "Balanced layouts with teal dividers and modern typography. Perfect for product designers, marketers, and creative roles.",
      hue: COLORS.teal,
      themeColor: COLORS.tealDark,
      previewLines: [0.9, 0.6, 0.85, 0.5, 0.75, 0.4, 0.8]
    },
    {
      name: "Ashford",
      tag: "Executive / Classic",
      desc: "Traditional, centered serif headers for an authoritative and polished presentation. Great for managers, executives, and finance.",
      hue: "#2D3748",
      themeColor: "#4A5568",
      previewLines: [0.85, 0.55, 0.8, 0.65, 0.7, 0.5, 0.75]
    },
    {
      name: "Luma",
      tag: "Minimalist / Sleek",
      desc: "Clean, high-density monospace layout for maximum data efficiency. Excellent for minimalist designs, operations, or recruiters.",
      hue: "#718096",
      themeColor: COLORS.textMid,
      previewLines: [0.9, 0.5, 0.7, 0.6, 0.8, 0.45, 0.65]
    },
    {
      name: "Pulse",
      tag: "Technical / Developer",
      desc: "Deep navy sidebar layout optimized for technical skills, languages, and certifications. Recommended for engineers, developers, and IT.",
      hue: "#1E3A8A",
      themeColor: "#1E3E8F",
      previewLines: [0.8, 0.7, 0.9, 0.55, 0.75, 0.6, 0.85]
    }
  ];

  const handleConfirm = () => {
    onSelect(activeTemplate);
  };

  return (
    <div className="min-h-[calc(100vh-64px)] py-12 px-4 sm:px-6 lg:px-8 flex flex-col items-center" style={{ backgroundColor: COLORS.cream }}>
      <div className="w-full max-w-6xl flex flex-col gap-8">
        
        {/* Top Info */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="flex flex-col gap-1.5">
            <h1 className="serif text-3xl text-gray-900 leading-tight">Select a visual template</h1>
            <p className="text-xs sm:text-sm text-gray-500 font-light">
              Choose the look that represents you best. You can change this template anytime with one click.
            </p>
          </div>
          
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-xs font-semibold hover:opacity-80 transition-opacity"
            style={{ color: COLORS.textMid }}
          >
            <ArrowLeft size={14} />
            <span>Back to prompt</span>
          </button>
        </div>

        {/* Templates Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Gallery selector (Col span 7) */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-5">
            {templates.map((t) => {
              const isSelected = activeTemplate === t.name;
              return (
                <div
                  key={t.name}
                  onClick={() => setActiveTemplate(t.name)}
                  className={`bg-white rounded-2xl border-2 p-5 cursor-pointer flex flex-col gap-4 transition-all duration-300 relative group overflow-hidden ${
                    isSelected ? "shadow-md scale-[1.01]" : "hover:border-[#7BC4BE]/50 hover:shadow-sm"
                  }`}
                  style={{
                    borderColor: isSelected ? COLORS.teal : COLORS.border,
                  }}
                >
                  {/* Selected checkmark */}
                  {isSelected && (
                    <div className="absolute top-3 right-3 w-5 h-5 rounded-full flex items-center justify-center text-white" style={{ backgroundColor: COLORS.teal }}>
                      <Check size={12} strokeWidth={3} />
                    </div>
                  )}

                  {/* Template Visual Thumbnail */}
                  <div className="w-full h-40 bg-gray-50 rounded-xl border border-gray-100 overflow-hidden flex flex-col transition-transform duration-300 group-hover:scale-[1.02]">
                    {/* Header bar */}
                    {t.name === "Pulse" ? (
                      <div className="w-full h-full grid grid-cols-12">
                        <div className="col-span-4 h-full" style={{ background: `linear-gradient(180deg, ${COLORS.tealDeep}, #1E3A8A)` }} />
                        <div className="col-span-8 h-full p-3 flex flex-col gap-1.5 bg-white">
                          <div className="h-3 w-1/2 rounded bg-gray-200" />
                          <div className="h-2 w-1/3 rounded bg-blue-100" />
                          <div className="flex flex-col gap-1 mt-2">
                            <div className="h-1.5 w-full rounded bg-gray-100" />
                            <div className="h-1.5 w-5/6 rounded bg-gray-100" />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="w-full h-full flex flex-col bg-white">
                        <div className={`p-3 border-b flex flex-col gap-1`} style={{ borderColor: COLORS.border, background: t.name === "Ashford" ? "white" : "transparent" }}>
                          <div className={`h-3 w-2/5 rounded`} style={{ background: t.name === "Ashford" ? "black" : t.hue }} />
                          <div className="h-2 w-1/4 rounded bg-gray-200" />
                        </div>
                        <div className="p-3 flex flex-col gap-1.5">
                          {t.previewLines.slice(0, 3).map((w, index) => (
                            <div key={index} className="h-1.5 rounded bg-gray-100" style={{ width: `${w * 100}%` }} />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Template description info */}
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-[#1A2B2A] text-sm">{t.name}</span>
                      <span className="text-[9px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded" style={{ backgroundColor: "rgba(123, 196, 190, 0.12)", color: COLORS.tealDeep }}>
                        {t.tag.split(" / ")[0]}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 font-light leading-relaxed">
                      {t.desc}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Large dynamic template preview & confirmation (Col span 5) */}
          <div className="lg:col-span-5 flex flex-col gap-5 sticky top-24">
            <div className="bg-white rounded-2xl border p-6 shadow-md flex flex-col gap-5" style={{ borderColor: COLORS.border }}>
              <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: COLORS.border }}>
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Live Preview: {activeTemplate}</span>
                <span className="text-xs text-gray-400 flex items-center gap-1">
                  <Eye size={12} /> Actual layout mockup
                </span>
              </div>

              {/* A4 Miniaturized view */}
              <div className="w-full origin-top border border-gray-100 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow relative">
                {/* Scale it down visually to fit layout */}
                <div className="scale-[0.6] w-[166%] origin-top-left -mb-[58%]">
                  <ResumePreview data={resumeData} template={activeTemplate} />
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={handleConfirm}
                className="w-full btn-hero py-3 px-6 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold transition-all duration-300 cursor-pointer shadow-lg select-none"
                style={{
                  background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`,
                  boxShadow: "0 4px 20px rgba(75, 158, 152, 0.35)",
                  color: "white"
                }}
              >
                <span>Use {activeTemplate} Template</span>
                <ChevronRight size={16} />
              </button>
            </div>

            {/* Note text */}
            <p className="text-xs text-gray-400 font-light text-center px-4">
              Tip: The AI has prepared your data. Press continue to edit individual bullets, tailor sections, and export your PDF.
            </p>
          </div>

        </div>

      </div>
    </div>
  );
}
