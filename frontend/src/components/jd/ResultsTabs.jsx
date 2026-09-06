import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart3,
  ArrowRightLeft,
  Lightbulb,
  FileText,
} from "lucide-react";
import OverviewTab from "./OverviewTab";
import ChangesTab from "./ChangesTab";
import SuggestionsTab from "./SuggestionsTab";
import ResumePreviewTab from "./ResumePreviewTab";

const TABS = [
  { id: "overview", label: "Overview", icon: BarChart3 },
  { id: "changes", label: "Changes", icon: ArrowRightLeft },
  { id: "suggestions", label: "Suggestions", icon: Lightbulb },
  { id: "resume", label: "Resume", icon: FileText },
];

export default function ResultsTabs({
  scores,
  gaps,
  changes,
  validation,
  recommendations,
  knowledgeContext,
  resumeContent,
  onAccept,
  onEdit,
  onExport,
}) {
  const [activeTab, setActiveTab] = useState("overview");

  const renderTab = () => {
    switch (activeTab) {
      case "overview":
        return <OverviewTab scores={scores} gaps={gaps} />;
      case "changes":
        return <ChangesTab changes={changes} validation={validation} />;
      case "suggestions":
        return (
          <SuggestionsTab
            recommendations={recommendations}
            knowledgeContext={knowledgeContext}
          />
        );
      case "resume":
        return (
          <ResumePreviewTab
            resumeContent={resumeContent}
            onAccept={onAccept}
            onEdit={onEdit}
            onExport={onExport}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      {/* Tab Bar */}
      <div className="flex items-center gap-1 bg-white/5 rounded-xl p-1 border border-white/10 overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                isActive
                  ? "bg-[#7BC4BE] text-[#1A2B2A] shadow-md shadow-[#7BC4BE]/15"
                  : "text-gray-400 hover:text-white hover:bg-white/5"
              }`}
            >
              <Icon size={14} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.15 }}
        >
          {renderTab()}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
