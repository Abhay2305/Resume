"""System Prompt Builder.

Creates system-level prompts with platform rules, AI behavior, and output constraints.
"""
import json
import os
from typing import Any, Dict, List, Optional


class SystemPromptBuilder:
    """Builds system prompts for AI interactions."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        filepath = os.path.join(self.data_dir, "prompt_templates.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def build(self, prompt_type: str = "resume_tailoring") -> str:
        """Build system prompt for given type."""
        system_prompts = self._templates.get("system_prompts", {})
        prompt_data = system_prompts.get(prompt_type, system_prompts.get("resume_tailoring", {}))
        return prompt_data.get("content", "")

    def build_with_context(
        self,
        prompt_type: str,
        additional_rules: Optional[List[str]] = None,
    ) -> str:
        """Build system prompt with additional rules."""
        base_prompt = self.build(prompt_type)
        if additional_rules:
            rules_text = "\n\nAdditional Rules:\n" + "\n".join(f"- {rule}" for rule in additional_rules)
            return base_prompt + rules_text
        return base_prompt
