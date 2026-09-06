import { useReveal } from "./hooks/useReveal";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import ScrollShowcase from "./components/ScrollShowcase";
import CoverLetterSection from "./components/CoverLetterSection";
import Workflow from "./components/Workflow";
import Pricing from "./components/Pricing";
import Footer from "./components/Footer";
export default function LandingPage({ onBuildResume }) {
  useReveal();
  return (
    <>
      <Navbar />
      <Hero onBuildResume={onBuildResume} />
      
      <ScrollShowcase onBuildResume={onBuildResume} />
      
      <CoverLetterSection />
      <Workflow />
      <Pricing />
      
      <Footer />
    </>
  );
}
