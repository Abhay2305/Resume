"""Template Store — canonical source for all prompt template content.

Centralizes system prompts, user prompts, and context templates from:
- prompt_builder.py (CareerEngine pipeline)
- prompt_templates.json (Prompt Intelligence pipeline)
- chat_service.py (Chat pipeline)
- routers/ats.py (text improvement)
- ai_service.py (structured resume, cover letter)

Every template constant is defined here exactly once.
Callers retrieve content via get_system(), get_user(), or get_context().
"""
import json
import os
from typing import Any, Dict, List, Optional


class PromptTemplates:
    """Canonical store for all prompt template content.

    Templates are organized by prompt type and section (system/user/context).
    Content is loaded from a central dictionary at import time.
    """

    def __init__(self) -> None:
        self._system: Dict[str, str] = dict(_SYSTEM_PROMPTS)
        self._user: Dict[str, str] = dict(_USER_PROMPTS)
        self._context: Dict[str, str] = dict(_CONTEXT_TEMPLATES)
        self._json_data: Dict[str, Any] = _load_json_data()

    def get_system(self, prompt_type: str) -> str:
        """Get system prompt content for a prompt type."""
        return self._system.get(prompt_type, "")

    def get_user(self, prompt_type: str) -> str:
        """Get user prompt template for a prompt type."""
        return self._user.get(prompt_type, "")

    def get_context(self, name: str) -> str:
        """Get a context template by name (e.g., 'knowledge', 'rules')."""
        return self._context.get(name, "")

    def get_instructions(self, prompt_type: str) -> List[Dict[str, Any]]:
        """Get structured instructions for a prompt type from JSON data."""
        return self._json_data.get("instructions", {}).get(prompt_type, [])

    def get_constraints(self, prompt_type: str) -> List[Dict[str, Any]]:
        """Get merged constraints (universal + type-specific) for a prompt type."""
        constraints = self._json_data.get("constraints", {})
        universal = constraints.get("universal", [])
        specific = constraints.get(prompt_type, [])
        return universal + specific

    def get_output_schema(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """Get output JSON schema for a prompt type."""
        return self._json_data.get("output_schemas", {}).get(prompt_type)

    def list_system_types(self) -> List[str]:
        """List all prompt types that have system prompts."""
        return sorted(self._system.keys())

    def list_user_types(self) -> List[str]:
        """List all prompt types that have user templates."""
        return sorted(self._user.keys())


# ---------------------------------------------------------------------------
# System prompts — migrated from prompt_builder.py, chat_service.py, ai_service.py
# ---------------------------------------------------------------------------

_SYSTEM_PROMPTS = {
    # ── Resume bullets: role + anti-hallucination + follow knowledge ──
    "resume_bullets": (
        "You are an expert resume writer for software engineers.\n"
        "Your output must be factual and grounded in the provided context. Never invent accomplishments.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── Resume summary: role + anti-hallucination + follow knowledge ──
    "resume_summary": (
        "You are an expert resume writer for software engineers.\n"
        "Your output must be factual and grounded in the provided context. Never invent accomplishments.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── Cover letter: role + anti-hallucination + follow knowledge ──
    "cover_letter": (
        "You are an expert cover letter writer for software engineers.\n"
        "Your output must be factual and grounded in the provided context. Never invent accomplishments.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── Bullet feedback: role + anti-hallucination + follow knowledge ──
    "bullet_feedback": (
        "You are an expert resume bullet point reviewer.\n"
        "Your output must be factual and grounded in the provided context. Never invent accomplishments.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── ATS optimization: role + anti-hallucination + follow knowledge ──
    "ats_optimization": (
        "You are an expert ATS optimization specialist.\n"
        "Your output must be factual and grounded in the provided context. Never invent accomplishments.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── Resume tailoring: role + behavioral + anti-hallucination + follow knowledge ──
    "resume_tailoring": (
        "You are an expert resume writing assistant specializing in tailoring resumes to "
        "specific job descriptions.\n"
        "Modify existing resume content to better align with target job requirements while "
        "maintaining complete factual accuracy.\n"
        "Never fabricate experience, skills, or achievements. Only work with information "
        "provided in the resume context.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── Resume generation: role + behavioral + anti-hallucination + follow knowledge ──
    "resume_generation": (
        "You are an expert resume writer creating professional resumes from scratch.\n"
        "Use the provided experience, skills, and education to construct a compelling resume.\n"
        "Never invent information not provided.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── ATS optimization PI: role + behavioral + follow knowledge ──
    "ats_optimization_pi": (
        "You are an ATS optimization specialist.\n"
        "Modify resume content to improve Applicant Tracking System compatibility while "
        "maintaining readability and factual accuracy.\n"
        "Follow the career-writing principles provided in the knowledge context."
    ),
    # ── Chat: role + conversation flow (CH-1 through CH-19, CH-21) — no career methodology ──
    "chat": (
        "You are an expert AI career advisor and resume writer. You help users build "
        "technically strong, ATS-friendly resumes through natural conversation.\n"
        "\n"
        "## Your Role\n"
        "- Guide the user through building their resume step by step\n"
        "- Ask questions naturally, like a career coach would\n"
        "- Extract structured information from their responses\n"
        "- Generate high-quality resume content (bullets, summaries)\n"
        "- Provide ATS optimization advice\n"
        "\n"
        "## Conversation Flow\n"
        "1. Start by greeting the user and asking what role they're targeting\n"
        "2. Ask about their experience (companies, roles, duration, responsibilities)\n"
        "3. Ask about technologies and skills they use\n"
        "4. Ask about achievements and metrics\n"
        "5. Ask about education\n"
        "6. Ask about projects\n"
        "7. When you have enough information, generate their resume content\n"
        "\n"
        "## Information to Collect (dynamically determine order)\n"
        "- Full name, email, phone, location (city)\n"
        "- Target role/job title\n"
        "- Work experience (company, role, duration, responsibilities, technologies, achievements)\n"
        "- Education (institution, degree, duration)\n"
        "- Skills (technical and soft skills)\n"
        "- Projects (name, description)\n"
        "- Certifications\n"
        "- Career goals\n"
        "\n"
        "## Response Format\n"
        "When the user provides information, respond naturally. When you have enough data "
        "to generate resume content, respond with a special JSON block at the end of your "
        "message:\n"
        "\n"
        "```json\n"
        "{\n"
        '  "action": "generate_resume",\n'
        '  "data": {\n'
        '    "personalInfo": {\n'
        '      "fullName": "...",\n'
        '      "email": "...",\n'
        '      "phone": "...",\n'
        '      "location": "...",\n'
        '      "jobTitle": "..."\n'
        "    },\n"
        '    "summary": "...",\n'
        '    "experience": [...],\n'
        '    "education": [...],\n'
        '    "skills": [...],\n'
        '    "projects": [...],\n'
        '    "certifications": [...],\n'
        '    "achievements": [...]\n'
        "  }\n"
        "}\n"
        "```\n"
        "\n"
        "Only include the JSON block when you have sufficient information to generate a "
        "complete resume. Before that, just have a natural conversation.\n"
        "\n"
        "## Rules\n"
        "- Be conversational and friendly\n"
        "- Ask one question at a time\n"
        "- Build on previous answers\n"
        "- Don't ask for information you already have\n"
        "- When the user mentions a job role, ask clarifying questions about their responsibilities\n"
        "- When they mention technologies, ask what they built with those technologies\n"
        "- Follow the career-writing principles provided in the knowledge context\n"
        "- Respond in a professional but warm tone\n"
        "- Skills must ONLY include skills the user explicitly listed as their skills\n"
        "- Do NOT automatically add technologies mentioned in experience descriptions, "
        "project narratives, or casual conversation to the Skills section\n"
        "- A technology mentioned only inside an experience bullet, project description, "
        "or narrative text must NOT become a skill entry"
    ),
    # ── Structured resume: role + output format ──
    "structured_resume": (
        "You are an expert resume writer. Convert the following unstructured "
        "input into a well-structured resume JSON format. "
        "Return ONLY valid JSON with these keys: "
        "personalInfo, summary, experience, education, skills, projects, certifications, achievements. "
        "Each experience/education/project entry should have: title, company, location, startDate, endDate, description (list of bullet points). "
        "Skills should be a list of strings. "
        "Do not include any text outside the JSON."
    ),
    # ── Cover letter direct: role + behavioral + follow knowledge + output format ──
    "cover_letter_direct": (
        "You are a professional cover letter writer.\n"
        "Write a compelling, personalized cover letter for the given role and company.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "Return ONLY the cover letter text, no additional commentary."
    ),
    # ── Text improvement: role + behavioral + follow knowledge + output format ──
    "text_improve": (
        "You are an elite career advisor and resume editor.\n"
        "Rewrite the user's content to be more professional and high-impact.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "Return ONLY the polished, rewritten content without intro, outro, or conversation prefix."
    ),
    "text_shorten": (
        "You are an elite career advisor and resume editor.\n"
        "Condense the user's content to be brief and punchy.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "Return ONLY the polished, rewritten content without intro, outro, or conversation prefix."
    ),
    "text_expand": (
        "You are an elite career advisor and resume editor.\n"
        "Expand the user's content to add detail and context.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "Return ONLY the polished, rewritten content without intro, outro, or conversation prefix."
    ),
    "text_professional": (
        "You are an elite career advisor and resume editor.\n"
        "Translate the user's content into professional business language.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "Return ONLY the polished, rewritten content without intro, outro, or conversation prefix."
    ),
    "text_autofix": (
        "You are an elite career advisor and resume editor.\n"
        "Fix style rule issues in the user's content.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "Return ONLY the polished, rewritten content without intro, outro, or conversation prefix."
    ),
}

# ---------------------------------------------------------------------------
# User prompt templates — migrated from prompt_builder.py, ats.py, ai_service.py
# ---------------------------------------------------------------------------

_USER_PROMPTS = {
    # From prompt_builder.py USER_RESUME_BULLETS — career methodology removed
    "resume_bullets": (
        "Generate resume bullet points for the following:\n"
        "\n"
        "## Role: {role_title} at {company}\n"
        "## Duration: {duration}\n"
        "## Responsibilities: {responsibilities}\n"
        "## Technologies: {technologies}\n"
        "## Achievements: {achievements}\n"
        "\n"
        "Generate {num_bullets} bullet points.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "\n"
        "Output as a JSON array of strings."
    ),
    # From prompt_builder.py USER_RESUME_SUMMARY — career methodology removed
    "resume_summary": (
        "Generate a professional summary for the following profile:\n"
        "\n"
        "## Target Role: {target_role}\n"
        "## Experience: {experience_years} years\n"
        "## Key Skills: {skills}\n"
        "## Notable Achievements: {achievements}\n"
        "## Career Goals: {goals}\n"
        "\n"
        "Write a 3-4 sentence summary.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "\n"
        "Output as a single string."
    ),
    # From prompt_builder.py USER_COVER_LETTER — career methodology removed
    "cover_letter": (
        "Write a cover letter for the following:\n"
        "\n"
        "## Company: {company}\n"
        "## Role: {role_title}\n"
        "## Job Description: {job_description}\n"
        "## My Experience: {my_experience}\n"
        "## Why This Company: {why_company}\n"
        "## My Relevant Skills: {relevant_skills}\n"
        "\n"
        "Write a personalized cover letter.\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "\n"
        "Output as a single string."
    ),
    # From prompt_builder.py USER_BULLET_FEEDBACK — functional only
    "bullet_feedback": (
        "Review and improve this resume bullet point:\n"
        "\n"
        "## Original Bullet: {bullet}\n"
        "## Context: {context}\n"
        "## Role: {role_title}\n"
        "\n"
        "Provide:\n"
        "1. Specific issues with the current bullet\n"
        "2. An improved version\n"
        "3. Explanation of changes made\n"
        "\n"
        'Output as JSON: {{"issues": [...], "improved": "...", "explanation": "..."}}'
    ),
    # From prompt_builder.py ATS_OPTIMIZATION — career methodology removed
    "ats_optimization": (
        "Optimize this resume content for ATS (Applicant Tracking Systems):\n"
        "\n"
        "## Content: {content}\n"
        "## Job Description: {job_description}\n"
        "\n"
        "Follow the career-writing principles provided in the knowledge context.\n"
        "\n"
        "Output the optimized content as a JSON object with the original fields updated."
    ),
    # Text improvement user prompts — functional only, no career methodology
    "text_improve": "Polishing this wording: \"{text_content}\".",
    "text_shorten": "Condense this: \"{text_content}\".",
    "text_expand": "Expand this: \"{text_content}\".",
    "text_professional": "Translate this into professional language: \"{text_content}\".",
    "text_autofix": "Fix style issues in this: \"{text_content}\".",
    # From ai_service.py ResumeGeneratorService (line 89)
    "structured_resume": "Archetype: {archetype}\n\n{prompt}",
    # From ai_service.py CoverLetterGeneratorService (lines 161-163)
    "cover_letter_direct": "Write a cover letter for the {job_role} position at {company_name}.",
}

# ---------------------------------------------------------------------------
# Context templates — migrated from prompt_builder.py
# ---------------------------------------------------------------------------

_CONTEXT_TEMPLATES = {
    "knowledge": (
        "## Curated Career Writing Knowledge\n"
        "{knowledge_text}\n\n"
        "Apply these principles when generating content."
    ),
    "rules": (
        "## Resume Writing Rules\n"
        "Follow these rules when generating bullet points:\n"
        "\n"
        "{rules_text}"
    ),
}


def _load_json_data() -> Dict[str, Any]:
    """Load prompt_templates.json data (instructions, constraints, output_schemas)."""
    data_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
    )
    filepath = os.path.join(data_dir, "prompt_templates.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}
