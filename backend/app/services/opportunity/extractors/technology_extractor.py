"""Technology Extractor.

Extracts technology stack items from opportunity text.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from app.models.opportunity import EntityType


class TechnologyExtractor:
    """Extracts technologies from opportunity sections."""

    def __init__(self):
        self.technologies_data = self._load_data("skills.json")
        self.technology_categories = {
            "language": self.technologies_data.get("programming_languages", []),
            "framework": self.technologies_data.get("web_frameworks", []),
            "database": self.technologies_data.get("databases", []),
            "cloud_platform": self.technologies_data.get("cloud_platforms", []),
            "devops_tool": self.technologies_data.get("devops_tools", []),
            "ai_ml": self.technologies_data.get("ai_ml_tools", []),
        }

    def _load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract technologies from sections.

        Args:
            sections: Detected sections from parser.

        Returns:
            Dictionary with 'entities' list containing technology entities.
        """
        entities = []

        # Combine all text for technology extraction
        all_text = "\n".join(sections.values())

        for entity_type, tech_list in self.technology_categories.items():
            found_techs = self._extract_techs_from_text(all_text, tech_list)
            for tech in found_techs:
                entities.append({
                    "entity_type": entity_type,
                    "entity_value": tech,
                    "is_required": True,
                })

        return {"entities": entities}

    def _extract_techs_from_text(self, text: str, tech_list: List[str]) -> List[str]:
        """Extract technologies from text using dictionary matching.

        Args:
            text: Text to extract technologies from.
            tech_list: List of technologies to match.

        Returns:
            List of matched technologies.
        """
        if not text:
            return []

        text_lower = text.lower()
        found_techs = []

        for tech in tech_list:
            # Use word boundary matching for short techs
            if len(tech) <= 3:
                pattern = r"\b" + re.escape(tech) + r"\b"
                if re.search(pattern, text_lower):
                    found_techs.append(tech)
            else:
                # For longer techs, just check if they appear in the text
                if tech in text_lower:
                    found_techs.append(tech)

        return list(set(found_techs))
