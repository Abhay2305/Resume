import { useState, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, RefreshCw, Sparkles } from "lucide-react";
import { api } from "../services/api";
import JDInputStep from "../components/jd/JDInputStep";
import ResumeSelectStep from "../components/jd/ResumeSelectStep";
import AnalysisProgress from "../components/jd/AnalysisProgress";
import ResultsTabs from "../components/jd/ResultsTabs";
import QuickActions from "../components/jd/QuickActions";

const WIZARD_STEPS = [
  { id: "jd", label: "Job Description" },
  { id: "resume", label: "Select Resume" },
  { id: "analyzing", label: "Analyzing" },
  { id: "results", label: "Results" },
];

const PIPELINE_STEPS = [
  "understanding_jd",
  "reading_resume",
  "finding_gaps",
  "matching_ats",
  "applying_best_practices",
  "generating_resume",
  "reviewing",
];


export default function JDBasedPage() {
  const navigate = useNavigate();
  const [wizardStep, setWizardStep] = useState(0);
  const [loading] = useState(false);
  const [error, setError] = useState(null);

  // Pipeline state
  const [currentPipelineStep, setCurrentPipelineStep] = useState(null);
  const [completedSteps, setCompletedSteps] = useState([]);

  // Per-stage timing, errors, and status tracking
  const [stageErrors, setStageErrors] = useState({});
  const [stageStatuses, setStageStatuses] = useState({});
  const [stageTimings, setStageTimings] = useState({});
  const pipelineStartTimeRef = useRef(null);
  const pipelineRunningRef = useRef(false);

  // Data state
  const [jdText, setJdText] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [resumeId, setResumeId] = useState(null);

  // Results state
  const [scores, setScores] = useState(null);
  const [gaps, setGaps] = useState([]);
  const [changes, setChanges] = useState([]);
  const [validation, setValidation] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [knowledgeContext, setKnowledgeContext] = useState(null);
  const [resumeContent, setResumeContent] = useState(null);

  const mountedRef = useRef(true);

  // Stage timing helpers
  const startStage = (stepId) => {
    setStageTimings((prev) => ({ ...prev, [stepId]: performance.now() }));
    setStageStatuses((prev) => ({ ...prev, [stepId]: "running" }));
  };

  const completeStage = (stepId) => {
    setStageTimings((prev) => {
      const startTime = prev[stepId];
      if (startTime) {
        return { ...prev, [stepId]: performance.now() - startTime };
      }
      return prev;
    });
    setStageStatuses((prev) => ({ ...prev, [stepId]: "completed" }));
  };

  const failStage = (stepId, errMsg) => {
    setStageTimings((prev) => {
      const startTime = prev[stepId];
      if (startTime) {
        return { ...prev, [stepId]: performance.now() - startTime };
      }
      return prev;
    });
    setStageStatuses((prev) => ({ ...prev, [stepId]: "failed" }));
    setStageErrors((prev) => ({ ...prev, [stepId]: errMsg }));
  };

  const advancePipeline = useCallback((stepId) => {
    setCompletedSteps((prev) => [...prev, stepId]);
    const nextIndex = PIPELINE_STEPS.indexOf(stepId) + 1;
    if (nextIndex < PIPELINE_STEPS.length) {
      setCurrentPipelineStep(PIPELINE_STEPS[nextIndex]);
    }
  }, []);

  // Step 1: Handle JD submission
  const handleJDNext = async (text) => {
    setJdText(text);
    setWizardStep(1);
  };

  // Step 2: Handle Resume submission - trigger full pipeline
  const handleResumeNext = async (text, selectedResumeId) => {
    if (pipelineRunningRef.current) return;
    pipelineRunningRef.current = true;

    setResumeText(text);
    setResumeId(selectedResumeId);
    setWizardStep(2);
    setError(null);
    setStageErrors({});
    setStageStatuses({});
    setStageTimings({});
    pipelineStartTimeRef.current = performance.now();

    // Start pipeline
    setCurrentPipelineStep(PIPELINE_STEPS[0]);
    setCompletedSteps([]);

    try {
      // Stage 1: Create and parse Opportunity (JD)
      setCurrentPipelineStep("understanding_jd");
      startStage("understanding_jd");
      const opp = await api.opportunities.create(jdText);
      if (!mountedRef.current) return;

      // Parse the JD
      await api.opportunities.parse(opp.id);
      completeStage("understanding_jd");
      advancePipeline("understanding_jd");

      // Stage 2: Create and parse Resume Intelligence
      setCurrentPipelineStep("reading_resume");
      startStage("reading_resume");
      let profileId = selectedResumeId;
      if (!profileId) {
        const profile = await api.resumeIntelligence.create(text, "JD Tailored Resume");
        profileId = profile.id;
      }
      if (!mountedRef.current) return;

      await api.resumeIntelligence.parse(profileId);
      completeStage("reading_resume");
      advancePipeline("reading_resume");

      // Stage 3: Gap Analysis
      setCurrentPipelineStep("finding_gaps");
      startStage("finding_gaps");
      const gap = await api.gapAnalysis.create(profileId, opp.id);
      if (!mountedRef.current) return;

      const analyzed = await api.gapAnalysis.analyze(gap.id);
      if (!mountedRef.current) return;
      setScores(analyzed);

      const gapDetails = await api.gapAnalysis.getGaps(gap.id);
      if (!mountedRef.current) return;
      setGaps(gapDetails?.gap_results || gapDetails || []);
      completeStage("finding_gaps");
      advancePipeline("finding_gaps");

      // Stage 4: ATS Keywords (part of gap analysis, just advance)
      setCurrentPipelineStep("matching_ats");
      startStage("matching_ats");
      completeStage("matching_ats");
      advancePipeline("matching_ats");

      // Stage 5: Knowledge Retrieval (non-fatal)
      setCurrentPipelineStep("applying_best_practices");
      startStage("applying_best_practices");
      try {
        await api.knowledge.retrieve(gap.id);
        const kContext = await api.knowledge.getContext(gap.id);
        if (!mountedRef.current) return;
        setKnowledgeContext(kContext?.context || kContext);
        completeStage("applying_best_practices");
      } catch (knowledgeErr) {
        failStage("applying_best_practices", knowledgeErr.message || "Knowledge retrieval failed");
        setStageStatuses((prev) => ({ ...prev, applying_best_practices: "failed" }));
      }
      advancePipeline("applying_best_practices");

      // Get recommendations
      const recs = await api.gapAnalysis.getRecommendations(gap.id);
      if (!mountedRef.current) return;
      setRecommendations(recs?.recommendations || recs || []);

      // Stage 6: Prompt Building + AI Execution
      setCurrentPipelineStep("generating_resume");
      startStage("generating_resume");
      const promptPkg = await api.promptIntelligence.build(gap.id);
      if (!mountedRef.current) return;

      const execution = await api.aiExecution.execute(promptPkg.package_id);
      if (!mountedRef.current) return;

      const aiResponse = await api.aiExecution.getResponse(execution.execution_id);
      if (!mountedRef.current) return;

      const parsedResponse = aiResponse?.parsed_response;
      if (parsedResponse?.resume_content) {
        setResumeContent(parsedResponse.resume_content);
      } else if (parsedResponse?.content) {
        setResumeContent(parsedResponse.content);
      } else if (typeof parsedResponse === "string") {
        setResumeContent(parsedResponse);
      } else {
        const rawResp = await api.aiExecution.get(execution.execution_id);
        setResumeContent(rawResp?.raw_response || "Resume content generated successfully.");
      }
      completeStage("generating_resume");
      advancePipeline("generating_resume");

      // Stage 7: Validation (non-fatal, skippable)
      setCurrentPipelineStep("reviewing");
      startStage("reviewing");
      try {
        const validation_ = await api.aiResponseIntelligence.validate(execution.execution_id);
        if (!mountedRef.current) return;
        setValidation(validation_);

        const changesData = await api.aiResponseIntelligence.getChanges(validation_.validation_id);
        if (!mountedRef.current) return;
        setChanges(changesData?.changes || changesData || []);
        completeStage("reviewing");
      } catch (validationErr) {
        failStage("reviewing", validationErr.message || "Validation failed");
        setStageStatuses((prev) => ({ ...prev, reviewing: "failed" }));
      }
      advancePipeline("reviewing");

      // All done - show results
      setCurrentPipelineStep(null);
      setWizardStep(3);
    } catch (err) {
      console.error("Pipeline error:", err);
      if (mountedRef.current) {
        // Mark current step as failed
        if (currentPipelineStep) {
          failStage(currentPipelineStep, err.message || "Stage failed");
        }

        // Handle specific error types
        if (err.status === 401) {
          setError("Your session has expired. Please log in again.");
        } else if (err.status === 403) {
          setError("You do not have permission to perform this action.");
        } else if (err.status >= 500) {
          setError("Server error. Please try again later.");
        } else if (err.message?.includes("timeout") || err.message?.includes("Timeout")) {
          setError("Request timed out. Please try again.");
        } else {
          setError(err.message || "An error occurred during analysis. Please try again.");
        }
      }
    } finally {
      pipelineRunningRef.current = false;
    }
  };

  const handleRetry = () => {
    setError(null);
    setStageErrors({});
    setStageStatuses({});
    setStageTimings({});
    setWizardStep(2);
    handleResumeNext(resumeText, resumeId);
  };

  const handleAccept = () => {
    alert("Changes accepted! Your resume has been updated.");
  };

  const handleEdit = () => {
    navigate("/dashboard");
  };

  const handleExport = async () => {
    if (!resumeContent) return;
    try {
      const blob = await api.pdf.export(
        `<div style="font-family: Georgia, serif; padding: 40px; line-height: 1.6; white-space: pre-wrap;">${resumeContent}</div>`,
        "tailored-resume.pdf"
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "tailored-resume.pdf";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Failed to export PDF: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white">
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate("/dashboard")}
              className="p-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
            >
              <ArrowLeft size={16} />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#7BC4BE] to-[#4A9E98] flex items-center justify-center">
                  <Sparkles size={16} className="text-white" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  JD-Based Resume Builder
                </h1>
              </div>
              <p className="text-gray-400 text-xs mt-1">
                Tailor your resume to any job description using AI
              </p>
            </div>
          </div>
          {wizardStep === 3 && (
            <button
              onClick={() => {
                setWizardStep(0);
                setJdText("");
                setResumeText("");
                setScores(null);
                setGaps([]);
                setChanges([]);
                setRecommendations([]);
                setKnowledgeContext(null);
                setResumeContent(null);
                setValidation(null);
                setCompletedSteps([]);
                setCurrentPipelineStep(null);
                setError(null);
                setStageErrors({});
                setStageStatuses({});
                setStageTimings({});
                pipelineStartTimeRef.current = null;
              }}
              className="px-4 py-2 bg-white/10 hover:bg-white/15 text-white border border-white/10 rounded-xl text-xs font-semibold transition-all flex items-center gap-2"
            >
              <RefreshCw size={14} />
              Start New
            </button>
          )}
        </div>

        {/* Step Indicator */}
        <div className="flex justify-center gap-2 mb-8">
          {WIZARD_STEPS.map((step, i) => (
            <button
              key={step.id}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[10px] font-semibold transition-all ${
                i === wizardStep
                  ? "bg-[#7BC4BE] text-[#1A2B2A]"
                  : i < wizardStep
                  ? "bg-[#7BC4BE]/20 text-[#7BC4BE]"
                  : "bg-white/5 text-gray-500"
              }`}
            >
              {i < wizardStep ? "✓" : i + 1}
              {step.label}
            </button>
          ))}
        </div>

        {/* Quick Actions (shown on results page) */}
        {wizardStep === 3 && (
          <div className="mb-6">
            <QuickActions jdText={jdText} resumeText={resumeContent || resumeText} />
          </div>
        )}

        {/* Step Content */}
        <div className="min-h-[400px]">
          <AnimatePresence mode="wait">
            {/* Step 1: JD Input */}
            {wizardStep === 0 && (
              <motion.div
                key="jd"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <JDInputStep onNext={handleJDNext} loading={loading} />
              </motion.div>
            )}

            {/* Step 2: Resume Select */}
            {wizardStep === 1 && (
              <motion.div
                key="resume"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <ResumeSelectStep
                  onNext={handleResumeNext}
                  onBack={() => setWizardStep(0)}
                  loading={loading}
                />
              </motion.div>
            )}

            {/* Step 3: Analyzing */}
            {wizardStep === 2 && (
              <motion.div
                key="analyzing"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <AnalysisProgress
                  currentStep={currentPipelineStep}
                  completedSteps={completedSteps}
                  error={error}
                  onRetry={error ? handleRetry : null}
                  stageTimings={stageTimings}
                  stageErrors={stageErrors}
                  stageStatuses={stageStatuses}
                />
              </motion.div>
            )}

            {/* Step 4: Results */}
            {wizardStep === 3 && (
              <motion.div
                key="results"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                <ResultsTabs
                  scores={scores}
                  gaps={gaps}
                  changes={changes}
                  validation={validation}
                  recommendations={recommendations}
                  knowledgeContext={knowledgeContext}
                  resumeContent={resumeContent}
                  onAccept={handleAccept}
                  onEdit={handleEdit}
                  onExport={handleExport}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
