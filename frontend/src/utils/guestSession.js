/**
 * Guest Session Management
 * 
 * Manages a unified guest_resume_session object in localStorage
 * to preserve the complete resume-building workflow for guests.
 */

const SESSION_KEY = "guest_resume_session";

const defaultSession = {
  basicInfo: {},
  chatHistory: [],
  generatedResume: null,
  selectedTemplate: null,
  editorState: null,
  theme: {},
  formatting: {},
  hiddenSections: [],
  sectionOrder: [],
  pendingDownload: false,
  createdAt: new Date().toISOString(),
};

export function getGuestSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY);
    if (!raw) return { ...defaultSession };
    const parsed = JSON.parse(raw);
    return { ...defaultSession, ...parsed };
  } catch {
    return { ...defaultSession };
  }
}

export function saveGuestSession(session) {
  try {
    const existing = getGuestSession();
    const merged = { ...existing, ...session };
    localStorage.setItem(SESSION_KEY, JSON.stringify(merged));
    return merged;
  } catch (err) {
    console.error("Failed to save guest session:", err);
    return null;
  }
}

export function clearGuestSession() {
  try {
    localStorage.removeItem(SESSION_KEY);
  } catch (err) {
    console.error("Failed to clear guest session:", err);
  }
}

export function hasPendingGuestSession() {
  const session = getGuestSession();
  return session.pendingDownload === true;
}

export function markPendingDownload() {
  return saveGuestSession({ pendingDownload: true });
}

export function clearPendingDownload() {
  return saveGuestSession({ pendingDownload: false });
}
