"""Gap Validator.

Verifies AI actually addressed the detected gaps.
Rejects unnecessary modifications.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GapValidator:
    """Validates that AI response addresses detected gaps.

    Ensures AI modifications are relevant to identified gaps
    and rejects unnecessary changes.
    """

    def validate(
        self,
        response_data: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        gap_results: List[Dict[str, Any]],
    ) -> Tuple[bool, float, List[Dict[str, Any]], Dict[str, Any]]:
        """Validate AI response against gap analysis.

        Args:
            response_data: The parsed AI response.
            gap_analysis: The gap analysis summary.
            gap_results: Individual gap results by category.

        Returns:
            Tuple of (is_valid, score, issues, details).
        """
        issues = []
        details = {}
        score = 100.0

        if not response_data:
            return False, 0.0, [{"type": "empty_response", "message": "No response to validate"}], {}

        if not gap_analysis:
            return True, 70.0, [{"type": "no_gap_analysis", "message": "No gap analysis available"}], {}

        # Check skill gaps were addressed
        skill_issues = self._validate_skill_gaps_addressed(response_data, gap_results)
        issues.extend(skill_issues)
        score -= len(skill_issues) * 5.0

        # Check technology gaps were addressed
        tech_issues = self._validate_technology_gaps_addressed(response_data, gap_results)
        issues.extend(tech_issues)
        score -= len(tech_issues) * 5.0

        # Check experience gaps were addressed
        exp_issues = self._validate_experience_gaps_addressed(response_data, gap_results)
        issues.extend(exp_issues)
        score -= len(exp_issues) * 5.0

        # Check for unnecessary modifications
        unnecessary_issues = self._validate_no_unnecessary_modifications(response_data, gap_results)
        issues.extend(unnecessary_issues)
        score -= len(unnecessary_issues) * 8.0

        # Check overall match score improvement
        improvement_issues = self._validate_improvement(response_data, gap_analysis)
        issues.extend(improvement_issues)
        score -= len(improvement_issues) * 10.0

        score = max(0.0, min(100.0, score))
        is_valid = score >= 40.0

        details["total_issues"] = len(issues)
        details["gaps_addressed"] = self._count_gaps_addressed(response_data, gap_results)
        details["total_gaps"] = len(gap_results)

        return is_valid, score, issues, details

    def _validate_skill_gaps_addressed(
        self, response: Dict[str, Any], gap_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check that skill gaps were addressed in the response."""
        issues = []

        skill_gap = next((g for g in gap_results if g.get("category") == "skills"), None)
        if not skill_gap:
            return issues

        missing_items = skill_gap.get("missing_items", "")
        if not missing_items:
            return issues

        # Parse missing items (stored as comma-separated or JSON)
        missing_skills = self._parse_gap_items(missing_items)
        response_skills = response.get("skills", [])

        if isinstance(response_skills, list):
            response_skills_lower = {s.lower() for s in response_skills if isinstance(s, str)}
            for skill in missing_skills:
                if skill.lower() not in response_skills_lower:
                    issues.append({
                        "type": "gap_not_addressed",
                        "category": "skills",
                        "value": skill,
                        "message": f"Missing skill '{skill}' not added to response",
                    })

        return issues

    def _validate_technology_gaps_addressed(
        self, response: Dict[str, Any], gap_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check that technology gaps were addressed."""
        issues = []

        tech_gap = next((g for g in gap_results if g.get("category") == "technology"), None)
        if not tech_gap:
            return issues

        missing_items = tech_gap.get("missing_items", "")
        if not missing_items:
            return issues

        missing_tech = self._parse_gap_items(missing_items)
        response_skills = response.get("skills", [])

        if isinstance(response_skills, list):
            response_skills_lower = {s.lower() for s in response_skills if isinstance(s, str)}
            for tech in missing_tech:
                if tech.lower() not in response_skills_lower:
                    issues.append({
                        "type": "gap_not_addressed",
                        "category": "technology",
                        "value": tech,
                        "message": f"Missing technology '{tech}' not addressed",
                    })

        return issues

    def _validate_experience_gaps_addressed(
        self, response: Dict[str, Any], gap_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check that experience gaps were addressed."""
        issues = []

        exp_gap = next((g for g in gap_results if g.get("category") == "experience"), None)
        if not exp_gap:
            return issues

        missing_items = exp_gap.get("missing_items", "")
        if not missing_items:
            return issues

        # Experience gaps are harder to address programmatically
        # Just check if the response has meaningful experience content
        experience = response.get("experience", [])
        if not isinstance(experience, list) or len(experience) == 0:
            issues.append({
                "type": "gap_not_addressed",
                "category": "experience",
                "message": "Experience gap not addressed - no experience entries in response",
            })

        return issues

    def _validate_no_unnecessary_modifications(
        self, response: Dict[str, Any], gap_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Check that AI didn't make changes beyond what gaps require."""
        issues = []

        # Get categories with gaps
        gap_categories = {g.get("category") for g in gap_results if g.get("missing_items")}

        # Categories that were modified in response
        modified_categories = set()

        if response.get("summary"):
            modified_categories.add("summary")
        if response.get("experience"):
            modified_categories.add("experience")
        if response.get("skills"):
            modified_categories.add("skills")
        if response.get("education"):
            modified_categories.add("education")
        if response.get("certifications"):
            modified_categories.add("certifications")
        if response.get("projects"):
            modified_categories.add("projects")

        # Check for modifications in categories without gaps
        for category in modified_categories:
            if category not in gap_categories and category not in ("summary", "skills"):
                issues.append({
                    "type": "unnecessary_modification",
                    "category": category,
                    "message": f"AI modified '{category}' but no gaps were identified in this category",
                })

        return issues

    def _validate_improvement(
        self, response: Dict[str, Any], gap_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate that the response would improve the match score."""
        issues = []

        current_score = gap_analysis.get("overall_match_score", 0)
        if current_score and current_score >= 0.8:
            # Already a good match - any changes should be minor
            experience = response.get("experience", [])
            if isinstance(experience, list) and len(experience) > 10:
                issues.append({
                    "type": "excessive_modification",
                    "message": "Response has too many experience entries for a high-match scenario",
                })

        return issues

    def _count_gaps_addressed(
        self, response: Dict[str, Any], gap_results: List[Dict[str, Any]]
    ) -> int:
        """Count how many gaps were addressed."""
        addressed = 0

        for gap in gap_results:
            category = gap.get("category", "")
            missing_items = gap.get("missing_items", "")

            if not missing_items:
                continue

            missing = self._parse_gap_items(missing_items)
            response_items = self._get_response_items(response, category)

            if response_items:
                for item in missing:
                    if any(item.lower() in str(r).lower() for r in response_items):
                        addressed += 1

        return addressed

    def _parse_gap_items(self, items: Any) -> List[str]:
        """Parse gap items from various formats."""
        if isinstance(items, list):
            return [str(i) for i in items]
        if isinstance(items, str):
            if items.startswith("["):
                try:
                    import json
                    return json.loads(items)
                except (json.JSONDecodeError, TypeError):
                    pass
            return [i.strip() for i in items.split(",") if i.strip()]
        return []

    def _get_response_items(self, response: Dict[str, Any], category: str) -> List[str]:
        """Get response items for a category."""
        if category in ("skills", "technology"):
            return response.get("skills", [])
        if category == "certifications":
            return response.get("certifications", [])
        if category == "education":
            edu = response.get("education", [])
            if isinstance(edu, list):
                return [e.get("degree", "") for e in edu if isinstance(e, dict)]
        return []
