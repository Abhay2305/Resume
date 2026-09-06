"""Context Builders.

Build context sections for prompts from various knowledge sources.
"""
import json
from typing import Any, Dict, List, Optional


class ResumeContextBuilder:
    """Builds resume context for prompts."""

    def build(self, resume_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "summary": resume_knowledge.get("summary", ""),
            "skills": resume_knowledge.get("skills", []),
            "technologies": resume_knowledge.get("technologies", {}),
            "experience": resume_knowledge.get("experience_summary", {}),
            "education": resume_knowledge.get("education_summary", {}),
            "certifications": resume_knowledge.get("certifications", []),
            "projects": resume_knowledge.get("projects", []),
            "achievements": resume_knowledge.get("achievements", []),
            "total_experience_years": resume_knowledge.get("total_experience_years", 0),
        }

    def build_text_representation(self, resume_knowledge: Dict[str, Any]) -> str:
        parts = []
        summary = resume_knowledge.get("summary", "")
        if summary:
            parts.append(f"Summary: {summary}")
        skills = resume_knowledge.get("skills", [])
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")
        return "\n".join(parts)


class OpportunityContextBuilder:
    """Builds opportunity context for prompts."""

    def build(
        self,
        opportunity_entities: List[Dict[str, Any]],
        opportunity_parsed_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        entities_by_type = {}
        for entity in opportunity_entities:
            etype = entity.get("entity_type", "unknown")
            entities_by_type.setdefault(etype, []).append(entity.get("entity_value", ""))

        parsed = opportunity_parsed_data or {}
        return {
            "entities": entities_by_type,
            "responsibilities": parsed.get("responsibilities", []),
            "benefits": parsed.get("benefits", []),
            "ats_keywords": parsed.get("ats_keywords", []),
        }


class GapContextBuilder:
    """Builds gap analysis context for prompts."""

    def build(self, gap_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "overall_match_score": gap_analysis_data.get("overall_match_score", 0),
            "skill_match_score": gap_analysis_data.get("skill_match_score", 0),
            "technology_match_score": gap_analysis_data.get("technology_match_score", 0),
            "experience_match_score": gap_analysis_data.get("experience_match_score", 0),
            "education_match_score": gap_analysis_data.get("education_match_score", 0),
            "certification_match_score": gap_analysis_data.get("certification_match_score", 0),
            "keyword_match_score": gap_analysis_data.get("keyword_match_score", 0),
            "total_gaps": gap_analysis_data.get("total_gaps", 0),
            "total_recommendations": gap_analysis_data.get("total_recommendations", 0),
        }


class KnowledgeContextBuilder:
    """Builds knowledge context for prompts. Reuses Phase 4 output."""

    def build(self, knowledge_context_data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for key in ["summary_rules", "experience_rules", "skills_rules", "education_rules",
                     "projects_rules", "certifications_rules", "ats_rules", "formatting_rules",
                     "cover_letter_rules"]:
            rules_json = knowledge_context_data.get(key, "[]")
            try:
                result[key] = json.loads(rules_json) if isinstance(rules_json, str) else rules_json
            except (json.JSONDecodeError, TypeError):
                result[key] = []
        result["citations"] = knowledge_context_data.get("citations", [])
        return result
