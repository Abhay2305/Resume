"""Keyword Gap Analyzer.

Detects missing ATS keywords and weak keyword density.
"""
from typing import Any, Dict, List, Optional


class KeywordGapAnalyzer:
    """Analyzes keyword gaps for ATS optimization."""

    def analyze(
        self,
        ats_keywords: List[str],
        resume_text: str,
        resume_summary: str = "",
    ) -> Dict[str, Any]:
        """Analyze keyword gaps.

        Args:
            ats_keywords: Keywords from the job description.
            resume_text: Full resume text content.
            resume_summary: Resume summary text.

        Returns:
            Dictionary with keyword analysis.
        """
        resume_lower = resume_text.lower()
        summary_lower = resume_summary.lower() if resume_summary else ""

        result = {
            "found": [],
            "missing": [],
            "weak": [],
            "score": 0.0,
        }

        for keyword in ats_keywords:
            keyword_lower = keyword.lower().strip()
            if not keyword_lower:
                continue

            in_full_text = keyword_lower in resume_lower
            in_summary = keyword_lower in summary_lower

            if in_full_text or in_summary:
                count = resume_lower.count(keyword_lower) + (1 if in_summary and not in_full_text else 0)
                if count >= 3:
                    density = "strong"
                elif count >= 2:
                    density = "moderate"
                elif in_summary:
                    density = "in_summary"
                else:
                    density = "weak"

                result["found"].append({
                    "keyword": keyword,
                    "count": count,
                    "density": density,
                    "in_summary": in_summary,
                })
            else:
                result["missing"].append(keyword)

        total = len(ats_keywords)
        found_count = len(result["found"])

        result["score"] = round(found_count / total, 2) if total > 0 else 1.0

        weak_keywords = [
            item["keyword"]
            for item in result["found"]
            if item["density"] in ("weak", "moderate")
        ]
        result["weak"] = weak_keywords

        return result

    def get_missing_keywords(
        self, ats_keywords: List[str], resume_text: str
    ) -> List[str]:
        """Get only missing keywords."""
        resume_lower = resume_text.lower()
        return [
            kw for kw in ats_keywords
            if kw.lower().strip() not in resume_lower
        ]

    def get_keyword_density(
        self, resume_text: str, keywords: List[str]
    ) -> Dict[str, int]:
        """Get keyword density counts."""
        resume_lower = resume_text.lower()
        density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            if keyword_lower:
                density[keyword] = resume_lower.count(keyword_lower)
        return density
