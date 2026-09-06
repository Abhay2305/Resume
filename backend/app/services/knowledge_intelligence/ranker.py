"""Knowledge Ranker.

Ranks knowledge rules based on gap analysis results.
Deterministic only - no embeddings, no vector search, no LLM.
"""
from typing import Any, Dict, List, Optional


class KnowledgeRanker:
    """Ranks knowledge rules based on gap analysis results."""

    PRIORITY_WEIGHTS = {
        "critical": 4.0,
        "high": 3.0,
        "medium": 2.0,
        "low": 1.0,
    }

    CATEGORY_WEIGHTS = {
        "quantification": 1.5,
        "keywords": 1.4,
        "tailoring": 1.3,
        "impact": 1.2,
        "action_verbs": 1.1,
        "relevance": 1.1,
        "clarity": 1.0,
        "specificity": 1.0,
        "formatting": 0.9,
        "length": 0.8,
    }

    def rank(
        self,
        rules: List[Dict[str, Any]],
        gap_categories: List[str],
        gap_actions: List[str],
        source_confidence: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, Any]]:
        """Rank rules based on gap analysis.

        Args:
            rules: List of knowledge rules.
            gap_categories: Categories from gap analysis (e.g., ['skills', 'experience']).
            gap_actions: Actions from gap analysis (e.g., ['add_skill', 'highlight_experience']).
            source_confidence: Source confidence scores.

        Returns:
            Ranked list of rules with relevance scores.
        """
        scored_rules = []

        for rule in rules:
            score = self._calculate_score(rule, gap_categories, gap_actions, source_confidence)
            scored_rules.append({**rule, "_relevance_score": score})

        scored_rules.sort(key=lambda x: x["_relevance_score"], reverse=True)

        return scored_rules

    def _calculate_score(
        self,
        rule: Dict[str, Any],
        gap_categories: List[str],
        gap_actions: List[str],
        source_confidence: Optional[Dict[str, float]],
    ) -> float:
        """Calculate relevance score for a rule."""
        score = 0.0

        rule_section = rule.get("section_name", "").lower()
        rule_category = rule.get("category", "").lower()
        rule_priority = rule.get("priority", "medium").lower()
        rule_source = rule.get("source", "")

        for gap_cat in gap_categories:
            if gap_cat.lower() == rule_section:
                score += 2.0
                break

        section_mapping = {
            "skills": ["skills", "keywords"],
            "technology": ["skills", "experience"],
            "experience": ["experience"],
            "education": ["education"],
            "certifications": ["certifications"],
            "keywords": ["skills", "summary", "experience"],
            "summary": ["summary"],
            "projects": ["projects"],
            "achievements": ["achievements"],
            "leadership": ["leadership"],
            "formatting": ["formatting"],
        }
        for gap_cat in gap_categories:
            related_sections = section_mapping.get(gap_cat, [])
            if rule_section in related_sections:
                score += 1.0

        for action in gap_actions:
            action_categories = self._get_categories_for_action(action)
            if rule_category in action_categories:
                score += 1.5

        priority_weight = self.PRIORITY_WEIGHTS.get(rule_priority, 1.0)
        score += priority_weight

        category_weight = self.CATEGORY_WEIGHTS.get(rule_category, 1.0)
        score += category_weight

        if source_confidence and rule_source in source_confidence:
            score += source_confidence[rule_source] * 2.0

        confidence = rule.get("confidence", 0.8)
        score *= confidence

        return round(score, 2)

    def _get_categories_for_action(self, action: str) -> List[str]:
        """Get categories related to a gap action."""
        action_mapping = {
            "add_skill": ["quantification", "keywords", "relevance"],
            "strengthen_skill": ["impact", "specificity"],
            "add_technology": ["keywords", "relevance"],
            "highlight_experience": ["quantification", "action_verbs", "impact"],
            "add_education": ["specificity"],
            "add_certification": ["keywords", "relevance"],
            "add_keyword": ["keywords", "ats"],
            "enhance_keyword": ["keywords", "ats"],
            "rewrite_summary": ["clarity", "tailoring", "length"],
            "expand_project": ["specificity", "impact", "quantification"],
            "reorder_skills": ["keywords", "ats"],
            "remove_technology": ["relevance", "tailoring"],
            "add_metrics": ["quantification", "impact"],
            "add_achievements": ["impact", "quantification"],
        }
        return action_mapping.get(action, [])

    def get_top_rules(
        self,
        ranked_rules: List[Dict[str, Any]],
        max_rules: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get top N ranked rules.

        Args:
            ranked_rules: Ranked list of rules.
            max_rules: Maximum number of rules to return.

        Returns:
            Top N rules.
        """
        return ranked_rules[:max_rules]

    def filter_by_section(
        self,
        ranked_rules: List[Dict[str, Any]],
        section: str,
    ) -> List[Dict[str, Any]]:
        """Filter ranked rules by section.

        Args:
            ranked_rules: Ranked list of rules.
            section: Section name to filter by.

        Returns:
            Filtered rules for the section.
        """
        return [
            rule for rule in ranked_rules
            if rule.get("section_name", "").lower() == section.lower()
        ]
