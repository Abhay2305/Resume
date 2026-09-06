"""Response Schema Validator.

Validates AI response JSON structure, required fields, data types,
and output schema compliance. Rejects malformed AI responses.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS = ["summary", "experience", "skills"]
VALID_SECTION_KEYS = [
    "personalInfo", "summary", "experience", "education",
    "skills", "projects", "certifications", "achievements",
]
VALID_EXPERIENCE_FIELDS = ["title", "company", "startDate", "description"]
VALID_EDUCATION_FIELDS = ["degree", "institution", "field", "startDate"]


class ResponseSchemaValidator:
    """Validates AI response JSON structure against expected schema.

    Checks for required sections, correct data types, and structural integrity.
    """

    def validate(
        self,
        response_data: Dict[str, Any],
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, float, List[Dict[str, Any]], Dict[str, Any]]:
        """Validate AI response schema.

        Args:
            response_data: The parsed AI response.
            output_schema: Optional expected output schema from prompt package.

        Returns:
            Tuple of (is_valid, score, issues, details).
        """
        issues = []
        details = {}
        score = 100.0

        if not response_data:
            return False, 0.0, [{"type": "empty_response", "message": "AI response is empty"}], {}

        if not isinstance(response_data, dict):
            return False, 0.0, [{"type": "invalid_type", "message": "Response is not a dictionary"}], {}

        # Check required sections
        for section in REQUIRED_SECTIONS:
            if section not in response_data:
                issues.append({
                    "type": "missing_section",
                    "section": section,
                    "message": f"Required section '{section}' is missing",
                })
                score -= 20.0

        # Validate summary
        if "summary" in response_data:
            summary = response_data["summary"]
            if not isinstance(summary, str):
                issues.append({
                    "type": "invalid_type",
                    "section": "summary",
                    "message": "Summary must be a string",
                })
                score -= 10.0
            elif len(summary.strip()) < 10:
                issues.append({
                    "type": "too_short",
                    "section": "summary",
                    "message": "Summary is too short (minimum 10 characters)",
                })
                score -= 5.0

        # Validate experience
        if "experience" in response_data:
            exp_issues = self._validate_experience(response_data["experience"])
            issues.extend(exp_issues)
            score -= len(exp_issues) * 5.0

        # Validate skills
        if "skills" in response_data:
            skills = response_data["skills"]
            if not isinstance(skills, list):
                issues.append({
                    "type": "invalid_type",
                    "section": "skills",
                    "message": "Skills must be a list",
                })
                score -= 10.0
            elif len(skills) == 0:
                issues.append({
                    "type": "empty_section",
                    "section": "skills",
                    "message": "Skills list is empty",
                })
                score -= 5.0

        # Validate against custom output schema if provided
        if output_schema:
            schema_issues = self._validate_against_schema(response_data, output_schema)
            issues.extend(schema_issues)
            score -= len(schema_issues) * 3.0

        # Validate data types for known fields
        type_issues = self._validate_data_types(response_data)
        issues.extend(type_issues)
        score -= len(type_issues) * 2.0

        score = max(0.0, min(100.0, score))
        is_valid = score >= 50.0 and len([i for i in issues if i["type"] in ("missing_section", "empty_response")]) == 0

        details["total_issues"] = len(issues)
        details["score"] = score
        details["sections_found"] = [k for k in response_data.keys() if k in VALID_SECTION_KEYS]

        return is_valid, score, issues, details

    def _validate_experience(self, experience: Any) -> List[Dict[str, Any]]:
        """Validate experience entries."""
        issues = []

        if not isinstance(experience, list):
            issues.append({
                "type": "invalid_type",
                "section": "experience",
                "message": "Experience must be a list",
            })
            return issues

        for i, entry in enumerate(experience):
            if not isinstance(entry, dict):
                issues.append({
                    "type": "invalid_entry",
                    "section": "experience",
                    "index": i,
                    "message": f"Experience entry {i} is not a dictionary",
                })
                continue

            for field in VALID_EXPERIENCE_FIELDS:
                if field not in entry:
                    issues.append({
                        "type": "missing_field",
                        "section": "experience",
                        "index": i,
                        "field": field,
                        "message": f"Experience entry {i} missing field '{field}'",
                    })

            if "description" in entry and isinstance(entry["description"], list):
                if len(entry["description"]) == 0:
                    issues.append({
                        "type": "empty_bullets",
                        "section": "experience",
                        "index": i,
                        "message": f"Experience entry {i} has no bullet points",
                    })

        return issues

    def _validate_against_schema(
        self, data: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Validate data against a custom output schema."""
        issues = []

        if "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    issues.append({
                        "type": "schema_violation",
                        "field": field,
                        "message": f"Required field '{field}' missing per output schema",
                    })

        if "properties" in schema:
            for field, props in schema["properties"].items():
                if field in data:
                    expected_type = props.get("type")
                    if expected_type == "string" and not isinstance(data[field], str):
                        issues.append({
                            "type": "schema_type_mismatch",
                            "field": field,
                            "message": f"Field '{field}' should be string",
                        })
                    elif expected_type == "array" and not isinstance(data[field], list):
                        issues.append({
                            "type": "schema_type_mismatch",
                            "field": field,
                            "message": f"Field '{field}' should be array",
                        })

        return issues

    def _validate_data_types(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate data types for known fields."""
        issues = []

        type_map = {
            "summary": str,
            "skills": list,
            "experience": list,
            "education": list,
            "projects": list,
            "certifications": list,
            "achievements": list,
        }

        for field, expected_type in type_map.items():
            if field in data and not isinstance(data[field], expected_type):
                issues.append({
                    "type": "type_mismatch",
                    "field": field,
                    "message": f"Field '{field}' should be {expected_type.__name__}",
                })

        return issues
