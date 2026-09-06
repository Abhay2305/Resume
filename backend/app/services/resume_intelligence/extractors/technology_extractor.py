"""Technology Extractor.

Extracts technologies from resume sections.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List


class TechnologyExtractor:
    """Extracts technologies from resume sections."""

    def __init__(self):
        self.skills_data = self._load_data("skills.json")

    def _load_data(self, filename: str) -> Dict[str, Any]:
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        all_text = "\n".join(sections.values())

        tech_categories = {
            "web_frameworks": "framework",
            "data_science": "technology",
            "devops_tools": "devops_tool",
            "cloud_platforms": "cloud_platform",
            "databases": "database",
            "mobile": "technology",
            "testing": "technology",
            "ai_ml": "ai_ml",
        }

        for category, entity_type in tech_categories.items():
            items = self.skills_data.get(category, [])
            for item in items:
                if len(item) <= 3:
                    pattern = r"\b" + re.escape(item) + r"\b"
                    if re.search(pattern, all_text.lower()):
                        entities.append({
                            "entity_type": entity_type,
                            "entity_value": item,
                        })
                else:
                    if item.lower() in all_text.lower():
                        entities.append({
                            "entity_type": entity_type,
                            "entity_value": item,
                        })

        seen = set()
        unique_entities = []
        for e in entities:
            key = (e["entity_type"], e["entity_value"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)

        return {"entities": unique_entities}
