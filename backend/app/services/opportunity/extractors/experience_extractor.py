"""Experience Extractor.

Extracts experience requirements from opportunity text.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.models.opportunity import EntityType


class ExperienceExtractor:
    """Extracts experience requirements from opportunity sections."""

    def __init__(self):
        self.experience_data = self._load_data("experience_patterns.json")
        self.education_data = self._load_data("education.json")
        self.years_patterns = [
            re.compile(pattern) for pattern in self.experience_data.get("years_patterns", [])
        ]
        self.level_keywords = self.experience_data.get("level_keywords", {})
        self.level_mapping = self.experience_data.get("level_mapping", {})

    def _load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract experience requirements from sections.

        Args:
            sections: Detected sections from parser.

        Returns:
            Dictionary with 'entities' list and 'parsed_data' dict.
        """
        entities = []
        parsed_data = {}

        all_text = "\n".join(sections.values())

        # Extract years of experience
        min_years, max_years = self._extract_years(all_text)
        if min_years is not None:
            parsed_data["min_experience_years"] = min_years
        if max_years is not None:
            parsed_data["max_experience_years"] = max_years

        # Extract experience level
        level = self._extract_level(all_text)
        if level:
            parsed_data["experience_level"] = level
            entities.append({
                "entity_type": EntityType.EXPERIENCE_LEVEL.value,
                "entity_value": level,
                "is_required": True,
            })

        # Extract education requirements
        education_reqs = self._extract_education(all_text)
        for edu in education_reqs:
            entities.append({
                "entity_type": EntityType.EDUCATION.value,
                "entity_value": edu,
                "is_required": True,
            })

        return {"entities": entities, "parsed_data": parsed_data}

    def _extract_years(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract years of experience from text.

        Args:
            text: Text to extract from.

        Returns:
            Tuple of (min_years, max_years).
        """
        min_years = None
        max_years = None

        for pattern in self.years_patterns:
            match = pattern.search(text)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    min_years = int(groups[0])
                    max_years = int(groups[1])
                elif len(groups) == 1:
                    min_years = int(groups[0])
                    max_years = min_years
                break

        return min_years, max_years

    def _extract_level(self, text: str) -> Optional[str]:
        """Extract experience level from text.

        Args:
            text: Text to extract from.

        Returns:
            Experience level string.
        """
        text_lower = text.lower()

        for level, keywords in self.level_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level

        return None

    def _extract_education(self, text: str) -> List[str]:
        """Extract education requirements from text.

        Args:
            text: Text to extract from.

        Returns:
            List of education requirements.
        """
        education_reqs = []

        degrees = self.education_data.get("degrees", [])
        fields = self.education_data.get("fields", [])

        text_lower = text.lower()

        # Check for degree requirements
        for degree in degrees:
            if degree.lower() in text_lower:
                education_reqs.append(degree)

        # Check for field requirements
        for field in fields:
            if field.lower() in text_lower:
                education_reqs.append(field)

        return list(set(education_reqs))
