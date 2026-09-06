import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, ArrowRight, Eye, EyeOff } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { useGoogleSignIn } from "../hooks/useGoogleSignIn";
import { api } from "../services/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login, loginWithGoogle, sessionExpired, clearSessionExpired } = useAuth();

  // Get return URL and message from location state
  const returnUrl = location.state?.returnUrl;
  const welcomeMessage = location.state?.message;

  // Show session expired message
  React.useEffect(() => {
    if (sessionExpired) {
      (async () => {
        setError("Your session has expired. Please log in again.");
        clearSessionExpired();
      })();
    }
  }, [sessionExpired, clearSessionExpired]);

  const checkProfileAndRedirect = async () => {
    // If there's a return URL, go there directly
    if (returnUrl) {
      // For guest resume flows, check if there's pending data to restore
      const hasGuestData = localStorage.getItem("guest_resume_session") || 
                          localStorage.getItem("guest_resume_data") ||
                          localStorage.getItem("guest_ai_resume_data");
      
      if (hasGuestData) {
        // Navigate to the return URL to restore the session
        navigate(returnUrl, { replace: true });
        return;
      }
    }

    try {
      const profile = await api.user.getProfile();
      if (!profile.profile_completed && !profile.job_title) {
        navigate("/profile/setup");
      } else {
        navigate(returnUrl || "/dashboard");
      }
    } catch {
      navigate(returnUrl || "/dashboard");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password, rememberMe);
      await checkProfileAndRedirect();
    } catch (err) {
      setError(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (response) => {
    setError("");
    setLoading(true);
    try {
      await loginWithGoogle(response.credential);
      await checkProfileAndRedirect();
    } catch (err) {
      setError(err.message || "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  };

  useGoogleSignIn("google-signin-button", handleGoogleSuccess);

  return (
    <div className="min-h-screen bg-gradient-to-tr from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
      {/* Decorative Blur Orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#7BC4BE]/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FAD07A]/5 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden"
      >
        {/* Top Accent Line */}
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

        <div className="text-center mb-8">
          <Link to="/" className="inline-block mb-3">
            <span className="text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-1.5">
              <span className="text-[#7BC4BE]">&#10022;</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
            </span>
          </Link>
          <h2 className="text-xl font-medium text-white/90">Welcome back</h2>
          <p className="text-sm text-gray-400 mt-1">Sign in to your professional career hub</p>
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mb-6 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs rounded-lg text-center"
          >
            {error}
          </motion.div>
        )}

        {/* Welcome message for return URL */}
        {welcomeMessage && !error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mb-6 p-3 bg-[#7BC4BE]/10 border border-[#7BC4BE]/20 text-[#7BC4BE] text-xs rounded-lg text-center"
          >
            {welcomeMessage}
          </motion.div>
        )}

        {/* Google Sign-In Button */}
        <div className="mb-6">
          <div id="google-signin-button" className="w-full flex justify-center" />
        </div>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10" />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="px-2 bg-transparent text-gray-400">or continue with email</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Email Address</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                <Mail size={16} />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="text-xs font-semibold uppercase tracking-wider text-gray-400">Password</label>
              <Link to="/forgot-password" className="text-xs text-[#7BC4BE] hover:underline font-semibold">
                Forgot password?
              </Link>
            </div>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                <Lock size={16} />
              </span>
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-10 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {/* Remember Me */}
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-white/20 bg-white/5 text-[#7BC4BE] focus:ring-[#7BC4BE] focus:ring-offset-0"
              />
              <span className="text-sm text-gray-400">Remember me</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-semibold rounded-xl py-3 text-sm transition-all flex items-center justify-center gap-1.5 shadow-lg shadow-[#7BC4BE]/10 disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center gap-1.5">
                <svg className="animate-spin h-4 w-4 text-[#1A2B2A]" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Signing In...
              </span>
            ) : (
              <>
                Access Account <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-white/5 text-center text-xs text-gray-400">
          New to Prompt Resume?{" "}
          <Link to="/register" className="text-[#7BC4BE] hover:underline font-semibold">
            Create an Account
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
