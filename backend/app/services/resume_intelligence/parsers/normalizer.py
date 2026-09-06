"""Resume Normalizer.

Responsible for cleaning text, standardizing formatting,
normalizing whitespace, and standardizing extracted values.
"""
import re
from typing import Any, Dict, List, Optional


class ResumeNormalizer:
    """Normalizes parsed resume data."""

    def normalize(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all fields in parsed data.

        Args:
            parsed_data: Parsed data from ResumeParser.

        Returns:
            Normalized data with clean text and standardized values.
        """
        sections = parsed_data.get("sections", {})
        metadata = parsed_data.get("metadata", {})

        normalized_sections = {}
        for section_name, content in sections.items():
            normalized_sections[section_name] = self._clean_text(content)

        return {
            "raw_text": parsed_data.get("raw_text", ""),
            "sections": normalized_sections,
            "metadata": metadata,
        }

    def _clean_text(self, text: str) -> str:
        """Clean text by removing special characters and normalizing."""
        if not text:
            return ""
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        return text.strip()

    def normalize_list(self, items: List[str]) -> List[str]:
        """Normalize a list of strings."""
        if not items:
            return []
        normalized = []
        seen = set()
        for item in items:
            clean_item = self._clean_text(item).lower()
            if clean_item and clean_item not in seen:
                seen.add(clean_item)
                normalized.append(clean_item)
        return sorted(normalized)

    def normalize_date(self, value: str) -> Optional[str]:
        """Standardize date format to YYYY-MM-DD or YYYY-MM."""
        if not value:
            return None
        value = value.strip()
        month_map = {
            "jan": "01", "january": "01", "feb": "02", "february": "02",
            "mar": "03", "march": "03", "apr": "04", "april": "04",
            "may": "05", "jun": "06", "june": "06",
            "jul": "07", "july": "07", "aug": "08", "august": "08",
            "sep": "09", "september": "09", "oct": "10", "october": "10",
            "nov": "11", "november": "11", "dec": "12", "december": "12",
        }
        for month_name, month_num in month_map.items():
            if month_name in value.lower():
                year_match = re.search(r"(\d{4})", value)
                if year_match:
                    return f"{year_match.group(1)}-{month_num}"
        year_match = re.search(r"(\d{4})", value)
        if year_match:
            return year_match.group(1)
        return value

    def normalize_experience_level(self, value: str) -> str:
        """Standardize experience level."""
        if not value:
            return ""
        value_lower = value.lower().strip()
        level_mapping = {
            "junior": "junior", "entry level": "junior", "entry-level": "junior",
            "associate": "junior", "graduate": "junior",
            "mid": "mid", "mid level": "mid", "mid-level": "mid",
            "intermediate": "mid", "experienced": "mid",
            "senior": "senior", "sr.": "senior", "sr": "senior", "seasoned": "senior",
            "lead": "lead", "tech lead": "lead", "team lead": "lead",
            "staff": "staff", "principal": "principal",
            "director": "director", "vp": "executive", "cto": "executive",
        }
        return level_mapping.get(value_lower, value_lower)
