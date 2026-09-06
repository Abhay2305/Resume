"""Location Extractor.

Extracts location and work arrangement from opportunity text.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models.opportunity import EntityType


class LocationExtractor:
    """Extracts location information from opportunity sections."""

    def __init__(self):
        self.location_data = self._load_data("location_patterns.json")
        self.employment_data = self._load_data("employment_types.json")
        self.remote_keywords = self.location_data.get("remote_keywords", [])
        self.hybrid_keywords = self.location_data.get("hybrid_keywords", [])
        self.onsite_keywords = self.location_data.get("onsite_keywords", [])
        self.common_locations = self.location_data.get("common_locations", {})
        self.employment_types = self.employment_data.get("types", {})

    def _load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract location and employment information from sections.

        Args:
            sections: Detected sections from parser.

        Returns:
            Dictionary with 'entities' list and 'parsed_data' dict.
        """
        entities = []
        parsed_data = {}

        all_text = "\n".join(sections.values())

        # Extract remote policy
        remote_policy = self._extract_remote_policy(all_text)
        if remote_policy:
            parsed_data["remote_policy"] = remote_policy
            entities.append({
                "entity_type": EntityType.REMOTE_POLICY.value,
                "entity_value": remote_policy,
                "is_required": True,
            })

        # Extract location
        location = self._extract_location(all_text)
        if location:
            entities.append({
                "entity_type": EntityType.LOCATION.value,
                "entity_value": location,
                "is_required": True,
            })

        # Extract employment type
        employment_type = self._extract_employment_type(all_text)
        if employment_type:
            parsed_data["employment_type"] = employment_type
            entities.append({
                "entity_type": EntityType.EMPLOYMENT_TYPE.value,
                "entity_value": employment_type,
                "is_required": True,
            })

        return {"entities": entities, "parsed_data": parsed_data}

    def _extract_remote_policy(self, text: str) -> Optional[str]:
        """Extract remote work policy from text.

        Args:
            text: Text to extract from.

        Returns:
            Remote policy string.
        """
        text_lower = text.lower()

        for keyword in self.remote_keywords:
            if keyword in text_lower:
                return "remote"

        for keyword in self.hybrid_keywords:
            if keyword in text_lower:
                return "hybrid"

        for keyword in self.onsite_keywords:
            if keyword in text_lower:
                return "onsite"

        return None

    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text.

        Args:
            text: Text to extract from.

        Returns:
            Location string.
        """
        text_lower = text.lower()

        # Check for common locations
        for region, locations in self.common_locations.items():
            for location in locations:
                if location.lower() in text_lower:
                    return location

        return None

    def _extract_employment_type(self, text: str) -> Optional[str]:
        """Extract employment type from text.

        Args:
            text: Text to extract from.

        Returns:
            Employment type string.
        """
        text_lower = text.lower()

        for emp_type, aliases in self.employment_types.items():
            for alias in aliases:
                if alias.lower() in text_lower:
                    return emp_type

        return None
