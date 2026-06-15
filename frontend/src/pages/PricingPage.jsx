import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Check, Star, ShieldAlert } from "lucide-react";
import { api } from "../services/api";

export default function PricingPage() {
  const [currentPlan, setCurrentPlan] = useState("free");
  const [loading, setLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAuth = async () => {
      const auth = api.isAuthenticated();
      setIsLoggedIn(auth);
      if (auth) {
        try {
          const sub = await api.getSubscription();
          setCurrentPlan(sub.plan_type);
        } catch (err) {
          console.error(err);
        }
      }
    };
    checkAuth();
  }, []);

  const handleUpgrade = async (planType) => {
    if (!isLoggedIn) {
      navigate("/register");
      return;
    }
    if (planType === currentPlan) return;
    
    setLoading(true);
    try {
      await api.upgradeSubscription(planType);
      alert(`Successfully upgraded to ${planType.toUpperCase()}!`);
      setCurrentPlan(planType);
      navigate("/dashboard");
    } catch (err) {
      alert("Upgrade failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const tiers = [
    {
      name: "Free Plan",
      price: "$0",
      description: "Ideal for fresh graduates testing out ATS principles.",
      features: [
        "1 ATS-optimized resume",
        "Harvard rules checks (Standard)",
        "Basic markdown text export",
        "Simulated AI recommendations"
      ],
      planKey: "free",
      cta: "Current Plan",
      popular: false
    },
    {
      name: "Pro Professional",
      price: "$29",
      period: "/month",
      description: "Perfect for active job seekers targeting tier-1 tech & finance companies.",
      features: [
        "Unlimited resumes and cover letters",
        "Full Playwright PDF exports",
        "Real-time ATS scoring system",
        "AI assistant block rewriter",
        "24 premium templates catalog access"
      ],
      planKey: "pro",
      cta: "Upgrade to Pro",
      popular: true
    },
    {
      name: "Enterprise Career",
      price: "$99",
      period: "/month",
      description: "For agencies, career consultancies, and executive professionals.",
      features: [
        "Everything in Pro Plan",
        "Priority Gemini LLM throughput",
        "Custom template styling engine",
        "Dedicated API key usage limits",
        "1-on-1 career consultant access mock sessions"
      ],
      planKey: "enterprise",
      cta: "Upgrade to Enterprise",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-[#0F1E1E] text-white flex flex-col">
      {/* Header */}
      <header className="px-6 py-4 border-b border-white/5 backdrop-blur-md sticky top-0 z-50 flex justify-between items-center bg-[#0F1E1E]/80">
        <Link to="/">
          <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
            <span className="text-[#7BC4BE]">✦</span> Prompt<span className="text-[#7BC4BE]">Resume</span>
          </span>
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/about" className="text-gray-300 hover:text-white text-sm transition-all">About</Link>
          <Link to="/contact" className="text-gray-300 hover:text-white text-sm transition-all">Contact</Link>
          {isLoggedIn ? (
            <Link to="/dashboard" className="px-4 py-2 bg-white/10 hover:bg-white/15 rounded-lg text-sm transition-all border border-white/10">Dashboard</Link>
          ) : (
            <>
              <Link to="/login" className="text-gray-300 hover:text-white text-sm font-medium transition-all">Sign In</Link>
              <Link to="/register" className="px-4 py-2 bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] rounded-lg text-sm font-semibold transition-all">Start Free</Link>
            </>
          )}
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 py-16 px-4 max-w-6xl mx-auto w-full relative">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-[#7BC4BE]/5 rounded-full blur-[100px] pointer-events-none" />

        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight mb-4 text-white">
            Simple, Transparent <span className="text-[#7BC4BE]">Pricing</span>
          </h1>
          <p className="text-gray-400 max-w-xl mx-auto text-base">
            Choose the plan that suits your career path. Secure job interviews with ATS-approved Harvard-style resumes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers.map((tier, idx) => {
            const isCurrent = tier.planKey === currentPlan;
            return (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className={`rounded-2xl p-8 backdrop-blur-md border flex flex-col justify-between relative overflow-hidden transition-all duration-300 ${
                  tier.popular
                    ? "bg-white/10 border-[#7BC4BE] shadow-xl shadow-[#7BC4BE]/5"
                    : "bg-white/5 border-white/10 hover:border-white/20"
                }`}
              >
                {tier.popular && (
                  <div className="absolute top-4 right-4 bg-[#7BC4BE] text-[#1A2B2A] text-[10px] font-bold tracking-widest uppercase px-2.5 py-1 rounded-full flex items-center gap-1">
                    <Star size={10} fill="currentColor" /> Most Popular
                  </div>
                )}

                <div>
                  <h3 className="text-lg font-bold text-white mb-2">{tier.name}</h3>
                  <div className="flex items-baseline mb-3">
                    <span className="text-4xl font-extrabold text-white">{tier.price}</span>
                    {tier.period && <span className="text-gray-400 text-sm ml-1">{tier.period}</span>}
                  </div>
                  <p className="text-gray-400 text-xs leading-relaxed mb-6 border-b border-white/5 pb-6">
                    {tier.description}
                  </p>

                  <ul className="space-y-4 mb-8">
                    {tier.features.map((feature, fIdx) => (
                      <li key={fIdx} className="flex items-start gap-2.5 text-xs text-gray-300">
                        <Check size={14} className="text-[#7BC4BE] shrink-0 mt-0.5" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleUpgrade(tier.planKey)}
                  disabled={loading || isCurrent}
                  className={`w-full py-3 rounded-xl text-xs font-bold transition-all ${
                    isCurrent
                      ? "bg-white/5 border border-white/10 text-gray-400 cursor-default"
                      : tier.popular
                      ? "bg-[#7BC4BE] hover:bg-[#8AD6CF] text-[#1A2B2A] shadow-md shadow-[#7BC4BE]/10"
                      : "bg-white/10 hover:bg-white/15 text-white border border-white/10"
                  }`}
                >
                  {isCurrent ? "Active Plan" : tier.cta}
                </button>
              </motion.div>
            );
          })}
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-white/5 text-center text-xs text-gray-500 bg-[#0A1414]">
        © 2026 Prompt Resume. All rights reserved. Made for professional ATS styling.
      </footer>
    </div>
  );
}
