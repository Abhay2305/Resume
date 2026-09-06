"""Extractor Orchestrator.

Coordinates all extractors to extract entities from parsed opportunity data.
"""
from typing import Any, Dict, List

from app.services.opportunity.extractors.experience_extractor import ExperienceExtractor
from app.services.opportunity.extractors.location_extractor import LocationExtractor
from app.services.opportunity.extractors.metadata_extractor import MetadataExtractor
from app.services.opportunity.extractors.skill_extractor import SkillExtractor
from app.services.opportunity.extractors.technology_extractor import TechnologyExtractor


class ExtractorOrchestrator:
    """Orchestrates all extractors to extract entities from sections."""

    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.technology_extractor = TechnologyExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.location_extractor = LocationExtractor()
        self.metadata_extractor = MetadataExtractor()

    def extract(self, sections: Dict[str, str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all entities from sections.

        Args:
            sections: Detected sections from parser.
            metadata: Metadata from parser.

        Returns:
            Dictionary with 'entities' list and 'parsed_data' dict.
        """
        all_entities = []
        all_parsed_data = {}

        # Extract skills
        result = self.skill_extractor.extract(sections)
        all_entities.extend(result["entities"])

        # Extract technologies
        result = self.technology_extractor.extract(sections)
        all_entities.extend(result["entities"])

        # Extract experience
        result = self.experience_extractor.extract(sections)
        all_entities.extend(result["entities"])
        all_parsed_data.update(result["parsed_data"])

        # Extract location
        result = self.location_extractor.extract(sections)
        all_entities.extend(result["entities"])
        all_parsed_data.update(result["parsed_data"])

        # Extract metadata
        result = self.metadata_extractor.extract(sections)
        all_entities.extend(result["entities"])
        all_parsed_data.update(result["parsed_data"])

        return {
            "entities": all_entities,
            "parsed_data": all_parsed_data,
        }
