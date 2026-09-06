"""Rule Verifier.

Checks extracted rules against existing rules for duplicates, conflicts,
and consistency. Generates verification reports.
"""
import logging
import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.8
NEAR_DUPLICATE_THRESHOLD = 0.9

CONTRADICTION_PAIRS = [
    ("always", "never"),
    ("must", "must not"),
    ("should", "should not"),
    ("include", "exclude"),
    ("use", "avoid"),
    ("start with", "do not start with"),
    ("add", "remove"),
    ("keep", "remove"),
    ("begin", "end"),
]


class RuleVerifier:
    """Verifies rules for duplicates, conflicts, and consistency."""

    def __init__(self):
        self._verification_log: List[Dict[str, Any]] = []

    def _normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"[^\w\s]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text

    def _compute_similarity(self, text1: str, text2: str) -> float:
        norm1 = self._normalize_text(text1)
        norm2 = self._normalize_text(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()

    def _detect_exact_duplicate(
        self,
        new_rule: Dict[str, Any],
        existing_rules: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        new_hash = new_rule.get("rule_hash", "")
        if not new_hash:
            return None
        for existing in existing_rules:
            if existing.get("rule_hash") == new_hash:
                return {
                    "type": "exact_duplicate",
                    "new_rule_id": new_rule.get("rule_id"),
                    "existing_rule_id": existing.get("rule_id"),
                    "rule_hash": new_hash,
                    "confidence": 1.0,
                }
        return None

    def _detect_semantic_duplicate(
        self,
        new_rule: Dict[str, Any],
        existing_rules: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        duplicates = []
        new_instruction = new_rule.get("instruction", "")
        for existing in existing_rules:
            existing_instruction = existing.get("instruction", "")
            similarity = self._compute_similarity(new_instruction, existing_instruction)
            if similarity >= SIMILARITY_THRESHOLD:
                duplicates.append({
                    "type": "semantic_duplicate",
                    "new_rule_id": new_rule.get("rule_id"),
                    "existing_rule_id": existing.get("rule_id"),
                    "similarity": round(similarity, 3),
                    "confidence": round(similarity, 3),
                })
        return duplicates

    def _detect_conflicts(
        self,
        new_rule: Dict[str, Any],
        existing_rules: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        conflicts = []
        new_instruction = new_rule.get("instruction", "").lower()
        new_section = new_rule.get("section_name", "")
        for existing in existing_rules:
            existing_instruction = existing.get("instruction", "").lower()
            existing_section = existing.get("section_name", "")
            if new_section != existing_section:
                continue
            for positive, negative in CONTRADICTION_PAIRS:
                if (positive in new_instruction and negative in existing_instruction) or \
                   (negative in new_instruction and positive in existing_instruction):
                    conflicts.append({
                        "type": "conflict",
                        "new_rule_id": new_rule.get("rule_id"),
                        "existing_rule_id": existing.get("rule_id"),
                        "section": new_section,
                        "contradiction": f"'{positive}' vs '{negative}'",
                        "confidence": 0.8,
                    })
                    break
        return conflicts

    def verify_rule(
        self,
        new_rule: Dict[str, Any],
        existing_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        issues = []
        exact = self._detect_exact_duplicate(new_rule, existing_rules)
        if exact:
            issues.append(exact)
        semantic = self._detect_semantic_duplicate(new_rule, existing_rules)
        issues.extend(semantic)
        conflicts = self._detect_conflicts(new_rule, existing_rules)
        issues.extend(conflicts)
        has_critical = any(
            i["type"] in ("exact_duplicate", "conflict") for i in issues
        )
        return {
            "rule_id": new_rule.get("rule_id", "unknown"),
            "verified": not has_critical,
            "issues": issues,
            "issue_count": len(issues),
            "has_exact_duplicate": exact is not None,
            "has_semantic_duplicates": len(semantic) > 0,
            "has_conflicts": len(conflicts) > 0,
        }

    def verify_rules_batch(
        self,
        new_rules: List[Dict[str, Any]],
        existing_rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        results = []
        total_issues = 0
        for rule in new_rules:
            result = self.verify_rule(rule, existing_rules)
            results.append(result)
            total_issues += result["issue_count"]
            existing_rules = [r for r in existing_rules
                              if r.get("rule_id") != result["rule_id"]]
        verified_count = sum(1 for r in results if r["verified"])
        return {
            "total_new_rules": len(new_rules),
            "verified": verified_count,
            "rejected": len(new_rules) - verified_count,
            "total_issues": total_issues,
            "results": results,
        }

    def generate_report(
        self,
        verification_result: Dict[str, Any],
    ) -> str:
        lines = [
            "=== Rule Verification Report ===",
            f"Total new rules: {verification_result['total_new_rules']}",
            f"Verified: {verification_result['verified']}",
            f"Rejected: {verification_result['rejected']}",
            f"Total issues: {verification_result['total_issues']}",
            "",
        ]
        for result in verification_result["results"]:
            status = "PASS" if result["verified"] else "FAIL"
            lines.append(f"[{status}] {result['rule_id']}: {result['issue_count']} issues")
            for issue in result["issues"]:
                lines.append(f"  - {issue['type']}: {issue}")
        return "\n".join(lines)

    def get_verification_log(self) -> List[Dict[str, Any]]:
        return list(self._verification_log)

    def log_verification(
        self,
        rule_id: str,
        result: Dict[str, Any],
    ) -> None:
        self._verification_log.append({
            "rule_id": rule_id,
            "verified": result.get("verified", False),
            "issue_count": result.get("issue_count", 0),
        })
