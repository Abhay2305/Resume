"""Knowledge Rule Extractor.

Converts knowledge into structured rules. Every rule contains:
rule_id, source, section, priority, category, instruction, reason, examples.
"""
import json
import os
from typing import Any, Dict, List, Optional


class KnowledgeRuleExtractor:
    """Extracts structured rules from knowledge documents."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._rules_data = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        """Load rules from JSON file."""
        filepath = os.path.join(self.data_dir, "knowledge_rules.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def extract_from_document(self, document_key: str) -> List[Dict[str, Any]]:
        """Extract rules from a document by key.

        Args:
            document_key: The document key (e.g., 'harvard_resume').

        Returns:
            List of structured rule dictionaries.
        """
        rules_key = f"{document_key}_rules"
        return self._rules_data.get(rules_key, [])

    def extract_by_section(self, section_name: str) -> List[Dict[str, Any]]:
        """Extract all rules for a specific section across all documents.

        Args:
            section_name: Section name (e.g., 'Experience', 'Skills').

        Returns:
            List of rules matching the section.
        """
        all_rules = []
        for key, rules in self._rules_data.items():
            if key.endswith("_rules") and isinstance(rules, list):
                for rule in rules:
                    if rule.get("section", "").lower() == section_name.lower():
                        all_rules.append(rule)
        return all_rules

    def extract_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Extract all rules for a specific category.

        Args:
            category: Category name (e.g., 'Quantification', 'Keywords').

        Returns:
            List of rules matching the category.
        """
        all_rules = []
        for key, rules in self._rules_data.items():
            if key.endswith("_rules") and isinstance(rules, list):
                for rule in rules:
                    if rule.get("category", "").lower() == category.lower():
                        all_rules.append(rule)
        return all_rules

    def extract_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Extract all rules for a specific priority level.

        Args:
            priority: Priority level (e.g., 'High', 'Critical').

        Returns:
            List of rules matching the priority.
        """
        all_rules = []
        for key, rules in self._rules_data.items():
            if key.endswith("_rules") and isinstance(rules, list):
                for rule in rules:
                    if rule.get("priority", "").lower() == priority.lower():
                        all_rules.append(rule)
        return all_rules

    def extract_all(self) -> List[Dict[str, Any]]:
        """Extract all rules from all documents.

        Returns:
            List of all structured rules.
        """
        all_rules = []
        for key, rules in self._rules_data.items():
            if key.endswith("_rules") and isinstance(rules, list):
                all_rules.extend(rules)
        return all_rules

    def get_available_documents(self) -> List[str]:
        """Get list of available document keys."""
        return [
            key.replace("_rules", "")
            for key in self._rules_data.keys()
            if key.endswith("_rules")
        ]

    def normalize_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a rule to standard format.

        Args:
            rule: Raw rule dictionary.

        Returns:
            Normalized rule dictionary.
        """
        return {
            "rule_id": rule.get("rule_id", ""),
            "source": rule.get("source", ""),
            "section_name": rule.get("section", ""),
            "priority": rule.get("priority", "medium"),
            "category": rule.get("category", ""),
            "instruction": rule.get("instruction", ""),
            "reason": rule.get("reason", ""),
            "examples": json.dumps(rule.get("examples", [])),
        }
