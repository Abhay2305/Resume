import { useReveal } from "./hooks/useReveal";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import CoverLetterSection from "./components/CoverLetterSection";
import ATSSection from "./components/ATSSection";
import Templates from "./components/Templates";
import Workflow from "./components/Workflow";
import Testimonials from "./components/Testimonials";
import Pricing from "./components/Pricing";
import FAQ from "./components/FAQ";
import Footer from "./components/Footer";
import FinalCTA from "./components/FinalCTA";

export default function LandingPage({ onBuildResume }) {
  // Initialize the scroll reveal animations once on the parent
  useReveal();

  return (
    <>
      <Navbar onBuildResume={onBuildResume} />
      <Hero onBuildResume={onBuildResume} />
      
      {/* You can also extract Stats, AI Mode, Before/After into their own components */}
      
      <Templates onBuildResume={onBuildResume} />
      {/* <ATSSection /> */}
      <CoverLetterSection />
      <Workflow />
      <Testimonials />
      <Pricing />
      <FAQ />
      
      <FinalCTA onBuildResume={onBuildResume} />
      
      <Footer />
    </>
  );
}




// import { useState, useEffect, useRef } from "react";

// const COLORS = {
//   teal: "#7BC4BE",
//   tealLight: "#A8D8D3",
//   tealDark: "#4A9E98",
//   tealDeep: "#2D7A74",
//   ivory: "#F4F1EA",
//   cream: "#FFFDF8",
//   amber: "#F6B233",
//   amberLight: "#FAD07A",
//   amberDark: "#D4920F",
//   text: "#1A2B2A",
//   textMid: "#3D5552",
//   textMuted: "#6B8A87",
//   border: "rgba(123,196,190,0.25)",
//   borderMid: "rgba(123,196,190,0.45)",
// };

// const css = `
//   @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

//   *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

//   :root {
//     --teal: #7BC4BE;
//     --teal-light: #A8D8D3;
//     --teal-dark: #4A9E98;
//     --teal-deep: #2D7A74;
//     --ivory: #F4F1EA;
//     --cream: #FFFDF8;
//     --amber: #F6B233;
//     --amber-light: #FAD07A;
//     --amber-dark: #D4920F;
//     --text: #1A2B2A;
//     --text-mid: #3D5552;
//     --text-muted: #6B8A87;
//     --border: rgba(123,196,190,0.25);
//     --border-mid: rgba(123,196,190,0.45);
//   }

//   html { scroll-behavior: smooth; }

//   body {
//     font-family: 'DM Sans', sans-serif;
//     background: var(--cream);
//     color: var(--text);
//     overflow-x: hidden;
//     line-height: 1.6;
//   }

//   .serif { font-family: 'DM Serif Display', serif; }

//   /* ANIMATIONS */
//   @keyframes fadeUp {
//     from { opacity: 0; transform: translateY(28px); }
//     to   { opacity: 1; transform: translateY(0); }
//   }
//   @keyframes fadeIn {
//     from { opacity: 0; } to { opacity: 1; }
//   }
//   @keyframes float {
//     0%,100% { transform: translateY(0px); }
//     50%      { transform: translateY(-8px); }
//   }
//   @keyframes floatSlow {
//     0%,100% { transform: translateY(0px) rotate(0deg); }
//     50%      { transform: translateY(-12px) rotate(2deg); }
//   }
//   @keyframes pulse {
//     0%,100% { opacity: 0.5; transform: scale(1); }
//     50%      { opacity: 1; transform: scale(1.12); }
//   }
//   @keyframes atsGrow {
//     from { width: 0%; }
//     to   { width: 94%; }
//   }
//   @keyframes shimmer {
//     0%   { background-position: -200% center; }
//     100% { background-position: 200% center; }
//   }
//   @keyframes typewrite {
//     from { width: 0; }
//     to   { width: 100%; }
//   }
//   @keyframes blink {
//     0%,100% { border-color: transparent; }
//     50%      { border-color: var(--teal); }
//   }
//   @keyframes orbit {
//     from { transform: rotate(0deg) translateX(56px) rotate(0deg); }
//     to   { transform: rotate(360deg) translateX(56px) rotate(-360deg); }
//   }
//   @keyframes scanLine {
//     0%   { top: 0%; opacity: 0.6; }
//     100% { top: 100%; opacity: 0; }
//   }
//   @keyframes pixelFloat {
//     0%,100% { transform: translateY(0) translateX(0); opacity: 0.6; }
//     25%      { transform: translateY(-6px) translateX(3px); opacity: 1; }
//     75%      { transform: translateY(4px) translateX(-2px); opacity: 0.4; }
//   }
//   @keyframes gradientShift {
//     0%   { background-position: 0% 50%; }
//     50%  { background-position: 100% 50%; }
//     100% { background-position: 0% 50%; }
//   }
//   @keyframes slideInLeft {
//     from { opacity: 0; transform: translateX(-32px); }
//     to   { opacity: 1; transform: translateX(0); }
//   }
//   @keyframes slideInRight {
//     from { opacity: 0; transform: translateX(32px); }
//     to   { opacity: 1; transform: translateX(0); }
//   }
//   @keyframes countUp {
//     from { opacity: 0; transform: translateY(10px); }
//     to   { opacity: 1; transform: translateY(0); }
//   }
//   @keyframes spin {
//     from { transform: rotate(0deg); }
//     to   { transform: rotate(360deg); }
//   }
//   @keyframes checkPop {
//     0%   { transform: scale(0) rotate(-10deg); opacity: 0; }
//     70%  { transform: scale(1.2) rotate(3deg); opacity: 1; }
//     100% { transform: scale(1) rotate(0deg); opacity: 1; }
//   }
//   @keyframes lineGrow {
//     from { transform: scaleX(0); }
//     to   { transform: scaleX(1); }
//   }
//   @keyframes waveIn {
//     0%   { clip-path: inset(0 100% 0 0); }
//     100% { clip-path: inset(0 0% 0 0); }
//   }

//   .anim-fadeUp   { animation: fadeUp 0.7s cubic-bezier(.22,1,.36,1) both; }
//   .anim-fadeIn   { animation: fadeIn 0.6s ease both; }
//   .anim-float    { animation: float 4s ease-in-out infinite; }
//   .anim-floatSlow{ animation: floatSlow 6s ease-in-out infinite; }
//   .anim-pulse    { animation: pulse 2.5s ease-in-out infinite; }

//   .delay-1 { animation-delay: 0.1s; }
//   .delay-2 { animation-delay: 0.2s; }
//   .delay-3 { animation-delay: 0.3s; }
//   .delay-4 { animation-delay: 0.4s; }
//   .delay-5 { animation-delay: 0.5s; }
//   .delay-6 { animation-delay: 0.6s; }
//   .delay-7 { animation-delay: 0.7s; }
//   .delay-8 { animation-delay: 0.8s; }
//   .delay-9 { animation-delay: 0.9s; }
//   .delay-10{ animation-delay: 1.0s; }
//   .delay-12{ animation-delay: 1.2s; }
//   .delay-15{ animation-delay: 1.5s; }

//   /* SCROLL REVEAL */
//   .reveal {
//     opacity: 0;
//     transform: translateY(24px);
//     transition: opacity 0.7s cubic-bezier(.22,1,.36,1), transform 0.7s cubic-bezier(.22,1,.36,1);
//   }
//   .reveal.visible {
//     opacity: 1;
//     transform: translateY(0);
//   }
//   .reveal-left {
//     opacity: 0;
//     transform: translateX(-24px);
//     transition: opacity 0.7s cubic-bezier(.22,1,.36,1), transform 0.7s cubic-bezier(.22,1,.36,1);
//   }
//   .reveal-left.visible { opacity: 1; transform: translateX(0); }
//   .reveal-right {
//     opacity: 0;
//     transform: translateX(24px);
//     transition: opacity 0.7s cubic-bezier(.22,1,.36,1), transform 0.7s cubic-bezier(.22,1,.36,1);
//   }
//   .reveal-right.visible { opacity: 1; transform: translateX(0); }

//   /* NAV */
//   .nav {
//     position: fixed; top: 0; left: 0; right: 0; z-index: 100;
//     padding: 0 2rem;
//     height: 68px;
//     display: flex; align-items: center; justify-content: space-between;
//     transition: background 0.3s, box-shadow 0.3s;
//   }
//   .nav.scrolled {
//     background: rgba(255,253,248,0.92);
//     backdrop-filter: blur(14px);
//     box-shadow: 0 1px 0 rgba(123,196,190,0.2);
//   }
//   .nav-logo {
//     display: flex; align-items: center; gap: 10px;
//     font-family: 'DM Serif Display', serif;
//     font-size: 1.3rem; color: var(--text); text-decoration: none;
//   }
//   .nav-logo-mark {
//     width: 34px; height: 34px; border-radius: 10px;
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     display: flex; align-items: center; justify-content: center;
//     color: white; font-size: 0.85rem; font-weight: 600;
//     box-shadow: 0 2px 8px rgba(75,158,152,0.35);
//   }
//   .nav-links {
//     display: flex; align-items: center; gap: 2rem;
//     list-style: none;
//   }
//   .nav-links a {
//     color: var(--text-mid); text-decoration: none; font-size: 0.9rem;
//     font-weight: 400; transition: color 0.2s;
//   }
//   .nav-links a:hover { color: var(--text); }
//   .nav-cta {
//     display: flex; align-items: center; gap: 12px;
//   }
//   .btn-ghost {
//     background: none; border: 1px solid var(--border-mid);
//     color: var(--text-mid); padding: 8px 18px; border-radius: 8px;
//     font-size: 0.875rem; cursor: pointer; transition: all 0.2s;
//     font-family: 'DM Sans', sans-serif;
//   }
//   .btn-ghost:hover { border-color: var(--teal); color: var(--text); }
//   .btn-primary {
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     color: white; border: none; padding: 9px 20px; border-radius: 8px;
//     font-size: 0.875rem; font-weight: 500; cursor: pointer;
//     transition: all 0.2s; box-shadow: 0 2px 8px rgba(75,158,152,0.3);
//     font-family: 'DM Sans', sans-serif;
//   }
//   .btn-primary:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(75,158,152,0.4); }
//   .btn-primary:active { transform: translateY(0); }

//   /* HERO */
//   .hero {
//     min-height: 100vh;
//     padding: 120px 2rem 80px;
//     display: grid;
//     grid-template-columns: 1fr 1fr;
//     gap: 5rem;
//     align-items: center;
//     max-width: 1200px;
//     margin: 0 auto;
//     position: relative;
//   }
//   .hero-bg {
//     position: fixed; inset: 0; z-index: -1;
//     background: var(--cream);
//     overflow: hidden;
//   }
//   .hero-bg-blob1 {
//     position: absolute; top: -15%; left: -10%;
//     width: 65vw; height: 65vw; border-radius: 50%;
//     background: radial-gradient(circle, rgba(168,216,211,0.18) 0%, transparent 70%);
//   }
//   .hero-bg-blob2 {
//     position: absolute; bottom: -10%; right: -10%;
//     width: 50vw; height: 50vw; border-radius: 50%;
//     background: radial-gradient(circle, rgba(246,178,51,0.1) 0%, transparent 70%);
//   }
//   .hero-bg-grid {
//     position: absolute; inset: 0;
//     background-image:
//       linear-gradient(rgba(123,196,190,0.06) 1px, transparent 1px),
//       linear-gradient(90deg, rgba(123,196,190,0.06) 1px, transparent 1px);
//     background-size: 48px 48px;
//   }

//   /* Pixel particles */
//   .pixel-particle {
//     position: absolute; width: 3px; height: 3px;
//     background: var(--teal); border-radius: 0;
//     animation: pixelFloat 3s ease-in-out infinite;
//   }

//   .hero-badge {
//     display: inline-flex; align-items: center; gap: 8px;
//     background: rgba(123,196,190,0.12); border: 1px solid var(--border-mid);
//     border-radius: 100px; padding: 6px 14px 6px 8px;
//     font-size: 0.8rem; color: var(--teal-deep); margin-bottom: 1.5rem;
//   }
//   .hero-badge-dot {
//     width: 6px; height: 6px; border-radius: 50%;
//     background: var(--teal); animation: pulse 2s ease-in-out infinite;
//   }

//   .hero-headline {
//     font-family: 'DM Serif Display', serif;
//     font-size: clamp(2.8rem, 5vw, 4.2rem);
//     line-height: 1.1;
//     color: var(--text);
//     margin-bottom: 1.25rem;
//   }
//   .hero-headline em {
//     font-style: italic;
//     color: var(--teal-dark);
//     position: relative;
//   }
//   .hero-headline em::after {
//     content: '';
//     position: absolute;
//     bottom: -2px; left: 0; right: 0; height: 2px;
//     background: linear-gradient(90deg, var(--teal), var(--amber));
//     border-radius: 2px;
//     transform-origin: left;
//     animation: lineGrow 1s 0.8s cubic-bezier(.22,1,.36,1) both;
//   }

//   .hero-sub {
//     font-size: 1.1rem; color: var(--text-mid); line-height: 1.7;
//     margin-bottom: 2rem; font-weight: 300; max-width: 480px;
//   }

//   .hero-modes {
//     display: flex; gap: 12px; margin-bottom: 2rem; flex-wrap: wrap;
//   }
//   .hero-mode-chip {
//     display: flex; align-items: center; gap: 6px;
//     background: white; border: 1px solid var(--border-mid);
//     border-radius: 8px; padding: 7px 14px;
//     font-size: 0.82rem; color: var(--text-mid); font-weight: 400;
//     box-shadow: 0 1px 3px rgba(0,0,0,0.04);
//   }
//   .hero-mode-chip-dot {
//     width: 7px; height: 7px; border-radius: 1px;
//     background: var(--teal); flex-shrink: 0;
//   }
//   .hero-mode-chip-dot.amber { background: var(--amber); }

//   .hero-ctas {
//     display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
//   }
//   .btn-hero {
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     color: white; border: none; padding: 14px 28px; border-radius: 10px;
//     font-size: 1rem; font-weight: 500; cursor: pointer;
//     transition: all 0.25s cubic-bezier(.22,1,.36,1);
//     box-shadow: 0 4px 20px rgba(75,158,152,0.35);
//     font-family: 'DM Sans', sans-serif;
//     display: flex; align-items: center; gap: 8px;
//   }
//   .btn-hero:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(75,158,152,0.45); }
//   .btn-hero-sec {
//     background: none; border: 1px solid var(--border-mid); color: var(--text-mid);
//     padding: 13px 24px; border-radius: 10px; font-size: 0.95rem;
//     cursor: pointer; transition: all 0.2s; font-family: 'DM Sans', sans-serif;
//     display: flex; align-items: center; gap: 8px;
//   }
//   .btn-hero-sec:hover { border-color: var(--teal); color: var(--text); background: rgba(123,196,190,0.06); }

//   /* HERO VISUAL */
//   .hero-visual {
//     position: relative;
//     height: 560px;
//   }
//   .resume-card {
//     position: absolute;
//     background: white;
//     border-radius: 16px;
//     box-shadow: 0 8px 40px rgba(29,79,75,0.12), 0 2px 8px rgba(29,79,75,0.06);
//     border: 1px solid var(--border);
//     overflow: hidden;
//   }
//   .resume-main {
//     width: 300px;
//     top: 20px; left: 20px;
//     animation: float 5s ease-in-out infinite;
//   }
//   .resume-header {
//     background: linear-gradient(135deg, var(--teal-dark), var(--teal));
//     padding: 20px;
//     color: white;
//   }
//   .resume-name {
//     font-family: 'DM Serif Display', serif;
//     font-size: 1.1rem; margin-bottom: 2px;
//   }
//   .resume-role {
//     font-size: 0.72rem; opacity: 0.85; font-weight: 300;
//   }
//   .resume-body {
//     padding: 16px;
//   }
//   .resume-section-label {
//     font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em;
//     text-transform: uppercase; color: var(--teal-dark);
//     margin-bottom: 6px; display: flex; align-items: center; gap: 5px;
//   }
//   .resume-section-label::after {
//     content: ''; flex: 1; height: 1px; background: var(--border-mid);
//   }
//   .resume-line {
//     height: 5px; border-radius: 3px;
//     background: var(--ivory); margin-bottom: 4px;
//   }
//   .resume-line.active {
//     background: linear-gradient(90deg, var(--teal-light), var(--teal));
//     animation: shimmer 2s linear infinite;
//     background-size: 200% auto;
//   }
//   .resume-line-short { width: 55%; }
//   .resume-line-med   { width: 75%; }
//   .resume-line-full  { width: 95%; }

//   .ats-badge {
//     position: absolute;
//     top: 0; right: -10px;
//     background: white;
//     border-radius: 14px;
//     padding: 14px 18px;
//     box-shadow: 0 6px 24px rgba(29,79,75,0.15);
//     border: 1px solid var(--border);
//     animation: float 4.5s 0.5s ease-in-out infinite;
//     min-width: 140px;
//   }
//   .ats-label {
//     font-size: 0.65rem; color: var(--text-muted); font-weight: 500;
//     letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 6px;
//   }
//   .ats-score {
//     font-family: 'DM Serif Display', serif;
//     font-size: 2.2rem; color: var(--text); line-height: 1;
//     display: flex; align-items: baseline; gap: 3px;
//   }
//   .ats-score span { font-size: 1rem; color: var(--text-muted); font-family: 'DM Sans', sans-serif; }
//   .ats-bar-track {
//     height: 5px; background: var(--ivory); border-radius: 3px;
//     margin-top: 8px; overflow: hidden;
//   }
//   .ats-bar-fill {
//     height: 100%; border-radius: 3px;
//     background: linear-gradient(90deg, var(--teal), var(--amber));
//     animation: atsGrow 2s 0.8s cubic-bezier(.22,1,.36,1) both;
//   }

//   .ai-prompt-card {
//     position: absolute;
//     bottom: 40px; left: 0;
//     width: 280px;
//     background: white;
//     border-radius: 14px;
//     padding: 16px;
//     box-shadow: 0 6px 24px rgba(29,79,75,0.12);
//     border: 1px solid var(--border);
//     animation: float 5.5s 1s ease-in-out infinite;
//   }
//   .ai-prompt-label {
//     font-size: 0.65rem; color: var(--teal-dark); font-weight: 600;
//     letter-spacing: 0.08em; text-transform: uppercase;
//     margin-bottom: 8px; display: flex; align-items: center; gap: 5px;
//   }
//   .ai-prompt-text {
//     font-size: 0.78rem; color: var(--text-mid); line-height: 1.5;
//     border-left: 2px solid var(--teal-light); padding-left: 8px;
//     font-style: italic;
//   }
//   .ai-prompt-btn {
//     margin-top: 10px;
//     width: 100%; background: var(--ivory);
//     border: none; border-radius: 7px; padding: 8px;
//     font-size: 0.75rem; color: var(--teal-dark); font-weight: 500;
//     cursor: pointer; transition: background 0.2s;
//     font-family: 'DM Sans', sans-serif;
//     display: flex; align-items: center; justify-content: center; gap: 5px;
//   }
//   .ai-prompt-btn:hover { background: rgba(123,196,190,0.18); }

//   .recruiter-badge {
//     position: absolute;
//     top: 180px; right: -30px;
//     background: linear-gradient(135deg, var(--amber), var(--amber-dark));
//     color: white; border-radius: 12px; padding: 10px 14px;
//     font-size: 0.72rem; font-weight: 500;
//     box-shadow: 0 4px 16px rgba(246,178,51,0.35);
//     animation: float 6s 0.3s ease-in-out infinite;
//     max-width: 150px; text-align: center;
//   }
//   .recruiter-badge-icon { font-size: 1.1rem; margin-bottom: 2px; }

//   .export-chip {
//     position: absolute;
//     bottom: 110px; right: -20px;
//     background: white;
//     border: 1px solid var(--border-mid);
//     border-radius: 8px; padding: 8px 12px;
//     font-size: 0.72rem; color: var(--text-mid);
//     box-shadow: 0 3px 12px rgba(29,79,75,0.1);
//     display: flex; align-items: center; gap: 6px;
//     animation: float 4s 0.8s ease-in-out infinite;
//   }
//   .export-chip-dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; flex-shrink: 0; }

//   /* STATS STRIP */
//   .stats-strip {
//     background: white;
//     border-top: 1px solid var(--border);
//     border-bottom: 1px solid var(--border);
//     padding: 2rem;
//   }
//   .stats-inner {
//     max-width: 1100px; margin: 0 auto;
//     display: flex; align-items: center;
//     justify-content: space-between; flex-wrap: wrap; gap: 2rem;
//   }
//   .stat-item {
//     text-align: center; flex: 1; min-width: 120px;
//   }
//   .stat-number {
//     font-family: 'DM Serif Display', serif;
//     font-size: 2rem; color: var(--text); line-height: 1;
//     display: flex; align-items: baseline; justify-content: center; gap: 2px;
//   }
//   .stat-number sup { font-size: 0.9rem; color: var(--teal-dark); margin-right: 1px; }
//   .stat-number sub { font-size: 0.8rem; color: var(--teal-dark); }
//   .stat-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; font-weight: 400; }
//   .stat-divider { width: 1px; height: 48px; background: var(--border-mid); flex-shrink: 0; }

//   .company-logos {
//     display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;
//     border-left: 1px solid var(--border-mid); padding-left: 2rem;
//   }
//   .company-logo {
//     font-family: 'DM Serif Display', serif;
//     font-size: 1rem; color: var(--text-muted); letter-spacing: -0.02em;
//     opacity: 0.5;
//   }

//   /* SECTION COMMON */
//   .section {
//     padding: 100px 2rem;
//     max-width: 1200px;
//     margin: 0 auto;
//   }
//   .section-tag {
//     display: inline-flex; align-items: center; gap: 6px;
//     background: rgba(123,196,190,0.12); border: 1px solid var(--border-mid);
//     border-radius: 100px; padding: 5px 14px;
//     font-size: 0.75rem; font-weight: 500;
//     color: var(--teal-dark); letter-spacing: 0.05em;
//     text-transform: uppercase; margin-bottom: 1rem;
//   }
//   .section-tag-amber {
//     background: rgba(246,178,51,0.1); border-color: rgba(246,178,51,0.3);
//     color: var(--amber-dark);
//   }
//   .section-headline {
//     font-family: 'DM Serif Display', serif;
//     font-size: clamp(2rem, 3.5vw, 3rem);
//     color: var(--text); line-height: 1.2; margin-bottom: 1rem;
//   }
//   .section-sub {
//     font-size: 1.05rem; color: var(--text-mid); font-weight: 300;
//     max-width: 580px; line-height: 1.7;
//   }
//   .section-sub.centered { text-align: center; margin: 0 auto 3rem; }
//   .text-centered { text-align: center; }

//   /* AI MODE SECTION */
//   .ai-section-grid {
//     display: grid; grid-template-columns: 1fr 1fr;
//     gap: 5rem; align-items: center;
//   }
//   .ai-feature-list {
//     display: flex; flex-direction: column; gap: 1.25rem; margin-top: 2rem;
//   }
//   .ai-feature-item {
//     display: flex; align-items: flex-start; gap: 14px;
//     padding: 16px; background: white; border-radius: 12px;
//     border: 1px solid var(--border);
//     transition: border-color 0.2s, box-shadow 0.2s;
//   }
//   .ai-feature-item:hover {
//     border-color: var(--teal-light);
//     box-shadow: 0 4px 16px rgba(123,196,190,0.15);
//   }
//   .ai-feature-icon {
//     width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
//     background: linear-gradient(135deg, rgba(168,216,211,0.4), rgba(123,196,190,0.2));
//     display: flex; align-items: center; justify-content: center;
//     font-size: 1rem;
//   }
//   .ai-feature-title { font-size: 0.9rem; font-weight: 500; color: var(--text); margin-bottom: 2px; }
//   .ai-feature-desc  { font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; }

//   /* PROMPT DEMO */
//   .prompt-demo {
//     background: white; border-radius: 20px;
//     border: 1px solid var(--border);
//     box-shadow: 0 8px 40px rgba(29,79,75,0.08);
//     overflow: hidden;
//   }
//   .prompt-demo-header {
//     background: var(--ivory); padding: 12px 20px;
//     display: flex; align-items: center; gap: 6px;
//     border-bottom: 1px solid var(--border);
//   }
//   .demo-dot { width: 10px; height: 10px; border-radius: 50%; }
//   .demo-dot.r { background: #ff5f57; }
//   .demo-dot.y { background: #ffbd2e; }
//   .demo-dot.g { background: #28c840; }
//   .demo-title {
//     margin-left: 6px; font-size: 0.75rem; color: var(--text-muted);
//   }
//   .prompt-body { padding: 20px; }
//   .prompt-label {
//     font-size: 0.7rem; font-weight: 600; color: var(--teal-dark);
//     letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px;
//   }
//   .prompt-input {
//     background: var(--ivory); border-radius: 10px;
//     border: 1px solid var(--border-mid);
//     padding: 14px; font-size: 0.85rem;
//     color: var(--text-mid); line-height: 1.6; margin-bottom: 14px;
//     font-style: italic; position: relative;
//   }
//   .cursor-blink {
//     display: inline-block; width: 2px; height: 14px;
//     background: var(--teal); vertical-align: middle; margin-left: 2px;
//     animation: blink 1s step-end infinite;
//   }
//   .generate-btn {
//     width: 100%; background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     color: white; border: none; border-radius: 9px; padding: 12px;
//     font-size: 0.88rem; font-weight: 500; cursor: pointer;
//     font-family: 'DM Sans', sans-serif; display: flex;
//     align-items: center; justify-content: center; gap: 8px;
//     transition: all 0.2s;
//   }
//   .generate-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(75,158,152,0.35); }

//   .result-preview {
//     margin-top: 14px; padding: 14px;
//     background: rgba(123,196,190,0.06);
//     border-radius: 10px; border: 1px solid rgba(123,196,190,0.2);
//   }
//   .result-preview-title {
//     font-size: 0.72rem; font-weight: 600; color: var(--teal-dark);
//     letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 8px;
//     display: flex; align-items: center; gap: 5px;
//   }
//   .result-line {
//     height: 6px; border-radius: 3px; background: rgba(123,196,190,0.3);
//     margin-bottom: 5px;
//     animation: shimmer 2.5s linear infinite;
//     background: linear-gradient(90deg, rgba(123,196,190,0.2) 25%, rgba(123,196,190,0.5) 50%, rgba(123,196,190,0.2) 75%);
//     background-size: 200% auto;
//   }

//   /* MANUAL MODE */
//   .manual-grid {
//     display: grid; grid-template-columns: repeat(3, 1fr);
//     gap: 1.5rem; margin-top: 2.5rem;
//   }
//   .step-card {
//     background: white; border-radius: 16px;
//     border: 1px solid var(--border);
//     padding: 24px;
//     transition: all 0.25s cubic-bezier(.22,1,.36,1);
//     position: relative; overflow: hidden;
//   }
//   .step-card::before {
//     content: '';
//     position: absolute; inset: 0;
//     background: linear-gradient(135deg, rgba(123,196,190,0.06), transparent);
//     opacity: 0; transition: opacity 0.25s;
//   }
//   .step-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(29,79,75,0.1); border-color: var(--teal-light); }
//   .step-card:hover::before { opacity: 1; }
//   .step-number {
//     font-family: 'DM Serif Display', serif;
//     font-size: 2.5rem; color: rgba(123,196,190,0.3);
//     line-height: 1; margin-bottom: 12px;
//   }
//   .step-title { font-size: 0.95rem; font-weight: 500; color: var(--text); margin-bottom: 6px; }
//   .step-desc { font-size: 0.82rem; color: var(--text-muted); line-height: 1.6; }

//   /* TEMPLATES */
//   .templates-section { background: var(--ivory); padding: 100px 0; }
//   .templates-inner { max-width: 1200px; margin: 0 auto; padding: 0 2rem; }
//   .template-grid {
//     display: grid; grid-template-columns: repeat(4, 1fr);
//     gap: 1.5rem; margin-top: 3rem;
//   }
//   .template-card {
//     background: white; border-radius: 16px; overflow: hidden;
//     border: 1px solid var(--border);
//     transition: all 0.3s cubic-bezier(.22,1,.36,1);
//     cursor: pointer;
//   }
//   .template-card:hover {
//     transform: translateY(-6px) scale(1.01);
//     box-shadow: 0 20px 48px rgba(29,79,75,0.14);
//     border-color: var(--teal);
//   }
//   .template-preview {
//     height: 220px; position: relative;
//     overflow: hidden; display: flex; flex-direction: column;
//   }
//   .template-preview-header {
//     padding: 16px;
//     display: flex; flex-direction: column; gap: 5px;
//   }
//   .template-preview-name-line {
//     height: 10px; width: 60%; border-radius: 5px; background: white;
//   }
//   .template-preview-role-line {
//     height: 7px; width: 40%; border-radius: 4px; background: rgba(255,255,255,0.6);
//   }
//   .template-preview-body {
//     flex: 1; padding: 12px 16px; background: white;
//     display: flex; flex-direction: column; gap: 6px;
//   }
//   .template-line {
//     height: 5px; border-radius: 3px; background: var(--ivory);
//   }
//   .template-info {
//     padding: 14px 16px;
//     border-top: 1px solid var(--border);
//     display: flex; justify-content: space-between; align-items: center;
//   }
//   .template-name { font-size: 0.85rem; font-weight: 500; color: var(--text); }
//   .template-tag {
//     font-size: 0.68rem; font-weight: 500; padding: 3px 8px;
//     border-radius: 5px; background: rgba(123,196,190,0.12);
//     color: var(--teal-dark); letter-spacing: 0.03em;
//   }

//   /* ATS SECTION */
//   .ats-section {
//     background: linear-gradient(135deg, var(--teal-deep), var(--teal-dark));
//     padding: 100px 2rem; color: white; overflow: hidden; position: relative;
//   }
//   .ats-section-inner {
//     max-width: 1100px; margin: 0 auto;
//     display: grid; grid-template-columns: 1fr 1fr;
//     gap: 6rem; align-items: center;
//   }
//   .ats-section .section-tag { background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.2); color: rgba(255,255,255,0.85); }
//   .ats-section .section-headline { color: white; }
//   .ats-section .section-sub { color: rgba(255,255,255,0.7); }

//   .ats-meter-card {
//     background: rgba(255,255,255,0.08); backdrop-filter: blur(12px);
//     border: 1px solid rgba(255,255,255,0.15);
//     border-radius: 20px; padding: 28px;
//   }
//   .ats-criteria { display: flex; flex-direction: column; gap: 14px; }
//   .ats-crit-row { display: flex; flex-direction: column; gap: 5px; }
//   .ats-crit-top { display: flex; justify-content: space-between; align-items: center; }
//   .ats-crit-label { font-size: 0.82rem; color: rgba(255,255,255,0.8); }
//   .ats-crit-pct { font-size: 0.8rem; font-weight: 500; color: var(--amber-light); }
//   .ats-crit-track { height: 6px; background: rgba(255,255,255,0.12); border-radius: 3px; overflow: hidden; }
//   .ats-crit-fill {
//     height: 100%; border-radius: 3px;
//     background: linear-gradient(90deg, rgba(255,255,255,0.5), var(--amber-light));
//     transition: width 1.5s cubic-bezier(.22,1,.36,1);
//   }
//   .ats-bg-circle {
//     position: absolute; border-radius: 50%; opacity: 0.06;
//     background: white;
//   }

//   /* BEFORE AFTER */
//   .before-after-section {
//     padding: 100px 2rem; background: white;
//   }
//   .before-after-inner { max-width: 1100px; margin: 0 auto; }
//   .before-after-grid {
//     display: grid; grid-template-columns: 1fr auto 1fr;
//     gap: 2rem; align-items: start; margin-top: 3.5rem;
//   }
//   .ba-card {
//     background: var(--cream); border-radius: 16px;
//     border: 1px solid var(--border);
//     padding: 24px; position: relative; overflow: hidden;
//   }
//   .ba-card.after {
//     background: white;
//     border-color: rgba(123,196,190,0.4);
//     box-shadow: 0 8px 32px rgba(29,79,75,0.08);
//   }
//   .ba-label {
//     font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
//     text-transform: uppercase; margin-bottom: 16px;
//     display: flex; align-items: center; gap: 6px;
//   }
//   .ba-label.bad { color: #dc2626; }
//   .ba-label.good { color: var(--teal-dark); }
//   .ba-content { display: flex; flex-direction: column; gap: 10px; }
//   .ba-block {
//     border-radius: 8px; padding: 10px 12px;
//     font-size: 0.8rem; line-height: 1.5;
//   }
//   .ba-block.messy {
//     background: rgba(220,38,38,0.05); border: 1px solid rgba(220,38,38,0.15);
//     color: #7f1d1d;
//   }
//   .ba-block.clean {
//     background: rgba(123,196,190,0.08); border: 1px solid rgba(123,196,190,0.25);
//     color: var(--text-mid);
//   }
//   .ba-block-title { font-weight: 600; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 3px; }
//   .ba-arrow {
//     display: flex; align-items: center; justify-content: center;
//     padding: 20px 0; margin-top: 60px;
//   }
//   .ba-arrow-icon {
//     width: 48px; height: 48px; border-radius: 50%;
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     display: flex; align-items: center; justify-content: center;
//     color: white; font-size: 1.2rem; font-weight: 600;
//     box-shadow: 0 4px 16px rgba(75,158,152,0.35);
//   }

//   /* WORKFLOW */
//   .workflow-section { padding: 100px 2rem; background: var(--ivory); }
//   .workflow-inner { max-width: 1000px; margin: 0 auto; }
//   .workflow-steps {
//     display: flex; flex-direction: column; gap: 0; margin-top: 4rem;
//     position: relative;
//   }
//   .workflow-steps::before {
//     content: ''; position: absolute; left: 28px; top: 28px; bottom: 28px;
//     width: 2px; background: linear-gradient(to bottom, var(--teal-light), transparent);
//   }
//   .workflow-step {
//     display: flex; gap: 2rem; align-items: flex-start;
//     padding: 0 0 3rem 0;
//   }
//   .workflow-step-num {
//     width: 56px; height: 56px; border-radius: 16px; flex-shrink: 0;
//     background: white; border: 1px solid var(--border-mid);
//     display: flex; align-items: center; justify-content: center;
//     font-family: 'DM Serif Display', serif; font-size: 1.3rem; color: var(--teal-dark);
//     box-shadow: 0 2px 8px rgba(29,79,75,0.08); z-index: 1;
//   }
//   .workflow-step-content { flex: 1; padding-top: 10px; }
//   .workflow-step-title { font-size: 1.05rem; font-weight: 500; color: var(--text); margin-bottom: 6px; }
//   .workflow-step-desc { font-size: 0.88rem; color: var(--text-muted); line-height: 1.6; max-width: 520px; }

//   /* TESTIMONIALS */
//   .testimonials-section { padding: 100px 2rem; background: white; }
//   .testimonials-inner { max-width: 1100px; margin: 0 auto; }
//   .testimonials-grid {
//     display: grid; grid-template-columns: repeat(3, 1fr);
//     gap: 1.5rem; margin-top: 3rem;
//   }
//   .testimonial-card {
//     background: var(--cream); border-radius: 16px;
//     border: 1px solid var(--border);
//     padding: 24px;
//     transition: all 0.25s cubic-bezier(.22,1,.36,1);
//   }
//   .testimonial-card:hover {
//     transform: translateY(-3px); box-shadow: 0 10px 28px rgba(29,79,75,0.08);
//     border-color: var(--teal-light);
//   }
//   .testimonial-stars { color: var(--amber); font-size: 0.85rem; margin-bottom: 12px; letter-spacing: 2px; }
//   .testimonial-quote {
//     font-size: 0.9rem; color: var(--text-mid); line-height: 1.7;
//     margin-bottom: 16px; font-style: italic;
//   }
//   .testimonial-author { display: flex; align-items: center; gap: 10px; }
//   .testimonial-avatar {
//     width: 38px; height: 38px; border-radius: 50%;
//     display: flex; align-items: center; justify-content: center;
//     font-family: 'DM Serif Display', serif; font-size: 0.9rem;
//     font-weight: normal; flex-shrink: 0;
//   }
//   .testimonial-name { font-size: 0.85rem; font-weight: 500; color: var(--text); }
//   .testimonial-role { font-size: 0.75rem; color: var(--text-muted); }

//   /* PRICING */
//   .pricing-section { padding: 100px 2rem; background: var(--ivory); }
//   .pricing-inner { max-width: 900px; margin: 0 auto; text-align: center; }
//   .pricing-grid {
//     display: grid; grid-template-columns: repeat(3, 1fr);
//     gap: 1.5rem; margin-top: 3rem; text-align: left;
//   }
//   .pricing-card {
//     background: white; border-radius: 20px;
//     border: 1px solid var(--border);
//     padding: 28px;
//     transition: all 0.25s cubic-bezier(.22,1,.36,1);
//     position: relative;
//   }
//   .pricing-card.popular {
//     border-color: var(--teal);
//     box-shadow: 0 8px 32px rgba(123,196,190,0.2);
//   }
//   .pricing-card:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(29,79,75,0.1); }
//   .popular-badge {
//     position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     color: white; font-size: 0.7rem; font-weight: 600;
//     padding: 4px 14px; border-radius: 100px;
//     letter-spacing: 0.05em; text-transform: uppercase;
//   }
//   .pricing-plan { font-size: 0.8rem; font-weight: 600; color: var(--teal-dark);
//     letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 8px; }
//   .pricing-price {
//     font-family: 'DM Serif Display', serif;
//     font-size: 2.4rem; color: var(--text); line-height: 1;
//     margin-bottom: 4px; display: flex; align-items: baseline; gap: 2px;
//   }
//   .pricing-price-currency { font-size: 1.2rem; }
//   .pricing-price-period { font-size: 0.85rem; color: var(--text-muted); font-family: 'DM Sans', sans-serif; }
//   .pricing-desc { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 20px; line-height: 1.5; }
//   .pricing-features { display: flex; flex-direction: column; gap: 9px; margin-bottom: 24px; }
//   .pricing-feature {
//     display: flex; align-items: center; gap: 8px;
//     font-size: 0.82rem; color: var(--text-mid);
//   }
//   .pricing-check {
//     width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0;
//     background: rgba(123,196,190,0.15);
//     display: flex; align-items: center; justify-content: center;
//     font-size: 0.6rem; color: var(--teal-dark);
//   }
//   .btn-plan {
//     width: 100%; padding: 11px; border-radius: 9px;
//     font-size: 0.88rem; font-weight: 500; cursor: pointer;
//     font-family: 'DM Sans', sans-serif; transition: all 0.2s;
//     border: 1px solid var(--border-mid); background: none; color: var(--text-mid);
//   }
//   .btn-plan.primary {
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     color: white; border: none; box-shadow: 0 3px 10px rgba(75,158,152,0.3);
//   }
//   .btn-plan:hover { transform: translateY(-1px); }
//   .btn-plan.primary:hover { box-shadow: 0 6px 18px rgba(75,158,152,0.4); }

//   /* FAQ */
//   .faq-section { padding: 100px 2rem; background: white; }
//   .faq-inner { max-width: 720px; margin: 0 auto; }
//   .faq-list { margin-top: 3rem; display: flex; flex-direction: column; gap: 0; }
//   .faq-item {
//     border-bottom: 1px solid var(--border);
//     overflow: hidden;
//   }
//   .faq-question {
//     width: 100%; background: none; border: none; padding: 20px 0;
//     display: flex; justify-content: space-between; align-items: center;
//     font-size: 0.95rem; font-weight: 500; color: var(--text);
//     cursor: pointer; font-family: 'DM Sans', sans-serif; text-align: left;
//     gap: 1rem;
//   }
//   .faq-icon {
//     width: 24px; height: 24px; border-radius: 6px;
//     background: var(--ivory); border: 1px solid var(--border-mid);
//     display: flex; align-items: center; justify-content: center;
//     font-size: 0.8rem; color: var(--teal-dark); flex-shrink: 0;
//     transition: all 0.2s;
//   }
//   .faq-icon.open { background: var(--teal-dark); color: white; transform: rotate(45deg); }
//   .faq-answer {
//     font-size: 0.88rem; color: var(--text-muted); line-height: 1.7;
//     padding: 0 0 16px 0; max-height: 0; overflow: hidden;
//     transition: max-height 0.3s ease, padding 0.3s ease;
//   }
//   .faq-answer.open { max-height: 200px; padding-bottom: 16px; }

//   /* FINAL CTA */
//   .final-cta {
//     background: linear-gradient(135deg, var(--teal-deep) 0%, var(--teal-dark) 50%, var(--teal) 100%);
//     padding: 120px 2rem; text-align: center; position: relative; overflow: hidden;
//   }
//   .final-cta-inner { max-width: 680px; margin: 0 auto; position: relative; z-index: 2; }
//   .final-cta-headline {
//     font-family: 'DM Serif Display', serif;
//     font-size: clamp(2.4rem, 5vw, 3.8rem);
//     color: white; line-height: 1.15; margin-bottom: 1.25rem;
//   }
//   .final-cta-sub { font-size: 1.1rem; color: rgba(255,255,255,0.75); margin-bottom: 2.5rem; line-height: 1.7; font-weight: 300; }
//   .final-cta-btns { display: flex; align-items: center; justify-content: center; gap: 14px; flex-wrap: wrap; }
//   .btn-cta-white {
//     background: white; color: var(--teal-deep);
//     border: none; padding: 15px 32px; border-radius: 11px;
//     font-size: 1rem; font-weight: 500; cursor: pointer;
//     font-family: 'DM Sans', sans-serif;
//     transition: all 0.25s cubic-bezier(.22,1,.36,1);
//     box-shadow: 0 4px 20px rgba(0,0,0,0.15);
//   }
//   .btn-cta-white:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.2); }
//   .btn-cta-outline {
//     background: rgba(255,255,255,0.1); color: white;
//     border: 1px solid rgba(255,255,255,0.3); padding: 14px 28px; border-radius: 11px;
//     font-size: 1rem; cursor: pointer; font-family: 'DM Sans', sans-serif;
//     transition: all 0.2s;
//   }
//   .btn-cta-outline:hover { background: rgba(255,255,255,0.18); }
//   .final-cta-note { font-size: 0.8rem; color: rgba(255,255,255,0.45); margin-top: 1.5rem; }
//   .cta-bg-circle { position: absolute; border-radius: 50%; opacity: 0.07; background: white; }

//   /* FOOTER */
//   .footer { background: var(--text); padding: 60px 2rem 32px; color: rgba(255,255,255,0.7); }
//   .footer-inner { max-width: 1100px; margin: 0 auto; }
//   .footer-grid {
//     display: grid; grid-template-columns: 2fr 1fr 1fr 1fr;
//     gap: 3rem; margin-bottom: 3rem;
//   }
//   .footer-brand { }
//   .footer-logo {
//     display: flex; align-items: center; gap: 10px;
//     font-family: 'DM Serif Display', serif; font-size: 1.2rem;
//     color: white; margin-bottom: 12px;
//   }
//   .footer-logo-mark {
//     width: 30px; height: 30px; border-radius: 8px;
//     background: linear-gradient(135deg, var(--teal), var(--teal-dark));
//     display: flex; align-items: center; justify-content: center;
//     font-size: 0.75rem; color: white; font-weight: 600;
//   }
//   .footer-desc { font-size: 0.82rem; line-height: 1.7; max-width: 240px; }
//   .footer-col-title { font-size: 0.75rem; font-weight: 600; color: white; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 14px; }
//   .footer-links { display: flex; flex-direction: column; gap: 9px; }
//   .footer-links a { font-size: 0.82rem; color: rgba(255,255,255,0.55); text-decoration: none; transition: color 0.2s; }
//   .footer-links a:hover { color: var(--teal-light); }
//   .footer-bottom {
//     border-top: 1px solid rgba(255,255,255,0.08); padding-top: 24px;
//     display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;
//   }
//   .footer-copy { font-size: 0.78rem; color: rgba(255,255,255,0.35); }
//   .footer-badge {
//     font-size: 0.72rem; color: rgba(255,255,255,0.4);
//     display: flex; align-items: center; gap: 6px;
//   }
//   .footer-badge-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--teal); animation: pulse 2s ease-in-out infinite; }

//   /* PIXEL DECORATIONS */
//   .pixel-deco {
//     position: absolute; pointer-events: none;
//   }
//   .px-sq {
//     display: inline-block; width: 4px; height: 4px; background: var(--teal-light);
//   }

//   /* RESPONSIVE */
//   @media (max-width: 1024px) {
//     .hero { grid-template-columns: 1fr; gap: 3rem; padding-top: 100px; min-height: auto; }
//     .hero-visual { height: 420px; }
//     .ai-section-grid { grid-template-columns: 1fr; }
//     .template-grid { grid-template-columns: repeat(2, 1fr); }
//     .ats-section-inner { grid-template-columns: 1fr; gap: 3rem; }
//     .testimonials-grid { grid-template-columns: repeat(2, 1fr); }
//     .pricing-grid { grid-template-columns: 1fr; max-width: 380px; margin-left: auto; margin-right: auto; }
//     .footer-grid { grid-template-columns: 1fr 1fr; }
//     .manual-grid { grid-template-columns: repeat(2, 1fr); }
//   }
//   @media (max-width: 768px) {
//     .nav-links { display: none; }
//     .hero-headline { font-size: 2.4rem; }
//     .hero-visual { height: 360px; }
//     .before-after-grid { grid-template-columns: 1fr; }
//     .ba-arrow { display: none; }
//     .testimonials-grid { grid-template-columns: 1fr; }
//     .template-grid { grid-template-columns: repeat(2, 1fr); }
//     .manual-grid { grid-template-columns: 1fr; }
//     .footer-grid { grid-template-columns: 1fr; gap: 2rem; }
//     .stats-inner { gap: 1.5rem; }
//     .stat-divider { display: none; }
//     .company-logos { border: none; padding: 0; }
//   }
// `;

// const PIXELS = [
//   { top: "15%", left: "8%",  delay: "0s",   dur: "3.5s", size: 3, color: COLORS.teal },
//   { top: "25%", left: "92%", delay: "0.5s", dur: "4s",   size: 4, color: COLORS.amber },
//   { top: "60%", left: "5%",  delay: "1s",   dur: "3s",   size: 3, color: COLORS.tealLight },
//   { top: "70%", left: "95%", delay: "0.3s", dur: "5s",   size: 4, color: COLORS.teal },
//   { top: "40%", left: "3%",  delay: "1.5s", dur: "4.5s", size: 3, color: COLORS.amberLight },
//   { top: "80%", left: "88%", delay: "0.8s", dur: "3.8s", size: 3, color: COLORS.tealDark },
// ];

// const TEMPLATES = [
//   { name: "Meridian", tag: "Modern",    hue: COLORS.teal,    lines: [0.9,0.6,0.85,0.5,0.75,0.4,0.8] },
//   { name: "Ashford", tag: "Executive",  hue: "#4A5568",      lines: [0.85,0.55,0.8,0.65,0.7,0.5,0.75] },
//   { name: "Luma",    tag: "Minimal",    hue: COLORS.tealDark, lines: [0.9,0.5,0.7,0.6,0.8,0.45,0.65] },
//   { name: "Pulse",   tag: "Developer",  hue: "#1E3A8A",      lines: [0.8,0.7,0.9,0.55,0.75,0.6,0.85] },
// ];

// const TESTIMONIALS = [
//   {
//     stars: 5, avatar: "AK", bg: "rgba(123,196,190,0.18)", text: "#2D7A74",
//     quote: "Uploaded my experience as a prompt and had a polished, ATS-ready resume in under two minutes. Got three interviews that week.",
//     name: "Arjun K.", role: "Software Engineer, Fresher"
//   },
//   {
//     stars: 5, avatar: "SC", bg: "rgba(246,178,51,0.15)", text: "#8A5A00",
//     quote: "The manual mode gives me total control while the AI suggestions keep everything sharp. Best resume tool I've ever used.",
//     name: "Sophia C.", role: "Senior Product Manager"
//   },
//   {
//     stars: 5, avatar: "MR", bg: "rgba(123,196,190,0.18)", text: "#2D7A74",
//     quote: "Career switcher from teaching to UX — the AI understood my transferable skills immediately. Landed my first design role.",
//     name: "Marcus R.", role: "UX Designer, Career Switcher"
//   },
//   {
//     stars: 5, avatar: "PD", bg: "rgba(246,178,51,0.15)", text: "#8A5A00",
//     quote: "I was skeptical about AI resumes. Then I saw the before/after. The formatting and keyword optimization is genuinely impressive.",
//     name: "Priya D.", role: "Data Analyst"
//   },
//   {
//     stars: 5, avatar: "TN", bg: "rgba(123,196,190,0.18)", text: "#2D7A74",
//     quote: "Clean templates that don't scream 'template'. My recruiter asked which designer made my resume — it was the AI.",
//     name: "Theo N.", role: "Frontend Developer"
//   },
//   {
//     stars: 5, avatar: "RL", bg: "rgba(246,178,51,0.15)", text: "#8A5A00",
//     quote: "Exported a beautiful PDF and a Word version in one click. Applied to 20 companies that day. The speed is unreal.",
//     name: "Rita L.", role: "Marketing Graduate"
//   },
// ];

// const FAQS = [
//   { q: "What makes this different from other resume builders?", a: "We combine AI-powered generation with a fully manual mode, giving you the best of both worlds. Our ATS scoring engine analyzes your resume against real recruiter patterns, not generic templates." },
//   { q: "How does the AI resume mode work?", a: "You describe your background in natural language — experience, skills, goals. Our AI structures, formats, and optimizes this into a professionally written, ATS-friendly resume in under 60 seconds." },
//   { q: "Is my resume actually ATS-friendly?", a: "Yes. Every resume is analyzed against 40+ ATS criteria including keyword density, formatting standards, section hierarchy, and readability scores. You see your score and can improve it live." },
//   { q: "Can I export my resume in multiple formats?", a: "Absolutely. Export as PDF (presentation-perfect), DOCX (editable), and plain text (ATS parsing). All formats are optimized for their intended use." },
//   { q: "Is there a free plan?", a: "Yes. The free plan lets you create and export 2 resumes with core templates. Pro unlocks unlimited resumes, all templates, AI mode, and advanced ATS analysis." },
// ];

// const WORKFLOW_STEPS = [
//   { num: "01", title: "Choose your mode", desc: "Pick AI-assisted generation for speed, or manual mode for full control. Switch between them anytime." },
//   { num: "02", title: "Enter your information", desc: "Describe yourself in natural language (AI mode) or fill structured sections step-by-step (manual mode)." },
//   { num: "03", title: "AI formats and optimizes", desc: "Our system structures content, selects the right sections, applies professional formatting, and runs ATS analysis." },
//   { num: "04", title: "Review and refine", desc: "See your live ATS score. Edit any section inline. Swap templates instantly with one click." },
//   { num: "05", title: "Export and apply", desc: "Download PDF, DOCX, or plain text. Your resume is ready for job boards, email, and direct applications." },
// ];

// function useReveal() {
//   useEffect(() => {
//     const els = document.querySelectorAll(".reveal, .reveal-left, .reveal-right");
//     const obs = new IntersectionObserver(
//       entries => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("visible"); } }),
//       { threshold: 0.12 }
//     );
//     els.forEach(el => obs.observe(el));
//     return () => obs.disconnect();
//   }, []);
// }

// function useNav() {
//   const [scrolled, setScrolled] = useState(false);
//   useEffect(() => {
//     const fn = () => setScrolled(window.scrollY > 20);
//     window.addEventListener("scroll", fn);
//     return () => window.removeEventListener("scroll", fn);
//   }, []);
//   return scrolled;
// }

// function FAQItem({ q, a }) {
//   const [open, setOpen] = useState(false);
//   return (
//     <div className="faq-item">
//       <button className="faq-question" onClick={() => setOpen(!open)}>
//         {q}
//         <span className={`faq-icon${open ? " open" : ""}`}>+</span>
//       </button>
//       <div className={`faq-answer${open ? " open" : ""}`}>{a}</div>
//     </div>
//   );
// }

// function ATSCriteria() {
//   const [animated, setAnimated] = useState(false);
//   const ref = useRef();
//   useEffect(() => {
//     const obs = new IntersectionObserver(
//       ([e]) => { if (e.isIntersecting) setAnimated(true); },
//       { threshold: 0.3 }
//     );
//     if (ref.current) obs.observe(ref.current);
//     return () => obs.disconnect();
//   }, []);
//   const criteria = [
//     { label: "Keyword Density", pct: 94 },
//     { label: "Formatting Standards", pct: 98 },
//     { label: "Section Structure", pct: 91 },
//     { label: "Readability Score", pct: 97 },
//     { label: "Length Optimization", pct: 89 },
//   ];
//   return (
//     <div className="ats-meter-card" ref={ref}>
//       <div style={{ marginBottom: 20 }}>
//         <div style={{ fontSize: "0.7rem", color: "rgba(255,255,255,0.6)", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6 }}>ATS Analysis Score</div>
//         <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: "3rem", color: "white", lineHeight: 1, display: "flex", alignItems: "baseline", gap: 4 }}>
//           94 <span style={{ fontSize: "1rem", fontFamily: "'DM Sans', sans-serif", color: "rgba(255,255,255,0.55)" }}>/100</span>
//         </div>
//       </div>
//       <div className="ats-criteria">
//         {criteria.map((c, i) => (
//           <div className="ats-crit-row" key={i}>
//             <div className="ats-crit-top">
//               <span className="ats-crit-label">{c.label}</span>
//               <span className="ats-crit-pct">{c.pct}%</span>
//             </div>
//             <div className="ats-crit-track">
//               <div className="ats-crit-fill" style={{ width: animated ? `${c.pct}%` : "0%", transitionDelay: `${i * 0.15}s` }} />
//             </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }

// export default function LandingPage() {
//   const scrolled = useNav();
//   useReveal();

//   return (
//     <>
//       <style>{css}</style>

//       {/* NAV */}
//       <nav className={`nav${scrolled ? " scrolled" : ""}`}>
//         <a href="#" className="nav-logo">
//           <div className="nav-logo-mark">R</div>
//           Prompt Resume
//         </a>
//         <ul className="nav-links">
//           <li><a href="#features">Features</a></li>
//           <li><a href="#templates">Templates</a></li>
//           <li><a href="#how">How it works</a></li>
//           <li><a href="#pricing">Pricing</a></li>
//         </ul>
//         <div className="nav-cta">
//           <button className="btn-ghost">Log in</button>
//           <button className="btn-primary">Start free →</button>
//         </div>
//       </nav>

//       {/* HERO BG */}
//       <div className="hero-bg">
//         <div className="hero-bg-blob1" />
//         <div className="hero-bg-blob2" />
//         <div className="hero-bg-grid" />
//         {PIXELS.map((p, i) => (
//           <div key={i} className="pixel-particle" style={{
//             top: p.top, left: p.left,
//             animationDelay: p.delay, animationDuration: p.dur,
//             width: p.size, height: p.size, background: p.color,
//           }} />
//         ))}
//       </div>

//       {/* HERO */}
//       <section style={{ position: "relative" }}>
//         <div className="hero">
//           <div>
//             <div className="hero-badge anim-fadeUp delay-1">
//               <div className="hero-badge-dot" />
//               AI-Powered · ATS-Optimized · Interview-Ready
//             </div>
//             <h1 className="hero-headline anim-fadeUp delay-2">
//               Build resumes that<br />
//               <em>actually get you</em><br />
//               hired
//             </h1>
//             <p className="hero-sub anim-fadeUp delay-3">
//               Describe yourself in plain English — our AI builds a polished, ATS-friendly resume in under 60 seconds. Or take full manual control. Your resume, your way.
//             </p>
//             <div className="hero-modes anim-fadeUp delay-4">
//               <div className="hero-mode-chip">
//                 <div className="hero-mode-chip-dot" />
//                 AI Prompt Mode — instant generation
//               </div>
//               <div className="hero-mode-chip">
//                 <div className="hero-mode-chip-dot amber" />
//                 Manual Mode — full editing control
//               </div>
//             </div>
//             <div className="hero-ctas anim-fadeUp delay-5">
//               <button className="btn-hero">
//                 Build my resume
//                 <span style={{ fontSize: "1.1rem" }}>→</span>
//               </button>
//               <button className="btn-hero-sec">
//                 <span style={{ fontSize: "1rem" }}>▶</span>
//                 Watch demo
//               </button>
//             </div>
//             <div className="anim-fadeUp delay-6" style={{ marginTop: "1.5rem", fontSize: "0.78rem", color: COLORS.textMuted, display: "flex", alignItems: "center", gap: "1rem" }}>
//               <span>✓ Free forever plan</span>
//               <span>✓ No credit card needed</span>
//               <span>✓ Export in 60 seconds</span>
//             </div>
//           </div>

//           {/* HERO VISUAL */}
//           <div className="hero-visual anim-fadeIn delay-4">
//             {/* Main resume card */}
//             <div className="resume-card resume-main">
//               <div className="resume-header">
//                 <div className="resume-name">Alexandra Chen</div>
//                 <div className="resume-role">Senior Product Designer · San Francisco, CA</div>
//               </div>
//               <div className="resume-body">
//                 <div className="resume-section-label">Experience</div>
//                 <div className="resume-line resume-line-full active" style={{ marginBottom: 6 }} />
//                 <div className="resume-line resume-line-med active" style={{ marginBottom: 6 }} />
//                 <div className="resume-line resume-line-short" style={{ marginBottom: 12 }} />
//                 <div className="resume-section-label">Skills</div>
//                 <div style={{ display: "flex", gap: 5, flexWrap: "wrap", marginBottom: 12 }}>
//                   {["Figma", "React", "UX Research", "Prototyping"].map(s => (
//                     <span key={s} style={{ background: "rgba(123,196,190,0.12)", border: "1px solid rgba(123,196,190,0.25)", borderRadius: 5, padding: "2px 7px", fontSize: "0.62rem", color: COLORS.tealDark, fontWeight: 500 }}>{s}</span>
//                   ))}
//                 </div>
//                 <div className="resume-section-label">Education</div>
//                 <div className="resume-line resume-line-full" />
//                 <div className="resume-line resume-line-med" style={{ marginTop: 4 }} />
//               </div>
//             </div>

//             {/* ATS Badge */}
//             <div className="ats-badge">
//               <div className="ats-label">ATS Score</div>
//               <div className="ats-score">94<span>/100</span></div>
//               <div className="ats-bar-track"><div className="ats-bar-fill" /></div>
//               <div style={{ fontSize: "0.6rem", color: COLORS.textMuted, marginTop: 5 }}>↑ Excellent — recruiter ready</div>
//             </div>

//             {/* Recruiter badge */}
//             <div className="recruiter-badge">
//               <div className="recruiter-badge-icon">👁</div>
//               Recruiter<br />Reviewed ✓
//             </div>

//             {/* AI prompt card */}
//             <div className="ai-prompt-card">
//               <div className="ai-prompt-label">
//                 <span style={{ width: 6, height: 6, borderRadius: 1, background: COLORS.teal, display: "inline-block" }} />
//                 AI Prompt
//               </div>
//               <div className="ai-prompt-text">
//                 "5 years product design at startups, led design systems, shipped 3 mobile apps, Stanford CS grad..."
//                 <span className="cursor-blink" />
//               </div>
//               <button className="ai-prompt-btn">
//                 ✦ Generate resume →
//               </button>
//             </div>

//             {/* Export chip */}
//             <div className="export-chip">
//               <div className="export-chip-dot" />
//               PDF exported · 48 KB
//             </div>
//           </div>
//         </div>
//       </section>

//       {/* STATS STRIP */}
//       <div className="stats-strip">
//         <div className="stats-inner">
//           {[
//             { num: "240", suffix: "+", label: "Resumes created" },
//             { num: "94", suffix: "%", label: "ATS pass rate" },
//             { num: "3x", suffix: "", label: "More interviews" },
//             { num: "60", suffix: "s", label: "AI generation time" },
//           ].map((s, i) => (
//             <div key={i} className="stat-item reveal" style={{ transitionDelay: `${i * 0.1}s` }}>
//               <div className="stat-number">
//                 {s.num}<sub>{s.suffix}</sub>
//               </div>
//               <div className="stat-label">{s.label}</div>
//             </div>
//           ))}
//           <div className="stat-divider" />
//           <div className="company-logos reveal delay-5">
//             <span className="company-logo">Google</span>
//             <span className="company-logo">Meta</span>
//             <span className="company-logo">Stripe</span>
//             <span className="company-logo">Figma</span>
//             <span className="company-logo">Notion</span>
//           </div>
//         </div>
//       </div>

//       {/* AI MODE SECTION */}
//       <section className="section" id="features">
//         <div className="ai-section-grid">
//           <div>
//             <div className="section-tag reveal">✦ AI Resume Mode</div>
//             <h2 className="section-headline reveal delay-1">
//               Describe yourself.<br />
//               We write the rest.
//             </h2>
//             <p className="section-sub reveal delay-2">
//               No more staring at a blank page. Write a natural prompt about your background, goals, and experience — our AI structures it into a perfectly formatted, keyword-optimized resume.
//             </p>
//             <div className="ai-feature-list">
//               {[
//                 { icon: "✦", title: "Natural language input", desc: "Write like you're telling a friend about your career. Our AI understands context and intent." },
//                 { icon: "◈", title: "Smart keyword injection", desc: "Automatically identifies and inserts industry-relevant ATS keywords from your target role." },
//                 { icon: "⬡", title: "Instant formatting", desc: "Structures experience, education, and skills into clean, recruiter-approved sections." },
//                 { icon: "◎", title: "One-click regeneration", desc: "Don't like a section? Regenerate it with different tone, length, or emphasis." },
//               ].map((f, i) => (
//                 <div className={`ai-feature-item reveal delay-${i + 3}`} key={i}>
//                   <div className="ai-feature-icon">{f.icon}</div>
//                   <div>
//                     <div className="ai-feature-title">{f.title}</div>
//                     <div className="ai-feature-desc">{f.desc}</div>
//                   </div>
//                 </div>
//               ))}
//             </div>
//           </div>
//           <div className="reveal-right delay-2">
//             <div className="prompt-demo">
//               <div className="prompt-demo-header">
//                 <div className="demo-dot r" /><div className="demo-dot y" /><div className="demo-dot g" />
//                 <span className="demo-title">AI Resume Generator</span>
//               </div>
//               <div className="prompt-body">
//                 <div className="prompt-label">Your prompt</div>
//                 <div className="prompt-input">
//                   "Software engineer, 4 years at B2B SaaS startups. Built auth systems and REST APIs at scale. Led a team of 3. Used React, Node.js, PostgreSQL. Looking for senior roles at product-focused companies."
//                   <span className="cursor-blink" />
//                 </div>
//                 <button className="generate-btn">
//                   <span>✦</span> Generate my resume
//                 </button>
//                 <div className="result-preview">
//                   <div className="result-preview-title">
//                     <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#22c55e", display: "inline-block" }} />
//                     Resume generating...
//                   </div>
//                   {[0.9, 0.7, 0.85, 0.55, 0.75].map((w, i) => (
//                     <div key={i} className="result-line" style={{ width: `${w * 100}%`, animationDelay: `${i * 0.2}s` }} />
//                   ))}
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </section>

//       {/* MANUAL MODE */}
//       <div style={{ background: COLORS.ivory, padding: "100px 2rem" }}>
//         <div style={{ maxWidth: 1100, margin: "0 auto" }}>
//           <div className="text-centered">
//             <div className="section-tag section-tag-amber reveal" style={{ display: "inline-flex" }}>◈ Manual Mode</div>
//             <h2 className="section-headline reveal delay-1">Total control,<br />zero friction</h2>
//             <p className="section-sub centered reveal delay-2">
//               Prefer to write every word yourself? Our manual mode gives you a structured editor with smart suggestions, real-time ATS scoring, and instant formatting.
//             </p>
//           </div>
//           <div className="manual-grid">
//             {[
//               { n: "01", t: "Personal Details",    d: "Name, contact, location, LinkedIn, portfolio — clean auto-formatting." },
//               { n: "02", t: "Work Experience",     d: "Add roles with bullet point editor. AI suggests action verbs and impact metrics." },
//               { n: "03", t: "Skills & Tools",      d: "Tag-based skill input with visual grouping by category and proficiency." },
//               { n: "04", t: "Education",           d: "Degrees, certifications, GPA display options. Academic formatting built-in." },
//               { n: "05", t: "Projects & Portfolio",d: "Link-enabled project sections with tech stack tags and outcome bullets." },
//               { n: "06", t: "Export & Download",   d: "PDF, DOCX, or plain text with one click. Print-perfect layout guaranteed." },
//             ].map((s, i) => (
//               <div className={`step-card reveal delay-${i + 1}`} key={i}>
//                 <div className="step-number">{s.n}</div>
//                 <div className="step-title">{s.t}</div>
//                 <div className="step-desc">{s.d}</div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* TEMPLATES */}
//       <div className="templates-section" id="templates">
//         <div className="templates-inner">
//           <div className="text-centered">
//             <div className="section-tag reveal" style={{ display: "inline-flex" }}>◧ Resume Templates</div>
//             <h2 className="section-headline reveal delay-1">Professional templates<br />that get noticed</h2>
//             <p className="section-sub centered reveal delay-2">
//               Every template is ATS-safe, recruiter-approved, and designed by professional resume writers and product designers.
//             </p>
//           </div>
//           <div className="template-grid">
//             {TEMPLATES.map((t, i) => (
//               <div className={`template-card reveal delay-${i + 2}`} key={i}>
//                 <div className="template-preview">
//                   <div className="template-preview-header" style={{ background: t.hue }}>
//                     <div className="template-preview-name-line" />
//                     <div className="template-preview-role-line" />
//                   </div>
//                   <div className="template-preview-body">
//                     {t.lines.map((w, j) => (
//                       <div key={j} className="template-line" style={{ width: `${w * 100}%` }} />
//                     ))}
//                   </div>
//                 </div>
//                 <div className="template-info">
//                   <span className="template-name">{t.name}</span>
//                   <span className="template-tag">{t.tag}</span>
//                 </div>
//               </div>
//             ))}
//           </div>
//           <div className="reveal delay-6" style={{ textAlign: "center", marginTop: "2.5rem" }}>
//             <button className="btn-ghost" style={{ padding: "11px 28px", fontSize: "0.9rem" }}>Browse all 24 templates →</button>
//           </div>
//         </div>
//       </div>

//       {/* ATS SECTION */}
//       <div className="ats-section">
//         <div style={{ position: "absolute", top: "10%", right: "5%", width: 300, height: 300 }} className="ats-bg-circle anim-floatSlow" />
//         <div style={{ position: "absolute", bottom: "5%", left: "3%", width: 200, height: 200 }} className="ats-bg-circle anim-float" />
//         <div className="ats-section-inner">
//           <div>
//             <div className="section-tag reveal">◎ ATS Optimization</div>
//             <h2 className="section-headline reveal delay-1">Pass every ATS<br />filter, every time</h2>
//             <p className="section-sub reveal delay-2">
//               Over 99% of Fortune 500 companies use ATS software. Our real-time analyzer ensures your resume is always optimized for both human recruiters and automated systems.
//             </p>
//             <div className="reveal delay-3" style={{ marginTop: "2rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
//               {["Keyword density analysis against job descriptions", "Section hierarchy and formatting checks", "File format compatibility verification", "Readability and length scoring"].map((item, i) => (
//                 <div key={i} style={{ display: "flex", alignItems: "center", gap: 12, fontSize: "0.88rem", color: "rgba(255,255,255,0.8)" }}>
//                   <div style={{ width: 20, height: 20, borderRadius: 6, background: "rgba(255,255,255,0.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.7rem", flexShrink: 0, color: COLORS.amberLight }}>✓</div>
//                   {item}
//                 </div>
//               ))}
//             </div>
//           </div>
//           <div className="reveal-right delay-3">
//             <ATSCriteria />
//           </div>
//         </div>
//       </div>

//       {/* BEFORE / AFTER */}
//       <div className="before-after-section">
//         <div className="before-after-inner">
//           <div className="text-centered">
//             <div className="section-tag reveal" style={{ display: "inline-flex" }}>⟲ Transformation</div>
//             <h2 className="section-headline reveal delay-1">The before & after<br />speaks for itself</h2>
//             <p className="section-sub centered reveal delay-2">
//               From rough notes to recruiter-ready in one AI pass. See what our system does to a typical first draft.
//             </p>
//           </div>
//           <div className="before-after-grid">
//             <div className="ba-card reveal-left delay-2">
//               <div className="ba-label bad">✗ Before — Raw draft</div>
//               <div className="ba-content">
//                 <div className="ba-block messy">
//                   <div className="ba-block-title">Summary</div>
//                   im a developer with experience doing stuff at various companies. i know react and some other things. looking for a new job.
//                 </div>
//                 <div className="ba-block messy">
//                   <div className="ba-block-title">Work</div>
//                   worked at tech startup 2021-2023. did frontend things. also did backend sometimes. team was small.
//                 </div>
//                 <div className="ba-block messy">
//                   <div className="ba-block-title">Skills</div>
//                   react, js, html, css, git, some python, databases, etc.
//                 </div>
//               </div>
//             </div>

//             <div className="ba-arrow reveal delay-3">
//               <div className="ba-arrow-icon">→</div>
//             </div>

//             <div className="ba-card after reveal-right delay-2">
//               <div className="ba-label good">✓ After — AI optimized</div>
//               <div className="ba-content">
//                 <div className="ba-block clean">
//                   <div className="ba-block-title">Professional Summary</div>
//                   Full-stack engineer with 3+ years building scalable React applications. Proven track record shipping production features in fast-paced startup environments with cross-functional teams.
//                 </div>
//                 <div className="ba-block clean">
//                   <div className="ba-block-title">Experience</div>
//                   Frontend Engineer · TechCo (2021–2023) · Developed 12 React components used by 40K+ users · Reduced API response time by 35% through query optimization.
//                 </div>
//                 <div className="ba-block clean">
//                   <div className="ba-block-title">Skills</div>
//                   React · TypeScript · Node.js · PostgreSQL · Python · Git · REST APIs · Agile/Scrum
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>

//       {/* WORKFLOW */}
//       <div className="workflow-section" id="how">
//         <div className="workflow-inner">
//           <div>
//             <div className="section-tag reveal">⬡ How It Works</div>
//             <h2 className="section-headline reveal delay-1">From blank page to<br />interview in 5 steps</h2>
//           </div>
//           <div className="workflow-steps">
//             {WORKFLOW_STEPS.map((s, i) => (
//               <div className={`workflow-step reveal delay-${i + 2}`} key={i}>
//                 <div className="workflow-step-num">{s.num}</div>
//                 <div className="workflow-step-content">
//                   <div className="workflow-step-title">{s.title}</div>
//                   <div className="workflow-step-desc">{s.desc}</div>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* TESTIMONIALS */}
//       <div className="testimonials-section">
//         <div className="testimonials-inner">
//           <div className="text-centered">
//             <div className="section-tag reveal" style={{ display: "inline-flex" }}>◈ Testimonials</div>
//             <h2 className="section-headline reveal delay-1">Trusted by job seekers<br />across every industry</h2>
//           </div>
//           <div className="testimonials-grid">
//             {TESTIMONIALS.map((t, i) => (
//               <div className={`testimonial-card reveal delay-${i + 2}`} key={i}>
//                 <div className="testimonial-stars">{"★".repeat(t.stars)}</div>
//                 <p className="testimonial-quote">"{t.quote}"</p>
//                 <div className="testimonial-author">
//                   <div className="testimonial-avatar" style={{ background: t.bg, color: t.text }}>{t.avatar}</div>
//                   <div>
//                     <div className="testimonial-name">{t.name}</div>
//                     <div className="testimonial-role">{t.role}</div>
//                   </div>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* PRICING */}
//       <div className="pricing-section" id="pricing">
//         <div className="pricing-inner">
//           <div className="section-tag reveal" style={{ display: "inline-flex" }}>◧ Pricing</div>
//           <h2 className="section-headline reveal delay-1">Simple, transparent pricing</h2>
//           <p className="section-sub centered reveal delay-2">Start free. Upgrade when you're ready. No hidden fees, no surprise charges.</p>
//           <div className="pricing-grid">
//             {[
//               {
//                 plan: "Free",
//                 price: "0",
//                 desc: "Perfect for getting started",
//                 features: ["2 resumes", "5 templates", "PDF export", "Basic ATS score", "Manual mode"],
//                 cta: "Start free",
//                 popular: false,
//               },
//               {
//                 plan: "Pro",
//                 price: "9",
//                 desc: "For serious job seekers",
//                 features: ["Unlimited resumes", "All 24 templates", "AI resume mode", "Advanced ATS analysis", "PDF + DOCX export", "Priority support"],
//                 cta: "Start Pro",
//                 popular: true,
//               },
//               {
//                 plan: "Team",
//                 price: "29",
//                 desc: "For career coaches & teams",
//                 features: ["Everything in Pro", "Up to 10 seats", "Shared template library", "Bulk export", "Analytics dashboard", "Custom branding"],
//                 cta: "Contact us",
//                 popular: false,
//               },
//             ].map((p, i) => (
//               <div className={`pricing-card${p.popular ? " popular" : ""} reveal delay-${i + 2}`} key={i}>
//                 {p.popular && <div className="popular-badge">Most Popular</div>}
//                 <div className="pricing-plan">{p.plan}</div>
//                 <div className="pricing-price">
//                   <span className="pricing-price-currency">$</span>
//                   {p.price}
//                   <span className="pricing-price-period">/mo</span>
//                 </div>
//                 <p className="pricing-desc">{p.desc}</p>
//                 <div className="pricing-features">
//                   {p.features.map((f, j) => (
//                     <div className="pricing-feature" key={j}>
//                       <div className="pricing-check">✓</div>
//                       {f}
//                     </div>
//                   ))}
//                 </div>
//                 <button className={`btn-plan${p.popular ? " primary" : ""}`}>{p.cta}</button>
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* FAQ */}
//       <div className="faq-section">
//         <div className="faq-inner">
//           <div className="text-centered">
//             <div className="section-tag reveal" style={{ display: "inline-flex" }}>? FAQ</div>
//             <h2 className="section-headline reveal delay-1">Common questions</h2>
//           </div>
//           <div className="faq-list">
//             {FAQS.map((f, i) => (
//               <div className={`reveal delay-${i + 2}`} key={i}>
//                 <FAQItem q={f.q} a={f.a} />
//               </div>
//             ))}
//           </div>
//         </div>
//       </div>

//       {/* FINAL CTA */}
//       <div className="final-cta">
//         <div className="cta-bg-circle" style={{ width: 500, height: 500, top: "-20%", right: "-10%" }} />
//         <div className="cta-bg-circle" style={{ width: 300, height: 300, bottom: "-15%", left: "-5%" }} />
//         <div className="final-cta-inner">
//           <h2 className="final-cta-headline reveal">
//             Your next interview<br />
//             <em style={{ fontStyle: "italic", color: COLORS.amberLight }}>starts with one resume</em>
//           </h2>
//           <p className="final-cta-sub reveal delay-2">
//             Join 240,000+ job seekers who built their career-winning resume on ResumeAI. Free to start, results in 60 seconds.
//           </p>
//           <div className="final-cta-btns reveal delay-3">
//             <button className="btn-cta-white">Build my resume — it's free</button>
//             <button className="btn-cta-outline">Explore templates</button>
//           </div>
//           <p className="final-cta-note reveal delay-4">No credit card · No setup · Instant export</p>
//         </div>
//       </div>

//       {/* FOOTER */}
//       <footer className="footer">
//         <div className="footer-inner">
//           <div className="footer-grid">
//             <div className="footer-brand">
//               <div className="footer-logo">
//                 <div className="footer-logo-mark">R</div>
//                 ResumeAI
//               </div>
//               <p className="footer-desc">
//                 The AI-powered resume builder built for modern job seekers. Professional, fast, and ATS-ready.
//               </p>
//             </div>
//             <div>
//               <div className="footer-col-title">Product</div>
//               <div className="footer-links">
//                 <a href="#">AI Resume Mode</a>
//                 <a href="#">Manual Builder</a>
//                 <a href="#">Templates</a>
//                 <a href="#">ATS Checker</a>
//                 <a href="#">Pricing</a>
//               </div>
//             </div>
//             <div>
//               <div className="footer-col-title">Company</div>
//               <div className="footer-links">
//                 <a href="#">About</a>
//                 <a href="#">Blog</a>
//                 <a href="#">Careers</a>
//                 <a href="#">Press</a>
//                 <a href="#">Contact</a>
//               </div>
//             </div>
//             <div>
//               <div className="footer-col-title">Legal</div>
//               <div className="footer-links">
//                 <a href="#">Privacy Policy</a>
//                 <a href="#">Terms of Service</a>
//                 <a href="#">Cookie Policy</a>
//                 <a href="#">GDPR</a>
//               </div>
//             </div>
//           </div>
//           <div className="footer-bottom">
//             <div className="footer-copy">© 2025 ResumeAI. All rights reserved.</div>
//             <div className="footer-badge">
//               <div className="footer-badge-dot" />
//               All systems operational
//             </div>
//           </div>
//         </div>
//       </footer>
//     </>
//   );
// }




