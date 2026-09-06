import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import LandingPage from "./LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import PricingPage from "./pages/PricingPage";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Dashboard from "./pages/Dashboard";
import AIChatPage from "./pages/AIChatPage";
import ResumeEditorWrapper from "./pages/ResumeEditorWrapper";
import AuthSettings from "./pages/AuthSettings";
import VerifyEmail from "./pages/VerifyEmail";
import KnowledgePage from "./pages/KnowledgePage";
import ResumeIntelligencePage from "./pages/ResumeIntelligencePage";
import ProfileSetup from "./pages/ProfileSetup";
import JDBasedPage from "./pages/JDBasedPage";
import ResumeCreationFlow from "./pages/ResumeCreationFlow";
import GuestResumeEditor from "./pages/GuestResumeEditor";
import { useAuth } from "./hooks/useAuth";

// Route guard to protect private dashboard/editor workflows
function PrivateRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#0F1E1E' }}>
        <div style={{ color: '#7BC4BE', fontSize: '14px' }}>Loading...</div>
      </div>
    );
  }
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

// Guest-only route — redirect to dashboard if already logged in
function GuestRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

// Wrapper to handle navigation callbacks inside LandingPage
function LandingPageWrapper() {
  const navigate = useNavigate();
  const handleBuildResume = () => {
    // All users go through the creation flow (Basic Info → Method Selection)
    navigate("/resume/create-flow");
  };
  
  return <LandingPage onBuildResume={handleBuildResume} />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Pages */}
        <Route path="/" element={<LandingPageWrapper />} />
        <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><Register /></GuestRoute>} />
        <Route path="/forgot-password" element={<GuestRoute><ForgotPassword /></GuestRoute>} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        {/* AI Chat - No auth required, backend controls conversation */}
        <Route path="/resume/create" element={<AIChatPage />} />

        {/* Resume Creation Flow - No auth required, guests can build resumes */}
        <Route 
          path="/resume/create-flow" 
          element={<ResumeCreationFlow />} 
        />

        {/* Guest Resume Editor - No auth required, stores data in localStorage */}
        <Route 
          path="/resume/guest-edit" 
          element={<GuestResumeEditor />} 
        />

        {/* Resume Editor - Auth required only at download */}
        <Route path="/resume/edit/:id" element={<ResumeEditorWrapper />} />

        {/* Dashboard - Auth required */}
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />

        {/* Auth Settings - Auth required */}
        <Route 
          path="/settings/auth" 
          element={
            <PrivateRoute>
              <AuthSettings />
            </PrivateRoute>
          } 
        />

        {/* Profile Setup - Auth required */}
        <Route 
          path="/profile/setup" 
          element={
            <PrivateRoute>
              <ProfileSetup />
            </PrivateRoute>
          } 
        />

        {/* Knowledge Intelligence - Auth required */}
        <Route
          path="/knowledge"
          element={
            <PrivateRoute>
              <KnowledgePage />
            </PrivateRoute>
          }
        />

        {/* Resume Intelligence - Auth required */}
        <Route
          path="/resume-intelligence"
          element={
            <PrivateRoute>
              <ResumeIntelligencePage />
            </PrivateRoute>
          }
        />
        <Route
          path="/resume-intelligence/:id"
          element={
            <PrivateRoute>
              <ResumeIntelligencePage />
            </PrivateRoute>
          }
        />

        {/* JD-Based Resume Builder - Auth required */}
        <Route
          path="/jd-based"
          element={
            <PrivateRoute>
              <JDBasedPage />
            </PrivateRoute>
          }
        />

        {/* Redirection fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
