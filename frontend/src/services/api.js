const BASE_URL = "http://localhost:8000/api";

const getHeaders = (isJson = true) => {
  const headers = {};
  if (isJson) {
    headers["Content-Type"] = "application/json";
  }
  const token = localStorage.getItem("token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // Authentication
  async register(email, password, fullName) {
    const res = await fetch(`${BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Registration failed");
    }
    return res.json();
  },

  async login(email, password) {
    const res = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Invalid credentials");
    }
    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    return data;
  },

  logout() {
    localStorage.removeItem("token");
  },

  isAuthenticated() {
    return !!localStorage.getItem("token");
  },

  async getMe() {
    const res = await fetch(`${BASE_URL}/auth/me`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  // User & Profile & Billing
  async getProfile() {
    const res = await fetch(`${BASE_URL}/user/profile`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch profile");
    return res.json();
  },

  async updateProfile(profileData) {
    const res = await fetch(`${BASE_URL}/user/profile`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(profileData),
    });
    if (!res.ok) throw new Error("Failed to update profile");
    return res.json();
  },

  async getSubscription() {
    const res = await fetch(`${BASE_URL}/user/subscription`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch subscription");
    return res.json();
  },

  async upgradeSubscription(planType) {
    const res = await fetch(`${BASE_URL}/user/subscription/upgrade?plan_type=${planType}`, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to upgrade subscription");
    return res.json();
  },

  async getBillingHistory() {
    const res = await fetch(`${BASE_URL}/user/billing/history`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to fetch billing history");
    return res.json();
  },

  // Resumes
  async createResume(title, templateId = "harvard") {
    const res = await fetch(`${BASE_URL}/resume/create`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ title, template_id: templateId }),
    });
    if (!res.ok) throw new Error("Failed to create resume");
    return res.json();
  },

  async listResumes() {
    const res = await fetch(`${BASE_URL}/resume/list`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load resumes");
    return res.json();
  },

  async getResume(id) {
    const res = await fetch(`${BASE_URL}/resume/${id}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load resume details");
    return res.json();
  },

  async updateResume(id, title, templateId) {
    const res = await fetch(`${BASE_URL}/resume/${id}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify({ title, template_id: templateId }),
    });
    if (!res.ok) throw new Error("Failed to update resume settings");
    return res.json();
  },

  async saveResumeSections(id, sections) {
    // sections: Array of { section_type, content, position }
    const res = await fetch(`${BASE_URL}/resume/${id}/sections`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify(sections),
    });
    if (!res.ok) throw new Error("Failed to save resume content");
    return res.json();
  },

  async deleteResume(id) {
    const res = await fetch(`${BASE_URL}/resume/${id}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete resume");
    return res.json();
  },

  async generateResumeFromPrompt(prompt, archetype = "experienced") {
    const res = await fetch(`${BASE_URL}/resume/generate`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({ prompt, archetype }),
    });
    if (!res.ok) throw new Error("Failed to parse prompt and generate resume");
    return res.json();
  },

  // Cover Letters
  async generateCoverLetter(title, jobRole, companyName, experienceSummary) {
    const res = await fetch(`${BASE_URL}/cover-letter/generate`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        title,
        job_role: jobRole,
        company_name: companyName,
        experience_summary: experienceSummary,
      }),
    });
    if (!res.ok) throw new Error("Failed to generate cover letter");
    return res.json();
  },

  async listCoverLetters() {
    const res = await fetch(`${BASE_URL}/cover-letter/list`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load cover letters");
    return res.json();
  },

  async getCoverLetter(id) {
    const res = await fetch(`${BASE_URL}/cover-letter/${id}`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load cover letter details");
    return res.json();
  },

  async updateCoverLetter(id, title, content) {
    const res = await fetch(`${BASE_URL}/cover-letter/${id}`, {
      method: "PUT",
      headers: getHeaders(),
      body: JSON.stringify({ title, content }),
    });
    if (!res.ok) throw new Error("Failed to update cover letter");
    return res.json();
  },

  async deleteCoverLetter(id) {
    const res = await fetch(`${BASE_URL}/cover-letter/${id}`, {
      method: "DELETE",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to delete cover letter");
    return res.json();
  },

  // Templates
  async listTemplates() {
    const res = await fetch(`${BASE_URL}/templates`, {
      method: "GET",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to load templates catalog");
    return res.json();
  },

  // ATS Scoring & AI Assistants
  async analyzeATS(resumeId) {
    const res = await fetch(`${BASE_URL}/ats/analyze/${resumeId}`, {
      method: "POST",
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error("Failed to analyze ATS score");
    return res.json();
  },

  async improveText(textContent, actionType, sectionType = "summary") {
    const res = await fetch(`${BASE_URL}/ats/improve-text`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        text_content: textContent,
        action_type: actionType,
        section_type: sectionType,
      }),
    });
    if (!res.ok) throw new Error("Failed to improve text via AI");
    return res.json();
  },

  // PDF Export
  async exportPDF(htmlContent, filename = "resume.pdf") {
    const res = await fetch(`${BASE_URL}/pdf/export`, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify({
        html_content: htmlContent,
        filename: filename,
      }),
    });
    if (!res.ok) throw new Error("Failed to export PDF file");
    return res.blob(); // Get raw blob of PDF
  },
};
