import { useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Lock, ArrowRight, ArrowLeft, Eye, EyeOff, CheckCircle } from "lucide-react";
import { api } from "../services/api";
import { validatePassword, getPasswordStrength, getStrengthLabel } from "../utils/passwordValidation";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-tr from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
        <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#7BC4BE]/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FAD07A]/5 rounded-full blur-[120px] pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />
          <div className="text-center">
            <h2 className="text-xl font-medium text-white/90 mb-2">Invalid Reset Link</h2>
            <p className="text-sm text-gray-400 mb-6">
              This password reset link is invalid or missing a token.
            </p>
            <Link
              to="/forgot-password"
              className="text-[#7BC4BE] hover:underline font-semibold text-sm"
            >
              Request a new reset link
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  const strength = getPasswordStrength(newPassword);
  const strengthInfo = getStrengthLabel(strength);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    const pwCheck = validatePassword(newPassword);
    if (!pwCheck.valid) {
      setError(pwCheck.errors[0]);
      return;
    }

    setLoading(true);
    try {
      await api.auth.resetPassword(token, newPassword, confirmPassword);
      setSuccess(true);
    } catch (err) {
      setError(err.message || "Failed to reset password. The link may have expired.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-tr from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
        <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#7BC4BE]/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FAD07A]/5 rounded-full blur-[120px] pointer-events-none" />

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden"
        >
          <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

          <div className="text-center mb-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-500/10 flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-emerald-400" />
            </div>
            <h2 className="text-xl font-medium text-white/90">Password Reset Complete</h2>
            <p className="text-sm text-gray-400 mt-2">
              Your password has been updated successfully.
            </p>
          </div>

          <button
            onClick={() => navigate("/login")}
            className="w-full bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-semibold rounded-xl py-3 text-sm transition-all flex items-center justify-center gap-1.5 shadow-lg shadow-[#7BC4BE]/10"
          >
            Sign In with New Password <ArrowRight size={16} />
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-tr from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-[#7BC4BE]/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FAD07A]/5 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 p-8 rounded-2xl shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

        <div className="text-center mb-8">
          <Link to="/" className="inline-block mb-3">
            <span className="text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-1.5">
              <span className="text-[#7BC4BE]">&#10022;</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
            </span>
          </Link>
          <h2 className="text-xl font-medium text-white/90">Set new password</h2>
          <p className="text-sm text-gray-400 mt-1">Choose a strong password for your account</p>
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

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
              New Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                <Lock size={16} />
              </span>
              <input
                type={showPassword ? "text" : "password"}
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
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

            {/* Password strength indicator */}
            {newPassword.length > 0 && (
              <div className="mt-2">
                <div className="flex gap-1 h-1">
                  <div className={`flex-1 rounded-full ${strength >= 25 ? strengthInfo.color : "bg-white/10"}`} />
                  <div className={`flex-1 rounded-full ${strength >= 50 ? strengthInfo.color : "bg-white/10"}`} />
                  <div className={`flex-1 rounded-full ${strength >= 75 ? strengthInfo.color : "bg-white/10"}`} />
                  <div className={`flex-1 rounded-full ${strength >= 100 ? strengthInfo.color : "bg-white/10"}`} />
                </div>
                <p className={`text-xs mt-1 ${strength < 30 ? "text-rose-400" : strength < 60 ? "text-amber-400" : "text-emerald-400"}`}>
                  {strengthInfo.label}
                </p>
              </div>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
              Confirm Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                <Lock size={16} />
              </span>
              <input
                type={showConfirm ? "text" : "password"}
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-10 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all"
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-white transition-colors"
              >
                {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {confirmPassword && newPassword !== confirmPassword && (
              <p className="text-xs text-rose-400 mt-1">Passwords do not match</p>
            )}
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
                Resetting...
              </span>
            ) : (
              <>
                Reset Password <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-white/5 text-center text-xs text-gray-400">
          <Link to="/login" className="text-[#7BC4BE] hover:underline font-semibold inline-flex items-center gap-1">
            <ArrowLeft size={12} /> Back to Sign In
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
