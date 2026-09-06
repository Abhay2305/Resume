import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  ArrowLeft,
  Play,
  RefreshCw,
  FileText,
  Trash2,
} from "lucide-react";
import { api } from "../services/api";

import ResumeOverviewCard from "../components/ResumeOverviewCard";
import ResumePersonalInfoCard from "../components/ResumePersonalInfoCard";
import ResumeSummaryCard from "../components/ResumeSummaryCard";
import ExperienceTimeline from "../components/ExperienceTimeline";
import EducationCard from "../components/EducationCard";
import ProjectCard from "../components/ProjectCard";
import SkillCategoryCard from "../components/SkillCategoryCard";
import CertificationCard from "../components/CertificationCard";
import ResumeKnowledgeCard from "../components/ResumeKnowledgeCard";
import ResumeLoading from "../components/ResumeLoading";
import ResumeEmptyState from "../components/ResumeEmptyState";
import ResumeErrorState from "../components/ResumeErrorState";

// ─── List View ──────────────────────────────────────────────────────────────

function ResumeList() {
  const navigate = useNavigate();
  const mountedRef = useRef(true);
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const loadProfiles = useCallback(async (p = 1) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.resumeIntelligence.list(p, 20);
      if (!mountedRef.current) return;
      setProfiles(res.items || []);
      setTotal(res.total || 0);
      setPage(res.page || p);
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err.message || "Failed to load resumes.");
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProfiles(1);
    return () => { mountedRef.current = false; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    try {
      await api.resumeIntelligence.delete(id);
      setProfiles((prev) => prev.filter((p) => p.id !== id));
      setTotal((prev) => prev - 1);
    } catch (err) {
      alert(err.message || "Failed to delete resume.");
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "—";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const STATUS_COLORS = {
    parsed: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    parsing: "text-amber-400 bg-amber-400/10 border-amber-400/20",
    pending: "text-gray-400 bg-white/5 border-white/10",
    failed: "text-rose-400 bg-rose-400/10 border-rose-400/20",
    archived: "text-gray-500 bg-white/5 border-white/10",
  };

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
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
                  <Brain size={16} className="text-white" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  Resume Intelligence
                </h1>
              </div>
              <p className="text-gray-400 text-xs mt-1">
                AI-parsed resume profiles with extracted knowledge and structured intelligence.
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <ResumeLoading variant="cards" />
        ) : error ? (
          <ResumeErrorState message={error} onRetry={() => loadProfiles(page)} />
        ) : profiles.length === 0 ? (
          <ResumeEmptyState type="profiles" />
        ) : (
          <div className="space-y-4">
            {profiles.map((profile) => (
              <div
                key={profile.id}
                className="bg-white/5 border border-white/10 rounded-2xl p-5 flex items-center justify-between hover:bg-white/[0.07] transition-all cursor-pointer"
                onClick={() => navigate(`/resume-intelligence/${profile.id}`)}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-[#7BC4BE]/15 flex items-center justify-center shrink-0">
                    <FileText size={18} className="text-[#7BC4BE]" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-white">
                      {profile.title || "Untitled Resume"}
                    </p>
                    <div className="flex items-center gap-3 mt-1">
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${
                          STATUS_COLORS[profile.status] || STATUS_COLORS.pending
                        }`}
                      >
                        {profile.status}
                      </span>
                      <span className="text-[11px] text-gray-500">
                        {formatDate(profile.created_at)}
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(profile.id);
                  }}
                  className="p-2 rounded-lg text-gray-500 hover:text-rose-400 hover:bg-rose-400/10 transition-all"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}

            {/* Pagination */}
            {total > 20 && (
              <div className="flex items-center justify-center gap-3 pt-4">
                <button
                  onClick={() => loadProfiles(page - 1)}
                  disabled={page <= 1}
                  className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs font-semibold text-gray-400 hover:text-white hover:bg-white/10 transition-all disabled:opacity-30"
                >
                  Previous
                </button>
                <span className="text-xs text-gray-500">
                  Page {page} of {Math.ceil(total / 20)}
                </span>
                <button
                  onClick={() => loadProfiles(page + 1)}
                  disabled={page >= Math.ceil(total / 20)}
                  className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs font-semibold text-gray-400 hover:text-white hover:bg-white/10 transition-all disabled:opacity-30"
                >
                  Next
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Detail View ────────────────────────────────────────────────────────────

function ResumeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const mountedRef = useRef(true);

  const [profile, setProfile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [entities, setEntities] = useState([]);
  const [knowledge, setKnowledge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [parseResult, setParseResult] = useState(null);

  async function fetchDetail() {
    setLoading(true);
    setError(null);
    try {
      const profileData = await api.resumeIntelligence.get(id);
      if (!mountedRef.current) return;
      setProfile(profileData);

      if (profileData.status === "parsed") {
        const [parsed, entityRes, knowledgeRes] = await Promise.allSettled([
          api.resumeIntelligence.getParsed(id),
          api.resumeIntelligence.getEntities(id),
          api.resumeIntelligence.getKnowledge(id),
        ]);

        if (!mountedRef.current) return;
        if (parsed.status === "fulfilled") setParsedData(parsed.value?.data || null);
        if (entityRes.status === "fulfilled") setEntities(entityRes.value?.data || []);
        if (knowledgeRes.status === "fulfilled") setKnowledge(knowledgeRes.value?.data || null);
      }
    } catch (err) {
      if (!mountedRef.current) return;
      setError(err.message || "Failed to load resume details.");
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }

  useEffect(() => {
    mountedRef.current = true;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const profileData = await api.resumeIntelligence.get(id);
        if (!mountedRef.current) return;
        setProfile(profileData);

        if (profileData.status === "parsed") {
          const [parsed, entityRes, knowledgeRes] = await Promise.allSettled([
            api.resumeIntelligence.getParsed(id),
            api.resumeIntelligence.getEntities(id),
            api.resumeIntelligence.getKnowledge(id),
          ]);

          if (!mountedRef.current) return;
          if (parsed.status === "fulfilled") setParsedData(parsed.value?.data || null);
          if (entityRes.status === "fulfilled") setEntities(entityRes.value?.data || []);
          if (knowledgeRes.status === "fulfilled") setKnowledge(knowledgeRes.value?.data || null);
        }
      } catch (err) {
        if (!mountedRef.current) return;
        setError(err.message || "Failed to load resume details.");
      } finally {
        if (mountedRef.current) setLoading(false);
      }
    })();
    return () => { mountedRef.current = false; };
  }, [id]);

  const handleParse = async () => {
    setParsing(true);
    setParseResult(null);
    try {
      const res = await api.resumeIntelligence.parse(id);
      setParseResult(res);
      // Reload detail after parsing
      await fetchDetail();
    } catch (err) {
      setParseResult({ error: err.message || "Parse failed." });
    } finally {
      setParsing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate("/resume-intelligence")}
              className="p-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
            >
              <ArrowLeft size={16} />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#7BC4BE] to-[#4A9E98] flex items-center justify-center">
                  <Brain size={16} className="text-white" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  {profile?.title || "Resume Intelligence"}
                </h1>
              </div>
              <p className="text-gray-400 text-xs mt-1">
                Structured intelligence extracted from your resume.
              </p>
            </div>
          </div>

          {profile?.status !== "parsed" && (
            <button
              onClick={handleParse}
              disabled={parsing}
              className="px-4 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {parsing ? (
                <>
                  <RefreshCw size={14} className="animate-spin" />
                  Parsing...
                </>
              ) : (
                <>
                  <Play size={14} />
                  Parse Resume
                </>
              )}
            </button>
          )}
        </div>

        {/* Parse result notification */}
        {parseResult && (
          <div className="mb-6">
            {parseResult.error ? (
              <div className="bg-rose-500/10 border border-rose-500/20 rounded-2xl p-4">
                <p className="text-xs text-rose-400 font-semibold">
                  Parse failed: {parseResult.error}
                </p>
              </div>
            ) : (
              <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-4">
                <p className="text-xs text-emerald-400 font-semibold">
                  Resume parsed successfully. Status: {parseResult.status}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Content */}
        {loading ? (
          <ResumeLoading variant="spinner" />
        ) : error ? (
          <ResumeErrorState message={error} onRetry={fetchDetail} />
        ) : !profile ? (
          <ResumeEmptyState type="detail" />
        ) : (
          <AnimatePresence mode="wait">
            <motion.div
              key="detail"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="space-y-6"
            >
              {/* Overview */}
              <ResumeOverviewCard profile={profile} />

              {/* Knowledge-based sections */}
              {knowledge && (
                <>
                  <ResumePersonalInfoCard knowledge={knowledge} />
                  <ResumeSummaryCard knowledge={knowledge} parsedData={parsedData} />
                  <ExperienceTimeline knowledge={knowledge} parsedData={parsedData} />
                  <EducationCard knowledge={knowledge} parsedData={parsedData} />
                  <ProjectCard knowledge={knowledge} parsedData={parsedData} />
                  <SkillCategoryCard knowledge={knowledge} entities={entities} />
                  <CertificationCard knowledge={knowledge} />
                  <ResumeKnowledgeCard knowledge={knowledge} />
                </>
              )}

              {/* Fallback: parsed data without knowledge */}
              {!knowledge && parsedData && (
                <>
                  <ResumeSummaryCard knowledge={null} parsedData={parsedData} />
                  <ExperienceTimeline knowledge={null} parsedData={parsedData} />
                  <EducationCard knowledge={null} parsedData={parsedData} />
                  <ProjectCard knowledge={null} parsedData={parsedData} />
                </>
              )}

              {/* No parsed data yet */}
              {!knowledge && !parsedData && profile.status !== "parsed" && (
                <ResumeEmptyState type="parse" />
              )}
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}

// ─── Main Export ────────────────────────────────────────────────────────────

export default function ResumeIntelligencePage() {
  const { id } = useParams();
  return id ? <ResumeDetail /> : <ResumeList />;
}
