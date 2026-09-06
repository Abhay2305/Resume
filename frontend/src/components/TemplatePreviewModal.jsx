import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  ZoomIn,
  ZoomOut,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  FileText,
  Loader2,
  AlertCircle,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import ResumePreview from "./ResumePreview";

const DUMMY_RESUME_DATA = {
  personalInfo: {
    fullName: "Alexandra Chen",
    jobTitle: "Senior Software Engineer",
    email: "alexandra.chen@email.com",
    phone: "+1 (555) 987-6543",
    location: "San Francisco, CA",
    website: "alexchen.dev",
    linkedin: "linkedin.com/in/alexandrachen",
  },
  summary:
    "Results-driven software engineer with 8+ years of experience building scalable distributed systems, leading cross-functional teams, and delivering high-impact products. Passionate about clean architecture, developer experience, and mentoring emerging talent.",
  experience: [
    {
      role: "Senior Software Engineer",
      company: "TechCorp Inc.",
      duration: "Jan 2021 – Present",
      description:
        "• Architected and led migration of monolithic services to microservices, reducing deployment time by 60%\n• Designed real-time data pipeline processing 2M+ events/day using Kafka and PostgreSQL\n• Mentored 4 junior engineers through structured growth plans and weekly code reviews",
    },
    {
      role: "Software Engineer",
      company: "InnovateLabs",
      duration: "Jun 2018 – Dec 2020",
      description:
        "• Built and maintained REST APIs serving 500K+ daily active users with 99.9% uptime\n• Implemented CI/CD pipeline reducing release cycles from 2 weeks to 2 days\n• Collaborated with product and design to ship 3 major features ahead of schedule",
    },
  ],
  education: [
    {
      degree: "M.S. Computer Science",
      institution: "Stanford University",
      duration: "2016 – 2018",
      description: "Focus: Distributed Systems & Machine Learning",
    },
    {
      degree: "B.S. Computer Science",
      institution: "UC Berkeley",
      duration: "2012 – 2016",
      description: "Magna Cum Laude",
    },
  ],
  skills: [
    "Python",
    "TypeScript",
    "React",
    "Node.js",
    "PostgreSQL",
    "Kubernetes",
    "AWS",
    "Kafka",
    "GraphQL",
    "Redis",
  ],
  projects: [
    {
      name: "OpenMetrics Dashboard",
      description:
        "Open-source observability platform built with React, D3.js, and Go. 2.4K GitHub stars and used by 50+ companies worldwide.",
    },
    {
      name: "TaskFlow CLI",
      description:
        "Developer productivity tool for automating sprint workflows. Written in Rust with cross-platform support.",
    },
  ],
  certifications: [
    "AWS Solutions Architect – Professional",
    "Certified Kubernetes Administrator (CKA)",
  ],
  achievements: [
    "Speaker at ReactConf 2023 on Micro-Frontend Architecture",
    "Published article in InfoQ: Scaling Teams Through Technical Leadership",
    "Patent pending: Real-time Anomaly Detection in Distributed Systems",
  ],
};

const ZOOM_LEVELS = [0.35, 0.5, 0.65, 0.8, 1.0];
const MAX_NAME_LENGTH = 100;

export default function TemplatePreviewModal({
  isOpen,
  onClose,
  templates = [],
  initialTemplateId = "harvard",
  user,
  profile,
  onUseTemplate,
  onTemplateChange,
}) {
  const [activeTemplateId, setActiveTemplateId] = useState(initialTemplateId);
  const [zoomIndex, setZoomIndex] = useState(1);
  const [showNamePrompt, setShowNamePrompt] = useState(false);
  const [resumeName, setResumeName] = useState("");
  const [creating, setCreating] = useState(false);
  const [nameError, setNameError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const scrollContainerRef = useRef(null);
  const modalRef = useRef(null);
  const nameInputRef = useRef(null);
  const closeButtonRef = useRef(null);
  const previousFocusRef = useRef(null);

  const activeTemplate = templates.find((t) => t.id === activeTemplateId);
  const activeIndex = templates.findIndex((t) => t.id === activeTemplateId);

  const hasProfile = Boolean(
    profile?.job_title || profile?.summary || profile?.company
  );

  // Reset state and scroll when modal opens
  useEffect(() => {
    if (isOpen) {
      (async () => {
        setActiveTemplateId(initialTemplateId);
        setShowNamePrompt(false);
        setResumeName("");
        setNameError("");
      })();
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop = 0;
      }
    }
  }, [isOpen, initialTemplateId]);

  // Focus trap: save previous focus, focus modal on open
  useEffect(() => {
    if (isOpen) {
      previousFocusRef.current = document.activeElement;
      // Small delay to let the modal mount
      const timer = setTimeout(() => {
        if (showNamePrompt && nameInputRef.current) {
          nameInputRef.current.focus();
        } else if (closeButtonRef.current) {
          closeButtonRef.current.focus();
        }
      }, 50);
      return () => clearTimeout(timer);
    } else {
      // Restore focus on close
      if (previousFocusRef.current && previousFocusRef.current.focus) {
        previousFocusRef.current.focus();
      }
    }
  }, [isOpen, showNamePrompt]);

  const zoom = ZOOM_LEVELS[zoomIndex];

  // Notify parent when template changes (for persistence)
  const changeTemplate = useCallback(
    (id) => {
      setActiveTemplateId(id);
      if (onTemplateChange) onTemplateChange(id);
    },
    [onTemplateChange]
  );

  const handlePrev = useCallback(() => {
    if (activeIndex > 0) {
      changeTemplate(templates[activeIndex - 1].id);
    }
  }, [activeIndex, templates, changeTemplate]);

  const handleNext = useCallback(() => {
    if (activeIndex < templates.length - 1) {
      changeTemplate(templates[activeIndex + 1].id);
    }
  }, [activeIndex, templates, changeTemplate]);

  const handleZoomIn = () => {
    setZoomIndex((i) => Math.min(i + 1, ZOOM_LEVELS.length - 1));
  };

  const handleZoomOut = () => {
    setZoomIndex((i) => Math.max(i - 1, 0));
  };

  const handleUseTemplate = () => {
    const defaultName = profile?.job_title
      ? `${user?.full_name || "My"} - ${profile.job_title} Resume`
      : `${user?.full_name || "My"} Resume`;
    setResumeName(defaultName);
    setShowNamePrompt(true);
    setNameError("");
  };

  const validateName = (value) => {
    const trimmed = value.trim();
    if (!trimmed) return "Resume name is required";
    if (trimmed.length > MAX_NAME_LENGTH)
      return `Must be ${MAX_NAME_LENGTH} characters or less`;
    return "";
  };

  const handleNameChange = (e) => {
    const val = e.target.value;
    // Allow typing up to max+1 to show error, but store full value
    setResumeName(val);
    if (nameError) {
      const err = validateName(val);
      if (!err) setNameError("");
    }
  };

  const handleConfirmUse = async () => {
    const err = validateName(resumeName);
    if (err) {
      setNameError(err);
      nameInputRef.current?.focus();
      return;
    }
    setCreating(true);
    try {
      await onUseTemplate(activeTemplateId, resumeName.trim());
    } finally {
      setCreating(false);
    }
  };

  // Focus trap handler
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Escape") {
        if (showNamePrompt) {
          if (!creating) setShowNamePrompt(false);
        } else {
          onClose();
        }
        return;
      }

      if (e.key === "ArrowLeft" && !showNamePrompt) {
        handlePrev();
        return;
      }
      if (e.key === "ArrowRight" && !showNamePrompt) {
        handleNext();
        return;
      }

      // Focus trap within the modal
      if (e.key === "Tab" && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll(
          'button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    },
    [showNamePrompt, creating, onClose, handlePrev, handleNext]
  );

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={modalRef}
          role="dialog"
          aria-modal="true"
          aria-label="Template Preview"
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onKeyDown={handleKeyDown}
          tabIndex={-1}
        >
          {/* Backdrop */}
          <motion.div
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Modal Container */}
          <motion.div
            className="relative w-[95vw] h-[92vh] max-w-[1400px] bg-[#0F1E1E] rounded-2xl border border-white/10 shadow-2xl flex flex-col overflow-hidden"
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 border-b border-white/10 shrink-0">
              <div className="flex items-center gap-3">
                {/* Sidebar toggle - mobile & desktop */}
                <button
                  onClick={() => setSidebarOpen((o) => !o)}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all hidden md:flex"
                  title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
                  aria-label={sidebarOpen ? "Hide template sidebar" : "Show template sidebar"}
                >
                  {sidebarOpen ? (
                    <PanelLeftClose size={14} />
                  ) : (
                    <PanelLeftOpen size={14} />
                  )}
                </button>

                <div className="w-8 h-8 rounded-lg bg-[#7BC4BE]/15 flex items-center justify-center">
                  <FileText size={16} className="text-[#7BC4BE]" />
                </div>
                <div>
                  <h2 className="text-sm font-bold text-white">
                    Template Preview
                  </h2>
                  <p className="text-[10px] text-gray-400">
                    {activeTemplate
                      ? activeTemplate.name
                      : "Select a template"}
                    {activeTemplate && (
                      <span className="ml-1.5 text-[#7BC4BE] font-semibold">
                        ({activeIndex + 1}/{templates.length})
                      </span>
                    )}
                  </p>
                </div>
              </div>

              {/* Zoom Controls */}
              <div className="flex items-center gap-1 sm:gap-2">
                <button
                  onClick={handleZoomOut}
                  disabled={zoomIndex === 0}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  title="Zoom Out"
                  aria-label="Zoom out"
                >
                  <ZoomOut size={14} />
                </button>
                <button
                  className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white text-[10px] font-bold tabular-nums transition-all min-w-[48px]"
                  title="Reset Zoom"
                  aria-label={`Zoom level ${Math.round(zoom * 100)} percent`}
                >
                  {Math.round(zoom * 100)}%
                </button>
                <button
                  onClick={handleZoomIn}
                  disabled={zoomIndex === ZOOM_LEVELS.length - 1}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  title="Zoom In"
                  aria-label="Zoom in"
                >
                  <ZoomIn size={14} />
                </button>
              </div>

              {/* Template Navigation & Close */}
              <div className="flex items-center gap-1 sm:gap-2">
                <button
                  onClick={handlePrev}
                  disabled={activeIndex <= 0}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  title="Previous Template (←)"
                  aria-label="Previous template"
                >
                  <ChevronLeft size={14} />
                </button>
                <button
                  onClick={handleNext}
                  disabled={activeIndex >= templates.length - 1}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  title="Next Template (→)"
                  aria-label="Next template"
                >
                  <ChevronRight size={14} />
                </button>
                <button
                  ref={closeButtonRef}
                  onClick={onClose}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white transition-all ml-1 sm:ml-2"
                  title="Close (Esc)"
                  aria-label="Close template preview"
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="flex flex-1 overflow-hidden min-h-0">
              {/* Left: Template Sidebar */}
              <AnimatePresence initial={false}>
                {sidebarOpen && (
                  <motion.div
                    initial={{ width: 0, opacity: 0 }}
                    animate={{ width: 224, opacity: 1 }}
                    exit={{ width: 0, opacity: 0 }}
                    transition={{ duration: 0.2, ease: "easeInOut" }}
                    className="border-r border-white/10 overflow-hidden shrink-0 hidden md:block"
                  >
                    <div className="w-56 h-full overflow-y-auto p-3 space-y-1.5">
                      <p className="text-[9px] font-bold uppercase tracking-widest text-gray-500 px-2 py-1">
                        Templates
                      </p>
                      {templates.map((t) => {
                        const isActive = t.id === activeTemplateId;
                        return (
                        <button
                          key={t.id}
                          onClick={() => changeTemplate(t.id)}
                          aria-label={`Preview ${t.name} template`}
                          aria-pressed={isActive}
                          className={`w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all ${
                            isActive
                              ? "bg-[#7BC4BE] text-[#1A2B2A] font-bold shadow-md shadow-[#7BC4BE]/15"
                              : "text-gray-400 hover:text-white hover:bg-white/5"
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            <span
                              className="w-2.5 h-2.5 rounded-full shrink-0 border"
                              style={{
                                backgroundColor:
                                  t.color_scheme?.primary || "#888",
                                borderColor: isActive
                                  ? "rgba(0,0,0,0.2)"
                                  : "rgba(255,255,255,0.1)",
                              }}
                            />
                            <div className="truncate">
                              <div className="font-semibold truncate">
                                {t.name}
                              </div>
                              <div
                                className={`text-[9px] ${
                                  isActive
                                    ? "text-[#1A2B2A]/60"
                                    : "text-gray-500"
                                }`}
                              >
                                {t.category}
                              </div>
                            </div>
                          </div>
                        </button>
                        );
                      })}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Mobile Sidebar Overlay */}
              <AnimatePresence>
                {sidebarOpen && (
                  <motion.div
                    className="fixed inset-0 z-40 md:hidden"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <div
                      className="absolute inset-0 bg-black/50"
                      onClick={() => setSidebarOpen(false)}
                    />
                    <motion.div
                      className="absolute left-0 top-0 bottom-0 w-64 bg-[#0F1E1E] border-r border-white/10 overflow-y-auto p-3 space-y-1.5"
                      initial={{ x: -256 }}
                      animate={{ x: 0 }}
                      exit={{ x: -256 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="flex items-center justify-between px-2 py-1 mb-2">
                        <p className="text-[9px] font-bold uppercase tracking-widest text-gray-500">
                          Templates
                        </p>
                        <button
                          onClick={() => setSidebarOpen(false)}
                          className="p-1 rounded text-gray-400 hover:text-white"
                          aria-label="Close template list"
                        >
                          <X size={12} />
                        </button>
                      </div>
                      {templates.map((t) => {
                        const isActive = t.id === activeTemplateId;
                        return (
                          <button
                            key={t.id}
                            onClick={() => {
                              changeTemplate(t.id);
                              setSidebarOpen(false);
                            }}
                            className={`w-full text-left px-3 py-2.5 rounded-xl text-xs transition-all ${
                              isActive
                                ? "bg-[#7BC4BE] text-[#1A2B2A] font-bold shadow-md shadow-[#7BC4BE]/15"
                                : "text-gray-400 hover:text-white hover:bg-white/5"
                            }`}
                          >
                            <div className="flex items-center gap-2">
                              <span
                                className="w-2.5 h-2.5 rounded-full shrink-0 border"
                                style={{
                                  backgroundColor:
                                    t.color_scheme?.primary || "#888",
                                  borderColor: isActive
                                    ? "rgba(0,0,0,0.2)"
                                    : "rgba(255,255,255,0.1)",
                                }}
                              />
                              <div className="truncate">
                                <div className="font-semibold truncate">
                                  {t.name}
                                </div>
                                <div
                                  className={`text-[9px] ${
                                    isActive
                                      ? "text-[#1A2B2A]/60"
                                      : "text-gray-500"
                                  }`}
                                >
                                  {t.category}
                                </div>
                              </div>
                            </div>
                          </button>
                        );
                      })}
                    </motion.div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Center: Preview Area */}
              <div
                ref={scrollContainerRef}
                className="flex-1 overflow-auto flex items-start justify-center p-4 sm:p-8"
                style={{
                  background:
                    "radial-gradient(circle at center, #16302F 0%, #0F1E1E 70%)",
                }}
              >
                <div
                  className="transition-transform duration-300 ease-out origin-top"
                  style={{ transform: `scale(${zoom})` }}
                >
                  <div className="w-[794px] shadow-2xl rounded-sm overflow-hidden">
                    <ResumePreview
                      data={DUMMY_RESUME_DATA}
                      template={activeTemplateId}
                    />
                  </div>
                </div>
              </div>

              {/* Right: Details Panel */}
              <div className="w-72 border-l border-white/10 overflow-y-auto shrink-0 p-5 flex-col gap-5 hidden lg:flex">
                {activeTemplate && (
                  <>
                    {/* Template Info */}
                    <div>
                      <h3 className="text-sm font-bold text-white mb-1">
                        {activeTemplate.name}
                      </h3>
                      <span className="inline-block text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#7BC4BE]/15 text-[#7BC4BE]">
                        {activeTemplate.category}
                      </span>
                    </div>

                    {/* Profile Hint */}
                    <div
                      className={`px-3 py-2.5 rounded-xl text-[11px] leading-relaxed border ${
                        hasProfile
                          ? "bg-emerald-400/5 border-emerald-400/20 text-emerald-300"
                          : "bg-amber-400/5 border-amber-400/20 text-amber-300"
                      }`}
                    >
                      {hasProfile
                        ? "This template will automatically be populated using your saved profile."
                        : "You can edit every section after selecting this template."}
                    </div>

                    {/* Color Palette */}
                    <div>
                      <p className="text-[9px] font-bold uppercase tracking-widest text-gray-500 mb-2">
                        Color Palette
                      </p>
                      <div className="flex gap-2">
                        {["primary", "secondary", "accent", "text"].map(
                          (key) => (
                            <div
                              key={key}
                              className="flex flex-col items-center gap-1"
                            >
                              <div
                                className="w-8 h-8 rounded-lg border border-white/10"
                                style={{
                                  backgroundColor:
                                    activeTemplate.color_scheme?.[key] ||
                                    "#888",
                                }}
                              />
                              <span className="text-[8px] text-gray-500 capitalize">
                                {key}
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>

                    {/* Layout Details */}
                    <div>
                      <p className="text-[9px] font-bold uppercase tracking-widest text-gray-500 mb-2">
                        Layout Details
                      </p>
                      <div className="space-y-2">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-gray-400">Structure</span>
                          <span className="text-white font-medium capitalize">
                            {(
                              activeTemplate.layout_schema?.structure ||
                              "single-column"
                            ).replace(/-/g, " ")}
                          </span>
                        </div>
                        <div className="flex justify-between text-[11px]">
                          <span className="text-gray-400">Font</span>
                          <span className="text-white font-medium capitalize">
                            {activeTemplate.layout_schema?.fontFamily ||
                              "sans-serif"}
                          </span>
                        </div>
                        <div className="flex justify-between text-[11px]">
                          <span className="text-gray-400">Margins</span>
                          <span className="text-white font-medium">
                            {activeTemplate.layout_schema?.margins ||
                              "0.75in"}
                          </span>
                        </div>
                        <div className="flex justify-between text-[11px]">
                          <span className="text-gray-400">Header</span>
                          <span className="text-white font-medium capitalize">
                            {activeTemplate.layout_schema?.headerStyle ||
                              "left"}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Section Order */}
                    <div>
                      <p className="text-[9px] font-bold uppercase tracking-widest text-gray-500 mb-2">
                        Section Order
                      </p>
                      <div className="space-y-1">
                        {(
                          activeTemplate.layout_schema?.section_order || [
                            "summary",
                            "experience",
                            "education",
                            "skills",
                          ]
                        ).map((sec, idx) => (
                          <div
                            key={sec}
                            className="flex items-center gap-2 text-[11px] text-gray-300"
                          >
                            <span className="w-4 h-4 rounded bg-white/5 flex items-center justify-center text-[9px] font-bold text-gray-500">
                              {idx + 1}
                            </span>
                            <span className="capitalize">{sec}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Spacer */}
                    <div className="flex-1" />

                    {/* Use Template Button */}
                    <button
                      onClick={handleUseTemplate}
                      className="w-full py-3 px-4 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-lg shadow-[#7BC4BE]/20"
                      aria-label={`Use ${activeTemplate.name} template`}
                    >
                      <Sparkles size={14} />
                      Use This Template
                    </button>
                  </>
                )}
              </div>
            </div>

            {/* Mobile: Sticky bottom bar with Use Template */}
            <div className="lg:hidden border-t border-white/10 p-4 shrink-0 bg-[#0F1E1E]">
              <div className="flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold text-white truncate">
                    {activeTemplate?.name || "Template"}
                  </p>
                  <p className="text-[10px] text-gray-400">
                    {activeTemplate?.category}
                    {hasProfile && (
                      <span className="ml-1.5 text-emerald-400">
                        Profile auto-fill available
                      </span>
                    )}
                  </p>
                </div>
                <button
                  onClick={handleUseTemplate}
                  className="shrink-0 px-5 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-2"
                  aria-label={`Use ${activeTemplate?.name} template`}
                >
                  <Sparkles size={14} />
                  Use Template
                </button>
              </div>
            </div>

            {/* Name Prompt Dialog */}
            <AnimatePresence>
              {showNamePrompt && (
                <motion.div
                  className="absolute inset-0 z-[60] flex items-center justify-center bg-black/60 backdrop-blur-sm"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  role="dialog"
                  aria-modal="true"
                  aria-label="Name your resume"
                >
                  <motion.div
                    className="w-full max-w-md mx-4 bg-[#16302F] border border-white/10 rounded-2xl p-6 shadow-2xl"
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                  >
                    <h3 className="text-base font-bold text-white mb-1">
                      Name Your Resume
                    </h3>
                    <p className="text-[11px] text-gray-400 mb-1">
                      This helps you identify it in your dashboard.
                    </p>
                    <p className="text-[10px] text-gray-500 mb-4">
                      You can change it later.
                    </p>

                    <div className="mb-1">
                      <label
                        htmlFor="resume-name-input"
                        className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5"
                      >
                        Resume Name
                      </label>
                      <input
                        ref={nameInputRef}
                        id="resume-name-input"
                        type="text"
                        value={resumeName}
                        onChange={handleNameChange}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" && !creating) handleConfirmUse();
                        }}
                        placeholder="e.g. Software Engineer - Google Application"
                        maxLength={MAX_NAME_LENGTH + 5}
                        aria-invalid={Boolean(nameError)}
                        aria-describedby={
                          nameError ? "resume-name-error" : "resume-name-hint"
                        }
                        className={`w-full bg-white/5 border rounded-xl py-3 px-4 text-white text-sm focus:outline-none focus:border-[#7BC4BE] placeholder-gray-500 transition-colors ${
                          nameError
                            ? "border-rose-400/60"
                            : "border-white/10"
                        }`}
                      />
                    </div>

                    {/* Character count + error */}
                    <div className="flex items-center justify-between mb-4 min-h-[18px]">
                      <span
                        id="resume-name-error"
                        role="alert"
                        className="text-[10px] text-rose-400 flex items-center gap-1"
                      >
                        {nameError && (
                          <>
                            <AlertCircle size={10} />
                            {nameError}
                          </>
                        )}
                      </span>
                      <span
                        id="resume-name-hint"
                        className={`text-[10px] tabular-nums ${
                          resumeName.length > MAX_NAME_LENGTH
                            ? "text-rose-400"
                            : "text-gray-500"
                        }`}
                      >
                        {resumeName.length}/{MAX_NAME_LENGTH}
                      </span>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          if (!creating) setShowNamePrompt(false);
                        }}
                        disabled={creating}
                        className="flex-1 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 rounded-xl text-xs font-semibold transition-all disabled:opacity-50"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={handleConfirmUse}
                        disabled={creating || !resumeName.trim()}
                        className="flex-1 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        aria-label="Create resume and open editor"
                      >
                        {creating ? (
                          <>
                            <Loader2 size={12} className="animate-spin" />
                            Creating your resume...
                          </>
                        ) : (
                          <>
                            <Sparkles size={12} />
                            Create & Edit
                          </>
                        )}
                      </button>
                    </div>
                  </motion.div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
