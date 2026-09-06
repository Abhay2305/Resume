"""Provenance Tracker.

Tracks rule source lineage from PDF to active rule. Every rule in the knowledge
repository must have complete provenance: source_document, source_page,
extraction_confidence, extraction_timestamp, rule_hash.
"""
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PROVENANCE_FIELDS = [
    "source_document",
    "source_page",
    "source_section",
    "source_evidence",
    "extraction_confidence",
    "extraction_timestamp",
    "rule_hash",
]

HAND_AUTHORED_SOURCE = "hand-authored"


class ProvenanceTracker:
    """Tracks and verifies rule source lineage."""

    def __init__(self):
        self._lineage_log: List[Dict[str, Any]] = []

    def assign_provenance(
        self,
        rule: Dict[str, Any],
        source_document: str,
        source_page: Optional[int] = None,
        source_section: Optional[str] = None,
        source_evidence: Optional[str] = None,
        extraction_confidence: float = 0.8,
    ) -> Dict[str, Any]:
        provenanced = dict(rule)
        provenanced["source_document"] = source_document
        provenanced["source_page"] = source_page
        provenanced["source_section"] = source_section
        provenanced["source_evidence"] = source_evidence
        provenanced["extraction_confidence"] = extraction_confidence
        provenanced["extraction_timestamp"] = datetime.utcnow().isoformat()
        if "rule_hash" not in provenanced or not provenanced["rule_hash"]:
            provenanced["rule_hash"] = self._compute_hash(
                provenanced.get("instruction", "")
            )
        return provenanced

    def assign_hand_authored_provenance(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        return self.assign_provenance(
            rule=rule,
            source_document=HAND_AUTHORED_SOURCE,
            source_page=None,
            source_section=None,
            source_evidence=None,
            extraction_confidence=1.0,
        )

    def _compute_hash(self, instruction: str) -> str:
        return hashlib.sha256(instruction.strip().encode("utf-8")).hexdigest()[:16]

    def verify_provenance(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        for field in PROVENANCE_FIELDS:
            if field not in rule:
                issues.append(f"Missing provenance field: {field}")
        if rule.get("source_document") == HAND_AUTHORED_SOURCE:
            if rule.get("source_page") is not None:
                issues.append("Hand-authored rules should not have source_page")
            if rule.get("extraction_confidence", 0) < 1.0:
                issues.append("Hand-authored rules should have confidence 1.0")
        else:
            if not rule.get("source_document"):
                issues.append("Non-hand-authored rule missing source_document")
            if rule.get("source_page") is None:
                issues.append("Non-hand-authored rule missing source_page")
            confidence = rule.get("extraction_confidence", 0)
            if not (0.0 <= confidence <= 1.0):
                issues.append(f"Confidence out of range: {confidence}")
        if not rule.get("extraction_timestamp"):
            issues.append("Missing extraction_timestamp")
        if not rule.get("rule_hash"):
            issues.append("Missing rule_hash")
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "rule_id": rule.get("rule_id", "unknown"),
        }

    def compute_lineage(
        self, rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "rule_id": rule.get("rule_id", "unknown"),
            "source_document": rule.get("source_document"),
            "source_page": rule.get("source_page"),
            "source_section": rule.get("source_section"),
            "source_evidence": rule.get("source_evidence"),
            "extraction_confidence": rule.get("extraction_confidence"),
            "extraction_timestamp": rule.get("extraction_timestamp"),
            "rule_hash": rule.get("rule_hash"),
            "state": rule.get("state", "unknown"),
            "version": rule.get("version", 1),
        }

    def detect_modification(
        self, original: Dict[str, Any], modified: Dict[str, Any]
    ) -> Dict[str, Any]:
        changes = []
        for key in ["instruction", "domain", "priority", "category", "section_name"]:
            if original.get(key) != modified.get(key):
                changes.append({
                    "field": key,
                    "old_value": original.get(key),
                    "new_value": modified.get(key),
                })
        original_hash = original.get("rule_hash", "")
        modified_hash = modified.get("rule_hash", "")
        hash_changed = original_hash != modified_hash
        return {
            "rule_id": original.get("rule_id", "unknown"),
            "modified": len(changes) > 0 or hash_changed,
            "changes": changes,
            "hash_changed": hash_changed,
            "original_hash": original_hash,
            "modified_hash": modified_hash,
        }

    def get_lineage_log(self) -> List[Dict[str, Any]]:
        return list(self._lineage_log)

    def log_lineage_event(
        self,
        rule_id: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = {
            "rule_id": rule_id,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
        }
        self._lineage_log.append(event)

    def get_lineage_for_rule(self, rule_id: str) -> List[Dict[str, Any]]:
        return [e for e in self._lineage_log if e["rule_id"] == rule_id]

    def validate_rules_batch(
        self, rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        results = [self.verify_provenance(rule) for rule in rules]
        valid_count = sum(1 for r in results if r["valid"])
        return {
            "total": len(rules),
            "valid": valid_count,
            "invalid": len(rules) - valid_count,
            "results": results,
        }
