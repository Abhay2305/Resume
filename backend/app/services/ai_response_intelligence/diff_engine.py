"""Diff Engine.

Generates deterministic change sets comparing original resume against AI response.
Never overwrites the resume. Produces Added, Removed, Modified, Moved changes.
"""
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class DiffEngine:
    """Generates deterministic diffs between original resume and AI response.

    Produces structured change sets without modifying the original resume.
    """

    def generate_diff(
        self,
        original_data: Dict[str, Any],
        response_data: Dict[str, Any],
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Generate diff between original and AI response.

        Args:
            original_data: Original resume knowledge.
            response_data: AI response data.

        Returns:
            Tuple of (diffs, summary).
        """
        diffs = []

        # Diff summary
        diffs.extend(self._diff_text_field(original_data, response_data, "summary", "summary"))

        # Diff experience
        diffs.extend(self._diff_experience(original_data, response_data))

        # Diff skills
        diffs.extend(self._diff_list_field(original_data, response_data, "skills", "skills"))

        # Diff education
        diffs.extend(self._diff_education(original_data, response_data))

        # Diff certifications
        diffs.extend(self._diff_list_field(original_data, response_data, "certifications", "certifications"))

        # Diff projects
        diffs.extend(self._diff_projects(original_data, response_data))

        # Diff achievements
        diffs.extend(self._diff_list_field(original_data, response_data, "achievements", "achievements"))

        # Generate summary
        summary = self._generate_summary(diffs)

        return diffs, summary

    def _diff_text_field(
        self,
        original: Dict[str, Any],
        response: Dict[str, Any],
        field: str,
        section: str,
    ) -> List[Dict[str, Any]]:
        """Diff a text field between original and response."""
        diffs = []
        original_val = original.get(field, "")
        response_val = response.get(field, "")

        if not original_val and response_val:
            diffs.append({
                "section": section,
                "change_type": "added",
                "original_value": None,
                "new_value": response_val,
                "field_path": field,
            })
        elif original_val and not response_val:
            diffs.append({
                "section": section,
                "change_type": "removed",
                "original_value": original_val,
                "new_value": None,
                "field_path": field,
            })
        elif original_val != response_val:
            diffs.append({
                "section": section,
                "change_type": "modified",
                "original_value": original_val,
                "new_value": response_val,
                "field_path": field,
            })

        return diffs

    def _diff_list_field(
        self,
        original: Dict[str, Any],
        response: Dict[str, Any],
        field: str,
        section: str,
    ) -> List[Dict[str, Any]]:
        """Diff a list field between original and response."""
        diffs = []
        original_items = original.get(field, [])
        response_items = response.get(field, [])

        if not isinstance(original_items, list):
            original_items = []
        if not isinstance(response_items, list):
            response_items = []

        original_set = {str(i).lower() for i in original_items}
        response_set = {str(i).lower() for i in response_items}

        # Added items
        for item in response_items:
            if str(item).lower() not in original_set:
                diffs.append({
                    "section": section,
                    "change_type": "added",
                    "original_value": None,
                    "new_value": str(item),
                    "field_path": f"{field}[+]",
                })

        # Removed items
        for item in original_items:
            if str(item).lower() not in response_set:
                diffs.append({
                    "section": section,
                    "change_type": "removed",
                    "original_value": str(item),
                    "new_value": None,
                    "field_path": f"{field}[-]",
                })

        return diffs

    def _diff_experience(
        self,
        original: Dict[str, Any],
        response: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Diff experience entries."""
        diffs = []
        original_exp = original.get("experience_summary", [])
        response_exp = response.get("experience", [])

        if not isinstance(original_exp, list):
            original_exp = []
        if not isinstance(response_exp, list):
            response_exp = []

        # Index by company for comparison
        original_by_company = {}
        for entry in original_exp:
            if isinstance(entry, dict) and entry.get("company"):
                original_by_company[entry["company"].lower()] = entry

        response_by_company = {}
        for entry in response_exp:
            if isinstance(entry, dict) and entry.get("company"):
                response_by_company[entry["company"].lower()] = entry

        # Check for modified/added entries
        for company, resp_entry in response_by_company.items():
            if company in original_by_company:
                orig_entry = original_by_company[company]
                # Check for modifications
                changes = self._compare_experience_entries(orig_entry, resp_entry)
                for change in changes:
                    diffs.append({
                        "section": "experience",
                        "change_type": "modified",
                        "original_value": change["original"],
                        "new_value": change["new"],
                        "field_path": f"experience[{company}].{change['field']}",
                    })
            else:
                # New entry
                diffs.append({
                    "section": "experience",
                    "change_type": "added",
                    "original_value": None,
                    "new_value": json.dumps(resp_entry),
                    "field_path": f"experience[{company}]",
                })

        # Check for removed entries
        for company in original_by_company:
            if company not in response_by_company:
                diffs.append({
                    "section": "experience",
                    "change_type": "removed",
                    "original_value": json.dumps(original_by_company[company]),
                    "new_value": None,
                    "field_path": f"experience[{company}]",
                })

        return diffs

    def _diff_education(
        self,
        original: Dict[str, Any],
        response: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Diff education entries."""
        diffs = []
        original_edu = original.get("education_summary", [])
        response_edu = response.get("education", [])

        if not isinstance(original_edu, list):
            original_edu = []
        if not isinstance(response_edu, list):
            response_edu = []

        # Simple comparison by institution
        original_institutions = {
            e.get("institution", "").lower(): e
            for e in original_edu
            if isinstance(e, dict) and e.get("institution")
        }
        response_institutions = {
            e.get("institution", "").lower(): e
            for e in response_edu
            if isinstance(e, dict) and e.get("institution")
        }

        for inst, entry in response_institutions.items():
            if inst not in original_institutions:
                diffs.append({
                    "section": "education",
                    "change_type": "added",
                    "original_value": None,
                    "new_value": json.dumps(entry),
                    "field_path": f"education[{inst}]",
                })

        for inst in original_institutions:
            if inst not in response_institutions:
                diffs.append({
                    "section": "education",
                    "change_type": "removed",
                    "original_value": json.dumps(original_institutions[inst]),
                    "new_value": None,
                    "field_path": f"education[{inst}]",
                })

        return diffs

    def _diff_projects(
        self,
        original: Dict[str, Any],
        response: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Diff project entries."""
        diffs = []
        original_projects = original.get("projects", [])
        response_projects = response.get("projects", [])

        if not isinstance(original_projects, list):
            original_projects = []
        if not isinstance(response_projects, list):
            response_projects = []

        # Simple count comparison
        if len(response_projects) > len(original_projects):
            diffs.append({
                "section": "projects",
                "change_type": "added",
                "original_value": f"{len(original_projects)} projects",
                "new_value": f"{len(response_projects)} projects",
                "field_path": "projects",
            })
        elif len(response_projects) < len(original_projects):
            diffs.append({
                "section": "projects",
                "change_type": "removed",
                "original_value": f"{len(original_projects)} projects",
                "new_value": f"{len(response_projects)} projects",
                "field_path": "projects",
            })

        return diffs

    def _compare_experience_entries(
        self, original: Dict[str, Any], response: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Compare two experience entries and return differences."""
        changes = []

        for field in ["title", "company", "startDate", "endDate"]:
            orig_val = original.get(field, "")
            resp_val = response.get(field, "")
            if orig_val != resp_val:
                changes.append({
                    "field": field,
                    "original": str(orig_val) if orig_val else None,
                    "new": str(resp_val) if resp_val else None,
                })

        # Compare bullet points
        orig_bullets = original.get("description", [])
        resp_bullets = response.get("description", [])
        if isinstance(orig_bullets, list) and isinstance(resp_bullets, list):
            if orig_bullets != resp_bullets:
                changes.append({
                    "field": "description",
                    "original": json.dumps(orig_bullets),
                    "new": json.dumps(resp_bullets),
                })

        return changes

    def _generate_summary(self, diffs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of all changes."""
        summary = {
            "total_changes": len(diffs),
            "by_type": {"added": 0, "removed": 0, "modified": 0, "moved": 0},
            "by_section": {},
        }

        for diff in diffs:
            change_type = diff.get("change_type", "modified")
            section = diff.get("section", "unknown")

            summary["by_type"][change_type] = summary["by_type"].get(change_type, 0) + 1
            summary["by_section"][section] = summary["by_section"].get(section, 0) + 1

        return summary
