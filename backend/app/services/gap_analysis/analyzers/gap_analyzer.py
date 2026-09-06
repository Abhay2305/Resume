"""Gap Analyzer Orchestrator.

Coordinates all individual analyzers and produces unified gap results.
"""
from typing import Any, Dict, List, Optional

from app.services.gap_analysis.analyzers.skill_gap_analyzer import SkillGapAnalyzer
from app.services.gap_analysis.analyzers.technology_gap_analyzer import TechnologyGapAnalyzer
from app.services.gap_analysis.analyzers.experience_gap_analyzer import ExperienceGapAnalyzer
from app.services.gap_analysis.analyzers.education_gap_analyzer import EducationGapAnalyzer
from app.services.gap_analysis.analyzers.certification_gap_analyzer import CertificationGapAnalyzer
from app.services.gap_analysis.analyzers.keyword_gap_analyzer import KeywordGapAnalyzer


class GapAnalyzerOrchestrator:
    """Orchestrates all gap analyzers and produces unified results."""

    def __init__(self):
        self.skill_analyzer = SkillGapAnalyzer()
        self.technology_analyzer = TechnologyGapAnalyzer()
        self.experience_analyzer = ExperienceGapAnalyzer()
        self.education_analyzer = EducationGapAnalyzer()
        self.certification_analyzer = CertificationGapAnalyzer()
        self.keyword_analyzer = KeywordGapAnalyzer()

    def analyze(
        self,
        resume_knowledge: Dict[str, Any],
        opportunity_entities: List[Dict[str, Any]],
        opportunity_parsed_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run full gap analysis.

        Args:
            resume_knowledge: Structured Resume Knowledge.
            opportunity_entities: Extracted opportunity entities.
            opportunity_parsed_data: Parsed opportunity data (optional).

        Returns:
            Dictionary with results from all analyzers.
        """
        resume_skills = resume_knowledge.get("skills", [])
        resume_technologies = resume_knowledge.get("technologies", {})
        resume_experience = self._extract_experience(resume_knowledge)
        resume_education = self._extract_education(resume_knowledge)
        resume_certifications = resume_knowledge.get("certifications", [])
        resume_summary = resume_knowledge.get("summary", "")
        resume_text = self._build_resume_text(resume_knowledge)

        required_skills, preferred_skills = self._extract_skills_from_entities(opportunity_entities)
        required_technologies = self._extract_technologies_from_entities(opportunity_entities)
        experience_info = self._extract_experience_from_entities(opportunity_entities)
        education_info = self._extract_education_from_entities(opportunity_entities)
        required_certs, preferred_certs = self._extract_certs_from_entities(opportunity_entities)
        ats_keywords = self._extract_ats_keywords(opportunity_parsed_data)

        results = {
            "skills": self.skill_analyzer.analyze(
                required_skills, preferred_skills, resume_skills
            ),
            "technology": self.technology_analyzer.analyze(
                required_technologies, resume_technologies
            ),
            "experience": self.experience_analyzer.analyze(
                experience_info.get("required_years"),
                experience_info.get("required_roles", []),
                experience_info.get("responsibilities", []),
                resume_experience,
            ),
            "education": self.education_analyzer.analyze(
                education_info.get("required_degree"),
                education_info.get("required_field"),
                resume_education,
            ),
            "certifications": self.certification_analyzer.analyze(
                required_certs, preferred_certs, resume_certifications
            ),
            "keywords": self.keyword_analyzer.analyze(
                ats_keywords, resume_text, resume_summary
            ),
        }

        return results

    def _extract_experience(self, knowledge: Dict) -> Dict[str, Any]:
        """Extract experience data from resume knowledge."""
        exp_summary = knowledge.get("experience_summary", {})
        roles = []
        if isinstance(exp_summary, dict):
            entries = exp_summary.get("entries", [])
            roles = [e.get("role", "") for e in entries if isinstance(e, dict)]
        elif isinstance(exp_summary, list):
            roles = [e.get("role", "") for e in exp_summary if isinstance(e, dict)]

        return {
            "total_years": knowledge.get("total_experience_years", 0),
            "roles": roles,
            "responsibilities": [],
        }

    def _extract_education(self, knowledge: Dict) -> Dict[str, Any]:
        """Extract education data from resume knowledge."""
        edu_summary = knowledge.get("education_summary", {})
        degrees = []
        fields = []
        institutions = []

        if isinstance(edu_summary, dict):
            degrees = edu_summary.get("degrees", [])
            fields = edu_summary.get("fields_of_study", [])
            institutions = edu_summary.get("institutions", [])
        elif isinstance(edu_summary, list):
            for entry in edu_summary:
                if isinstance(entry, dict):
                    degrees.extend(entry.get("degrees", []))
                    fields.extend(entry.get("fields_of_study", []))
                    institutions.extend(entry.get("institutions", []))

        return {
            "degrees": degrees,
            "fields_of_study": fields,
            "institutions": institutions,
        }

    def _extract_skills_from_entities(
        self, entities: List[Dict]
    ) -> tuple:
        """Extract required and preferred skills from opportunity entities."""
        required = []
        preferred = []
        for entity in entities:
            if entity.get("entity_type") == "skill":
                if entity.get("is_required", True):
                    required.append(entity["entity_value"])
                else:
                    preferred.append(entity["entity_value"])
        return required, preferred

    def _extract_technologies_from_entities(
        self, entities: List[Dict]
    ) -> Dict[str, List[str]]:
        """Extract technologies from opportunity entities by category."""
        tech_categories = {
            "technology": "general",
            "framework": "frontend",
            "language": "backend",
            "database": "database",
            "cloud_platform": "cloud",
            "devops_tool": "devops",
            "ai_ml": "ai_ml",
        }

        result = {}
        for entity in entities:
            entity_type = entity.get("entity_type", "")
            if entity_type in tech_categories:
                category = tech_categories[entity_type]
                if category not in result:
                    result[category] = []
                result[category].append(entity["entity_value"])

        return result

    def _extract_experience_from_entities(
        self, entities: List[Dict]
    ) -> Dict[str, Any]:
        """Extract experience requirements from opportunity entities."""
        required_years = None
        required_roles = []
        responsibilities = []

        for entity in entities:
            etype = entity.get("entity_type", "")
            evalue = entity.get("entity_value", "")
            metadata = entity.get("entity_metadata", {})

            if etype == "experience_level":
                if "years" in str(metadata).lower():
                    try:
                        years_str = str(metadata.get("years", evalue))
                        required_years = int("".join(filter(str.isdigit, years_str)))
                    except (ValueError, TypeError):
                        pass
            elif etype == "role":
                required_roles.append(evalue)
            elif etype == "responsibility":
                responsibilities.append(evalue)

        return {
            "required_years": required_years,
            "required_roles": required_roles,
            "responsibilities": responsibilities,
        }

    def _extract_education_from_entities(
        self, entities: List[Dict]
    ) -> Dict[str, Any]:
        """Extract education requirements from opportunity entities."""
        required_degree = None
        required_field = None

        for entity in entities:
            etype = entity.get("entity_type", "")
            evalue = entity.get("entity_value", "")

            if etype == "education":
                if not required_degree:
                    required_degree = evalue
                elif not required_field:
                    required_field = evalue

        return {
            "required_degree": required_degree,
            "required_field": required_field,
        }

    def _extract_certs_from_entities(
        self, entities: List[Dict]
    ) -> tuple:
        """Extract required and preferred certifications from opportunity entities."""
        required = []
        preferred = []
        for entity in entities:
            if entity.get("entity_type") == "certification":
                if entity.get("is_required", True):
                    required.append(entity["entity_value"])
                else:
                    preferred.append(entity["entity_value"])
        return required, preferred

    def _extract_ats_keywords(
        self, parsed_data: Optional[Dict]
    ) -> List[str]:
        """Extract ATS keywords from parsed opportunity data."""
        if not parsed_data:
            return []
        return parsed_data.get("ats_keywords", [])

    def _build_resume_text(self, knowledge: Dict) -> str:
        """Build a text representation of the resume for keyword analysis."""
        parts = []

        summary = knowledge.get("summary", "")
        if summary:
            parts.append(summary)

        skills = knowledge.get("skills", [])
        if skills:
            parts.append(" ".join(skills))

        technologies = knowledge.get("technologies", {})
        if isinstance(technologies, dict):
            for category, techs in technologies.items():
                if isinstance(techs, list):
                    parts.append(" ".join(str(t) for t in techs))

        experience = knowledge.get("experience_summary", {})
        if isinstance(experience, dict):
            entries = experience.get("entries", [])
            for entry in entries:
                if isinstance(entry, dict):
                    parts.append(entry.get("role", ""))
                    parts.append(entry.get("company", ""))
                    parts.append(" ".join(entry.get("bullets", [])))
        elif isinstance(experience, list):
            for entry in experience:
                if isinstance(entry, dict):
                    parts.append(entry.get("role", ""))
                    parts.append(entry.get("company", ""))
                    parts.append(" ".join(entry.get("bullets", [])))

        return " ".join(parts).lower()
