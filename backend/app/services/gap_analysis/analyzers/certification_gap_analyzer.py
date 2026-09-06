"""Certification Gap Analyzer.

Compares certification requirements from opportunity against resume certifications.
"""
from typing import Any, Dict, List, Optional

from app.services.gap_analysis.analyzers.base_analyzer import BaseAnalyzer


class CertificationGapAnalyzer(BaseAnalyzer):
    """Analyzes certification gaps between opportunity requirements and resume."""

    def __init__(self):
        super().__init__()
        self._synonyms = self._load_synonyms("skill_synonyms.json")

    def analyze(
        self,
        required_certifications: List[str],
        preferred_certifications: List[str],
        resume_certifications: List[str],
    ) -> Dict[str, Any]:
        """Analyze certification gaps.

        Args:
            required_certifications: Certifications required by the opportunity.
            preferred_certifications: Certifications preferred by the opportunity.
            resume_certifications: Certifications the candidate has.

        Returns:
            Dictionary with required/preferred analysis and overall score.
        """
        result = {
            "required": self._analyze_certs(required_certifications, resume_certifications),
            "preferred": self._analyze_certs(preferred_certifications, resume_certifications),
        }

        scores = []
        if required_certifications:
            scores.append(result["required"]["score"])
        if preferred_certifications:
            scores.append(result["preferred"]["score"])

        result["score"] = round(sum(scores) / len(scores), 2) if scores else 1.0

        return result

    def _analyze_certs(
        self, required: List[str], available: List[str]
    ) -> Dict[str, Any]:
        """Analyze a set of certifications against available."""
        required_norm = self.normalize_items(required)
        available_norm = self.normalize_items(available)

        matched = set()
        for req in required_norm:
            for avail in available_norm:
                if req in avail or avail in req:
                    matched.add(req)
                    break
                if self._cert_equivalent(req, avail):
                    matched.add(req)
                    break

        missing = required_norm - matched

        score = self.calculate_match_score(matched, required_norm)

        return {
            "matched": sorted(list(matched)),
            "missing": sorted(list(missing)),
            "score": score,
            "total_required": len(required_norm),
            "total_matched": len(matched),
        }

    def _cert_equivalent(self, cert1: str, cert2: str) -> bool:
        """Check if two certifications are equivalent."""
        cert_groups = {
            "aws": ["amazon web services", "aws certified", "aws"],
            "azure": ["microsoft azure", "azure certified", "azure"],
            "gcp": ["google cloud platform", "google cloud", "gcp certified", "gcp"],
            "kubernetes": ["cka", "ckad", "cks", "kubernetes certified"],
            "docker": ["docker certified", "dca"],
            "pmp": ["project management professional", "pmp"],
            "comptia": ["comptia a+", "comptia network+", "comptia security+", "comptia"],
        }

        for group_name, variants in cert_groups.items():
            if cert1 in variants and cert2 in variants:
                return True
            if cert1 == group_name and any(cert2.startswith(v.split()[0]) for v in variants):
                return True
            if cert2 == group_name and any(cert1.startswith(v.split()[0]) for v in variants):
                return True

        return False

    def get_all_certifications(self, resume_certs: List[str]) -> List[str]:
        """Return all certifications as a flat list."""
        return [c for c in resume_certs if c]
