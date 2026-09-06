"""Experience Extractor.

Extracts work experience entries from resume sections.
"""
import re
from typing import Any, Dict, List, Optional

DATE_RANGE_PATTERN = r"(\w+\s+\d{4})\s*[-–—]\s*(\w+\s+\d{4}|present|current|now)"
COMPANY_ROLE_PATTERN = r"^([^,\n]+),?\s*([^\n]+)?$"


class ExperienceExtractor:
    """Extracts experience from resume sections."""

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        parsed_data = {}

        exp_text = sections.get("experience", "")
        if not exp_text:
            return {"entities": entities, "parsed_data": parsed_data}

        entries = self._parse_experience_entries(exp_text)
        parsed_data["experience_entries"] = entries

        for entry in entries:
            if entry.get("role"):
                entities.append({
                    "entity_type": "role",
                    "entity_value": entry["role"],
                })
            if entry.get("company"):
                entities.append({
                    "entity_type": "company",
                    "entity_value": entry["company"],
                })
            if entry.get("duration_months"):
                entities.append({
                    "entity_type": "metric",
                    "entity_value": f"{entry['duration_months']} months",
                    "entity_metadata": {"metric_type": "duration"},
                })

        return {"entities": entities, "parsed_data": parsed_data}

    def _parse_experience_entries(self, text: str) -> List[Dict[str, Any]]:
        entries = []
        blocks = re.split(r"\n\s*\n", text)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            entry = {"raw_text": block, "bullets": []}
            lines = block.split("\n")

            header_line = lines[0] if lines else ""
            date_match = re.search(DATE_RANGE_PATTERN, header_line, re.IGNORECASE)
            if date_match:
                entry["start_date"] = date_match.group(1).strip()
                entry["end_date"] = date_match.group(2).strip()

            parts = header_line.split(" at ", 1)
            if len(parts) == 2:
                entry["role"] = parts[0].strip()
                entry["company"] = parts[1].strip()
            else:
                parts = header_line.split(" - ", 1)
                if len(parts) == 2:
                    entry["company"] = parts[0].strip()
                    entry["role"] = parts[1].strip()
                else:
                    entry["role"] = header_line.strip()

            for line in lines[1:]:
                line = line.strip()
                if line.startswith(("-", "•", "*", "–")):
                    bullet = line.lstrip("-•*– ").strip()
                    if bullet:
                        entry["bullets"].append(bullet)

            if entry.get("role") or entry.get("company") or entry.get("bullets"):
                entries.append(entry)

        return entries
