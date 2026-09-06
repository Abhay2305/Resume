import { motion } from "framer-motion";
import {
  FileText,
  Download,
  CheckCircle,
  Edit3,
  Sparkles,
  Copy,
  Printer,
} from "lucide-react";
import { useState } from "react";

export default function ResumePreviewTab({ resumeContent, onAccept, onEdit, onExport }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (!resumeContent) return;
    try {
      await navigator.clipboard.writeText(resumeContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API may fail
    }
  };

  const handlePrint = () => {
    if (!resumeContent) return;
    const printWindow = window.open("", "_blank");
    if (printWindow) {
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Tailored Resume</title>
          <style>
            body { font-family: 'Georgia', serif; line-height: 1.6; color: #1f2937; max-width: 800px; margin: 0 auto; padding: 40px; }
            h1 { font-size: 24px; margin-bottom: 8px; }
            h2 { font-size: 16px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px; margin-top: 24px; }
            p { margin: 4px 0; }
            .contact { color: #6b7280; font-size: 14px; }
            ul { padding-left: 20px; }
            li { margin: 4px 0; }
          </style>
        </head>
        <body>
          <pre style="white-space: pre-wrap; font-family: inherit;">${resumeContent}</pre>
        </body>
        </html>
      `);
      printWindow.document.close();
      printWindow.print();
    }
  };

  if (!resumeContent) {
    return (
      <div className="text-center py-12">
        <FileText size={32} className="mx-auto text-gray-600 mb-3" />
        <p className="text-sm text-gray-400">No resume generated yet</p>
        <p className="text-xs text-gray-500 mt-1">
          The tailored resume will appear here once generated.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Actions Bar */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <Sparkles size={14} className="text-[#7BC4BE]" />
          <span className="text-xs font-bold text-white">Tailored Resume</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-semibold text-gray-400 hover:text-white hover:bg-white/10 transition-all"
          >
            {copied ? (
              <>
                <CheckCircle size={12} className="text-emerald-400" />
                Copied
              </>
            ) : (
              <>
                <Copy size={12} />
                Copy
              </>
            )}
          </button>
          <button
            onClick={handlePrint}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-semibold text-gray-400 hover:text-white hover:bg-white/10 transition-all"
          >
            <Printer size={12} />
            Print
          </button>
          {onExport && (
            <button
              onClick={onExport}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-semibold text-gray-400 hover:text-white hover:bg-white/10 transition-all"
            >
              <Download size={12} />
              Export PDF
            </button>
          )}
        </div>
      </div>

      {/* Resume Content */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl p-8 shadow-2xl"
      >
        <div className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap font-serif">
          {resumeContent}
        </div>
      </motion.div>

      {/* Bottom Actions */}
      <div className="flex items-center justify-center gap-3 pt-2">
        <button
          onClick={onAccept}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-white rounded-xl text-xs font-bold transition-all shadow-lg shadow-emerald-500/20"
        >
          <CheckCircle size={14} />
          Accept Changes
        </button>
        <button
          onClick={onEdit}
          className="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 hover:bg-white/10 text-white rounded-xl text-xs font-bold transition-all"
        >
          <Edit3 size={14} />
          Edit Resume
        </button>
      </div>
    </div>
  );
}
