import { useState, useEffect } from "react";
import {
  Shield,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  RefreshCw,
  Eye,
  EyeOff,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { api } from "../services/api";
import ConfirmationDialog from "./ConfirmationDialog";

const STATE_ORDER = [
  "DISCOVERED",
  "EXTRACTED",
  "CLASSIFIED",
  "VERIFIED",
  "APPROVED",
  "ACTIVE",
  "VERSIONED",
  "AUDITED",
  "REJECTED",
];

const STATE_COLORS = {
  DISCOVERED: { bg: "bg-gray-100", text: "text-gray-700", icon: Clock },
  EXTRACTED: { bg: "bg-gray-200", text: "text-gray-700", icon: Clock },
  CLASSIFIED: { bg: "bg-yellow-100", text: "text-yellow-700", icon: AlertTriangle },
  VERIFIED: { bg: "bg-blue-100", text: "text-blue-700", icon: Eye },
  APPROVED: { bg: "bg-yellow-100", text: "text-yellow-700", icon: CheckCircle },
  ACTIVE: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle },
  VERSIONED: { bg: "bg-blue-100", text: "text-blue-700", icon: EyeOff },
  AUDITED: { bg: "bg-blue-100", text: "text-blue-700", icon: EyeOff },
  REJECTED: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
};

const STATE_BADGE_COLORS = {
  DISCOVERED: "bg-gray-500/15 text-gray-400",
  EXTRACTED: "bg-gray-500/15 text-gray-400",
  CLASSIFIED: "bg-yellow-500/15 text-yellow-400",
  VERIFIED: "bg-blue-500/15 text-blue-400",
  APPROVED: "bg-yellow-500/15 text-yellow-400",
  ACTIVE: "bg-green-500/15 text-green-400",
  VERSIONED: "bg-blue-500/15 text-blue-400",
  AUDITED: "bg-blue-500/15 text-blue-400",
  REJECTED: "bg-red-500/15 text-red-400",
};

const PAGE_SIZE = 10;

export default function GovernancePanel() {
  const [stats, setStats] = useState(null);
  const [selectedState, setSelectedState] = useState("VERIFIED");
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  // Confirmation dialog state
  const [confirmDialog, setConfirmDialog] = useState({
    isOpen: false,
    title: "",
    description: "",
    ruleId: "",
    currentState: "",
    newState: "",
    confirmLabel: "",
    confirmColor: "",
    action: null,
  });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.knowledge.getGovernanceStats();
        if (!cancelled) setStats(data);
      } catch (err) {
        if (!cancelled) console.error("Failed to load governance stats:", err);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.knowledge.getRulesByState(selectedState, 1, PAGE_SIZE);
        if (!cancelled) {
          setRules(data.items || []);
          setTotal(data.total || 0);
          setPage(data.page || 1);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load rules");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [selectedState]);

  async function loadStats() {
    try {
      const data = await api.knowledge.getGovernanceStats();
      setStats(data);
    } catch (err) {
      console.error("Failed to load governance stats:", err);
    }
  }

  async function loadRules(state, p) {
    setLoading(true);
    setError(null);
    try {
      const data = await api.knowledge.getRulesByState(state, p, PAGE_SIZE);
      setRules(data.items || []);
      setTotal(data.total || 0);
      setPage(data.page || 1);
    } catch (err) {
      setError(err.message || "Failed to load rules");
    } finally {
      setLoading(false);
    }
  }

  const openConfirmDialog = (rule, action, title, description, confirmLabel, confirmColor, newState) => {
    setConfirmDialog({
      isOpen: true,
      title,
      description,
      ruleId: rule.id,
      currentState: rule.state,
      newState,
      confirmLabel,
      confirmColor,
      action,
    });
  };

  const handleAction = async () => {
    const { ruleId, action } = confirmDialog;
    setActionLoading(ruleId);
    try {
      if (action === "approve") await api.knowledge.approveRule(ruleId);
      else if (action === "activate") await api.knowledge.activateRule(ruleId);
      else if (action === "deactivate") await api.knowledge.deactivateRule(ruleId);
      else if (action === "reject") await api.knowledge.rejectRule(ruleId);

      await loadRules(selectedState, page);
      await loadStats();
    } catch (err) {
      setError(err.message || `Failed to ${action} rule`);
    } finally {
      setActionLoading(null);
    }
  };

  const getNextActions = (state) => {
    switch (state) {
      case "VERIFIED":
        return [
          {
            label: "Approve",
            action: "approve",
            color: "bg-yellow-500",
            newState: "APPROVED",
            title: "Approve Rule",
            description: "This rule will be approved and available for activation.",
          },
          {
            label: "Reject",
            action: "reject",
            color: "bg-red-500",
            newState: "REJECTED",
            title: "Reject Rule",
            description: "This rule will be rejected and removed from the governance pipeline.",
          },
        ];
      case "APPROVED":
        return [
          {
            label: "Activate",
            action: "activate",
            color: "bg-green-500",
            newState: "ACTIVE",
            title: "Activate Rule",
            description: "This rule will become active and used in the AI pipeline.",
          },
          {
            label: "Reject",
            action: "reject",
            color: "bg-red-500",
            newState: "REJECTED",
            title: "Reject Rule",
            description: "This rule will be rejected and removed from the governance pipeline.",
          },
        ];
      case "ACTIVE":
        return [
          {
            label: "Deactivate",
            action: "deactivate",
            color: "bg-gray-500",
            newState: "REJECTED",
            title: "Deactivate Rule",
            description: "This rule will be deactivated and no longer used in the AI pipeline.",
          },
        ];
      default:
        return [];
    }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-2">
          {STATE_ORDER.map((state) => {
            const count = stats.by_state?.[state] || 0;
            const colors = STATE_COLORS[state];
            const Icon = colors.icon;
            return (
              <button
                key={state}
                onClick={() => setSelectedState(state)}
                className={`p-3 rounded-lg border-2 transition-all text-left ${
                  selectedState === state
                    ? "border-[#7BC4BE] shadow-md"
                    : "border-transparent hover:border-white/20"
                } ${colors.bg}`}
              >
                <div className="flex items-center gap-1.5">
                  <Icon className={`w-3.5 h-3.5 ${colors.text}`} />
                  <span className={`text-[10px] font-medium ${colors.text} leading-tight`}>
                    {state}
                  </span>
                </div>
                <div className={`text-lg font-bold mt-1 ${colors.text}`}>{count}</div>
              </button>
            );
          })}
        </div>
      )}

      {/* Rules List */}
      <div className="bg-white rounded-lg border">
        <div className="p-4 border-b flex items-center justify-between">
          <h3 className="font-semibold flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Rules: {selectedState}
            <span className="text-xs text-gray-400 font-normal">({total} total)</span>
          </h3>
          <button
            onClick={() => loadRules(selectedState, page)}
            className="p-2 hover:bg-gray-100 rounded"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="p-4 bg-red-50 text-red-700 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            {error}
          </div>
        )}

        {loading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : rules.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No rules in this state</div>
        ) : (
          <>
            <div className="divide-y">
              {rules.map((rule) => {
                const actions = getNextActions(selectedState, rule);
                return (
                  <div key={rule.id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${STATE_BADGE_COLORS[rule.state] || "bg-gray-500/15 text-gray-400"}`}>
                            {rule.state}
                          </span>
                          <span className="text-xs font-mono text-gray-500">
                            {rule.rule_key || rule.rule_id}
                          </span>
                          {rule.source_document && (
                            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                              {rule.source_document}
                              {rule.source_page != null && ` p.${rule.source_page}`}
                              {rule.source_section && ` / ${rule.source_section}`}
                            </span>
                          )}
                        </div>
                        <p className="text-sm mt-1 line-clamp-2">{rule.instruction}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span>Category: {rule.category}</span>
                          <span>Section: {rule.section_name}</span>
                          {rule.extraction_confidence != null && (
                            <span>Confidence: {(rule.extraction_confidence * 100).toFixed(0)}%</span>
                          )}
                          {rule.version != null && <span>v{rule.version}</span>}
                          {rule.rule_hash && (
                            <span className="font-mono text-[10px]">
                              Hash: {rule.rule_hash.substring(0, 8)}...
                            </span>
                          )}
                        </div>
                        {rule.source_evidence && (
                          <p className="text-xs text-gray-400 mt-1 italic line-clamp-1">
                            Evidence: {rule.source_evidence}
                          </p>
                        )}
                        {rule.extraction_timestamp && (
                          <p className="text-xs text-gray-400 mt-0.5">
                            Extracted: {rule.extraction_timestamp}
                          </p>
                        )}
                      </div>
                      {actions.length > 0 && (
                        <div className="flex items-center gap-2 ml-4">
                          {actions.map(({ label, action, color, newState, title, description }) => (
                            <button
                              key={action}
                              onClick={() =>
                                openConfirmDialog(
                                  rule,
                                  action,
                                  title,
                                  description,
                                  `Confirm ${label}`,
                                  action === "reject" ? "bg-red-500 hover:bg-red-600" : color === "bg-green-500" ? "bg-green-500 hover:bg-green-600" : color === "bg-yellow-500" ? "bg-yellow-500 hover:bg-yellow-600" : "bg-gray-500 hover:bg-gray-600",
                                  newState
                                )
                              }
                              disabled={actionLoading === rule.id}
                              className={`px-3 py-1 text-white text-sm rounded ${color} hover:opacity-90 disabled:opacity-50`}
                            >
                              {actionLoading === rule.id ? "..." : label}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="p-4 border-t flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  Page {page} of {totalPages}
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => loadRules(selectedState, page - 1)}
                    disabled={page <= 1}
                    className="p-1.5 rounded-lg bg-white/10 hover:bg-white/15 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronLeft size={14} />
                  </button>
                  <button
                    onClick={() => loadRules(selectedState, page + 1)}
                    disabled={page >= totalPages}
                    className="p-1.5 rounded-lg bg-white/10 hover:bg-white/15 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                  >
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={confirmDialog.isOpen}
        onClose={() => setConfirmDialog({ ...confirmDialog, isOpen: false })}
        onConfirm={handleAction}
        title={confirmDialog.title}
        description={confirmDialog.description}
        ruleKey={confirmDialog.ruleId}
        currentState={confirmDialog.currentState}
        newState={confirmDialog.newState}
        confirmLabel={confirmDialog.confirmLabel}
        confirmColor={confirmDialog.confirmColor}
        loading={actionLoading === confirmDialog.ruleId}
      />
    </div>
  );
}
