"""Match Scorer.

Produces deterministic match scores from gap analysis results.
No AI involved.
"""
from typing import Any, Dict, Optional


class MatchScorer:
    """Produces deterministic match scores from gap analysis results."""

    WEIGHTS = {
        "skills": 0.30,
        "technology": 0.25,
        "experience": 0.20,
        "education": 0.10,
        "certifications": 0.10,
        "keywords": 0.05,
    }

    def calculate_scores(
        self, gap_results: Dict[str, Any]
    ) -> Dict[str, Optional[float]]:
        """Calculate all match scores from gap analysis results.

        Args:
            gap_results: Results from GapAnalyzerOrchestrator.analyze().

        Returns:
            Dictionary of match scores.
        """
        skill_score = gap_results.get("skills", {}).get("score", 0.0)
        tech_score = gap_results.get("technology", {}).get("score", 0.0)
        exp_score = gap_results.get("experience", {}).get("score", 0.0)
        edu_score = gap_results.get("education", {}).get("score", 0.0)
        cert_score = gap_results.get("certifications", {}).get("score", 0.0)
        kw_score = gap_results.get("keywords", {}).get("score", 0.0)

        overall = self._weighted_average(
            skill_score, tech_score, exp_score, edu_score, cert_score, kw_score
        )

        return {
            "overall_match_score": overall,
            "skill_match_score": skill_score,
            "technology_match_score": tech_score,
            "experience_match_score": exp_score,
            "education_match_score": edu_score,
            "certification_match_score": cert_score,
            "keyword_match_score": kw_score,
        }

    def _weighted_average(
        self,
        skill_score: float,
        tech_score: float,
        exp_score: float,
        edu_score: float,
        cert_score: float,
        kw_score: float,
    ) -> float:
        """Calculate weighted average of scores."""
        weighted_sum = (
            skill_score * self.WEIGHTS["skills"]
            + tech_score * self.WEIGHTS["technology"]
            + exp_score * self.WEIGHTS["experience"]
            + edu_score * self.WEIGHTS["education"]
            + cert_score * self.WEIGHTS["certifications"]
            + kw_score * self.WEIGHTS["keywords"]
        )

        return round(weighted_sum, 2)

    def get_match_level(self, score: float) -> str:
        """Get human-readable match level."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.75:
            return "good"
        elif score >= 0.5:
            return "moderate"
        elif score >= 0.25:
            return "weak"
        else:
            return "poor"
