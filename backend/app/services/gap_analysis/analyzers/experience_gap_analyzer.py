"""Experience Gap Analyzer.

Compares experience requirements from opportunity against resume experience.
"""
from typing import Any, Dict, List, Optional


class ExperienceGapAnalyzer:
    """Analyzes experience gaps between opportunity requirements and resume."""

    def analyze(
        self,
        required_years: Optional[int],
        required_roles: List[str],
        required_responsibilities: List[str],
        resume_experience: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze experience gaps.

        Args:
            required_years: Minimum years of experience required.
            required_roles: Roles required or preferred by the opportunity.
            required_responsibilities: Key responsibilities mentioned.
            resume_experience: Resume experience summary.

        Returns:
            Dictionary with years analysis, role analysis, and score.
        """
        result = {
            "years": self._analyze_years(required_years, resume_experience.get("total_years", 0)),
            "roles": self._analyze_roles(required_roles, resume_experience.get("roles", [])),
            "responsibilities": self._analyze_responsibilities(
                required_responsibilities,
                resume_experience.get("responsibilities", []),
            ),
        }

        scores = []
        if required_years is not None:
            scores.append(result["years"]["score"])
        if required_roles:
            scores.append(result["roles"]["score"])
        if required_responsibilities:
            scores.append(result["responsibilities"]["score"])

        result["score"] = round(sum(scores) / len(scores), 2) if scores else 1.0

        return result

    def _analyze_years(
        self, required: Optional[int], actual: int
    ) -> Dict[str, Any]:
        """Analyze years of experience."""
        if required is None:
            return {
                "required": None,
                "actual": actual,
                "sufficient": True,
                "deficit": 0,
                "score": 1.0,
            }

        sufficient = actual >= required
        deficit = max(0, required - actual)

        if sufficient:
            score = 1.0
        elif deficit <= 1:
            score = 0.8
        elif deficit <= 2:
            score = 0.5
        else:
            score = 0.2

        return {
            "required": required,
            "actual": actual,
            "sufficient": sufficient,
            "deficit": deficit,
            "score": score,
        }

    def _analyze_roles(
        self, required_roles: List[str], resume_roles: List[str]
    ) -> Dict[str, Any]:
        """Analyze role matches."""
        required_norm = {r.lower().strip() for r in required_roles if r}
        resume_norm = {r.lower().strip() for r in resume_roles if r}

        matched = set()
        for req in required_norm:
            for res in resume_norm:
                if req in res or res in req:
                    matched.add(req)
                    break

        missing = required_norm - matched

        score = len(matched) / len(required_norm) if required_norm else 1.0

        return {
            "required": sorted(list(required_norm)),
            "matched": sorted(list(matched)),
            "missing": sorted(list(missing)),
            "score": round(score, 2),
        }

    def _analyze_responsibilities(
        self, required: List[str], resume_responsibilities: List[str]
    ) -> Dict[str, Any]:
        """Analyze responsibility coverage."""
        required_norm = {r.lower().strip() for r in required if r}
        resume_norm = {r.lower().strip() for r in resume_responsibilities if r}

        matched = set()
        for req in required_norm:
            for res in resume_norm:
                if req in res or res in req or self._has_keyword_overlap(req, res):
                    matched.add(req)
                    break

        missing = required_norm - matched

        score = len(matched) / len(required_norm) if required_norm else 1.0

        return {
            "matched": sorted(list(matched)),
            "missing": sorted(list(missing)),
            "score": round(score, 2),
        }

    def _has_keyword_overlap(self, text1: str, text2: str, threshold: float = 0.5) -> bool:
        """Check if two text strings have significant keyword overlap."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return False

        intersection = words1 & words2
        min_len = min(len(words1), len(words2))

        return len(intersection) / min_len >= threshold
