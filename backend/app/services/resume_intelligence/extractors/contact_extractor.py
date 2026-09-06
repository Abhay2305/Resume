"""Contact Extractor.

Extracts personal and contact information from resume sections.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List


class ContactExtractor:
    """Extracts contact information from resume sections."""

    def __init__(self):
        self.contact_data = self._load_data("contact_patterns.json")

    def _load_data(self, filename: str) -> Dict[str, Any]:
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        parsed_data = {}

        contact_text = sections.get("contact", "")
        general_text = sections.get("general", "")
        all_text = contact_text or general_text

        if not all_text:
            return {"entities": entities, "parsed_data": parsed_data}

        emails = re.findall(self.contact_data["email_pattern"], all_text)
        if emails:
            parsed_data["email"] = emails[0]
            entities.append({
                "entity_type": "contact",
                "entity_value": emails[0],
                "entity_metadata": {"contact_type": "email"},
            })

        for pattern in self.contact_data["phone_patterns"]:
            phones = re.findall(pattern, all_text)
            if phones:
                parsed_data["phone"] = phones[0]
                entities.append({
                    "entity_type": "contact",
                    "entity_value": phones[0],
                    "entity_metadata": {"contact_type": "phone"},
                })
                break

        for pattern in self.contact_data["linkedin_patterns"]:
            linkedin = re.findall(pattern, all_text)
            if linkedin:
                parsed_data["linkedin"] = linkedin[0]
                entities.append({
                    "entity_type": "contact",
                    "entity_value": linkedin[0],
                    "entity_metadata": {"contact_type": "linkedin"},
                })
                break

        for pattern in self.contact_data["github_patterns"]:
            github = re.findall(pattern, all_text)
            if github:
                parsed_data["github"] = github[0]
                entities.append({
                    "entity_type": "contact",
                    "entity_value": github[0],
                    "entity_metadata": {"contact_type": "github"},
                })
                break

        for pattern in self.contact_data["website_patterns"]:
            websites = re.findall(pattern, all_text)
            if websites:
                parsed_data["website"] = websites[0]
                entities.append({
                    "entity_type": "contact",
                    "entity_value": websites[0],
                    "entity_metadata": {"contact_type": "website"},
                })
                break

        first_line = all_text.split("\n")[0].strip()
        if first_line and not re.search(r"@", first_line) and len(first_line) < 60:
            parsed_data["name"] = first_line
            entities.append({
                "entity_type": "personal_info",
                "entity_value": first_line,
                "entity_metadata": {"field": "name"},
            })

        for keyword in self.contact_data["location_keywords"]:
            if keyword.lower() in all_text.lower():
                parsed_data["location"] = keyword
                entities.append({
                    "entity_type": "contact",
                    "entity_value": keyword,
                    "entity_metadata": {"contact_type": "location"},
                })
                break

        return {"entities": entities, "parsed_data": parsed_data}
