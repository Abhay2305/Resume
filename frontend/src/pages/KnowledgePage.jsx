import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  BookOpen,
  Lightbulb,
  Zap,
  Search,
  LayoutList,
  Shield,
} from "lucide-react";
import { api } from "../services/api";
import { useAuth } from "../hooks/useAuth";

import KnowledgeHeader from "../components/KnowledgeHeader";
import InsightCard from "../components/InsightCard";
import SuggestionCard from "../components/SuggestionCard";
import RecommendationGroup from "../components/RecommendationGroup";
import KnowledgeRetrievalPanel from "../components/KnowledgeRetrievalPanel";
import KnowledgeLoading from "../components/KnowledgeLoading";
import KnowledgeEmptyState from "../components/KnowledgeEmptyState";
import KnowledgeErrorState from "../components/KnowledgeErrorState";
import KnowledgeSearchBar from "../components/KnowledgeSearchBar";
import KnowledgePagination from "../components/KnowledgePagination";
import GovernancePanel from "../components/GovernancePanel";

const PAGE_SIZE = 20;

export default function KnowledgePage() {
  const { isAdmin } = useAuth();

  const TABS = [
    { id: "insights", label: "Insights", icon: Sparkles },
    { id: "recommendations", label: "Recommendations", icon: Lightbulb },
    ...(isAdmin ? [{ id: "governance", label: "Governance", icon: Shield }] : []),
    { id: "get", label: "Get Recommendations", icon: Zap },
    { id: "plan", label: "Your Plan", icon: LayoutList },
  ];

  const [activeTab, setActiveTab] = useState("insights");
  const mountedRef = useRef(true);

  // Documents (Insights) state
  const [documents, setDocuments] = useState([]);
  const [docPage, setDocPage] = useState(1);
  const [docTotal, setDocTotal] = useState(0);
  const [docLoading, setDocLoading] = useState(true);
  const [docError, setDocError] = useState(null);

  // Rules (Recommendations) state
  const [rules, setRules] = useState([]);
  const [rulePage, setRulePage] = useState(1);
  const [ruleTotal, setRuleTotal] = useState(0);
  const [ruleLoading, setRuleLoading] = useState(false);
  const [ruleError, setRuleError] = useState(null);
  const [ruleSearch, setRuleSearch] = useState("");

  // Retrieval state
  const [retrievalLoading, setRetrievalLoading] = useState(false);
  const [retrievalResult, setRetrievalResult] = useState(null);
  const [retrievalError, setRetrievalError] = useState(null);

  // Context (Plan) state
  const [context, setContext] = useState(null);
  const [contextRetrieval, setContextRetrieval] = useState(null);
  const [contextGapId, setContextGapId] = useState("");
  const [contextLoading, setContextLoading] = useState(false);
  const [contextError, setContextError] = useState(null);

  // Global
  const [refreshing, setRefreshing] = useState(false);

  // ── Documents (Insights) ──────────────────────────────────────────────────

  const loadDocuments = async (page = 1) => {
    setDocLoading(true);
    setDocError(null);
    try {
      const res = await api.knowledge.listDocuments(page, PAGE_SIZE);
      if (!mountedRef.current) return;
      setDocuments(res.items || []);
      setDocTotal(res.total || 0);
      setDocPage(res.page || page);
    } catch (err) {
      if (!mountedRef.current) return;
      console.error("Failed to load insights:", err);
      setDocError(err.message || "Failed to load knowledge sources.");
    } finally {
      if (mountedRef.current) setDocLoading(false);
    }
  };

  // ── Rules (Recommendations) ──────────────────────────────────────────────

  const loadRules = async (page = 1, search = null) => {
    setRuleLoading(true);
    setRuleError(null);
    try {
      const res = await api.knowledge.listRules(page, PAGE_SIZE, search);
      if (!mountedRef.current) return;
      setRules(res.items || []);
      setRuleTotal(res.total || 0);
      setRulePage(res.page || page);
    } catch (err) {
      if (!mountedRef.current) return;
      console.error("Failed to load recommendations:", err);
      setRuleError(err.message || "Failed to load recommendations.");
    } finally {
      if (mountedRef.current) setRuleLoading(false);
    }
  };

  const handleRuleSearch = useCallback(
    (query) => {
      setRuleSearch(query);
      loadRules(1, query || null);
    },
    []
  );

  // ── Retrieval ─────────────────────────────────────────────────────────────

  const handleRetrieve = useCallback(async (gapAnalysisId) => {
    setRetrievalLoading(true);
    setRetrievalError(null);
    setRetrievalResult(null);
    try {
      const res = await api.knowledge.retrieve(gapAnalysisId);
      if (!mountedRef.current) return;
      setRetrievalResult(res);
    } catch (err) {
      if (!mountedRef.current) return;
      console.error("Retrieval failed:", err);
      setRetrievalError(err.message || "Failed to generate recommendations.");
    } finally {
      if (mountedRef.current) setRetrievalLoading(false);
    }
  }, []);

  // ── Context (Plan) ───────────────────────────────────────────────────────

  const fetchContext = useCallback(async (gapAnalysisId) => {
    setContextLoading(true);
    setContextError(null);
    setContext(null);
    setContextRetrieval(null);
    try {
      const res = await api.knowledge.getContext(gapAnalysisId);
      if (!mountedRef.current) return;
      setContext(res.context || null);
      setContextRetrieval(res.context?.retrieval || null);
    } catch (err) {
      if (!mountedRef.current) return;
      console.error("Failed to load plan:", err);
      setContextError(err.message || "Failed to load your resume plan.");
    } finally {
      if (mountedRef.current) setContextLoading(false);
    }
  }, []);

  const handleContextSearch = useCallback(
    (e) => {
      e.preventDefault();
      if (contextGapId.trim()) {
        fetchContext(contextGapId.trim());
      }
    },
    [contextGapId, fetchContext]
  );

  // ── Initial load ──────────────────────────────────────────────────────────

  useEffect(() => {
    mountedRef.current = true;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadDocuments(1);
    return () => { mountedRef.current = false; };
  }, []);

  // ── Refresh ───────────────────────────────────────────────────────────────

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      if (activeTab === "insights") await loadDocuments(docPage);
      else if (activeTab === "recommendations") await loadRules(rulePage, ruleSearch || null);
    } finally {
      setRefreshing(false);
    }
  }, [activeTab, docPage, rulePage, ruleSearch]);

  // ── Tab change ────────────────────────────────────────────────────────────

  const handleTabChange = useCallback(
    (tabId) => {
      setActiveTab(tabId);
      if (tabId === "insights" && documents.length === 0) loadDocuments(1);
      if (tabId === "recommendations" && rules.length === 0) loadRules(1, ruleSearch || null);
    },
    [documents.length, rules.length, ruleSearch]
  );

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white">
      <div className="max-w-6xl mx-auto px-6 py-8">
        <KnowledgeHeader onRefresh={handleRefresh} loading={refreshing} />

        {/* Tab bar */}
        <div className="flex items-center gap-1 mb-6 bg-white/5 rounded-xl p-1 border border-white/10 overflow-x-auto">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
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

        {/* Tab content */}
        <AnimatePresence mode="wait">
          {/* ─── INSIGHTS TAB ───────────────────────────────────────────── */}
          {activeTab === "insights" && (
            <motion.div
              key="insights"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
            >
              <div className="mb-5">
                <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                  <BookOpen size={15} className="text-[#7BC4BE]" />
                  Knowledge Sources
                </h2>
                <p className="text-[11px] text-gray-500">
                  Writing standards and guidelines powering your AI resume recommendations.
                </p>
              </div>

              {docLoading ? (
                <KnowledgeLoading variant="cards" />
              ) : docError ? (
                <KnowledgeErrorState
                  message={docError}
                  onRetry={() => loadDocuments(docPage)}
                />
              ) : documents.length === 0 ? (
                <KnowledgeEmptyState type="documents" />
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {documents.map((doc) => (
                      <InsightCard key={doc.id} document={doc} />
                    ))}
                  </div>
                  <KnowledgePagination
                    page={docPage}
                    total={docTotal}
                    size={PAGE_SIZE}
                    onPageChange={(p) => loadDocuments(p)}
                  />
                </div>
              )}
            </motion.div>
          )}

          {/* ─── RECOMMENDATIONS TAB ────────────────────────────────────── */}
          {activeTab === "recommendations" && (
            <motion.div
              key="recommendations"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="space-y-4"
            >
              <div className="mb-1">
                <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                  <Lightbulb size={15} className="text-amber-400" />
                  Resume Recommendations
                </h2>
                <p className="text-[11px] text-gray-500">
                  AI-powered writing suggestions to strengthen your resume for your target role.
                </p>
              </div>

              <KnowledgeSearchBar
                onSearch={handleRuleSearch}
                placeholder="Search recommendations by keyword or section..."
              />

              {ruleLoading ? (
                <KnowledgeLoading variant="rules" />
              ) : ruleError ? (
                <KnowledgeErrorState
                  message={ruleError}
                  onRetry={() => loadRules(rulePage, ruleSearch || null)}
                />
              ) : rules.length === 0 ? (
                <KnowledgeEmptyState
                  type={ruleSearch ? "search" : "rules"}
                />
              ) : (
                <div className="space-y-3">
                  {rules.map((rule) => (
                    <SuggestionCard key={rule.id} rule={rule} />
                  ))}
                  <KnowledgePagination
                    page={rulePage}
                    total={ruleTotal}
                    size={PAGE_SIZE}
                    onPageChange={(p) => loadRules(p, ruleSearch || null)}
                  />
                </div>
              )}
            </motion.div>
          )}

          {/* ─── GOVERNANCE TAB ─────────────────────────────────────── */}
          {activeTab === "governance" && (
            <motion.div
              key="governance"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="space-y-4"
            >
              {isAdmin ? (
                <>
                  <div className="mb-1">
                    <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                      <Shield size={15} className="text-purple-400" />
                      Knowledge Governance
                    </h2>
                    <p className="text-[11px] text-gray-500">
                      Manage the lifecycle of knowledge rules: verify, approve, activate, or reject rules before they enter the AI pipeline.
                    </p>
                  </div>
                  <GovernancePanel />
                </>
              ) : (
                <div className="text-center py-12">
                  <Shield size={32} className="mx-auto text-gray-600 mb-3" />
                  <p className="text-sm text-gray-400">Access Denied</p>
                  <p className="text-xs text-gray-500 mt-1">
                    You do not have permission to view governance. Admin role required.
                  </p>
                </div>
              )}
            </motion.div>
          )}

          {/* ─── GET RECOMMENDATIONS TAB ────────────────────────────────── */}
          {activeTab === "get" && (
            <motion.div
              key="get"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
            >
              <div className="mb-5">
                <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                  <Zap size={15} className="text-[#7BC4BE]" />
                  Generate Personalized Recommendations
                </h2>
                <p className="text-[11px] text-gray-500">
                  Our AI matches your gap analysis against thousands of writing rules from top universities and ATS systems.
                </p>
              </div>

              <KnowledgeRetrievalPanel
                onRetrieve={handleRetrieve}
                loading={retrievalLoading}
                result={retrievalResult}
                error={retrievalError}
              />
            </motion.div>
          )}

          {/* ─── YOUR PLAN TAB ──────────────────────────────────────────── */}
          {activeTab === "plan" && (
            <motion.div
              key="plan"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.15 }}
              className="space-y-4"
            >
              <div className="mb-1">
                <h2 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                  <LayoutList size={15} className="text-[#7BC4BE]" />
                  Your Resume Improvement Plan
                </h2>
                <p className="text-[11px] text-gray-500">
                  Organized recommendations by resume section. Load your gap analysis to see your personalized plan.
                </p>
              </div>

              {/* Context search form */}
              <form
                onSubmit={handleContextSearch}
                className="bg-gradient-to-r from-[#7BC4BE]/10 to-[#7BC4BE]/5 border border-[#7BC4BE]/20 rounded-2xl p-6"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-xl bg-[#7BC4BE]/20 flex items-center justify-center">
                    <Search size={18} className="text-[#7BC4BE]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white">
                      Load Your Improvement Plan
                    </h3>
                    <p className="text-[11px] text-gray-400">
                      Enter your Gap Analysis ID to see recommendations organized by resume section.
                    </p>
                  </div>
                </div>
                <div className="flex gap-3 mt-4">
                  <input
                    type="text"
                    value={contextGapId}
                    onChange={(e) => setContextGapId(e.target.value)}
                    placeholder="Paste your Gap Analysis ID here..."
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] transition-colors"
                  />
                  <button
                    type="submit"
                    disabled={!contextGapId.trim() || contextLoading}
                    className="px-5 py-2.5 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-xl text-xs font-bold transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {contextLoading ? "Loading..." : "Load Plan"}
                  </button>
                </div>
              </form>

              {contextLoading ? (
                <KnowledgeLoading variant="spinner" />
              ) : contextError ? (
                <KnowledgeErrorState
                  message={contextError}
                  onRetry={() => fetchContext(contextGapId.trim())}
                />
              ) : context ? (
                <RecommendationGroup
                  context={context}
                  retrieval={contextRetrieval}
                />
              ) : (
                <KnowledgeEmptyState type="context" />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
