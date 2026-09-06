/**
 * Centralized API Service
 *
 * All frontend API requests go through this single service.
 * No component should directly call fetch(), axios(), or hardcoded URLs.
 *
 * Usage:
 *   import { api } from '@/services/api';
 *   const user = await api.auth.getMe();
 *   const resumes = await api.resumes.list();
 */

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function getHeaders(isJson = true) {
  const headers = {};
  if (isJson) {
    headers["Content-Type"] = "application/json";
  }
  const token = localStorage.getItem("token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

async function request(endpoint, options = {}) {
  const { method = "GET", body, isJson = true, raw = false } = options;
  const url = `${BASE_URL}${endpoint}`;

  const config = {
    method,
    headers: getHeaders(isJson),
  };

  if (body && method !== "GET") {
    config.body = isJson ? JSON.stringify(body) : body;
  }

  const res = await fetch(url, config);

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    const err = new Error(error.detail || `HTTP ${res.status}`);
    err.status = res.status;
    if (res.status === 401) {
      localStorage.removeItem("token");
    }
    throw err;
  }

  if (raw) return res;
  if (res.status === 204) return null;
  return res.json();
}

// ---------------------------------------------------------------------------
// API Modules
// ---------------------------------------------------------------------------

const auth = {
  async register(email, password, fullName) {
    return request("/auth/register", {
      method: "POST",
      body: { email, password, full_name: fullName },
    });
  },

  async login(email, password, rememberMe = false) {
    const data = await request("/auth/login", {
      method: "POST",
      body: { email, password, remember_me: rememberMe },
    });
    localStorage.setItem("token", data.access_token);
    return data;
  },

  async loginWithGoogle(credential) {
    const data = await request("/auth/google", {
      method: "POST",
      body: { credential },
    });
    localStorage.setItem("token", data.access_token);
    return data;
  },

  async getMe() {
    return request("/auth/me");
  },

  async logout() {
    try {
      await request("/auth/logout", { method: "POST" });
    } catch {
      // Ignore errors — client-side logout regardless
    }
    localStorage.removeItem("token");
  },

  isAuthenticated() {
    return !!localStorage.getItem("token");
  },

  async forgotPassword(email) {
    return request("/auth/forgot-password", {
      method: "POST",
      body: { email },
    });
  },

  async resetPassword(token, newPassword, confirmPassword) {
    return request("/auth/reset-password", {
      method: "POST",
      body: { token, new_password: newPassword, confirm_password: confirmPassword },
    });
  },

  // Email verification
  async sendVerification() {
    return request("/auth/send-verification", {
      method: "POST",
    });
  },

  async verifyEmail(token) {
    return request(`/auth/verify-email?token=${token}`);
  },

  // Change password
  async changePassword(currentPassword, newPassword, confirmPassword) {
    return request("/auth/change-password", {
      method: "POST",
      body: {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      },
    });
  },

  // Delete account
  async deleteAccount(password) {
    return request("/auth/account", {
      method: "DELETE",
      body: { password, confirmation: "DELETE" },
    });
  },

  // Auth settings
  async getSettings() {
    return request("/auth/settings");
  },
};

const user = {
  async getProfile() {
    return request("/user/profile");
  },

  async updateProfile(profileData) {
    return request("/user/profile", { method: "PUT", body: profileData });
  },

  async getSubscription() {
    return request("/user/subscription");
  },

  async upgradeSubscription(planType) {
    return request(`/user/subscription/upgrade?plan_type=${planType}`, {
      method: "POST",
    });
  },

  async getBillingHistory() {
    return request("/user/billing/history");
  },

  async getActivityLog() {
    return request("/user/activity");
  },
};

const resumes = {
  async create(title, templateId = "harvard") {
    return request("/resume/create", {
      method: "POST",
      body: { title, template_id: templateId },
    });
  },

  async list() {
    return request("/resume/list");
  },

  async get(id) {
    return request(`/resume/${id}`);
  },

  async update(id, title, templateId, sectionOrder = undefined) {
    const body = { title, template_id: templateId };
    if (sectionOrder !== undefined) {
      body.section_order = sectionOrder;
    }
    return request(`/resume/${id}`, {
      method: "PUT",
      body,
    });
  },

  async saveSections(id, sections) {
    return request(`/resume/${id}/sections`, {
      method: "PUT",
      body: sections,
    });
  },

  async delete(id) {
    return request(`/resume/${id}`, { method: "DELETE" });
  },

  async generateFromPrompt(prompt, archetype = "experienced") {
    return request("/resume/generate", {
      method: "POST",
      body: { prompt, archetype },
    });
  },

  async transferGuestResumes(guestSessionId = "guest") {
    return request("/resume/transfer-guest", {
      method: "POST",
      body: { guest_session_id: guestSessionId },
    });
  },
};

const coverLetters = {
  async generate(title, jobRole, companyName, experienceSummary) {
    return request("/cover-letter/generate", {
      method: "POST",
      body: {
        title,
        job_role: jobRole,
        company_name: companyName,
        experience_summary: experienceSummary,
      },
    });
  },

  async list() {
    return request("/cover-letter/list");
  },

  async get(id) {
    return request(`/cover-letter/${id}`);
  },

  async update(id, title, content) {
    return request(`/cover-letter/${id}`, {
      method: "PUT",
      body: { title, content },
    });
  },

  async delete(id) {
    return request(`/cover-letter/${id}`, { method: "DELETE" });
  },
};

const templates = {
  async list() {
    return request("/procs/templates/published");
  },

  async get(id) {
    return request(`/procs/templates/${id}`);
  },

  async getPublished() {
    return request("/procs/templates/published");
  },
};

const ats = {
  async analyze(resumeId) {
    return request(`/ats/analyze/${resumeId}`, { method: "POST" });
  },

  async improveText(textContent, actionType, sectionType = "summary") {
    return request("/ats/improve-text", {
      method: "POST",
      body: {
        text_content: textContent,
        action_type: actionType,
        section_type: sectionType,
      },
    });
  },
};

const career = {
  async generateBullets(data) {
    return request("/v1/career/bullets", { method: "POST", body: data });
  },

  async generateSummary(data) {
    return request("/v1/career/summary", { method: "POST", body: data });
  },

  async generateCoverLetter(data) {
    return request("/v1/career/cover-letter", { method: "POST", body: data });
  },

  async getBulletFeedback(data) {
    return request("/v1/career/bullet-feedback", { method: "POST", body: data });
  },

  async optimizeForATS(data) {
    return request("/v1/career/ats-optimize", { method: "POST", body: data });
  },

  async getKnowledgeStats() {
    return request("/v1/career/knowledge/stats");
  },

  async healthCheck() {
    return request("/v1/career/health");
  },
};

const chat = {
  async createSession(title = null) {
    return request("/chat/sessions", {
      method: "POST",
      body: { title },
    });
  },

  async listSessions() {
    return request("/chat/sessions");
  },

  async getSession(sessionId) {
    return request(`/chat/sessions/${sessionId}`);
  },

  async getMessages(sessionId) {
    return request(`/chat/sessions/${sessionId}/messages`);
  },

  async sendMessage(sessionId, message) {
    return request(`/chat/sessions/${sessionId}/messages`, {
      method: "POST",
      body: { message },
    });
  },

  async deleteSession(sessionId) {
    return request(`/chat/sessions/${sessionId}`, { method: "DELETE" });
  },

  async closeSession(sessionId) {
    return request(`/chat/sessions/${sessionId}/close`, { method: "POST" });
  },
};

const knowledge = {
  // Documents
  async listDocuments(page = 1, size = 20) {
    return request(`/knowledge/documents?page=${page}&size=${size}`);
  },

  async getDocument(documentId) {
    return request(`/knowledge/documents/${documentId}`);
  },

  async createDocument(data) {
    return request("/knowledge/documents", {
      method: "POST",
      body: data,
    });
  },

  async updateDocument(documentId, data) {
    return request(`/knowledge/documents/${documentId}`, {
      method: "PUT",
      body: data,
    });
  },

  async deleteDocument(documentId) {
    return request(`/knowledge/documents/${documentId}`, {
      method: "DELETE",
    });
  },

  // Rules
  async listRules(page = 1, size = 20, query = null) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (query) params.set("q", query);
    return request(`/knowledge/rules?${params.toString()}`);
  },

  async getRule(ruleId) {
    return request(`/knowledge/rules/${ruleId}`);
  },

  // Retrieval
  async retrieve(gapAnalysisId) {
    return request("/knowledge/retrieve", {
      method: "POST",
      body: { gap_analysis_id: gapAnalysisId },
    });
  },

  // Context
  async getContext(gapAnalysisId) {
    return request(`/knowledge/context/${gapAnalysisId}`);
  },

  // Governance
  async getRulesByState(state, page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/knowledge-intelligence/rules/by-state/${state}?${params.toString()}`);
  },

  async getGovernanceStats() {
    return request("/knowledge-intelligence/governance/stats");
  },

  async approveRule(ruleId) {
    return request(`/knowledge-intelligence/rules/${ruleId}/approve`, {
      method: "POST",
    });
  },

  async activateRule(ruleId) {
    return request(`/knowledge-intelligence/rules/${ruleId}/activate`, {
      method: "POST",
    });
  },

  async deactivateRule(ruleId) {
    return request(`/knowledge-intelligence/rules/${ruleId}/deactivate`, {
      method: "POST",
    });
  },

  async rejectRule(ruleId) {
    return request(`/knowledge-intelligence/rules/${ruleId}/reject`, {
      method: "POST",
    });
  },
};

const resumeIntelligence = {
  async create(rawText, title = null) {
    return request("/resume-intelligence/", {
      method: "POST",
      body: { raw_text: rawText, title },
    });
  },

  async list(page = 1, size = 20, status = null) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (status) params.set("status", status);
    return request(`/resume-intelligence/?${params.toString()}`);
  },

  async get(profileId) {
    return request(`/resume-intelligence/${profileId}`);
  },

  async update(profileId, data) {
    return request(`/resume-intelligence/${profileId}`, {
      method: "PUT",
      body: data,
    });
  },

  async delete(profileId) {
    return request(`/resume-intelligence/${profileId}`, { method: "DELETE" });
  },

  async parse(profileId) {
    return request(`/resume-intelligence/${profileId}/parse`, { method: "POST" });
  },

  async getParsed(profileId) {
    return request(`/resume-intelligence/${profileId}/parsed`);
  },

  async getEntities(profileId, entityType = null) {
    const params = entityType ? `?entity_type=${entityType}` : "";
    return request(`/resume-intelligence/${profileId}/entities${params}`);
  },

  async getKnowledge(profileId) {
    return request(`/resume-intelligence/${profileId}/knowledge`);
  },
};

const opportunities = {
  async create(rawText, title = null, company = null, url = null) {
    return request("/opportunities/", {
      method: "POST",
      body: { raw_text: rawText, title, company, url },
    });
  },

  async list(page = 1, size = 20, status = null) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    if (status) params.set("status", status);
    return request(`/opportunities/?${params.toString()}`);
  },

  async get(opportunityId) {
    return request(`/opportunities/${opportunityId}`);
  },

  async update(opportunityId, data) {
    return request(`/opportunities/${opportunityId}`, {
      method: "PUT",
      body: data,
    });
  },

  async delete(opportunityId) {
    return request(`/opportunities/${opportunityId}`, { method: "DELETE" });
  },

  async parse(opportunityId) {
    return request(`/opportunities/${opportunityId}/parse`, { method: "POST" });
  },

  async getParsed(opportunityId) {
    return request(`/opportunities/${opportunityId}/parsed`);
  },

  async getEntities(opportunityId, entityType = null) {
    const params = entityType ? `?entity_type=${entityType}` : "";
    return request(`/opportunities/${opportunityId}/entities${params}`);
  },
};

const gapAnalysis = {
  async create(resumeProfileId, opportunityId) {
    return request("/gap-analysis/", {
      method: "POST",
      body: { resume_profile_id: resumeProfileId, opportunity_id: opportunityId },
    });
  },

  async analyze(analysisId) {
    return request(`/gap-analysis/${analysisId}/analyze`, { method: "POST" });
  },

  async list(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/gap-analysis/?${params.toString()}`);
  },

  async get(analysisId) {
    return request(`/gap-analysis/${analysisId}`);
  },

  async getScores(analysisId) {
    return request(`/gap-analysis/${analysisId}/scores`);
  },

  async getGaps(analysisId) {
    return request(`/gap-analysis/${analysisId}/matches`);
  },

  async getRecommendations(analysisId) {
    return request(`/gap-analysis/${analysisId}/recommendations`);
  },

  async getMissing(analysisId) {
    return request(`/gap-analysis/${analysisId}/missing`);
  },

  async delete(analysisId) {
    return request(`/gap-analysis/${analysisId}`, { method: "DELETE" });
  },
};

const promptIntelligence = {
  async build(gapAnalysisId, promptType = "resume_tailoring", templateId = null) {
    return request("/prompt-intelligence/packages/build", {
      method: "POST",
      body: { gap_analysis_id: gapAnalysisId, prompt_type: promptType, template_id: templateId },
    });
  },

  async listPackages(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/prompt-intelligence/packages?${params.toString()}`);
  },

  async getPackage(packageId) {
    return request(`/prompt-intelligence/packages/${packageId}`);
  },

  async deletePackage(packageId) {
    return request(`/prompt-intelligence/packages/${packageId}`, { method: "DELETE" });
  },

  async listTemplates(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/prompt-intelligence/templates?${params.toString()}`);
  },

  async getTemplate(templateId) {
    return request(`/prompt-intelligence/templates/${templateId}`);
  },
};

const aiExecution = {
  async execute(promptPackageId, provider = null) {
    const body = { prompt_package_id: promptPackageId };
    if (provider) body.provider = provider;
    return request("/ai/execute", { method: "POST", body });
  },

  async list(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/ai/executions?${params.toString()}`);
  },

  async get(executionId) {
    return request(`/ai/executions/${executionId}`);
  },

  async getResponse(executionId) {
    return request(`/ai/executions/${executionId}/response`);
  },
};

const aiResponseIntelligence = {
  async validate(aiExecutionId) {
    return request("/ai-response/validate", {
      method: "POST",
      body: { ai_execution_id: aiExecutionId },
    });
  },

  async list(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/ai-response/validations?${params.toString()}`);
  },

  async get(validationId) {
    return request(`/ai-response/validations/${validationId}`);
  },

  async getDiff(validationId) {
    return request(`/ai-response/validations/${validationId}/diff`);
  },

  async getChanges(validationId) {
    return request(`/ai-response/validations/${validationId}/changes`);
  },

  async getReport(validationId) {
    return request(`/ai-response/validations/${validationId}/report`);
  },

  async getConfidence(validationId) {
    return request(`/ai-response/validations/${validationId}/confidence`);
  },
};

const pipeline = {
  async execute(resumeText, opportunityText, skipValidation = false) {
    return request("/pipeline/execute", {
      method: "POST",
      body: {
        resume_text: resumeText,
        opportunity_text: opportunityText,
        skip_validation: skipValidation,
      },
    });
  },

  async listRuns(page = 1, size = 20) {
    const params = new URLSearchParams({ page: String(page), size: String(size) });
    return request(`/pipeline/runs?${params.toString()}`);
  },

  async getRun(runId) {
    return request(`/pipeline/${runId}`);
  },

  async getStages(runId) {
    return request(`/pipeline/${runId}/stages`);
  },
};

const pdf = {
  async export(htmlContent, filename = "resume.pdf") {
    return request("/pdf/export", {
      method: "POST",
      body: { html_content: htmlContent, filename },
      raw: true,
    });
  },
};

// ---------------------------------------------------------------------------
// Export unified API object
// ---------------------------------------------------------------------------

export const api = {
  auth,
  user,
  resumes,
  coverLetters,
  templates,
  ats,
  career,
  chat,
  knowledge,
  resumeIntelligence,
  opportunities,
  gapAnalysis,
  promptIntelligence,
  aiExecution,
  aiResponseIntelligence,
  pipeline,
  pdf,
};

// Default export for backward compatibility
export default api;
