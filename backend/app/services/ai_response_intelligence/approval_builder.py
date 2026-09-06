"""Approval Package Builder.

Creates a structured package for frontend review.
The frontend should render this package directly.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ApprovalPackageBuilder:
    """Builds a structured approval package for frontend consumption.

    The package contains approved changes, rejected changes, warnings,
    confidence scores, supporting rules, and diff summary.
    """

    def build(
        self,
        changes: List[Dict[str, Any]],
        confidence_scores: List[Dict[str, Any]],
        validation_reports: Dict[str, Any],
        knowledge_rules: List[Dict[str, Any]],
        gap_results: List[Dict[str, Any]],
        diff_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build the approval package.

        Args:
            changes: Classified changes.
            confidence_scores: Confidence scores for each change.
            validation_reports: Validation results.
            knowledge_rules: Knowledge rules used.
            gap_results: Gap analysis results.
            diff_summary: Summary of diffs.

        Returns:
            Structured approval package.
        """
        approved_changes = []
        rejected_changes = []
        warnings = []

        for i, change in enumerate(changes):
            confidence = confidence_scores[i] if i < len(confidence_scores) else {}
            score = confidence.get("score", 50)
            risk = confidence.get("risk_level", "medium")

            change_with_confidence = {
                **change,
                "confidence_score": score,
                "confidence_risk_level": risk,
                "supporting_rule_id": confidence.get("supporting_rule_id"),
                "supporting_rule_source": confidence.get("supporting_rule_source"),
                "supporting_gap_id": confidence.get("supporting_gap_id"),
                "validation_result": confidence.get("validation_result", {}),
                "reasons": confidence.get("reasons", []),
            }

            # Auto-approve/reject based on confidence
            if score >= 70 and risk in ("low", "medium"):
                approved_changes.append(change_with_confidence)
            elif score < 40 or risk == "critical":
                rejected_changes.append(change_with_confidence)
            else:
                warnings.append(change_with_confidence)

        # Get supporting rules
        supporting_rules = self._extract_supporting_rules(
            approved_changes + warnings, knowledge_rules
        )

        # Build overall validation summary
        validation_summary = self._build_validation_summary(validation_reports)

        package = {
            "approved_changes": approved_changes,
            "rejected_changes": rejected_changes,
            "warnings": warnings,
            "confidence_scores": confidence_scores,
            "supporting_rules": supporting_rules,
            "diff_summary": diff_summary,
            "validation_summary": validation_summary,
            "overall_confidence": self._calculate_overall(confidence_scores),
            "total_changes": len(changes),
            "approved_count": len(approved_changes),
            "rejected_count": len(rejected_changes),
            "warning_count": len(warnings),
        }

        return package

    def _extract_supporting_rules(
        self,
        changes: List[Dict[str, Any]],
        knowledge_rules: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Extract knowledge rules that support the changes."""
        rule_keys = set()
        supporting = []

        for change in changes:
            rule_key = change.get("supporting_rule_id")
            if rule_key and rule_key not in rule_keys:
                rule_keys.add(rule_key)
                # Find the full rule
                for rule in knowledge_rules:
                    if rule.get("rule_key") == rule_key:
                        supporting.append({
                            "rule_key": rule.get("rule_key"),
                            "source": rule.get("source"),
                            "section_name": rule.get("section_name"),
                            "instruction": rule.get("instruction"),
                            "reason": rule.get("reason"),
                            "priority": rule.get("priority"),
                        })
                        break

        return supporting

    def _build_validation_summary(self, validation_reports: Dict[str, Any]) -> Dict[str, Any]:
        """Build summary of validation results."""
        summary = {
            "schema_valid": validation_reports.get("schema_valid", False),
            "truth_valid": validation_reports.get("truth_valid", False),
            "knowledge_valid": validation_reports.get("knowledge_valid", False),
            "gap_valid": validation_reports.get("gap_valid", False),
        }

        passed = sum(1 for v in summary.values() if v)
        total = len(summary)
        summary["pass_rate"] = round((passed / total) * 100, 2) if total > 0 else 0

        return summary

    def _calculate_overall(self, scores: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score."""
        if not scores:
            return 0.0

        total = sum(s.get("score", 0) for s in scores)
        return round(total / len(scores), 2)
