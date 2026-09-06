"""Education Extractor.

Extracts education entries from resume sections.
"""
import re
from typing import Any, Dict, List, Optional

DEGREE_PATTERNS = [
    r"\b(bachelor(?:'s|s)?|b\.?s\.?|b\.?a\.?|b\.?e\.?|b\.?tech\.?)\b",
    r"\b(master(?:'s|s)?|m\.?s\.?|m\.?a\.?|m\.?e\.?|m\.?tech\.?|mba)\b",
    r"\b(ph\.?d\.?|doctorate|doctoral)\b",
    r"\b(associate(?:'s|s)?|a\.?a\.?|a\.?s\.?)\b",
    r"\b(diploma|certificate|cert)\b",
]

FIELDS_OF_STUDY = [
    "computer science", "computer engineering", "software engineering",
    "information technology", "data science", "electrical engineering",
    "mechanical engineering", "mathematics", "physics", "chemistry",
    "business", "economics", "finance", "accounting", "marketing",
    "biology", "chemistry", "psychology", "sociology", "communications",
    "graphic design", "fine arts", "liberal arts", "political science",
]


class EducationExtractor:
    """Extracts education from resume sections."""

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        parsed_data = {}

        edu_text = sections.get("education", "")
        all_text = "\n".join(sections.values())

        degrees_found = []
        for pattern in DEGREE_PATTERNS:
            matches = re.findall(pattern, all_text.lower())
            for match in matches:
                clean = match.strip()
                if clean and clean not in degrees_found:
                    degrees_found.append(clean)
                    entities.append({
                        "entity_type": "degree",
                        "entity_value": clean,
                    })

        fields_found = []
        for field in FIELDS_OF_STUDY:
            if field.lower() in all_text.lower():
                if field not in fields_found:
                    fields_found.append(field)
                    entities.append({
                        "entity_type": "field_of_study",
                        "entity_value": field,
                    })

        institutions = self._extract_institutions(edu_text or all_text)
        if institutions:
            parsed_data["institutions"] = institutions

        return {"entities": entities, "parsed_data": parsed_data}

    def _extract_institutions(self, text: str) -> List[str]:
        if not text:
            return []
        institutions = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if any(kw in line.lower() for kw in ["university", "college", "institute", "school", "academy"]):
                if len(line) < 100:
                    institutions.append(line)
        return institutions
