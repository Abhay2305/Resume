"""Instruction Builder.

Creates deterministic instructions for AI prompts.
"""
import json
import os
from typing import Any, Dict, List, Optional


class InstructionBuilder:
    """Builds instructions for prompts."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        filepath = os.path.join(self.data_dir, "prompt_templates.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def build(self, prompt_type: str = "resume_tailoring") -> List[Dict[str, Any]]:
        instructions = self._templates.get("instructions", {})
        return instructions.get(prompt_type, instructions.get("resume_tailoring", []))

    def build_with_context(
        self,
        prompt_type: str,
        gap_categories: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        base_instructions = self.build(prompt_type)
        contextual = list(base_instructions)
        if gap_categories:
            for category in gap_categories:
                contextual.append({
                    "id": f"INST_CTX_{category.upper()}",
                    "instruction": f"Focus on improving {category} section based on gap analysis.",
                    "priority": "high",
                    "category": category,
                })
        if recommendations:
            for rec in recommendations[:5]:
                contextual.append({
                    "id": f"INST_REC_{rec.get('action', 'unknown').upper()}",
                    "instruction": rec.get("description", ""),
                    "priority": rec.get("priority", "medium"),
                    "category": rec.get("category", "general"),
                })
        return contextual


class ConstraintBuilder:
    """Builds constraints for prompts."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        filepath = os.path.join(self.data_dir, "prompt_templates.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def build(self, prompt_type: str = "resume_tailoring") -> List[Dict[str, Any]]:
        constraints = self._templates.get("constraints", {})
        universal = constraints.get("universal", [])
        specific = constraints.get(prompt_type, [])
        return universal + specific

    def build_text(self, prompt_type: str = "resume_tailoring") -> str:
        constraints = self.build(prompt_type)
        return "\n".join(f"- {c['constraint']}" for c in constraints)
