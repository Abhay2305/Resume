"""Technology Gap Analyzer.

Compares required technologies from opportunity against resume technologies.
"""
from typing import Any, Dict, List, Optional

from app.services.gap_analysis.analyzers.base_analyzer import BaseAnalyzer


class TechnologyGapAnalyzer(BaseAnalyzer):
    """Analyzes technology gaps between opportunity requirements and resume."""

    def __init__(self):
        super().__init__()
        self._synonyms = self._load_synonyms("technology_synonyms.json")

    def analyze(
        self,
        required_technologies: Dict[str, List[str]],
        resume_technologies: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """Analyze technology gaps by category.

        Args:
            required_technologies: Technologies required by opportunity, grouped by category.
                Example: {"frontend": ["React", "Vue"], "backend": ["Node"], "database": ["PostgreSQL"]}
            resume_technologies: Technologies the candidate has, grouped by category.

        Returns:
            Dictionary with per-category analysis and overall score.
        """
        result = {
            "categories": {},
            "score": 0.0,
            "total_required": 0,
            "total_matched": 0,
        }

        all_categories = set(required_technologies.keys()) | set(resume_technologies.keys())
        scores = []

        for category in all_categories:
            required = required_technologies.get(category, [])
            available = resume_technologies.get(category, [])

            category_result = self._analyze_category(category, required, available)
            result["categories"][category] = category_result

            result["total_required"] += category_result["total_required"]
            result["total_matched"] += category_result["total_matched"]

            if category_result["total_required"] > 0:
                scores.append(category_result["score"])

        if scores:
            result["score"] = round(sum(scores) / len(scores), 2)
        else:
            result["score"] = 1.0

        return result

    def _analyze_category(
        self, category: str, required: List[str], available: List[str]
    ) -> Dict[str, Any]:
        """Analyze technologies within a single category."""
        required_norm = self.normalize_items(required)
        available_norm = self.normalize_items(available)

        category_synonyms = self._synonyms.get("categories", {}).get(category, {})
        synonyms_dict = {cat: syns for cat, syns in self._synonyms.get("categories", {}).items()}

        matched_exact, missing_exact = self.exact_match(required_norm, available_norm)

        matched_syn, missing_syn, _ = self.synonym_match(
            missing_exact, available_norm, synonyms_dict
        )

        all_matched = matched_exact | matched_syn

        extra = available_norm - required_norm

        score = self.calculate_match_score(all_matched, required_norm)

        return {
            "category": category,
            "matched": sorted(list(all_matched)),
            "missing": sorted(list(missing_syn)),
            "extra": sorted(list(extra)),
            "score": round(score, 2),
            "total_required": len(required_norm),
            "total_matched": len(all_matched),
        }

    def get_all_technologies(
        self, resume_technologies: Dict[str, List[str]]
    ) -> List[str]:
        """Flatten all technologies from resume into a single list."""
        all_tech = []
        for category, techs in resume_technologies.items():
            all_tech.extend(techs)
        return all_tech

    def get_required_as_list(
        self, required_technologies: Dict[str, List[str]]
    ) -> List[str]:
        """Flatten all required technologies into a single list."""
        all_tech = []
        for category, techs in required_technologies.items():
            all_tech.extend(techs)
        return all_tech
