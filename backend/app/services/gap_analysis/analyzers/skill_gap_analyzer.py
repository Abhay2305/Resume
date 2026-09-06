"""Skill Gap Analyzer.

Compares required/preferred skills from opportunity against resume skills.
"""
from typing import Any, Dict, List, Optional

from app.services.gap_analysis.analyzers.base_analyzer import BaseAnalyzer


class SkillGapAnalyzer(BaseAnalyzer):
    """Analyzes skill gaps between opportunity requirements and resume."""

    def __init__(self):
        super().__init__()
        self._synonyms_raw = self._load_synonyms("skill_synonyms.json")
        self._synonyms = self._flatten_synonyms(self._synonyms_raw)

    def _flatten_synonyms(self, data: Dict) -> Dict[str, List[str]]:
        """Flatten nested synonym dictionary into flat {name: [synonyms]} format."""
        flat = {}
        for category, groups in data.items():
            if isinstance(groups, dict):
                for group_name, synonyms in groups.items():
                    flat[group_name] = synonyms
            elif isinstance(groups, list):
                flat[category] = groups
        return flat

    def analyze(
        self,
        required_skills: List[str],
        preferred_skills: List[str],
        resume_skills: List[str],
    ) -> Dict[str, Any]:
        """Analyze skill gaps.

        Args:
            required_skills: Skills required by the opportunity.
            preferred_skills: Skills preferred by the opportunity.
            resume_skills: Skills the candidate has.

        Returns:
            Dictionary with required/preferred analysis results.
        """
        result = {
            "required": self._analyze_skills(required_skills, resume_skills),
            "preferred": self._analyze_skills(preferred_skills, resume_skills),
        }

        result["score"] = self._calculate_weighted_score(
            result["required"]["score"],
            result["preferred"]["score"],
            len(required_skills),
            len(preferred_skills),
        )

        return result

    def _analyze_skills(
        self, required: List[str], available: List[str]
    ) -> Dict[str, Any]:
        """Analyze a set of required skills against available."""
        required_norm = self.normalize_items(required)
        available_norm = self.normalize_items(available)

        matched_exact, missing_exact = self.exact_match(required_norm, available_norm)

        matched_syn, missing_syn, _ = self.synonym_match(
            missing_exact, available_norm, self._synonyms
        )

        all_matched = matched_exact | matched_syn

        extra = available_norm - required_norm

        score = self.calculate_match_score(all_matched, required_norm)

        return {
            "matched": sorted(list(all_matched)),
            "missing": sorted(list(missing_syn)),
            "extra": sorted(list(extra)),
            "score": round(score, 2),
            "total_required": len(required_norm),
            "total_matched": len(all_matched),
        }

    def _calculate_weighted_score(
        self,
        required_score: float,
        preferred_score: float,
        required_count: int,
        preferred_count: int,
    ) -> float:
        """Calculate weighted score (required skills weighted more)."""
        if required_count == 0 and preferred_count == 0:
            return 1.0
        if required_count == 0:
            return preferred_score
        if preferred_count == 0:
            return required_score

        total = required_count + preferred_count
        weighted = (
            (required_score * required_count * 1.5)
            + (preferred_score * preferred_count * 0.5)
        ) / (total * 1.0)

        return round(min(weighted, 1.0), 2)
