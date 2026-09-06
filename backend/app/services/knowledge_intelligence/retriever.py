"""Knowledge Retriever.

Returns only relevant rules based on gap analysis.
"""
from typing import Any, Dict, List, Optional

from app.services.knowledge_intelligence.ranker import KnowledgeRanker


class KnowledgeRetriever:
    """Retrieves relevant knowledge rules based on gap analysis."""

    def __init__(self):
        self.ranker = KnowledgeRanker()

    def retrieve(
        self,
        all_rules: List[Dict[str, Any]],
        gap_results: Dict[str, Any],
        max_rules: int = 30,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant rules based on gap analysis.

        Args:
            all_rules: All available knowledge rules.
            gap_results: Gap analysis results.
            max_rules: Maximum number of rules to retrieve.

        Returns:
            Ranked list of relevant rules.
        """
        gap_categories = self._extract_categories(gap_results)
        gap_actions = self._extract_actions(gap_results)

        ranked_rules = self.ranker.rank(
            all_rules,
            gap_categories,
            gap_actions,
        )

        return self.ranker.get_top_rules(ranked_rules, max_rules)

    def _extract_categories(self, gap_results: Dict[str, Any]) -> List[str]:
        """Extract categories from gap results."""
        categories = []

        if "skills" in gap_results:
            categories.append("skills")
        if "technology" in gap_results:
            categories.append("technology")
        if "experience" in gap_results:
            categories.append("experience")
        if "education" in gap_results:
            categories.append("education")
        if "certifications" in gap_results:
            categories.append("certifications")
        if "keywords" in gap_results:
            categories.append("keywords")

        return categories

    def _extract_actions(self, gap_results: Dict[str, Any]) -> List[str]:
        """Extract recommended actions from gap results."""
        actions = []

        skills_data = gap_results.get("skills", {})
        if skills_data.get("required", {}).get("missing"):
            actions.append("add_skill")

        tech_data = gap_results.get("technology", {})
        for category_data in tech_data.get("categories", {}).values():
            if category_data.get("missing"):
                actions.append("add_technology")
                break

        exp_data = gap_results.get("experience", {})
        if not exp_data.get("years", {}).get("sufficient", True):
            actions.append("highlight_experience")
        if exp_data.get("roles", {}).get("missing"):
            actions.append("highlight_experience")

        edu_data = gap_results.get("education", {})
        if not edu_data.get("degree", {}).get("sufficient", True):
            actions.append("add_education")

        cert_data = gap_results.get("certifications", {})
        if cert_data.get("required", {}).get("missing"):
            actions.append("add_certification")

        kw_data = gap_results.get("keywords", {})
        if kw_data.get("missing"):
            actions.append("add_keyword")

        return list(set(actions))

    def get_section_rules(
        self,
        rules: List[Dict[str, Any]],
        section: str,
    ) -> List[Dict[str, Any]]:
        """Get rules for a specific section.

        Args:
            rules: List of rules.
            section: Section name.

        Returns:
            Rules for the section.
        """
        return [
            rule for rule in rules
            if rule.get("section_name", "").lower() == section.lower()
        ]
