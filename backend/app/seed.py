import json
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models import Template, ResumeRule

TEMPLATES_DATA = [
    # ATS CATEGORY
    {
        "id": "harvard",
        "name": "Harvard Standard",
        "category": "ATS",
        "color_scheme": {"primary": "#000000", "secondary": "#4A4A4A", "text": "#1A1A1A", "accent": "#A51C30", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    {
        "id": "stanford",
        "name": "Stanford Clean",
        "category": "ATS",
        "color_scheme": {"primary": "#8C1515", "secondary": "#4D4F53", "text": "#2E2D29", "accent": "#8C1515", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.75in", "headerStyle": "left", "section_order": ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"]}
    },
    {
        "id": "mit",
        "name": "MIT Compact",
        "category": "ATS",
        "color_scheme": {"primary": "#A31F34", "secondary": "#8A8B8C", "text": "#111111", "accent": "#A31F34", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.5in", "headerStyle": "left", "section_order": ["education", "skills", "experience", "projects", "certifications", "achievements"]}
    },
    {
        "id": "columbia",
        "name": "Columbia Classic",
        "category": "ATS",
        "color_scheme": {"primary": "#003087", "secondary": "#6CACE4", "text": "#1D252D", "accent": "#003087", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.8in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    {
        "id": "yale",
        "name": "Yale Editorial",
        "category": "ATS",
        "color_scheme": {"primary": "#00356B", "secondary": "#28619E", "text": "#0F0F0F", "accent": "#00356B", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    {
        "id": "princeton",
        "name": "Princeton Bold",
        "category": "ATS",
        "color_scheme": {"primary": "#EE7F2D", "secondary": "#222222", "text": "#1C1C1C", "accent": "#EE7F2D", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "left", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    # CORPORATE CATEGORY
    {
        "id": "executive",
        "name": "Executive Elite",
        "category": "Corporate",
        "color_scheme": {"primary": "#0F172A", "secondary": "#475569", "text": "#1E293B", "accent": "#B45309", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"]}
    },
    {
        "id": "consultant",
        "name": "Sleek Consultant",
        "category": "Corporate",
        "color_scheme": {"primary": "#1E293B", "secondary": "#64748B", "text": "#334155", "accent": "#0F766E", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.7in", "headerStyle": "left", "section_order": ["summary", "experience", "projects", "education", "skills", "certifications", "achievements"]}
    },
    {
        "id": "finance",
        "name": "Wall Street Finance",
        "category": "Corporate",
        "color_scheme": {"primary": "#064E3B", "secondary": "#115E59", "text": "#0F172A", "accent": "#0D9488", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "skills", "certifications", "achievements"]}
    },
    {
        "id": "product_manager",
        "name": "SaaS PM",
        "category": "Corporate",
        "color_scheme": {"primary": "#4F46E5", "secondary": "#475569", "text": "#1E293B", "accent": "#4F46E5", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-right", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["education", "skills", "certifications", "achievements"]}
    },
    {
        "id": "operations",
        "name": "Operations Lead",
        "category": "Corporate",
        "color_scheme": {"primary": "#334155", "secondary": "#475569", "text": "#0F172A", "accent": "#2563EB", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.75in", "headerStyle": "left", "section_order": ["summary", "experience", "education", "skills", "projects", "certifications", "achievements"]}
    },
    {
        "id": "management",
        "name": "Strategic Manager",
        "category": "Corporate",
        "color_scheme": {"primary": "#881337", "secondary": "#4C0519", "text": "#1F2937", "accent": "#9F1239", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.75in", "headerStyle": "centered", "section_order": ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]}
    },
    # TECHNOLOGY CATEGORY
    {
        "id": "software_engineer",
        "name": "Dev Standard",
        "category": "Technology",
        "color_scheme": {"primary": "#0F766E", "secondary": "#334155", "text": "#0F172A", "accent": "#0D9488", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications", "achievements"]}
    },
    {
        "id": "data_scientist",
        "name": "Data Analyst",
        "category": "Technology",
        "color_scheme": {"primary": "#1E3A8A", "secondary": "#475569", "text": "#1E293B", "accent": "#3B82F6", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications"]}
    },
    {
        "id": "ai_engineer",
        "name": "Neural AI Specialist",
        "category": "Technology",
        "color_scheme": {"primary": "#312E81", "secondary": "#4F46E5", "text": "#111827", "accent": "#F59E0B", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "skills", "experience", "projects", "education", "certifications"]}
    },
    {
        "id": "devops",
        "name": "Site Reliability DevOps",
        "category": "Technology",
        "color_scheme": {"primary": "#4C1D95", "secondary": "#6D28D9", "text": "#1F2937", "accent": "#8B5CF6", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "skills", "experience", "projects", "education"]}
    },
    {
        "id": "cloud_engineer",
        "name": "Cloud Systems Architect",
        "category": "Technology",
        "color_scheme": {"primary": "#0369A1", "secondary": "#0284C7", "text": "#0F172A", "accent": "#0EA5E9", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications"]}
    },
    {
        "id": "cybersecurity",
        "name": "SecOps Consultant",
        "category": "Technology",
        "color_scheme": {"primary": "#065F46", "secondary": "#047857", "text": "#111827", "accent": "#10B981", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "monospace", "margins": "0.65in", "headerStyle": "left", "section_order": ["summary", "skills", "experience", "projects", "education", "certifications"]}
    },
    # CREATIVE CATEGORY
    {
        "id": "ui_ux",
        "name": "Design Portfolio",
        "category": "Creative",
        "color_scheme": {"primary": "#6B21A8", "secondary": "#DB2777", "text": "#1F2937", "accent": "#F472B6", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.5in", "headerStyle": "banner", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "achievements"]}
    },
    {
        "id": "graphic_designer",
        "name": "Bold Art Studio",
        "category": "Creative",
        "color_scheme": {"primary": "#C2410C", "secondary": "#1E293B", "text": "#0F172A", "accent": "#EA580C", "background": "#FFFFFF"},
        "layout_schema": {"structure": "single-column", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "projects", "experience", "education", "skills"]}
    },
    {
        "id": "marketing",
        "name": "Growth Strategist",
        "category": "Creative",
        "color_scheme": {"primary": "#BE185D", "secondary": "#475569", "text": "#1E293B", "accent": "#F43F5E", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-right", "fontFamily": "sans-serif", "margins": "0.6in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "certifications"]}
    },
    {
        "id": "content_creator",
        "name": "Social Media Hub",
        "category": "Creative",
        "color_scheme": {"primary": "#1D4ED8", "secondary": "#2563EB", "text": "#1E293B", "accent": "#F59E0B", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-left", "fontFamily": "sans-serif", "margins": "0.55in", "headerStyle": "left", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education"]}
    },
    {
        "id": "photographer",
        "name": "Minimalist Frame",
        "category": "Creative",
        "color_scheme": {"primary": "#1F2937", "secondary": "#4B5563", "text": "#111827", "accent": "#78350F", "background": "#FCFBF7"},
        "layout_schema": {"structure": "single-column", "fontFamily": "serif", "margins": "0.8in", "headerStyle": "centered", "section_order": ["summary", "projects", "experience", "education"]}
    },
    {
        "id": "creative_director",
        "name": "Avant-Garde Lead",
        "category": "Creative",
        "color_scheme": {"primary": "#000000", "secondary": "#111827", "text": "#222222", "accent": "#FBBF24", "background": "#FFFFFF"},
        "layout_schema": {"structure": "two-column-right", "fontFamily": "sans-serif", "margins": "0.5in", "headerStyle": "banner", "section_order": ["summary", "experience", "projects"], "sidebarSections": ["skills", "education", "achievements"]}
    }
]

RULES_DATA = [
    {
        "category": "verbs",
        "rule_name": "Use Strong Action Verbs",
        "rule_description": "Bullet points must start with powerful verbs (e.g., Developed, Spearheaded, Implemented) to demonstrate initiative.",
        "rule_prompt_instruction": "Ensure all bullet points for work experiences begin with a strong action verb in the past tense (or present tense for current job). Avoid generic verbs like 'helped', 'worked', or 'was responsible for'."
    },
    {
        "category": "quantify",
        "rule_name": "Quantify Achievements",
        "rule_description": "Use metrics, growth percentages, and dollar amounts to back up success statements.",
        "rule_prompt_instruction": "Quantify outcomes where possible. If a task mentions working on a project, explain the scale (e.g., 'supporting 10k+ users', 'speeding up performance by 30%', or 'generating $50k in revenue')."
    },
    {
        "category": "first_person",
        "rule_name": "Avoid First-Person Pronouns",
        "rule_description": "Never use 'I', 'me', 'my', 'we' in resume bullet points or professional summaries.",
        "rule_prompt_instruction": "Eliminate first-person pronouns completely. Instead of 'I designed a database', write 'Designed a database'."
    },
    {
        "category": "punctuation",
        "rule_name": "Consistent Punctuation",
        "rule_description": "Use a consistent standard of trailing punctuation (periods or semicolons) at the end of lists.",
        "rule_prompt_instruction": "End every experience bullet point with a period. Ensure summary paragraphs are properly punctuated with standard sentence structures."
    },
    {
        "category": "ats",
        "rule_name": "ATS Section Standard",
        "rule_description": "Ensure clear segment headers for easy parsing.",
        "rule_prompt_instruction": "Ensure clear, standard section headings (Education, Experience, Projects, Skills) and avoid obscure custom section titles."
    }
]

def seed_db():
    db: Session = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("Database tables verified.")

        # Seed Templates
        for t_info in TEMPLATES_DATA:
            existing = db.query(Template).filter(Template.id == t_info["id"]).first()
            if not existing:
                template = Template(
                    id=t_info["id"],
                    name=t_info["name"],
                    category=t_info["category"],
                    color_scheme=t_info["color_scheme"],
                    layout_schema=t_info["layout_schema"]
                )
                db.add(template)
                print(f"Seeding template: {t_info['name']}")
        
        # Seed Rules
        for r_info in RULES_DATA:
            existing = db.query(ResumeRule).filter(ResumeRule.rule_name == r_info["rule_name"]).first()
            if not existing:
                rule = ResumeRule(
                    category=r_info["category"],
                    rule_name=r_info["rule_name"],
                    rule_description=r_info["rule_description"],
                    rule_prompt_instruction=r_info["rule_prompt_instruction"],
                    is_active=True
                )
                db.add(rule)
                print(f"Seeding rule: {r_info['rule_name']}")
        
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
