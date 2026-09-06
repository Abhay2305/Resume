"""Change Classifier.

Every change must be categorized by section and type.
Categories: Summary, Experience, Projects, Skills, Education, Certifications,
Keywords, Formatting, Achievements, Contact Information.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

CATEGORY_MAP = {
    "summary": "summary",
    "experience": "experience",
    "projects": "projects",
    "skills": "skills",
    "education": "education",
    "certifications": "certifications",
    "keywords": "keywords",
    "formatting": "formatting",
    "achievements": "achievements",
    "contact": "contact",
    "personalInfo": "contact",
}


class ChangeClassifier:
    """Classifies changes by category and assigns risk levels."""

    def classify(
        self,
        diffs: List[Dict[str, Any]],
        gap_results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Classify each diff into a categorized change set.

        Args:
            diffs: Raw diffs from DiffEngine.
            gap_results: Gap analysis results for context.

        Returns:
            List of classified change sets.
        """
        changes = []
        gap_categories = {g.get("category") for g in gap_results if g.get("missing_items")}

        for diff in diffs:
            section = diff.get("section", "unknown")
            change_type = diff.get("change_type", "modified")
            category = CATEGORY_MAP.get(section, section)

            # Determine risk level
            risk_level = self._assess_risk(change_type, category, gap_categories)

            # Build description
            description = self._build_description(diff, category)

            change = {
                "category": category,
                "change_type": change_type,
                "description": description,
                "original_value": diff.get("original_value"),
                "new_value": diff.get("new_value"),
                "risk_level": risk_level,
                "field_path": diff.get("field_path"),
                "section": section,
            }

            # Link to supporting gap if exists
            supporting_gap = self._find_supporting_gap(category, gap_results)
            if supporting_gap:
                change["supporting_gap_id"] = supporting_gap.get("id")

            changes.append(change)

        return changes

    def _assess_risk(
        self,
        change_type: str,
        category: str,
        gap_categories: set,
    ) -> str:
        """Assess risk level for a change."""
        # High risk: removing experience or education
        if change_type == "removed" and category in ("experience", "education"):
            return "high"

        # Medium risk: modifying summary or adding certifications
        if change_type == "modified" and category == "summary":
            return "medium"
        if change_type == "added" and category == "certifications":
            return "medium"

        # Low risk: adding skills or projects
        if change_type == "added" and category in ("skills", "projects", "achievements"):
            return "low"

        # If change addresses a gap, lower risk
        if category in gap_categories:
            return "low"

        # Default medium for modifications
        if change_type == "modified":
            return "medium"

        return "low"

    def _build_description(self, diff: Dict[str, Any], category: str) -> str:
        """Build human-readable description of the change."""
        change_type = diff.get("change_type", "modified")
        section = diff.get("section", category)
        original = diff.get("original_value")
        new = diff.get("new_value")

        if change_type == "added":
            if new:
                preview = str(new)[:100]
                return f"Added to {section}: {preview}"
            return f"Added new content to {section}"

        if change_type == "removed":
            if original:
                preview = str(original)[:100]
                return f"Removed from {section}: {preview}"
            return f"Removed content from {section}"

        if change_type == "modified":
            if original and new:
                orig_preview = str(original)[:50]
                new_preview = str(new)[:50]
                return f"Modified {section}: '{orig_preview}' -> '{new_preview}'"
            return f"Modified {section}"

        if change_type == "moved":
            return f"Moved content within {section}"

        return f"Changed {section}"

    def _find_supporting_gap(
        self,
        category: str,
        gap_results: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Find a gap result that supports this change."""
        for gap in gap_results:
            if gap.get("category") == category and gap.get("missing_items"):
                return gap
        return None

    def get_changes_by_category(
        self,
        changes: List[Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Group changes by category."""
        grouped = {}
        for change in changes:
            category = change.get("category", "unknown")
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(change)
        return grouped
