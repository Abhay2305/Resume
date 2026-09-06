"""Confidence Engine.

Every change receives a Confidence Score, Supporting Gap,
Supporting Knowledge Rule, Validation Result, and Risk Level.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    """Calculates confidence scores for each change.

    Each change receives:
    - Confidence Score (0-100)
    - Supporting Gap (if applicable)
    - Supporting Knowledge Rule (if applicable)
    - Validation Result
    - Risk Level
    """

    def calculate(
        self,
        changes: List[Dict[str, Any]],
        validation_reports: Dict[str, Any],
        knowledge_rules: List[Dict[str, Any]],
        gap_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Calculate confidence scores for all changes.

        Args:
            changes: Classified changes.
            validation_reports: Validation results by validator.
            knowledge_rules: Available knowledge rules.
            gap_results: Gap analysis results.

        Returns:
            List of confidence scores with supporting evidence.
        """
        scores = []

        for change in changes:
            score = self._calculate_single_confidence(
                change, validation_reports, knowledge_rules, gap_results
            )
            scores.append(score)

        return scores

    def _calculate_single_confidence(
        self,
        change: Dict[str, Any],
        validation_reports: Dict[str, Any],
        knowledge_rules: List[Dict[str, Any]],
        gap_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calculate confidence for a single change."""
        base_score = 50.0
        reasons = []

        # Factor 1: Change type (added changes for gaps = higher confidence)
        change_type = change.get("change_type", "modified")
        category = change.get("category", "unknown")

        if change_type == "added":
            # Check if this addresses a gap
            supporting_gap = self._find_supporting_gap(category, gap_results)
            if supporting_gap:
                base_score += 20.0
                reasons.append(f"Addresses gap in {category}")
            else:
                base_score -= 5.0
                reasons.append("Added change without supporting gap")

        elif change_type == "removed":
            base_score -= 15.0
            reasons.append("Removal requires strong justification")

        elif change_type == "modified":
            supporting_gap = self._find_supporting_gap(category, gap_results)
            if supporting_gap:
                base_score += 10.0
                reasons.append(f"Modification addresses gap in {category}")

        # Factor 2: Validation results
        schema_valid = validation_reports.get("schema_valid", False)
        truth_valid = validation_reports.get("truth_valid", False)
        knowledge_valid = validation_reports.get("knowledge_valid", False)

        if schema_valid:
            base_score += 5.0
            reasons.append("Schema validation passed")
        else:
            base_score -= 10.0
            reasons.append("Schema validation failed")

        if truth_valid:
            base_score += 10.0
            reasons.append("Truth validation passed")
        else:
            base_score -= 15.0
            reasons.append("Truth validation failed")

        if knowledge_valid:
            base_score += 5.0
            reasons.append("Knowledge validation passed")

        # Factor 3: Supporting knowledge rule
        supporting_rule = self._find_supporting_rule(category, knowledge_rules)
        if supporting_rule:
            base_score += 10.0
            reasons.append(f"Supported by rule: {supporting_rule.get('rule_key')}")

        # Factor 4: Risk level
        risk_level = change.get("risk_level", "medium")
        if risk_level == "low":
            base_score += 5.0
        elif risk_level == "high":
            base_score -= 10.0
        elif risk_level == "critical":
            base_score -= 20.0

        # Clamp score
        score = max(0.0, min(100.0, base_score))

        # Determine overall risk level
        if score >= 80:
            overall_risk = "low"
        elif score >= 60:
            overall_risk = "medium"
        elif score >= 40:
            overall_risk = "high"
        else:
            overall_risk = "critical"

        return {
            "change_description": change.get("description", ""),
            "category": category,
            "change_type": change_type,
            "score": round(score, 2),
            "risk_level": overall_risk,
            "supporting_gap_id": change.get("supporting_gap_id"),
            "supporting_rule_id": supporting_rule.get("rule_key") if supporting_rule else None,
            "supporting_rule_source": supporting_rule.get("source") if supporting_rule else None,
            "validation_result": {
                "schema_valid": schema_valid,
                "truth_valid": truth_valid,
                "knowledge_valid": knowledge_valid,
            },
            "reasons": reasons,
        }

    def _find_supporting_gap(
        self,
        category: str,
        gap_results: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Find a gap result supporting this category."""
        for gap in gap_results:
            if gap.get("category") == category and gap.get("missing_items"):
                return gap
        return None

    def _find_supporting_rule(
        self,
        category: str,
        knowledge_rules: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Find a knowledge rule supporting this category."""
        category_rule_map = {
            "summary": "summary",
            "experience": "experience",
            "skills": "skills",
            "education": "education",
            "certifications": "certifications",
            "projects": "projects",
            "achievements": "experience",
            "keywords": "ats",
        }

        target_section = category_rule_map.get(category, category)

        for rule in knowledge_rules:
            if rule.get("section_name") == target_section and rule.get("is_active", True):
                return rule

        return None

    def calculate_overall_confidence(self, scores: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence from individual scores."""
        if not scores:
            return 0.0

        total = sum(s.get("score", 0) for s in scores)
        return round(total / len(scores), 2)
