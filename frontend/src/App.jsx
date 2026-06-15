import React from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import LandingPage from "./LandingPage";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PricingPage from "./pages/PricingPage";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Dashboard from "./pages/Dashboard";
import ResumeCreateFlow from "./pages/ResumeCreateFlow";
import ResumeEditorWrapper from "./pages/ResumeEditorWrapper";
import { api } from "./services/api";

// Route guard to protect private dashboard/editor workflows
function PrivateRoute({ children }) {
  return api.isAuthenticated() ? children : <Navigate to="/login" replace />;
}

// Wrapper to handle navigation callbacks inside LandingPage
function LandingPageWrapper() {
  const navigate = useNavigate();
  
  const handleBuildResume = (templateName) => {
    if (api.isAuthenticated()) {
      navigate("/dashboard");
    } else {
      navigate("/register");
    }
  };
  
  return <LandingPage onBuildResume={handleBuildResume} />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Pages */}
        <Route path="/" element={<LandingPageWrapper />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        {/* Authenticated SaaS Dashboard & Workflows */}
        <Route 
          path="/dashboard" 
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/resume/create" 
          element={
            <PrivateRoute>
              <ResumeCreateFlow />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/resume/edit/:id" 
          element={
            <PrivateRoute>
              <ResumeEditorWrapper />
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