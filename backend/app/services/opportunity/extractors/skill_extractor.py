"""Skill Extractor.

Extracts required and preferred skills from opportunity text.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.models.opportunity import EntityType


class SkillExtractor:
    """Extracts skills from opportunity sections."""

    def __init__(self):
        self.skills_data = self._load_data("skills.json")
        self.all_skills = self._build_skill_index()

    def _load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def _build_skill_index(self) -> List[str]:
        """Build a flat list of all skills for matching."""
        all_skills = []
        for category, skills in self.skills_data.items():
            if isinstance(skills, list):
                all_skills.extend(skills)
        return list(set(all_skills))

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract skills from sections.

        Args:
            sections: Detected sections from parser.

        Returns:
            Dictionary with 'entities' list containing skill entities.
        """
        entities = []

        requirements_text = sections.get("requirements", "")
        preferred_text = sections.get("preferred", "")
        general_text = sections.get("general", "")

        # Extract required skills from requirements section
        required_skills = self._extract_skills_from_text(requirements_text)
        for skill in required_skills:
            entities.append({
                "entity_type": EntityType.SKILL.value,
                "entity_value": skill,
                "is_required": True,
            })

        # Extract preferred skills from preferred section
        preferred_skills = self._extract_skills_from_text(preferred_text)
        for skill in preferred_skills:
            entities.append({
                "entity_type": EntityType.SKILL.value,
                "entity_value": skill,
                "is_required": False,
            })

        # If no specific sections found, extract from general text
        if not required_skills and not preferred_skills and general_text:
            skills = self._extract_skills_from_text(general_text)
            for skill in skills:
                entities.append({
                    "entity_type": EntityType.SKILL.value,
                    "entity_value": skill,
                    "is_required": True,
                })

        return {"entities": entities}

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from text using dictionary matching.

        Args:
            text: Text to extract skills from.

        Returns:
            List of matched skills.
        """
        if not text:
            return []

        text_lower = text.lower()
        found_skills = []

        for skill in self.all_skills:
            # Use word boundary matching for short skills
            if len(skill) <= 3:
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            else:
                # For longer skills, just check if they appear in the text
                if skill in text_lower:
                    found_skills.append(skill)

        return list(set(found_skills))
