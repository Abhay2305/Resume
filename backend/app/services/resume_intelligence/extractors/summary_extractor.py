"""Summary Extractor.

Extracts the professional summary from resume sections.
"""
from typing import Any, Dict


class SummaryExtractor:
    """Extracts summary from resume sections."""

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        parsed_data = {}

        summary_text = sections.get("summary", "")
        if summary_text:
            parsed_data["summary"] = summary_text

        return {"entities": [], "parsed_data": parsed_data}
