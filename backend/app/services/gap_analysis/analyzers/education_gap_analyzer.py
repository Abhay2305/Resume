"""Education Gap Analyzer.

Compares education requirements from opportunity against resume education.
"""
from typing import Any, Dict, List, Optional


class EducationGapAnalyzer:
    """Analyzes education gaps between opportunity requirements and resume."""

    DEGREE_LEVELS = {
        "high school": 1,
        "diploma": 2,
        "associate": 3,
        "bachelor": 4,
        "bachelor's": 4,
        "bs": 4,
        "bsc": 4,
        "beng": 4,
        "master": 5,
        "master's": 5,
        "ms": 5,
        "msc": 5,
        "mba": 5,
        "ma": 5,
        "phd": 6,
        "doctorate": 6,
        "doctoral": 6,
    }

    def analyze(
        self,
        required_degree: Optional[str],
        required_field: Optional[str],
        resume_education: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze education gaps.

        Args:
            required_degree: Degree level required (e.g., "Bachelor's", "Master's").
            required_field: Field of study required (e.g., "Computer Science").
            resume_education: Resume education summary.

        Returns:
            Dictionary with degree and field analysis.
        """
        result = {
            "degree": self._analyze_degree(required_degree, resume_education.get("degrees", [])),
            "field": self._analyze_field(required_field, resume_education.get("fields_of_study", [])),
        }

        scores = []
        if required_degree:
            scores.append(result["degree"]["score"])
        if required_field:
            scores.append(result["field"]["score"])

        result["score"] = round(sum(scores) / len(scores), 2) if scores else 1.0

        return result

    def _get_degree_level(self, degree: str) -> int:
        """Convert degree string to numeric level."""
        degree_lower = degree.lower().strip()
        for key, level in self.DEGREE_LEVELS.items():
            if key in degree_lower:
                return level
        return 0

    def _analyze_degree(
        self, required: Optional[str], resume_degrees: List[str]
    ) -> Dict[str, Any]:
        """Analyze degree requirement."""
        if not required:
            return {
                "required": None,
                "resume_degrees": resume_degrees,
                "sufficient": True,
                "score": 1.0,
            }

        required_level = self._get_degree_level(required)
        resume_levels = [self._get_degree_level(d) for d in resume_degrees if d]
        max_resume_level = max(resume_levels) if resume_levels else 0

        sufficient = max_resume_level >= required_level if required_level > 0 else True

        if sufficient:
            score = 1.0
        elif max_resume_level >= required_level - 1:
            score = 0.7
        else:
            score = 0.3

        return {
            "required": required,
            "required_level": required_level,
            "resume_degrees": resume_degrees,
            "max_resume_level": max_resume_level,
            "sufficient": sufficient,
            "score": score,
        }

    def _analyze_field(
        self, required: Optional[str], resume_fields: List[str]
    ) -> Dict[str, Any]:
        """Analyze field of study requirement."""
        if not required:
            return {
                "required": None,
                "resume_fields": resume_fields,
                "match": True,
                "score": 1.0,
            }

        required_norm = required.lower().strip()
        resume_fields_norm = [f.lower().strip() for f in resume_fields if f]

        match = False
        for field in resume_fields_norm:
            if required_norm in field or field in required_norm:
                match = True
                break
            if self._has_field_overlap(required_norm, field):
                match = True
                break

        score = 1.0 if match else 0.5

        return {
            "required": required,
            "resume_fields": resume_fields,
            "match": match,
            "score": score,
        }

    def _has_field_overlap(self, field1: str, field2: str) -> bool:
        """Check if two fields have significant overlap."""
        words1 = set(field1.split())
        words2 = set(field2.split())

        if not words1 or not words2:
            return False

        intersection = words1 & words2
        return len(intersection) / min(len(words1), len(words2)) >= 0.5
