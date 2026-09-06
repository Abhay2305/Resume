"""Output Schema Builder.

Defines expected AI response format.
"""
import json
import os
from typing import Any, Dict


class OutputSchemaBuilder:
    """Builds output schema definitions."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        self._templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        filepath = os.path.join(self.data_dir, "prompt_templates.json")
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def build(self, prompt_type: str = "resume_tailoring") -> Dict[str, Any]:
        schemas = self._templates.get("output_schemas", {})
        return schemas.get(prompt_type, schemas.get("resume_tailoring", {}))

    def build_text(self, prompt_type: str = "resume_tailoring") -> str:
        schema = self.build(prompt_type)
        return json.dumps(schema, indent=2)
