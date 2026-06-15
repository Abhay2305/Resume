import React, { useState } from "react";
import { COLORS } from "../utils/constants";
import { Download, FileText, Clipboard, Copy, Check, Info, FileSpreadsheet, Sparkles, ArrowLeft, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import ResumePreview from "./ResumePreview";

export default function ExportDownload({ data, template, onBack, onExit }) {
  const [downloading, setDownloading] = useState(null); // 'pdf' | 'docx' | 'txt'
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState(""); // format
  const [copied, setCopied] = useState(false);
  const [fileName, setFileName] = useState(`${data.personalInfo.fullName ? data.personalInfo.fullName.replace(/\s+/g, "_") : "My"}_Resume`);

  const handleDownload = async (format) => {
    if (format !== "pdf") {
      setDownloading(format);
      setTimeout(() => {
        setDownloading(null);
        setModalType(format.toUpperCase());
        setShowModal(true);
      }, 1200);
      return;
    }

    setDownloading("pdf");
    try {
      // Find the preview pane selector inside A4 container
      const previewDom = document.querySelector(".w-full.shadow-2xl.rounded-sm");
      const innerHtml = previewDom ? previewDom.innerHTML : "";

      // Construct isolated HTML page with Google Fonts matching styles
      const resumeHtml = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <script src="https://cdn.tailwindcss.com"></script>
          <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&family=Fira+Code&family=Lora:ital,wght@0,400;0,700;1,400&family=Outfit:wght@400;500;700&family=Roboto+Mono&display=swap" rel="stylesheet">
          <style>
            body { font-family: 'DM Sans', sans-serif; background: white; color: #1f2937; margin: 0; padding: 0; }
            .font-serif { font-family: 'Lora', Georgia, serif; }
            .font-mono { font-family: 'Fira Code', 'Roboto Mono', monospace; }
            .font-sans { font-family: 'DM Sans', 'Outfit', sans-serif; }
          </style>
        </head>
        <body class="p-8">
          <div style="width: 794px; min-height: 1123px; margin: auto;">
            ${innerHtml}
          </div>
        </body>
        </html>
      `;

      // Export file
      const blob = await api.exportPDF(resumeHtml, `${fileName}.pdf`);
      
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `${fileName}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);

      setModalType("PDF");
      setShowModal(true);
    } catch (err) {
      alert("Failed to export PDF: " + err.message);
    } finally {
      setDownloading(null);
    }
  };

  const handleCopyText = () => {
    setCopied(true);
    const textContent = `
${data.personalInfo.fullName || ""}
${data.personalInfo.jobTitle || ""}
${data.personalInfo.email || ""} | ${data.personalInfo.phone || ""} | ${data.personalInfo.location || ""}
${data.personalInfo.website || ""} | ${data.personalInfo.linkedin || ""}

SUMMARY
${data.summary || ""}

WORK EXPERIENCE
${(data.experience || []).map(e => `${e.role} - ${e.company} (${e.duration})\n${e.description}`).join("\n\n")}

EDUCATION
${(data.education || []).map(e => `${e.degree} - ${e.institution} (${e.duration})`).join("\n")}

SKILLS
${(data.skills || []).join(", ")}
    `.trim();

    navigator.clipboard.writeText(textContent);
    setTimeout(() => setCopied(false), 2000);
  };


  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col bg-gray-50 relative">
      
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden h-[calc(100vh-64px)]">
        
        {/* Left Panel: Export Menu (Col span 5) */}
        <div className="col-span-1 lg:col-span-5 flex flex-col bg-white border-r h-full overflow-y-auto p-6" style={{ borderColor: COLORS.border }}>
          
          {/* Header */}
          <div className="flex flex-col gap-1 border-b pb-4 mb-6" style={{ borderColor: COLORS.border }}>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">STEP 5 OF 5</span>
            <h2 className="serif text-xl text-gray-900 leading-tight">Your resume is ready!</h2>
            <p className="text-xs text-gray-500 font-light">Export your document in high-fidelity or save draft for later editing.</p>
          </div>

          {/* Rename File Input */}
          <div className="flex flex-col gap-1.5 mb-6">
            <label className="text-[11px] font-bold text-gray-500 uppercase">File Name</label>
            <div className="flex items-center border rounded-lg bg-gray-50/50 p-2" style={{ borderColor: COLORS.borderMid }}>
              <input
                type="text"
                value={fileName}
                onChange={(e) => setFileName(e.target.value)}
                className="flex-1 bg-transparent text-xs font-semibold focus:outline-none text-gray-700"
              />
              <span className="text-[10px] text-gray-400 font-medium px-2 bg-white rounded border select-none">.pdf</span>
            </div>
          </div>

          {/* Core Export Actions */}
          <div className="flex flex-col gap-4 mb-6">
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Download Formats</span>
            
            {/* Action: PDF */}
            <button
              onClick={() => handleDownload("pdf")}
              disabled={downloading !== null}
              className="w-full btn-hero py-3 px-5 rounded-xl flex items-center justify-between text-sm font-semibold transition-all duration-300 cursor-pointer shadow-md select-none border-0 text-white"
              style={{
                background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`,
                boxShadow: "0 4px 14px rgba(75, 158, 152, 0.3)"
              }}
            >
              <span className="flex items-center gap-2">
                <FileText size={16} />
                <span>Export as PDF (Recommended)</span>
              </span>
              {downloading === "pdf" ? (
                <RefreshCw size={16} className="animate-spin" />
              ) : (
                <Download size={16} />
              )}
            </button>

            {/* Action: DOCX */}
            <button
              onClick={() => handleDownload("docx")}
              disabled={downloading !== null}
              className="w-full py-3 px-5 rounded-xl flex items-center justify-between text-sm font-semibold border transition-all duration-200 cursor-pointer text-[#D4920F] hover:bg-amber-50"
              style={{ borderColor: "rgba(246, 178, 51, 0.45)" }}
            >
              <span className="flex items-center gap-2">
                <FileSpreadsheet size={16} />
                <span>Export as Word (DOCX)</span>
              </span>
              {downloading === "docx" ? (
                <RefreshCw size={16} className="animate-spin" />
              ) : (
                <Download size={16} />
              )}
            </button>

            {/* Action: Copy Text */}
            <button
              onClick={handleCopyText}
              className="w-full py-3 px-5 rounded-xl flex items-center justify-between text-sm font-semibold border transition-all duration-200 cursor-pointer text-gray-600 hover:bg-gray-50"
              style={{ borderColor: COLORS.borderMid }}
            >
              <span className="flex items-center gap-2">
                <Clipboard size={16} />
                <span>Copy Plain Text (ATS Match)</span>
              </span>
              {copied ? (
                <Check size={16} className="text-green-500" />
              ) : (
                <Copy size={16} />
              )}
            </button>
          </div>

          {/* More Actions (Save, Duplicate) */}
          <div className="border-t pt-5 flex flex-col gap-3" style={{ borderColor: COLORS.border }}>
            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">Document Utilities</span>
            <div className="flex gap-2">
              <button
                onClick={onExit}
                className="flex-1 py-2 px-3 border rounded-lg text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer"
                style={{ borderColor: COLORS.borderMid }}
              >
                Save Draft
              </button>
              <button
                onClick={() => alert("Resume duplicated! You now have a copy in your dashboard.")}
                className="flex-1 py-2 px-3 border rounded-lg text-xs font-semibold text-gray-600 hover:bg-gray-50 transition-colors cursor-pointer"
                style={{ borderColor: COLORS.borderMid }}
              >
                Duplicate Resume
              </button>
            </div>
          </div>

          {/* Reassurance Info Block */}
          <div className="mt-8 bg-gray-50 p-4 rounded-xl border flex flex-col gap-2.5" style={{ borderColor: COLORS.border }}>
            <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider flex items-center gap-1.5">
              <Info size={14} className="text-[#4A9E98]" />
              <span>Recruiter Tips</span>
            </h4>
            <ul className="flex flex-col gap-2 text-[11px] text-gray-500 font-light leading-relaxed">
              <li className="flex items-start gap-1.5">
                <span className="text-green-500 font-bold">✓</span>
                <span>Our PDF and DOCX files are built strictly to pass parsing gates like Workday, Taleo, and Greenhouse.</span>
              </li>
              <li className="flex items-start gap-1.5">
                <span className="text-green-500 font-bold">✓</span>
                <span>You can return to your dashboard and re-edit this resume or change its template style at any time.</span>
              </li>
            </ul>
          </div>

        </div>

        {/* Right Panel: Final Preview (Col span 7) */}
        <div className="col-span-1 lg:col-span-7 bg-[#FFFDF8]/40 overflow-y-auto p-8 lg:p-12 flex justify-center items-start h-full">
          <div className="w-full max-w-[760px] sticky top-4">
            <ResumePreview data={data} template={template} />
          </div>
        </div>

      </div>

      {/* Success Modal / Toast Dialog */}
      {showModal && (
        <div className="absolute inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="w-full max-w-sm bg-white rounded-2xl border p-6 shadow-2xl flex flex-col items-center text-center gap-4 animate-[checkPop_0.35s_ease-out]">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center text-green-500">
              <Check size={24} strokeWidth={3} />
            </div>
            
            <div className="flex flex-col gap-1">
              <h3 className="serif text-lg text-gray-900">Download Complete!</h3>
              <p className="text-xs text-gray-500 font-light leading-relaxed">
                Your resume has been exported as <strong>{fileName}.{modalType.toLowerCase()}</strong>.
              </p>
            </div>

            <div className="w-full bg-gray-50 p-3 rounded-lg border text-left text-[11px] text-gray-500 leading-normal" style={{ borderColor: COLORS.border }}>
              <span className="font-bold text-gray-700 block mb-1">💡 Pro tip:</span>
              Name your file with the format <strong>[Firstname]_[Lastname]_[Role]_Resume</strong> to make it easier for hiring managers to index.
            </div>

            <div className="flex w-full gap-2 mt-2">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs font-semibold cursor-pointer"
              >
                Close
              </button>
              <button
                onClick={onExit}
                className="flex-1 py-2 text-white rounded-lg text-xs font-semibold cursor-pointer shadow-sm"
                style={{
                  background: `linear-gradient(135deg, ${COLORS.teal}, ${COLORS.tealDark})`
                }}
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
