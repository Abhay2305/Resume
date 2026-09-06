"""Knowledge Context Builder.

Builds structured context from retrieved rules.
No prompt generation - only structured context.
"""
import json
from typing import Any, Dict, List, Optional


class KnowledgeContextBuilder:
    """Builds structured knowledge context from retrieved rules."""

    SECTIONS = [
        "summary",
        "experience",
        "skills",
        "education",
        "projects",
        "certifications",
        "ats",
        "formatting",
        "cover_letter",
    ]

    def build(
        self,
        rules: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build structured context from rules.

        Args:
            rules: List of retrieved knowledge rules.

        Returns:
            Structured context dictionary.
        """
        context = {}

        for section in self.SECTIONS:
            section_rules = [
                rule for rule in rules
                if rule.get("section_name", "").lower() == section
            ]
            context[f"{section}_rules"] = json.dumps([
                self._format_rule(rule) for rule in section_rules
            ])

        context["total_rules"] = len(rules)
        context["citations"] = json.dumps(self._extract_citations(rules))

        return context

    def _format_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Format a rule for context output including provenance."""
        examples = rule.get("examples", "[]")
        if isinstance(examples, str):
            try:
                examples = json.loads(examples)
            except (json.JSONDecodeError, TypeError):
                examples = []

        formatted = {
            "rule_id": rule.get("rule_id", ""),
            "source": rule.get("source", ""),
            "section": rule.get("section_name", ""),
            "priority": rule.get("priority", "medium"),
            "category": rule.get("category", ""),
            "instruction": rule.get("instruction", ""),
            "reason": rule.get("reason", ""),
            "examples": examples,
        }

        # Include provenance if available
        source_document = rule.get("source_document")
        if source_document:
            formatted["provenance"] = {
                "source_document": source_document,
                "source_page": rule.get("source_page"),
                "source_evidence": rule.get("source_evidence"),
                "extraction_confidence": rule.get("extraction_confidence"),
                "extraction_timestamp": rule.get("extraction_timestamp"),
                "rule_hash": rule.get("rule_hash"),
                "state": rule.get("state", "ACTIVE"),
                "version": rule.get("version", 1),
            }

        return formatted

    def _extract_citations(self, rules: List[Dict[str, Any]]) -> List[str]:
        """Extract unique citations from rules including PDF source documents."""
        citations = set()
        for rule in rules:
            source = rule.get("source", "")
            if source:
                citations.add(source)
            source_document = rule.get("source_document", "")
            if source_document and source_document != "hand-authored":
                citations.add(source_document)
        return sorted(list(citations))

    def get_section_rules(
        self,
        context: Dict[str, Any],
        section: str,
    ) -> List[Dict[str, Any]]:
        """Get rules for a specific section from context.

        Args:
            context: Structured context.
            section: Section name.

        Returns:
            List of rules for the section.
        """
        key = f"{section}_rules"
        rules_json = context.get(key, "[]")
        try:
            return json.loads(rules_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_all_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all rules from context.

        Args:
            context: Structured context.

        Returns:
            List of all rules.
        """
        all_rules = []
        for section in self.SECTIONS:
            all_rules.extend(self.get_section_rules(context, section))
        return all_rules

    def get_citations(self, context: Dict[str, Any]) -> List[str]:
        """Get citations from context.

        Args:
            context: Structured context.

        Returns:
            List of citations.
        """
        citations_json = context.get("citations", "[]")
        try:
            return json.loads(citations_json)
        except (json.JSONDecodeError, TypeError):
            return []
