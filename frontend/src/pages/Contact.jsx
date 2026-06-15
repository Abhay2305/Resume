import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Mail, MessageSquare, Send, CheckCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function Contact() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    // Simulate API submission
    setTimeout(() => {
      setLoading(false);
      setSubmitted(true);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 border-b border-white/5 backdrop-blur-md sticky top-0 z-50 flex justify-between items-center bg-[#0F1E1E]/80">
        <Link to="/">
          <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
            <span className="text-[#7BC4BE]">✦</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
          </span>
        </Link>
        <div className="flex gap-4">
          <Link to="/about" className="text-gray-300 hover:text-white text-sm transition-all">About</Link>
          <Link to="/pricing" className="text-gray-300 hover:text-white text-sm transition-all">Pricing</Link>
          <Link to="/login" className="px-4 py-2 bg-white/10 hover:bg-white/15 rounded-lg text-sm transition-all border border-white/10">Sign In</Link>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 py-16 px-4 max-w-lg mx-auto w-full flex items-center justify-center">
        {submitted ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white/5 border border-white/10 p-8 rounded-2xl text-center space-y-4 shadow-xl"
          >
            <div className="w-16 h-16 bg-[#7BC4BE]/15 rounded-full flex items-center justify-center mx-auto text-[#7BC4BE]">
              <CheckCircle size={32} />
            </div>
            <h2 className="text-2xl font-bold text-white">Message Sent!</h2>
            <p className="text-gray-400 text-sm">
              Thank you for reaching out. A career advisor or support representative will contact you within 24 hours.
            </p>
            <Link
              to="/"
              className="inline-block mt-4 px-6 py-2.5 bg-white/10 hover:bg-white/15 text-white border border-white/10 rounded-xl text-xs font-semibold transition-all"
            >
              Back to Home
            </Link>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full bg-white/5 border border-white/10 p-8 rounded-2xl shadow-xl relative overflow-hidden backdrop-blur-sm"
          >
            <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-[#7BC4BE] via-[#FAD07A] to-[#7BC4BE]" />

            <div className="mb-6">
              <h1 className="text-2xl font-bold mb-1">Get in Touch</h1>
              <p className="text-gray-400 text-xs">
                Questions about templates, subscriptions, or custom integrations? Send us a message!
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Your Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Alex Mercer"
                  className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 px-3 text-white text-xs placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE]"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Email Address</label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-gray-400">
                    <Mail size={14} />
                  </span>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="alex@example.com"
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-bold uppercase tracking-wider text-gray-400 mb-1.5">Message / Inquiry</label>
                <div className="relative">
                  <span className="absolute top-3 left-3 text-gray-400">
                    <MessageSquare size={14} />
                  </span>
                  <textarea
                    required
                    rows={4}
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Describe your inquiry..."
                    className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-9 pr-3 text-white text-xs placeholder-gray-500 focus:outline-none focus:border-[#7BC4BE]"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-bold rounded-xl py-3 text-xs transition-all flex items-center justify-center gap-1.5 shadow-lg shadow-[#7BC4BE]/10"
              >
                {loading ? "Sending..." : (
                  <>
                    Send Message <Send size={12} />
                  </>
                )}
              </button>
            </form>
          </motion.div>
        )}
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5 text-center text-xs text-gray-500 bg-[#0A1414]">
        © 2026 Prompt Resume. All rights reserved.
      </footer>
    </div>
  );
}
