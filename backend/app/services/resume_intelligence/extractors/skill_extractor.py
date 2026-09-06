"""Skill Extractor.

Extracts skills from resume sections.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List


class SkillExtractor:
    """Extracts skills from resume sections."""

    def __init__(self):
        self.skills_data = self._load_data("skills.json")
        self.all_skills = self._build_skill_index()

    def _load_data(self, filename: str) -> Dict[str, Any]:
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def _build_skill_index(self) -> List[str]:
        all_skills = []
        for category, skills in self.skills_data.items():
            if isinstance(skills, list):
                all_skills.extend(skills)
        return list(set(all_skills))

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        skills_text = sections.get("skills", "")
        general_text = sections.get("general", "")
        text = skills_text or general_text

        if not text:
            return {"entities": entities}

        found_skills = self._extract_skills_from_text(text)
        for skill in found_skills:
            entities.append({
                "entity_type": "skill",
                "entity_value": skill,
            })

        return {"entities": entities}

    def _extract_skills_from_text(self, text: str) -> List[str]:
        if not text:
            return []
        text_lower = text.lower()
        found_skills = []
        for skill in self.all_skills:
            if len(skill) <= 3:
                pattern = r"\b" + re.escape(skill) + r"\b"
                if re.search(pattern, text_lower):
                    found_skills.append(skill)
            else:
                if skill in text_lower:
                    found_skills.append(skill)
        return list(set(found_skills))
