import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, FileText, Loader2, Bot, User, ArrowLeft } from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { saveGuestSession } from "../utils/guestSession";
import TemplateSelection from "../components/TemplateSelection";

/**
 * Strip JSON code blocks from AI response text.
 * Removes ```json ... ``` blocks and generic ``` ... ``` blocks containing JSON.
 * Falls back to a default confirmation message if the result is empty.
 */
function stripJsonBlocks(text) {
  if (!text || typeof text !== "string") return text;
  let cleaned = text.replace(/```json\s*[\s\S]*?```/g, "");
  cleaned = cleaned.replace(/```\s*[\s\S]*?```/g, "");
  cleaned = cleaned.trim();
  if (!cleaned) {
    return "I have enough information to build your resume! Click the button below to get started.";
  }
  return cleaned;
}

export default function AIChatPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [structuredData, setStructuredData] = useState(null);
  const [showTemplateSelection, setShowTemplateSelection] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState("harvard");
  const isGuest = location.state?.isGuest ?? !user;
  const prefillData = location.state?.prefill ?? null;
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize chat session
  useEffect(() => {
    (async () => {
      try {
        const session = await api.chat.createSession("Resume Building Chat");
        setSessionId(session.id);

        // Load existing messages if any
        const existingMessages = await api.chat.getMessages(session.id);
        if (existingMessages.length > 0) {
          setMessages(existingMessages);
        } else {
          // Add welcome message with prefill context if available
          let welcomeContent = "Hi! I'm your AI career advisor. I'll help you build a technically strong, ATS-friendly resume.\n\nLet's start with the basics - what role are you targeting? For example: Software Engineer, Data Scientist, Product Manager, etc.";
          
          if (prefillData?.name) {
            welcomeContent = `Hi ${prefillData.name}! I'm your AI career advisor. I'll help you build a technically strong, ATS-friendly resume.\n\nI see you're interested in building a resume. What role are you targeting? For example: Software Engineer, Data Scientist, Product Manager, etc.`;
          }
          
          setMessages([
            {
              id: "welcome",
              role: "assistant",
              content: welcomeContent,
            },
          ]);
        }
      } catch (err) {
        console.error("Failed to initialize session:", err);
        // Show welcome message with retry option
        setMessages([
          {
            id: "welcome",
            role: "assistant",
            content:
              "Hi! I'm your AI career advisor. I'll help you build a technically strong, ATS-friendly resume.\n\nLet's start with the basics - what role are you targeting?",
          },
        ]);
        // Show retry message after a delay
        setTimeout(() => {
          setMessages((prev) => [
            ...prev,
            {
              id: "session-error",
              role: "assistant",
              content:
                "⚠️ Unable to connect to the chat session. You can still type messages, but they may not be saved. Refresh the page to retry.",
            },
          ]);
        }, 1000);
      } finally {
        setInitializing(false);
      }
    })();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    // Check if we have a valid session
    if (!sessionId) {
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content:
            "Unable to connect to the chat session. Please refresh the page to try again.",
        },
      ]);
      return;
    }

    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    // Add user message to UI immediately
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: userMessage,
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      // Send to backend - backend controls the conversation
      const response = await api.chat.sendMessage(sessionId, userMessage);

      // Remove temp message and add real messages
      // Strip JSON code blocks from assistant messages before rendering
      const cleanMessage = stripJsonBlocks(response.message);
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMsg.id);
        return [
          ...filtered,
          {
            id: `user-${Date.now()}`,
            role: "user",
            content: userMessage,
          },
          {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: cleanMessage,
          },
        ];
      });

      // Check if AI returned structured data (resume ready to generate)
      if (response.structured_data) {
        setStructuredData(response.structured_data);
      }
    } catch (err) {
      console.error("Failed to send message:", err);
      // Remove temp message and show error
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMsg.id);
        return [
          ...filtered,
          {
            id: `error-${Date.now()}`,
            role: "assistant",
            content:
              "I apologize, but I encountered an error. Please try again.",
          },
        ];
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleGenerateResume = async () => {
    if (!structuredData) return;
    // Show template selection for both guest and authenticated users
    setShowTemplateSelection(true);
  };

  const handleTemplateConfirm = async (templateId) => {
    setSelectedTemplate(templateId);
    setLoading(true);
    try {
      if (isGuest || !user) {
        // Guest: Build resume data locally and navigate to template selection
        const resumeData = convertStructuredDataToResume(structuredData, prefillData);
        
        // Save to unified guest session
        saveGuestSession({
          basicInfo: prefillData || {},
          chatHistory: messages,
          generatedResume: resumeData,
          selectedTemplate: templateId,
          sectionOrder: resumeData.section_order,
          createdAt: new Date().toISOString(),
        });
        
        // Navigate to guest editor with editor step
        navigate("/resume/guest-edit", { state: { step: "editor" } });
      } else {
        // Authenticated: Create resume via backend, then update template
        const prompt = JSON.stringify(structuredData);
        const resume = await api.resumes.generateFromPrompt(prompt, "experienced");
        // Update template if not default
        if (templateId !== "harvard") {
          await api.resumes.update(resume.id, resume.title, templateId);
        }
        // Persist initial section_order
        await api.resumes.update(
          resume.id,
          resume.title,
          templateId,
          ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]
        );
        navigate(`/resume/edit/${resume.id}`);
      }
    } catch (err) {
      console.error("Failed to generate resume:", err);
      if (!isGuest && user) {
        // Try alternative for authenticated users
        try {
          const resume = await api.resumes.create("My Resume", templateId);
          navigate(`/resume/edit/${resume.id}`);
        } catch {
          alert("Failed to create resume. Please try again.");
        }
      } else {
        alert("Failed to generate resume. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleBackToChat = useCallback(() => {
    setShowTemplateSelection(false);
  }, []);

  // Convert AI structured data to resume editor format
  const convertStructuredDataToResume = (data, prefill) => {
    const normalizeDescription = (desc) => {
      if (Array.isArray(desc)) return desc.join("\n");
      return desc || "";
    };

    const personalInfo = {
      fullName: prefill?.name || data.personalInfo?.fullName || "",
      jobTitle: data.personalInfo?.jobTitle || data.targetRole || "",
      email: prefill?.email || data.personalInfo?.email || "",
      phone: prefill?.phone || data.personalInfo?.phone || "",
      location: prefill?.location || data.personalInfo?.location || "",
      website: prefill?.website || data.personalInfo?.website || "",
      linkedin: prefill?.linkedin || data.personalInfo?.linkedin || "",
    };

    const experience = (data.experience || []).map(exp => ({
      company: exp.company || "",
      role: exp.role || exp.title || "",
      duration: exp.duration || exp.dates || "",
      description: normalizeDescription(exp.description || exp.bullets),
    }));

    const education = (data.education || []).map(edu => ({
      institution: edu.institution || edu.school || "",
      degree: edu.degree || "",
      duration: edu.duration || edu.dates || "",
      description: normalizeDescription(edu.details || edu.description),
    }));

    const skills = data.skills || [];
    
    const projects = (data.projects || []).map(proj => ({
      name: proj.name || proj.title || "",
      description: normalizeDescription(proj.description),
    }));

    return {
      personalInfo,
      summary: data.summary || "",
      experience,
      education,
      skills,
      projects,
      certifications: data.certifications || [],
      achievements: data.achievements || [],
      section_order: ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"],
    };
  };

  if (initializing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 text-teal-400 animate-spin mx-auto mb-4" />
          <p className="text-teal-200">Initializing AI Career Advisor...</p>
        </div>
      </div>
    );
  }

  // Template selection view
  if (showTemplateSelection && structuredData) {
    const convertedData = convertStructuredDataToResume(structuredData, prefillData);
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900">
        {/* Header with back button */}
        <header className="bg-slate-900/80 backdrop-blur-sm border-b border-teal-800/50 px-4 py-3">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <button
              onClick={handleBackToChat}
              className="flex items-center gap-1.5 text-teal-300 hover:text-white text-sm transition-colors"
            >
              <ArrowLeft size={16} />
              <span>Back to Chat</span>
            </button>
            <div className="h-5 w-px bg-teal-800/50" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
              <span className="text-white font-semibold text-sm">Select a Template</span>
            </div>
          </div>
        </header>
        <TemplateSelection
          resumeData={convertedData}
          selectedTemplate={selectedTemplate}
          onSelect={handleTemplateConfirm}
          onBack={handleBackToChat}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-teal-900 to-slate-900 flex flex-col">
      {/* Header */}
      <header className="bg-slate-900/80 backdrop-blur-sm border-b border-teal-800/50 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-teal-400 to-teal-600 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-white font-semibold">AI Career Advisor</h1>
              <p className="text-teal-300 text-xs">
                {isGuest ? "Guest Mode - Sign in to save your resume" : "Building your resume through conversation"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {isGuest && (
              <button
                onClick={() => navigate("/login", { state: { returnUrl: "/resume/create" } })}
                className="px-3 py-1.5 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-semibold transition-all"
              >
                Sign In
              </button>
            )}
            <button
              onClick={() => navigate(isGuest ? "/" : "/")}
              className="text-teal-300 hover:text-white text-sm transition-colors"
            >
              Exit Chat
            </button>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <AnimatePresence>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-3 ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-lg bg-teal-500/20 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-teal-400" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-teal-600 text-white"
                      : "bg-slate-800/80 text-slate-100 border border-slate-700/50"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-slate-300" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-teal-500/20 flex items-center justify-center">
                <Bot className="w-4 h-4 text-teal-400" />
              </div>
              <div className="bg-slate-800/80 border border-slate-700/50 rounded-2xl px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-teal-400 rounded-full animate-bounce" />
                  <span
                    className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.1s" }}
                  />
                  <span
                    className="w-2 h-2 bg-teal-400 rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Generate Resume Button (when structured data is ready) */}
      <AnimatePresence>
        {structuredData && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="px-4 pb-4"
          >
            <div className="max-w-4xl mx-auto">
              {isGuest && (
                <p className="text-teal-300 text-xs text-center mb-2">
                  Sign in to save and download your resume
                </p>
              )}
              <button
                onClick={handleGenerateResume}
                disabled={loading}
                className="w-full bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-3 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <FileText className="w-5 h-5" />
                )}
                {isGuest ? "Sign In & Generate Resume" : "Generate My Resume"}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="bg-slate-900/80 backdrop-blur-sm border-t border-teal-800/50 px-4 py-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={!sessionId ? "Connecting..." : "Tell me about your experience, skills, or ask a question..."}
              disabled={loading || !sessionId}
              maxLength={5000}
              className="flex-1 bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500/50 disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading || !sessionId}
              className="bg-teal-600 hover:bg-teal-700 text-white rounded-xl px-4 py-3 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-slate-500 text-xs mt-2 text-center">
            {!sessionId 
              ? "Connecting to AI advisor..."
              : "The AI will guide you through building your resume. Be as detailed as possible."
            }
          </p>
        </div>
      </div>
    </div>
  );
}
