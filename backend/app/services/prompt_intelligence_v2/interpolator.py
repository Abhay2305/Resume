"""Variable Interpolator — safe substitution of context variables into templates.

Handles {variable} syntax with required/optional variable validation,
nested context resolution, and MissingVariables error on missing requireds.
"""
import re
from typing import Any, Dict, List, Optional, Set

from app.services.prompt_intelligence_v2.errors import MissingVariables


class VariableInterpolator:
    """Safely substitutes context variables into template strings.

    Uses {variable} syntax (matching existing prompt_builder.py convention).
    Validates required variables before substitution.
    Supports optional variables with empty-string defaults.
    Supports nested context via dot notation (e.g., {resume.skills}).
    """

    PLACEHOLDER_RE = re.compile(r"\{(\w+(?:\.\w+)*)\}")

    def interpolate(
        self,
        template: str,
        context: Dict[str, Any],
        required_variables: Optional[List[str]] = None,
        optional_variables: Optional[Optional[List[str]]] = None,
        prompt_type: Optional[str] = None,
    ) -> str:
        """Substitute variables in template with context values.

        Args:
            template: Template string with {variable} placeholders.
            context: Dictionary of variable values.
            required_variables: Variables that MUST be present in context.
            optional_variables: Variables that MAY be absent (default to "").
            prompt_type: For error reporting.

        Returns:
            Template with all placeholders replaced.

        Raises:
            MissingVariables: If required variables are missing from context.
        """
        required = required_variables or []
        optional = optional_variables or []

        # Find all placeholders in the template
        placeholders = set(self.PLACEHOLDER_RE.findall(template))

        # Validate required variables (resolve dot paths)
        missing = []
        for v in required:
            if v in optional:
                continue
            # Resolve dot path
            value = context
            found = True
            for part in v.split("."):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    found = False
                    break
            if not found or value is None:
                missing.append(v)
        if missing:
            raise MissingVariables(sorted(missing), prompt_type=prompt_type)

        # Build substitution map
        def _resolve(name: str) -> str:
            # Support nested access: "resume.skills" -> context["resume"]["skills"]
            value = context
            for part in name.split("."):
                if isinstance(value, dict):
                    value = value.get(part, "")
                else:
                    value = ""
                    break
            if value is None:
                return ""
            return str(value)

        def _replace(match: re.Match) -> str:
            var_name = match.group(1)
            return _resolve(var_name)

        return self.PLACEHOLDER_RE.sub(_replace, template)

    def find_placeholders(self, template: str) -> Set[str]:
        """Find all variable placeholders in a template."""
        return set(self.PLACEHOLDER_RE.findall(template))

    def validate_template(
        self,
        template: str,
        required_variables: Optional[List[str]] = None,
        optional_variables: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Validate that a template's placeholders match its variable declarations.

        Returns a dict with:
            - placeholders: all {variable} names found in template
            - undeclared: placeholders not in required or optional lists
            - unused_required: required variables not appearing as placeholders
        """
        placeholders = self.find_placeholders(template)
        required = set(required_variables or [])
        optional = set(optional_variables or [])

        declared = required | optional
        undeclared = placeholders - declared
        unused_required = required - placeholders

        return {
            "placeholders": sorted(placeholders),
            "undeclared": sorted(undeclared),
            "unused_required": sorted(unused_required),
        }
