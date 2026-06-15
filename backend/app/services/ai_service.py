import json
import re
from sqlalchemy.orm import Session
from .llm_service import LLMProviderService, PromptBuilderService
from ..models import AIRequest

# High-quality structured default mock models for fallback/manual modes
DEFAULT_MOCKS = {
    "experienced": {
        "personalInfo": {
            "fullName": "Alex Mercer",
            "jobTitle": "Lead Full-Stack Engineer",
            "email": "alex.mercer@devmail.com",
            "phone": "+1 (555) 019-2834",
            "location": "San Francisco, CA",
            "website": "alexmercer.dev",
            "linkedin": "linkedin.com/in/alexmercer"
        },
        "summary": "Innovative Lead Full-Stack Engineer with over 8 years of experience designing and deploying robust, scalable web architectures. Specialized in React, Python, PostgreSQL, and AWS systems, with a passion for optimizing app performance and leading agile teams.",
        "experience": [
            {
                "company": "TechNova Solutions",
                "role": "Senior Full-Stack Engineer",
                "duration": "2021 - Present",
                "description": "Spearheaded development of a high-throughput data dashboard, decreasing user query latencies by 35%.\nLed a team of 6 engineers in migrating monolithic API endpoints to FastAPI microservices, saving $15k in monthly hosting overhead.\nArchitected a PostgreSQL database cluster with advanced connection pooling to support 50k+ active concurrent connections."
            },
            {
                "company": "Streamline Code Corp",
                "role": "Software Engineer II",
                "duration": "2018 - 2021",
                "description": "Engineered real-time collaboration tools using WebSockets and React, increasing daily user engagement by 40%.\nOptimized Webpack/Vite bundlers to reduce initial landing page bundle sizes by 120KB, enhancing page load times."
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "Stanford University",
                "duration": "2014 - 2018",
                "description": "Focus in Software Engineering & Database Systems. Graduated with Honors."
            }
        ],
        "skills": ["React", "JavaScript", "Python", "FastAPI", "PostgreSQL", "SQLAlchemy", "AWS", "Docker", "Git", "Tailwind CSS"],
        "projects": [
            {
                "name": "CloudDB Architect",
                "description": "Created a lightweight local database abstraction designed for high-availability cloud deployments. Features integrated AES-256 encryption and instant S3 backup capabilities."
            }
        ],
        "certifications": ["AWS Certified Solutions Architect", "Google Cloud Professional Engineer"],
        "achievements": ["Recipient of TechNova Solutions Engineering Excellence Award 2023", "First Place at SF Hackathon 2019"]
    },
    "career_switcher": {
        "personalInfo": {
            "fullName": "Sarah Jenkins",
            "jobTitle": "Product Manager (former Ops Lead)",
            "email": "sarah.j@careermail.com",
            "phone": "+1 (555) 042-9988",
            "location": "Boston, MA",
            "website": "sarahjops.com",
            "linkedin": "linkedin.com/in/sarahjenkins"
        },
        "summary": "Results-driven Product Manager transitioning from a strong 6-year background in business operations. Experienced in cross-functional coordination, process automation, and database reporting. Certified Scrum Product Owner (CSPO).",
        "experience": [
            {
                "company": "Apex Global Logistics",
                "role": "Operations Manager",
                "duration": "2020 - Present",
                "description": "Spearheaded logistics workflow automation using custom reporting dashboards, trimming processing cycles by 20 hours per week.\nCollaborated directly with engineering leads to prioritize backlogs, accelerating shipping schedule features.\nAnalyzed warehouse data trends using SQL databases, resulting in an 18% reduction in inventory storage cost."
            }
        ],
        "education": [
            {
                "degree": "B.A. in Business Administration",
                "institution": "Boston University",
                "duration": "2012 - 2016",
                "description": "Focus in Supply Chain Management and Analytical Systems."
            }
        ],
        "skills": ["Product Management", "Scrum / Agile", "Operations Optimization", "SQL", "Data Analysis", "Project Management", "Jira", "Figma"],
        "projects": [
            {
                "name": "Logistics Dashboard Launch",
                "description": "Directed development of a real-time shipping analysis dashboard, aligning operations, design, and development teams."
            }
        ],
        "certifications": ["Certified Scrum Product Owner (CSPO)", "Lean Six Sigma Green Belt"],
        "achievements": ["Promoted to Operations Manager within 18 months of joining Apex Logistics", "Led cross-functional team that saved $80,000 in annual operational inefficiencies"]
    },
    "fresher": {
        "personalInfo": {
            "fullName": "Ethan Cole",
            "jobTitle": "Junior AI Engineer",
            "email": "ethan.cole@freshgraduate.com",
            "phone": "+1 (555) 987-6543",
            "location": "Austin, TX",
            "website": "ethancole.github.io",
            "linkedin": "linkedin.com/in/ethancole"
        },
        "summary": "Recent B.S. in Computer Science graduate from UT Austin. Passionate about Artificial Intelligence, Machine Learning, and natural language processing. Skilled in Python, PyTorch, SQL, and REST API development.",
        "experience": [
            {
                "company": "Cognitive Tech Labs",
                "role": "Machine Learning Intern",
                "duration": "Summer 2025",
                "description": "Implemented text summarization models using Python and PyTorch, improving API response quality by 15%.\nCurated and cleaned datasets of 1M+ tokens for training large language model pipelines."
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of Texas at Austin",
                "duration": "2022 - 2026",
                "description": "GPA: 3.8/4.0. Core coursework: Neural Networks, Data Structures, Database Management, Software Engineering."
            }
        ],
        "skills": ["Python", "PyTorch", "SQL", "Scikit-Learn", "Git", "REST APIs", "FastAPI", "Data Structures"],
        "projects": [
            {
                "name": "SmartResume Extractor",
                "description": "Developed a Python application that uses regex and text vectorization to parse unstructured career history into structured resume blocks."
            }
        ],
        "certifications": ["TensorFlow Developer Certificate"],
        "achievements": ["Dean's Honor List - All Semesters", "Winner of UT CS hackathon - Best AI Implementation Category"]
    }
}

class ResumeGeneratorService:
    def __init__(self):
        self.llm = LLMProviderService()

    def generate_structured_resume(self, db: Session, user_id: str, prompt: str, archetype: str = "experienced") -> dict:
        """
        Parses raw text prompt into a high-quality structured resume.
        Queries the database Harvard rules, applies them, and returns structured JSON.
        """
        system_rules = PromptBuilderService.get_active_rules_instruction(db)
        
        # We instruct Gemini to output structured JSON representing the resume
        llm_prompt = f"""
Convert the following raw user career experiences into a fully structured, professional, ATS-optimized resume.
The output MUST be a valid JSON object matching the schema below. Do not include markdown code block syntax (like ```json ... ```), write only raw JSON.

Schema:
{{
    "personalInfo": {{
        "fullName": "...",
        "jobTitle": "...",
        "email": "...",
        "phone": "...",
        "location": "...",
        "website": "...",
        "linkedin": "..."
    }},
    "summary": "...",
    "experience": [
        {{
            "company": "...",
            "role": "...",
            "duration": "...",
            "description": "Detailed bullet points separated by newline \\n"
        }}
    ],
    "education": [
        {{
            "degree": "...",
            "institution": "...",
            "duration": "...",
            "description": "..."
        }}
    ],
    "skills": ["skill1", "skill2", ...],
    "projects": [
        {{
            "name": "...",
            "description": "..."
        }}
    ],
    "certifications": ["...", ...],
    "achievements": ["...", ...]
}}

User Raw Text:
"{prompt}"

Archetype Focus: {archetype}
"""
        response_text = self.llm.generate(llm_prompt, system_instruction=system_rules)
        
        # Save request to database
        try:
            req = AIRequest(user_id=user_id, request_type="resume_gen", prompt=prompt, response=response_text)
            db.add(req)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error logging AI request: {e}")
            
        # Parse JSON
        try:
            # Clean up potential markdown formatting wrapping JSON
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```"):
                cleaned_text = re.sub(r"^```(json)?", "", cleaned_text)
                cleaned_text = re.sub(r"```$", "", cleaned_text)
                cleaned_text = cleaned_text.strip()
                
            return json.loads(cleaned_text)
        except Exception as e:
            print(f"Failed to parse JSON response: {e}. Falling back to high-quality mock data.")
            # Let's populate the mock template and customize it with name/email if we can find them
            mock_data = DEFAULT_MOCKS.get(archetype, DEFAULT_MOCKS["experienced"]).copy()
            # Try a simple name/email extraction
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', prompt)
            if email_match:
                mock_data["personalInfo"]["email"] = email_match.group(0)
            phone_match = re.search(r'\+?\d[\d -]{8,15}\d', prompt)
            if phone_match:
                mock_data["personalInfo"]["phone"] = phone_match.group(0)
            return mock_data

class CoverLetterGeneratorService:
    def __init__(self):
        self.llm = LLMProviderService()

    def generate_cover_letter(self, db: Session, user_id: str, job_role: str, company_name: str, experience_summary: str) -> str:
        system_rules = "Write in a professional, engaging business letter format. Avoid first-person pronouns where possible, but maintain personal touch since it's a cover letter."
        
        prompt = f"""
Write a professional, highly targeted cover letter for a candidate seeking the role of '{job_role}' at '{company_name}'.
The candidate's brief experience summary is:
"{experience_summary}"

The letter should start with 'Dear Hiring Team at {company_name},', follow standard paragraph spacing, and conclude with 'Sincerely,\n[Candidate Name]'.
Make it sound extremely persuasive, professional, and well-written.
"""
        response_text = self.llm.generate(prompt, system_instruction=system_rules)
        
        try:
            req = AIRequest(user_id=user_id, request_type="cover_letter_gen", prompt=prompt, response=response_text)
            db.add(req)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error logging AI Request: {e}")
            
        return response_text

class ATSScoreService:
    @staticmethod
    def calculate_score(resume_data: dict) -> dict:
        """
        Calculates a custom ATS readiness score (0-100) and feedback.
        Checks:
        1. Action verbs: 20 pts (Checks verbs at the start of bullet points)
        2. Keyword density: 20 pts (Checks important technical/business keywords)
        3. Resume length: 15 pts (Overall word count check)
        4. First-Person Pronouns: 15 pts (Presence of I, me, my, we)
        5. Section Completeness: 15 pts (Presence of essential sections)
        6. Formatting/Consistency: 15 pts (Punctuation and contact integrity)
        """
        score = 0
        details = {}
        recommendations = []

        personal_info = resume_data.get("personalInfo", {})
        summary = resume_data.get("summary", "")
        experience = resume_data.get("experience", [])
        education = resume_data.get("education", [])
        skills = resume_data.get("skills", [])
        projects = resume_data.get("projects", [])

        # 1. Section Completeness (Max 15)
        completeness = 0
        missing_sections = []
        if personal_info.get("fullName") and personal_info.get("email"):
            completeness += 3
        else:
            missing_sections.append("Contact Details")
        if summary:
            completeness += 3
        else:
            missing_sections.append("Summary Statement")
        if experience:
            completeness += 3
        else:
            missing_sections.append("Work Experience")
        if education:
            completeness += 3
        else:
            missing_sections.append("Education")
        if skills:
            completeness += 3
        else:
            missing_sections.append("Skills Catalog")
            
        score += completeness
        details["completeness"] = {"score": completeness, "max": 15}
        if missing_sections:
            recommendations.append(f"Add missing sections to complete your profile: {', '.join(missing_sections)}.")

        # 2. Action Verbs (Max 20)
        action_verbs = ["developed", "spearheaded", "implemented", "designed", "built", "managed", 
                        "led", "created", "optimized", "increased", "reduced", "architected", "engineered",
                        "analyzed", "facilitated", "formulated", "directed", "coordinated", "saved", "established"]
        verb_score = 0
        bullet_count = 0
        verb_matches = 0
        
        for exp in experience:
            desc = exp.get("description", "")
            bullets = [b.strip() for b in desc.split("\n") if b.strip()]
            for bullet in bullets:
                bullet_count += 1
                # Clean bullet characters like - or *
                clean_bullet = re.sub(r"^[\*\-\•\s]+", "", bullet).strip().lower()
                first_word = clean_bullet.split()[0] if clean_bullet.split() else ""
                # Strip punctuation
                first_word = re.sub(r"[^\w]", "", first_word)
                if first_word in action_verbs:
                    verb_matches += 1
                    
        if bullet_count > 0:
            verb_ratio = verb_matches / bullet_count
            verb_score = int(verb_ratio * 20)
        else:
            verb_score = 0
            
        score += verb_score
        details["action_verbs"] = {"score": verb_score, "max": 20, "count": verb_matches, "total": bullet_count}
        if verb_score < 15:
            recommendations.append("Ensure every experience bullet point starts with a strong action verb (e.g. 'Spearheaded', 'Optimized').")

        # 3. Keyword Density (Max 20)
        # Scan skills list and text content for essential keywords
        core_keywords = ["sql", "react", "python", "aws", "docker", "git", "agile", "postgres", 
                         "fastapi", "project management", "data analysis", "figma", "scrum", "development", "testing"]
        keyword_matches = 0
        full_text = json.dumps(resume_data).lower()
        
        for kw in core_keywords:
            if kw in full_text:
                keyword_matches += 1
                
        kw_score = min(20, keyword_matches * 2.5)  # 8 keywords matching gives max 20
        kw_score = int(kw_score)
        score += kw_score
        details["keywords"] = {"score": kw_score, "max": 20, "matches": keyword_matches}
        if kw_score < 15:
            recommendations.append("Incorporate more industry keywords (e.g., specific methodologies, tools, and databases) into your skills and descriptions.")

        # 4. First-Person Pronouns (Max 15 - starts at 15 and deducts)
        pronoun_score = 15
        pronouns_found = []
        pronouns_regex = r"\b(i|me|my|we|us|our)\b"
        
        # Scan experience and summary
        check_text = (summary + " " + " ".join([e.get("description", "") for e in experience])).lower()
        found = re.findall(pronouns_regex, check_text)
        if found:
            pronouns_found = list(set(found))
            deduction = min(15, len(found) * 3)
            pronoun_score -= deduction
            
        score += pronoun_score
        details["pronouns"] = {"score": pronoun_score, "max": 15, "found": pronouns_found}
        if pronoun_score < 15:
            recommendations.append(f"Remove first-person pronouns ({', '.join(pronouns_found)}) to adhere to objective writing principles.")

        # 5. Resume Length (Max 15)
        # Total words should be between 300 and 700 words for a 1-page resume
        words = len(re.findall(r"\w+", full_text))
        length_score = 0
        if 250 <= words <= 650:
            length_score = 15
        elif 150 <= words < 250 or 650 < words <= 900:
            length_score = 10
        else:
            length_score = 5
            
        score += length_score
        details["length"] = {"score": length_score, "max": 15, "word_count": words}
        if words < 250:
            recommendations.append("Your resume content is relatively sparse. Expand on your experiences to better demonstrate competence.")
        elif words > 700:
            recommendations.append("Your resume exceeds standard single-page lengths. Condense bullet points and remove redundant details.")

        # 6. Formatting Consistency (Max 15)
        formatting_score = 15
        issues = []
        
        # Check phone and email formats
        if personal_info.get("email") and "@" not in personal_info.get("email"):
            formatting_score -= 5
            issues.append("Invalid email format")
        if personal_info.get("phone") and len(re.sub(r"[^\d]", "", personal_info.get("phone"))) < 7:
            formatting_score -= 5
            issues.append("Invalid phone number format")
            
        # Check bullet point consistency (trailing punctuation)
        no_periods = 0
        total_bullets = 0
        for exp in experience:
            desc = exp.get("description", "")
            bullets = [b.strip() for b in desc.split("\n") if b.strip()]
            for bullet in bullets:
                total_bullets += 1
                if not bullet.endswith("."):
                    no_periods += 1
                    
        if total_bullets > 0 and no_periods / total_bullets > 0.3:
            formatting_score -= 5
            issues.append("Inconsistent bullet point periods")
            
        formatting_score = max(0, formatting_score)
        score += formatting_score
        details["formatting"] = {"score": formatting_score, "max": 15, "issues": issues}
        if issues:
            recommendations.append(f"Resolve formatting checks: {', '.join(issues)} (e.g. end all bullet points with periods).")

        return {
            "score": int(score),
            "details": details,
            "recommendations": recommendations
        }
