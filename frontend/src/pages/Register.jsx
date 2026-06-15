import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, User, ArrowRight } from "lucide-react";
import { api } from "../services/api";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.register(email, password, fullName);
      // Auto login after registration
      await api.login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Registration failed. Email might already exist.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-tr from-[#1A2B2A] via-[#0F1E1E] to-[#2D3F3E] flex items-center justify-center p-4">
      {/* Blur Orbs */}
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
              <span className="text-[#7BC4BE]">✦</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
            </span>
          </Link>
          <h2 className="text-xl font-medium text-white/90">Get started today</h2>
          <p className="text-sm text-gray-400 mt-1">Create an account to start building ATS resumes</p>
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
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Full Name</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                <User size={16} />
              </span>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all"
              />
            </div>
          </div>

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
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                <Lock size={16} />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE] focus:ring-1 focus:ring-[#7BC4BE] transition-all"
              />
            </div>
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
                Registering...
              </span>
            ) : (
              <>
                Register Account <ArrowRight size={16} />
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-white/5 text-center text-xs text-gray-400">
          Already have an account?{" "}
          <Link to="/login" className="text-[#7BC4BE] hover:underline font-semibold">
            Sign In
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
