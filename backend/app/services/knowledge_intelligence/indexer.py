"""Knowledge Indexer.

Creates deterministic indexes for knowledge rules.
"""
import json
import os
from typing import Any, Dict, List, Set


class KnowledgeIndexer:
    """Creates deterministic indexes for knowledge rules."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._index_data = self._load_index()
        self._indexes = {
            "by_section": {},
            "by_category": {},
            "by_priority": {},
            "by_source": {},
            "by_keyword": {},
        }

    def _load_index(self) -> Dict[str, Any]:
        """Load index mappings from JSON file."""
        filepath = os.path.join(self.data_dir, "knowledge_index.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def build_indexes(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build all indexes from rules.

        Args:
            rules: List of structured rules.

        Returns:
            Dictionary of indexes.
        """
        self._indexes = {
            "by_section": {},
            "by_category": {},
            "by_priority": {},
            "by_source": {},
            "by_keyword": {},
        }

        for rule in rules:
            section = rule.get("section_name", "")
            category = rule.get("category", "")
            priority = rule.get("priority", "")
            source = rule.get("source", "")

            if section:
                self._indexes["by_section"].setdefault(section, []).append(rule)
            if category:
                self._indexes["by_category"].setdefault(category, []).append(rule)
            if priority:
                self._indexes["by_priority"].setdefault(priority, []).append(rule)
            if source:
                self._indexes["by_source"].setdefault(source, []).append(rule)

            self._index_keywords(rule)

        return self._indexes

    def _index_keywords(self, rule: Dict[str, Any]) -> None:
        """Index rule by keywords from instruction and reason."""
        text = f"{rule.get('instruction', '')} {rule.get('reason', '')}".lower()
        keywords = set()

        for word in text.split():
            if len(word) > 3:
                keywords.add(word)

        for keyword in keywords:
            self._indexes["by_keyword"].setdefault(keyword, []).append(rule)

    def get_by_section(self, section: str) -> List[Dict[str, Any]]:
        """Get rules by section."""
        return self._indexes.get("by_section", {}).get(section, [])

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get rules by category."""
        return self._indexes.get("by_category", {}).get(category, [])

    def get_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get rules by priority."""
        return self._indexes.get("by_priority", {}).get(priority, [])

    def get_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get rules by source."""
        return self._indexes.get("by_source", {}).get(source, [])

    def get_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Get rules by keyword."""
        return self._indexes.get("by_keyword", {}).get(keyword.lower(), [])

    def get_sections_for_gap(self, gap_categories: List[str]) -> Set[str]:
        """Get relevant sections for gap analysis categories.

        Args:
            gap_categories: List of gap categories (e.g., ['skills', 'experience']).

        Returns:
            Set of relevant section names.
        """
        mapping = self._index_data.get("gap_category_to_section", {})
        sections = set()
        for category in gap_categories:
            sections.update(mapping.get(category, []))
        return sections

    def get_categories_for_action(self, action: str) -> List[str]:
        """Get relevant categories for a gap action.

        Args:
            action: Gap action (e.g., 'add_skill', 'highlight_experience').

        Returns:
            List of relevant categories.
        """
        mapping = self._index_data.get("gap_action_to_category", {})
        return mapping.get(action, [])

    def get_index_stats(self) -> Dict[str, int]:
        """Get statistics about the indexes."""
        return {
            "sections": len(self._indexes.get("by_section", {})),
            "categories": len(self._indexes.get("by_category", {})),
            "priorities": len(self._indexes.get("by_priority", {})),
            "sources": len(self._indexes.get("by_source", {})),
            "keywords": len(self._indexes.get("by_keyword", {})),
        }
