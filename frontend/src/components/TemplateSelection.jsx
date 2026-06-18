import React, { useState, useEffect } from "react";
import { COLORS } from "../utils/constants";
import { ChevronRight, ArrowLeft, Check, Eye, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import ResumePreview from "./ResumePreview";

const CATEGORY_ORDER = ["ATS", "Corporate", "Technology", "Creative"];

export default function TemplateSelection({ resumeData, selectedTemplate, onSelect, onBack }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTemplate, setActiveTemplate] = useState(selectedTemplate || "harvard");

  // Load the real, seeded template catalog from the backend so the gallery and
  // the selected identifiers match the IDs stored in the database.
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        setLoading(true);
        const list = await api.listTemplates();
        setTemplates(list);
        if (list.length > 0 && !list.some((t) => t.id === (selectedTemplate || activeTemplate))) {
          setActiveTemplate(list[0].id);
        }
      } catch (err) {
        setError(err.message || "Failed to load templates");
      } finally {
        setLoading(false);
      }
    };
    loadTemplates();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedTemplate) {
      setActiveTemplate(selectedTemplate);
    }
  }, [selectedTemplate]);

  const handleConfirm = () => {
    onSelect(activeTemplate);
  };

  const activeMeta = templates.find((t) => t.id === activeTemplate);

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center gap-4" style={{ backgroundColor: COLORS.cream }}>
        <RefreshCw className="animate-spin" size={34} style={{ color: COLORS.teal }} />
        <p className="text-gray-500 text-xs">Loading template catalog...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center gap-4" style={{ backgroundColor: COLORS.cream }}>
        <p className="text-rose-500 text-xs font-semibold">{error}</p>
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-lg border"
          style={{ borderColor: COLORS.borderMid, color: COLORS.textMid }}
        >
          <ArrowLeft size={14} /> Back
        </button>
      </div>
    );
  }

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
              const isSelected = activeTemplate === t.id;
              const colors = t.color_scheme || {};
              const layout = t.layout_schema || {};
              const isTwoColumn = (layout.structure || "").startsWith("two-column");
              return (
                <div
                  key={t.id}
                  onClick={() => setActiveTemplate(t.id)}
                  className={`bg-white rounded-2xl border-2 p-5 cursor-pointer flex flex-col gap-4 transition-all duration-300 relative group overflow-hidden ${
                    isSelected ? "shadow-md scale-[1.01]" : "hover:border-[#7BC4BE]/50 hover:shadow-sm"
                  }`}
                  style={{
                    borderColor: isSelected ? COLORS.teal : COLORS.border,
                  }}
                >
                  {/* Selected checkmark */}
                  {isSelected && (
                    <div className="absolute top-3 right-3 w-5 h-5 rounded-full flex items-center justify-center text-white z-10" style={{ backgroundColor: COLORS.teal }}>
                      <Check size={12} strokeWidth={3} />
                    </div>
                  )}

                  {/* Template Visual Thumbnail (driven by real template metadata) */}
                  <div className="w-full h-40 bg-gray-50 rounded-xl border border-gray-100 overflow-hidden flex flex-col transition-transform duration-300 group-hover:scale-[1.02]">
                    {/* Header bar */}
                    {isTwoColumn ? (
                      <div className="w-full h-full grid grid-cols-12">
                        <div className="col-span-4 h-full" style={{ background: `linear-gradient(180deg, ${colors.primary}, ${colors.accent || colors.secondary})` }} />
                        <div className="col-span-8 h-full p-3 flex flex-col gap-1.5 bg-white">
                          <div className="h-3 w-1/2 rounded bg-gray-200" />
                          <div className="h-2 w-1/3 rounded" style={{ background: `${colors.accent || colors.primary}40` }} />
                          <div className="flex flex-col gap-1 mt-2">
                            <div className="h-1.5 w-full rounded bg-gray-100" />
                            <div className="h-1.5 w-5/6 rounded bg-gray-100" />
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="w-full h-full flex flex-col bg-white">
                        <div className={`p-3 border-b flex flex-col gap-1 ${layout.headerStyle === "centered" ? "items-center" : "items-start"}`} style={{ borderColor: COLORS.border }}>
                          <div className={`h-3 w-2/5 rounded`} style={{ background: colors.primary }} />
                          <div className="h-2 w-1/4 rounded bg-gray-200" />
                        </div>
                        <div className="p-3 flex flex-col gap-1.5">
                          {[0.9, 0.7, 0.8].map((w, index) => (
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
                        {t.category}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 font-light leading-relaxed capitalize">
                      {(layout.structure || "single-column").replace(/-/g, " ")} · {layout.fontFamily || "sans-serif"}
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
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Live Preview: {activeMeta ? activeMeta.name : activeTemplate}</span>
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
                <span>Use {activeMeta ? activeMeta.name : "this"} Template</span>
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
