"""Prompt Validator.

Validates prompt packages before storage.
"""
from typing import Any, Dict, List, Optional


class PromptValidator:
    """Validates prompt packages."""

    MAX_TOKENS = 100000
    MIN_TOKENS = 100

    def validate(self, package: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        warnings = []
        if not package.get("system_prompt"):
            errors.append("System prompt is required")
        if not package.get("resume_context"):
            warnings.append("Resume context is empty")
        if not package.get("instructions"):
            warnings.append("No instructions provided")
        if not package.get("constraints"):
            warnings.append("No constraints provided")
        if not package.get("output_schema"):
            errors.append("Output schema is required")
        unresolved = self._check_unresolved_placeholders(package)
        if unresolved:
            errors.append(f"Unresolved placeholders: {', '.join(unresolved)}")
        duplicates = self._check_duplicates(package)
        if duplicates:
            warnings.append(f"Potential duplicate context: {', '.join(duplicates)}")
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def _check_unresolved_placeholders(self, package: Dict[str, Any]) -> List[str]:
        placeholders = []
        text = package.get("system_prompt", "")
        if "{{" in text and "}}" in text:
            import re
            found = re.findall(r"\{\{(\w+)\}\}", text)
            placeholders.extend(found)
        return placeholders

    def _check_duplicates(self, package: Dict[str, Any]) -> List[str]:
        duplicates = []
        instructions = package.get("instructions", [])
        if isinstance(instructions, list):
            seen = set()
            for inst in instructions:
                if isinstance(inst, dict):
                    text = inst.get("instruction", "")
                    if text in seen:
                        duplicates.append(f"Duplicate instruction: {text[:50]}")
                    seen.add(text)
        return duplicates

    def estimate_tokens(self, package: Dict[str, Any]) -> int:
        import json
        total_text = package.get("system_prompt", "")
        for key in ["resume_context", "opportunity_context", "gap_context", "knowledge_context"]:
            ctx = package.get(key, {})
            if isinstance(ctx, dict):
                total_text += json.dumps(ctx)
        for key in ["instructions", "constraints"]:
            items = package.get(key, [])
            if isinstance(items, list):
                total_text += json.dumps(items)
        schema = package.get("output_schema", {})
        total_text += json.dumps(schema)
        return len(total_text) // 4
