import { useRef } from "react";
import { motion, useScroll, useTransform, useSpring } from "framer-motion";
import ResumePreview from "./ResumePreview";

const DUMMY_RESUMES = [
  {
    template: "harvard",
    data: {
      personalInfo: { fullName: "Alexandra Chen", jobTitle: "Senior Software Engineer", email: "alex.chen@email.com", phone: "(555) 123-4567", location: "San Francisco, CA", linkedin: "linkedin.com/in/alexchen" },
      summary: "Experienced software engineer with 8+ years building scalable web applications. Led teams of 5-10 engineers, delivering products serving millions of users.",
      experience: [
        { role: "Senior Software Engineer", company: "TechCorp Inc.", duration: "2021 - Present", description: "Led migration of monolith to microservices, reducing deployment time by 60%. Mentored 4 junior engineers." },
        { role: "Software Engineer", company: "StartupXYZ", duration: "2018 - 2021", description: "Built core API serving 10M+ daily requests. Implemented CI/CD pipeline reducing release cycle from weeks to hours." }
      ],
      education: [{ degree: "B.S. Computer Science", institution: "Stanford University", duration: "2014 - 2018" }],
      skills: ["React", "Node.js", "Python", "AWS", "Docker", "PostgreSQL", "TypeScript"]
    }
  },
  {
    template: "stanford",
    data: {
      personalInfo: { fullName: "Marcus Johnson", jobTitle: "Product Manager", email: "marcus.j@email.com", phone: "(555) 234-5678", location: "New York, NY", linkedin: "linkedin.com/in/marcusj" },
      summary: "Strategic product manager with 6+ years driving growth at B2B SaaS companies. Data-driven approach with track record of launching features that increased revenue by 40%.",
      experience: [
        { role: "Senior Product Manager", company: "Enterprise Solutions", duration: "2020 - Present", description: "Launched 3 major features generating $5M ARR. Led cross-functional teams of 15+." },
        { role: "Product Manager", company: "GrowthTech", duration: "2017 - 2020", description: "Drove product strategy for SMB segment, increasing user base from 10K to 100K in 18 months." }
      ],
      education: [{ degree: "MBA", institution: "Harvard Business School", duration: "2015 - 2017" }],
      skills: ["Product Strategy", "Agile/Scrum", "SQL", "Tableau", "Jira", "A/B Testing", "User Research"]
    }
  },
  {
    template: "software_engineer",
    data: {
      personalInfo: { fullName: "Priya Patel", jobTitle: "Full Stack Developer", email: "priya.p@email.com", phone: "(555) 345-6789", location: "Seattle, WA", linkedin: "linkedin.com/in/priyap" },
      summary: "Full stack developer specializing in React and Node.js ecosystems. Built high-performance applications processing 1M+ transactions daily.",
      experience: [
        { role: "Full Stack Developer", company: "CloudScale", duration: "2021 - Present", description: "Architected real-time analytics dashboard handling 100K concurrent users. Reduced API response time by 70%." },
        { role: "Frontend Engineer", company: "WebApp Inc.", duration: "2019 - 2021", description: "Developed component library used across 5 products. Improved Core Web Vitals scores by 40%." }
      ],
      education: [{ degree: "B.S. Computer Science", institution: "University of Washington", duration: "2015 - 2019" }],
      skills: ["React", "TypeScript", "Node.js", "GraphQL", "AWS", "Redis", "MongoDB"]
    }
  },
  {
    template: "marketing",
    data: {
      personalInfo: { fullName: "Sarah Williams", jobTitle: "Digital Marketing Director", email: "sarah.w@email.com", phone: "(555) 456-7890", location: "Austin, TX", linkedin: "linkedin.com/in/sarahw" },
      summary: "Results-driven marketing leader with 10+ years scaling B2C brands. Expert in performance marketing, SEO, and content strategy.",
      experience: [
        { role: "Director of Marketing", company: "BrandForce", duration: "2019 - Present", description: "Scaled marketing team from 3 to 15. Grew organic traffic 300% and reduced CAC by 45%." },
        { role: "Performance Marketing Manager", company: "AdTech Solutions", duration: "2016 - 2019", description: "Managed $5M annual budget across Google, Meta, and TikTok. Achieved 6.2 ROAS across all channels." }
      ],
      education: [{ degree: "M.A. Marketing", institution: "Northwestern University", duration: "2014 - 2016" }],
      skills: ["SEO", "Google Ads", "Meta Ads", "HubSpot", "Analytics", "Content Strategy", "Team Leadership"]
    }
  },
  {
    template: "creative_director",
    data: {
      personalInfo: { fullName: "James Rodriguez", jobTitle: "Creative Director", email: "james.r@email.com", phone: "(555) 567-8901", location: "Los Angeles, CA", linkedin: "linkedin.com/in/jamesr" },
      summary: "Award-winning creative director with 12+ years crafting compelling brand narratives. Led campaigns for Fortune 500 brands generating 1B+ impressions.",
      experience: [
        { role: "Creative Director", company: "AgencyX", duration: "2018 - Present", description: "Led creative for Apple, Nike, and Spotify campaigns. Won 3 Cannes Lions and 5 Webby Awards." },
        { role: "Senior Designer", company: "DesignCo", duration: "2014 - 2018", description: "Created visual identities for 20+ startups. Led rebrand that increased client revenue by 25%." }
      ],
      education: [{ degree: "B.F.A. Graphic Design", institution: "Rhode Island School of Design", duration: "2010 - 2014" }],
      skills: ["Brand Strategy", "Art Direction", "Adobe Creative Suite", "Motion Graphics", "Team Leadership", "Client Relations"]
    }
  }
];

const CARD_W = 340;
const GAP_X = 340;
const GAP_Y = 200;

export default function ScrollShowcase() {
  const sectionRef = useRef(null);

  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"]
  });

  // The entire group translates diagonally as user scrolls through the section.
  // Starts offscreen lower-right, ends offscreen upper-left.
  // Animation spans full scroll — no blank space.
  const translateX = useTransform(scrollYProgress, [0, 1], ["100vw", "-240vw"]);
  const translateY = useTransform(scrollYProgress, [0, 1], ["100vh", "-190vh"]);

  const smoothX = useSpring(translateX, { stiffness: 30, damping: 28, mass: 1.4 });
  const smoothY = useSpring(translateY, { stiffness: 30, damping: 28, mass: 1.4 });

  return (
    <section className="diagonal-showcase" ref={sectionRef}>
      {/* Header — scrolls normally, no sticky */}
      <div className="diagonal-header">
        <div className="diagonal-tag">Portfolio</div>
        <h2 className="diagonal-title">
          Templates crafted for<br />
          <em>every career</em>
        </h2>
        <p className="diagonal-sub">
          Scroll to explore our curated collection of ATS-optimized,
          recruiter-approved resume designs.
        </p>
      </div>

      {/* Diagonal conveyor — five resumes in a queue, moving as one unit */}
      <motion.div
        className="diagonal-track"
        style={{ x: smoothX, y: smoothY }}
      >
        {DUMMY_RESUMES.map((resume, i) => (
          <div
            key={i}
            className="diagonal-resume-slot"
            style={{
              left: i * (CARD_W + GAP_X),
              top: i * GAP_Y,
              zIndex: DUMMY_RESUMES.length - i
            }}
          >
            <div className="diagonal-resume-card">
              <ResumePreview data={resume.data} template={resume.template} />
            </div>
            <div className="diagonal-resume-label">
              <span className="diagonal-resume-name">{resume.data.personalInfo.fullName}</span>
              <span className="diagonal-resume-title">{resume.data.personalInfo.jobTitle}</span>
            </div>
          </div>
        ))}
      </motion.div>


    </section>
  );
}
