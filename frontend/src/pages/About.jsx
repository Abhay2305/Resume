import React from "react";
import { Link } from "react-router-dom";
import { Shield, Sparkles, BookOpen, UserCheck } from "lucide-react";

export default function About() {
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
          <Link to="/pricing" className="text-gray-300 hover:text-white text-sm transition-all">Pricing</Link>
          <Link to="/contact" className="text-gray-300 hover:text-white text-sm transition-all">Contact</Link>
          <Link to="/login" className="px-4 py-2 bg-white/10 hover:bg-white/15 rounded-lg text-sm transition-all border border-white/10">Sign In</Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 py-16 px-6 max-w-4xl mx-auto w-full">
        <div className="text-center mb-16">
          <span className="px-3 py-1 rounded-full bg-[#7BC4BE]/10 border border-[#7BC4BE]/20 text-[#7BC4BE] text-xs font-semibold uppercase tracking-wider">
            Our Vision
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight mt-4 mb-4">
            Democratizing Executive <span className="text-[#7BC4BE]">Resume Writing</span>
          </h1>
          <p className="text-gray-400 max-w-xl mx-auto text-base">
            Prompt Resume was built by career advisors and AI engineers to solve the "blank page anxiety" of job application writing.
          </p>
        </div>

        <div className="space-y-12">
          <section className="bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
            <h2 className="text-xl font-bold text-white mb-3 flex items-center gap-2">
              <BookOpen size={20} className="text-[#7BC4BE]" /> The Harvard Knowledge Engine
            </h2>
            <p className="text-gray-300 text-sm leading-relaxed">
              Resumes aren't just descriptions of what you did; they are marketing pitch decks for your career. Our core differentiator is the 
              <strong> Harvard Knowledge Engine</strong>. Rather than using generic ChatGPT algorithms that make you sound like a robot, we index database 
              rules directly compiled from career consultants. We enforce the use of active verbs, mandate quantified metrics, and ban first-person pronouns, 
              aligning your background with elite standards.
            </p>
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                <Sparkles size={18} className="text-[#FAD07A]" /> Raw to Professional
              </h3>
              <p className="text-gray-400 text-xs leading-relaxed">
                You write down messy, bullet-point drafts. Our system parses, structures, and outputs polished professional summaries and achievements instantly.
              </p>
            </div>

            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-lg font-bold mb-2 flex items-center gap-2">
                <Shield size={18} className="text-[#7BC4BE]" /> Playwright Export
              </h3>
              <p className="text-gray-400 text-xs leading-relaxed">
                We generate PDF resumes using Playwright in headless Chromium, preserving margins, spacing, and typography so they are parsed perfectly by ATS screening bots.
              </p>
            </div>
          </div>

          <section className="text-center py-8">
            <h3 className="text-xl font-bold mb-3">Ready to transform your application?</h3>
            <Link
              to="/register"
              className="inline-block px-8 py-3.5 bg-gradient-to-r from-[#7BC4BE] to-[#4A9E98] hover:from-[#8AD6CF] hover:to-[#5BB2AC] text-[#1A2B2A] font-bold rounded-xl text-sm transition-all shadow-lg shadow-[#7BC4BE]/10"
            >
              Get Started for Free
            </Link>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5 text-center text-xs text-gray-500 bg-[#0A1414]">
        © 2026 Prompt Resume. All rights reserved.
      </footer>
    </div>
  );
}
