import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import PromptEntry from "../components/PromptEntry";
import AIGenerator from "../components/AIGenerator";

export default function ResumeCreateFlow() {
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();

  const handlePromptSubmit = async (promptText, archetype) => {
    setIsGenerating(true);
    try {
      // Run the AI generation and a minimum animation window in parallel.
      // Navigation happens only after the API call actually succeeds; the
      // minimum delay just prevents the loader from flashing on fast responses.
      const minAnimation = new Promise((resolve) => setTimeout(resolve, 2500));
      const [resume] = await Promise.all([
        api.generateResumeFromPrompt(promptText, archetype),
        minAnimation,
      ]);

      navigate(`/resume/edit/${resume.id}`);
    } catch (err) {
      alert("AI Generation failed: " + err.message);
      setIsGenerating(false);
    }
  };

  const handleStartManual = async () => {
    try {
      const res = await api.createResume("My Manual Resume", "harvard");
      navigate(`/resume/edit/${res.id}`);
    } catch (err) {
      alert("Manual initialization failed: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {isGenerating ? (
        <AIGenerator onComplete={() => {}} />
      ) : (
        <PromptEntry onSubmit={handlePromptSubmit} onStartManual={handleStartManual} />
      )}
    </div>
  );
}
