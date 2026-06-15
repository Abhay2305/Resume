import React, { useState } from "react";
import { COLORS } from "../utils/constants";
import { Sparkles, FileText, CheckCircle2, ChevronRight, CornerDownLeft } from "lucide-react";

export default function PromptEntry({ onSubmit, onStartManual }) {
  const [promptText, setPromptText] = useState("");

  const examples = [
    {
      label: "Experienced Pro",
      icon: "💼",
      preview: "Alexandra Chen · Senior Product Designer...",
      text: "I'm Alexandra Chen, a Senior Product Designer with 6 years of experience in San Francisco. I lead design systems at Vortex Tech and design mobile apps at Pixel & Co. I have a B.S. in CS from Stanford. My skills include Figma, React, and UX research. Shipped a Lumos Financial App project and won Vortex Hackathon 2023.",
      archetype: "experienced"
    },
    {
      label: "Career Switcher",
      icon: "🔄",
      preview: "Marcus Vance · Teacher to Data Analyst...",
      text: "I'm Marcus Vance, transitioning from an AP Math Educator to a Data Analyst. Based in Austin. Just finished Springboard's Data Analytics track. I taught stats for 8 years, analyzed class performance, and created an E-Commerce Cohort Dashboard in SQL/Tableau. Strong in Python, SQL, and data visualization.",
      archetype: "career_switcher"
    },
    {
      label: "Fresh Graduate",
      icon: "🎓",
      preview: "Emily Rodriguez · Recent Marketing Grad...",
      text: "I'm Emily Rodriguez, a recent Marketing & Media graduate from NYU, based in NY. Shipped a Brand Launch Capstone project. Had a Brand Marketing Internship at PepsiCo where I grew engagement by 12%. I know Google Analytics, Canva, and SEO writing. Certified in Google Analytics.",
      archetype: "fresher"
    }
  ];

  const handleExampleClick = (example) => {
    setPromptText(example.text);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!promptText.trim()) return;

    // Determine archetype from text to load corresponding mock data
    let archetype = "experienced";
    if (promptText.toLowerCase().includes("marcus") || promptText.toLowerCase().includes("teacher") || promptText.toLowerCase().includes("vance")) {
      archetype = "career_switcher";
    } else if (promptText.toLowerCase().includes("emily") || promptText.toLowerCase().includes("marketing") || promptText.toLowerCase().includes("rodriguez")) {
      archetype = "fresher";
    }

    onSubmit(promptText, archetype);
  };

  return (
    <div className="min-h-[calc(100vh-64px)] py-12 px-4 sm:px-6 lg:px-8 flex flex-col justify-center items-center relative overflow-hidden" style={{ backgroundColor: COLORS.cream }}>
      {/* Background Blobs */}
      <div className="absolute top-1/4 left-1/10 w-[40vw] h-[40vw] rounded-full filter blur-[100px] opacity-10 pointer-events-none" style={{ background: COLORS.teal }} />
      <div className="absolute bottom-1/4 right-1/10 w-[30vw] h-[30vw] rounded-full filter blur-[80px] opacity-10 pointer-events-none" style={{ background: COLORS.amber }} />

      <div className="w-full max-w-4xl flex flex-col items-center gap-8 relative z-10">
        
        {/* Title */}
        <div className="text-center max-w-2xl flex flex-col gap-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider self-center" style={{ backgroundColor: "rgba(123, 196, 190, 0.12)", color: COLORS.tealDeep, border: `1px solid ${COLORS.border}` }}>
            <Sparkles size={12} className="text-[#F6B233]" />
            <span>AI Prompt Mode</span>
          </div>
          <h1 className="serif text-3xl sm:text-4xl text-gray-900 leading-tight">
            Transform your story into a<br />
            <span className="relative inline-block">
              <em className="not-italic text-[#4A9E98]">career-winning resume</em>
              <span className="absolute bottom-0.5 left-0 right-0 h-[3px] rounded-full" style={{ background: `linear-gradient(90deg, ${COLORS.teal}, ${COLORS.amber})` }} />
            </span>
          </h1>
          <p className="text-sm sm:text-base text-gray-600 font-light">
            Describe yourself in plain English. Include your experience, background, and skills. We'll build a polished, ATS-optimized layout in seconds.
          </p>
        </div>

        {/* Workspace Layout */}
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-start mt-2">
          
          {/* Main Input Form (Col span 8) */}
          <div className="lg:col-span-8 flex flex-col gap-4 w-full">
            <form onSubmit={handleSubmit} className="w-full">
              <div className="w-full bg-white rounded-2xl shadow-xl border overflow-hidden p-6 transition-all duration-300 hover:shadow-2xl flex flex-col gap-4" style={{ borderColor: COLORS.borderMid }}>
                
                {/* Textarea Header */}
                <div className="flex items-center justify-between border-b pb-3" style={{ borderColor: COLORS.border }}>
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Describe your background</span>
                  </div>
                  <span className="text-xs font-medium text-gray-400">Natural English supported</span>
                </div>

                {/* Textarea */}
                <textarea
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  placeholder="e.g. 'I am Alexandra Chen. I have 6 years of experience in product design leading design systems at Vortex Tech. I went to Stanford, and I'm skilled in Figma and React...'"
                  className="w-full h-48 focus:outline-none resize-none text-sm text-gray-800 leading-relaxed font-sans"
                  style={{
                    backgroundColor: "transparent",
                  }}
                />

                {/* Textarea Footer & Submit */}
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between pt-3 border-t gap-3" style={{ borderColor: COLORS.border }}>
                  <span className="text-xs text-gray-400 flex items-center gap-1">
                    <CheckCircle2 size={12} className="text-[#7BC4BE]" /> Type or paste your info above to get started
                  </span>
                  
                  <button
                    type="submit"
                    disabled={!promptText.trim()}
                    className="btn-hero py-2.5 px-6 rounded-xl flex items-center justify-center gap-2 text-sm font-semibold transition-all duration-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed select-none"
                    style={{
                      background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`,
                      boxShadow: promptText.trim() ? "0 4px 14px rgba(75, 158, 152, 0.3)" : "none",
                      color: "white"
                    }}
                  >
                    <span>Generate Resume</span>
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>
            </form>

            {/* Clickable Examples Section */}
            <div className="flex flex-col gap-2.5">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Or start with an example prompt:</span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {examples.map((ex, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleExampleClick(ex)}
                    className="p-3 bg-white rounded-xl border hover:border-[#7BC4BE] hover:shadow-md transition-all text-left flex flex-col gap-1 cursor-pointer"
                    style={{ borderColor: COLORS.border }}
                  >
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm">{ex.icon}</span>
                      <span className="text-xs font-semibold text-gray-800">{ex.label}</span>
                    </div>
                    <span className="text-[10px] text-gray-400 truncate w-full">{ex.preview}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Guidelines Sidebar (Col span 4) */}
          <div className="lg:col-span-4 flex flex-col gap-5 w-full">
            <div className="bg-white rounded-2xl border p-5 flex flex-col gap-4 shadow-sm" style={{ borderColor: COLORS.border }}>
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
                <FileText size={14} className="text-[#F6B233]" />
                <span>Details to include</span>
              </h3>
              
              <ul className="flex flex-col gap-2.5 text-xs text-gray-600 font-light">
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                  <span>Full name, email, phone, location</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                  <span>Target job title & professional summary</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                  <span>Work history (companies, roles, achievements)</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                  <span>Education degrees & certifications</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                  <span>Key technical & soft skills</span>
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: COLORS.teal }} />
                  <span>Personal website, LinkedIn, or portfolio</span>
                </li>
              </ul>

              <div className="border-t pt-3" style={{ borderColor: COLORS.border }}>
                <button
                  onClick={onStartManual}
                  className="w-full text-center text-xs font-semibold py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-1 cursor-pointer"
                  style={{ color: COLORS.textMid, border: `1px solid ${COLORS.borderMid}` }}
                >
                  Start in Manual Mode
                </button>
              </div>
            </div>

            {/* Trust cues */}
            <div className="flex flex-col gap-2 text-xs text-gray-400 font-light px-2">
              <div className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-green-500" />
                <span>✓ 100% ATS-safe layout</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-green-500" />
                <span>✓ Fully editable at any step</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1 h-1 rounded-full bg-green-500" />
                <span>✓ Switch templates with one click</span>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  );
}
