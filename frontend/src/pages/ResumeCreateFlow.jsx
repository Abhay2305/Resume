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
      // 1. Submit prompt to AI FastAPI extractor
      const resume = await api.generateResumeFromPrompt(promptText, archetype);
      
      // 2. Allow the loading simulation (which has a 4 second interval) to complete for engaging UX
      setTimeout(() => {
        navigate(`/resume/edit/${resume.id}`);
      }, 4000);
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
