"""Recommendation Engine.

Generates deterministic recommendations from gap analysis results.
No AI involved.
"""
import json
import os
from typing import Any, Dict, List, Optional


class RecommendationEngine:
    """Generates deterministic recommendations from gap analysis results."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """Load recommendation templates."""
        filepath = os.path.join(self.data_dir, "recommendation_templates.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate(
        self,
        gap_results: Dict[str, Any],
        resume_knowledge: Dict[str, Any],
        opportunity_entities: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate recommendations from gap analysis results.

        Args:
            gap_results: Results from GapAnalyzerOrchestrator.analyze().
            resume_knowledge: Structured Resume Knowledge.
            opportunity_entities: Extracted opportunity entities.

        Returns:
            List of recommendation dictionaries.
        """
        recommendations = []

        recommendations.extend(self._skill_recommendations(gap_results.get("skills", {})))
        recommendations.extend(self._technology_recommendations(gap_results.get("technology", {})))
        recommendations.extend(self._experience_recommendations(gap_results.get("experience", {})))
        recommendations.extend(self._education_recommendations(gap_results.get("education", {})))
        recommendations.extend(self._certification_recommendations(gap_results.get("certifications", {})))
        recommendations.extend(self._keyword_recommendations(gap_results.get("keywords", {})))
        recommendations.extend(self._general_recommendations(resume_knowledge, gap_results))

        return self._deduplicate_recommendations(recommendations)

    def _skill_recommendations(self, skill_results: Dict) -> List[Dict[str, Any]]:
        """Generate skill-related recommendations."""
        recs = []

        required = skill_results.get("required", {})
        for skill in required.get("missing", []):
            recs.append({
                "category": "skills",
                "priority": "high",
                "action": "add_skill",
                "description": f"Add '{skill}' to your skills section",
                "target_item": skill,
            })

        preferred = skill_results.get("preferred", {})
        for skill in preferred.get("missing", []):
            recs.append({
                "category": "skills",
                "priority": "medium",
                "action": "add_skill",
                "description": f"Consider adding '{skill}' to your skills section",
                "target_item": skill,
            })

        matched = required.get("matched", [])
        if matched:
            top_skills = matched[:3]
            recs.append({
                "category": "skills",
                "priority": "medium",
                "action": "highlight_skill",
                "description": f"Highlight your {', '.join(top_skills)} experience prominently",
                "target_item": ", ".join(top_skills),
            })

        return recs

    def _technology_recommendations(self, tech_results: Dict) -> List[Dict[str, Any]]:
        """Generate technology-related recommendations."""
        recs = []

        categories = tech_results.get("categories", {})
        for category, data in categories.items():
            for tech in data.get("missing", []):
                priority = "high" if data.get("score", 1.0) < 0.5 else "medium"
                recs.append({
                    "category": "technologies",
                    "priority": priority,
                    "action": "add_technology",
                    "description": f"Add '{tech}' experience to your resume",
                    "target_item": tech,
                })

        return recs

    def _experience_recommendations(self, exp_results: Dict) -> List[Dict[str, Any]]:
        """Generate experience-related recommendations."""
        recs = []

        years = exp_results.get("years", {})
        if not years.get("sufficient", True):
            deficit = years.get("deficit", 0)
            recs.append({
                "category": "experience",
                "priority": "high",
                "action": "highlight_experience",
                "description": f"The role requires {years.get('required', 0)} years; you have {years.get('actual', 0)} years. Highlight all relevant experience.",
                "target_item": "experience",
            })

        roles = exp_results.get("roles", {})
        for role in roles.get("missing", []):
            recs.append({
                "category": "experience",
                "priority": "medium",
                "action": "highlight_experience",
                "description": f"Highlight your '{role}' experience more prominently",
                "target_item": role,
            })

        return recs

    def _education_recommendations(self, edu_results: Dict) -> List[Dict[str, Any]]:
        """Generate education-related recommendations."""
        recs = []

        degree = edu_results.get("degree", {})
        if not degree.get("sufficient", True):
            recs.append({
                "category": "education",
                "priority": "high",
                "action": "add_education",
                "description": f"The role requires a {degree.get('required', '')} degree",
                "target_item": degree.get("required", ""),
            })

        field = edu_results.get("field", {})
        if not field.get("match", True):
            recs.append({
                "category": "education",
                "priority": "medium",
                "action": "add_education",
                "description": f"Add your '{field.get('required', '')}' educational background",
                "target_item": field.get("required", ""),
            })

        return recs

    def _certification_recommendations(self, cert_results: Dict) -> List[Dict[str, Any]]:
        """Generate certification-related recommendations."""
        recs = []

        required = cert_results.get("required", {})
        for cert in required.get("missing", []):
            recs.append({
                "category": "certifications",
                "priority": "high",
                "action": "add_certification",
                "description": f"Obtain '{cert}' certification",
                "target_item": cert,
            })

        preferred = cert_results.get("preferred", {})
        for cert in preferred.get("missing", []):
            recs.append({
                "category": "certifications",
                "priority": "medium",
                "action": "add_certification",
                "description": f"Consider obtaining '{cert}' certification",
                "target_item": cert,
            })

        return recs

    def _keyword_recommendations(self, kw_results: Dict) -> List[Dict[str, Any]]:
        """Generate keyword-related recommendations."""
        recs = []

        for keyword in kw_results.get("missing", []):
            recs.append({
                "category": "keywords",
                "priority": "medium",
                "action": "add_keyword",
                "description": f"Add '{keyword}' to your resume for ATS optimization",
                "target_item": keyword,
            })

        for keyword in kw_results.get("weak", []):
            recs.append({
                "category": "keywords",
                "priority": "low",
                "action": "enhance_keyword",
                "description": f"Increase mentions of '{keyword}' in your resume",
                "target_item": keyword,
            })

        return recs

    def _general_recommendations(
        self, resume_knowledge: Dict, gap_results: Dict
    ) -> List[Dict[str, Any]]:
        """Generate general recommendations."""
        recs = []

        summary = resume_knowledge.get("summary", "")
        if not summary or len(summary) < 50:
            recs.append({
                "category": "summary",
                "priority": "high",
                "action": "rewrite_summary",
                "description": "Rewrite your summary to better align with this role",
                "target_item": "summary",
            })

        projects = resume_knowledge.get("projects", [])
        if isinstance(projects, list):
            for project in projects:
                if isinstance(project, dict):
                    desc = project.get("description", "")
                    if desc and len(str(desc)) < 100:
                        recs.append({
                            "category": "projects",
                            "priority": "medium",
                            "action": "expand_project",
                            "description": f"Expand your '{project.get('name', 'project')}' project description",
                            "target_item": project.get("name", "project"),
                        })

        achievements = resume_knowledge.get("achievements", [])
        if not achievements or len(achievements) < 3:
            recs.append({
                "category": "achievements",
                "priority": "high",
                "action": "add_metrics",
                "description": "Add quantified metrics to your experience bullets",
                "target_item": "achievements",
            })

        overall_score = gap_results.get("skills", {}).get("score", 0)
        if overall_score < 0.5:
            recs.append({
                "category": "skills",
                "priority": "high",
                "action": "reorder_skills",
                "description": "Reorder your skills to match the job requirements",
                "target_item": "skills",
            })

        return recs

    def _deduplicate_recommendations(
        self, recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate recommendations."""
        seen = set()
        unique = []
        for rec in recommendations:
            key = (rec["category"], rec["action"], rec["target_item"])
            if key not in seen:
                seen.add(key)
                unique.append(rec)
        return unique
