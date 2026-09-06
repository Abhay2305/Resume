"""Rule Approval and Repository Seeding.

Manages the approval workflow for verified rules and seeds the knowledge
repository with hand-authored rules. Enforces the governance lifecycle.
"""
import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

VALID_STATES = [
    "DISCOVERED",
    "EXTRACTED",
    "CLASSIFIED",
    "VERIFIED",
    "APPROVED",
    "ACTIVE",
    "VERSIONED",
    "AUDITED",
    "REJECTED",
]

STATE_TRANSITIONS = {
    "DISCOVERED": ["EXTRACTED", "REJECTED"],
    "EXTRACTED": ["CLASSIFIED", "REJECTED"],
    "CLASSIFIED": ["VERIFIED", "REJECTED"],
    "VERIFIED": ["APPROVED", "REJECTED"],
    "APPROVED": ["ACTIVE"],
    "ACTIVE": ["VERSIONED", "REJECTED"],
    "VERSIONED": ["AUDITED"],
    "AUDITED": [],
    "REJECTED": [],
}

HAND_AUTHORED_SOURCE = "hand-authored"


class RuleApproval:
    """Manages rule approval workflow and repository seeding."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
            )
        self.data_dir = data_dir
        self._transition_log: List[Dict[str, Any]] = []

    def _compute_hash(self, instruction: str) -> str:
        return hashlib.sha256(instruction.strip().encode("utf-8")).hexdigest()[:16]

    def can_transition(self, current_state: str, target_state: str) -> bool:
        if current_state not in VALID_STATES:
            return False
        allowed = STATE_TRANSITIONS.get(current_state, [])
        return target_state in allowed

    def transition_state(
        self,
        rule: Dict[str, Any],
        target_state: str,
        actor: str = "system",
        reason: str = "",
    ) -> Dict[str, Any]:
        current_state = rule.get("state", "DISCOVERED")
        if not self.can_transition(current_state, target_state):
            raise ValueError(
                f"Invalid transition: {current_state} -> {target_state}. "
                f"Allowed: {STATE_TRANSITIONS.get(current_state, [])}"
            )
        updated = dict(rule)
        updated["state"] = target_state
        self._log_transition(
            rule_id=rule.get("rule_id", "unknown"),
            from_state=current_state,
            to_state=target_state,
            actor=actor,
            reason=reason,
        )
        return updated

    def approve_rule(
        self,
        rule: Dict[str, Any],
        reviewer: str = "human",
    ) -> Dict[str, Any]:
        return self.transition_state(
            rule, "APPROVED", actor=reviewer, reason="Human review completed"
        )

    def activate_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        return self.transition_state(rule, "ACTIVE", actor="system", reason="Auto-activation after approval")

    def reject_rule(
        self,
        rule: Dict[str, Any],
        actor: str = "human",
        reason: str = "Failed review",
    ) -> Dict[str, Any]:
        return self.transition_state(rule, "REJECTED", actor=actor, reason=reason)

    def seed_hand_authored_rules(
        self,
        rules: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        seeded = []
        for rule in rules:
            seeded_rule = dict(rule)
            seeded_rule["source_document"] = HAND_AUTHORED_SOURCE
            seeded_rule["source_page"] = None
            seeded_rule["source_evidence"] = None
            seeded_rule["extraction_confidence"] = 1.0
            seeded_rule["extraction_timestamp"] = datetime.utcnow().isoformat()
            if not seeded_rule.get("rule_hash"):
                seeded_rule["rule_hash"] = self._compute_hash(
                    seeded_rule.get("instruction", "")
                )
            seeded_rule["state"] = "ACTIVE"
            seeded_rule["version"] = 1
            seeded.append(seeded_rule)
        return seeded

    def load_seed_rules_from_json(self) -> List[Dict[str, Any]]:
        filepath = os.path.join(self.data_dir, "knowledge_rules.json")
        if not os.path.exists(filepath):
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_rules = []
        for key, rules in data.items():
            if key.endswith("_rules") and isinstance(rules, list):
                for rule in rules:
                    normalized = {
                        "rule_id": rule.get("rule_id", ""),
                        "source": rule.get("source", ""),
                        "section_name": rule.get("section", ""),
                        "priority": rule.get("priority", "Medium"),
                        "category": rule.get("category", "General"),
                        "instruction": rule.get("instruction", ""),
                        "reason": rule.get("reason", ""),
                        "examples": rule.get("examples", []),
                    }
                    all_rules.append(normalized)
        return all_rules

    def get_seeded_rules_count(self) -> int:
        rules = self.load_seed_rules_from_json()
        return len(rules)

    def prepare_for_extraction(
        self,
        rule: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self.transition_state(rule, "EXTRACTED", actor="system", reason="Rule extracted from PDF")

    def prepare_for_classification(
        self,
        rule: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self.transition_state(rule, "CLASSIFIED", actor="system", reason="Rule classified")

    def prepare_for_verification(
        self,
        rule: Dict[str, Any],
    ) -> Dict[str, Any]:
        return self.transition_state(rule, "VERIFIED", actor="system", reason="Rule verified")

    def get_transition_log(self) -> List[Dict[str, Any]]:
        return list(self._transition_log)

    def get_transitions_for_rule(self, rule_id: str) -> List[Dict[str, Any]]:
        return [t for t in self._transition_log if t["rule_id"] == rule_id]

    def _log_transition(
        self,
        rule_id: str,
        from_state: str,
        to_state: str,
        actor: str,
        reason: str,
    ) -> None:
        self._transition_log.append({
            "rule_id": rule_id,
            "from_state": from_state,
            "to_state": to_state,
            "actor": actor,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
