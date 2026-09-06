"""Opportunity Normalizer.

Responsible for cleaning text, standardizing formatting,
normalizing whitespace, and standardizing extracted values.
"""
import re
from typing import Any, Dict, List, Optional


class OpportunityNormalizer:
    """Normalizes parsed opportunity data."""

    def normalize(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all fields in parsed data.

        Args:
            parsed_data: Parsed data from OpportunityParser.

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
        """Clean text by removing special characters and normalizing.

        Args:
            text: Text to clean.

        Returns:
            Cleaned text.
        """
        if not text:
            return ""

        # Remove multiple spaces
        text = re.sub(r" +", " ", text)

        # Remove multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def normalize_list(self, items: List[str]) -> List[str]:
        """Normalize a list of strings.

        Args:
            items: List of strings to normalize.

        Returns:
            Deduplicated, sorted list of normalized strings.
        """
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

    def normalize_employment_type(self, value: str) -> str:
        """Standardize employment type.

        Args:
            value: Employment type string.

        Returns:
            Standardized employment type.
        """
        if not value:
            return ""

        value_lower = value.lower().strip()

        type_mapping = {
            "full-time": "full-time",
            "full time": "full-time",
            "ft": "full-time",
            "permanent": "full-time",
            "regular": "full-time",
            "part-time": "part-time",
            "part time": "part-time",
            "pt": "part-time",
            "contract": "contract",
            "contractor": "contract",
            "1099": "contract",
            "freelance": "freelance",
            "freelancer": "freelance",
            "independent": "freelance",
            "internship": "internship",
            "intern": "internship",
            "co-op": "internship",
            "temporary": "temporary",
            "temp": "temporary",
            "fixed-term": "temporary",
        }

        return type_mapping.get(value_lower, value_lower)

    def normalize_remote_policy(self, value: str) -> str:
        """Standardize remote policy.

        Args:
            value: Remote policy string.

        Returns:
            Standardized remote policy.
        """
        if not value:
            return ""

        value_lower = value.lower().strip()

        remote_keywords = [
            "remote", "work from home", "wfh", "distributed",
            "fully remote", "100% remote", "all remote",
        ]
        hybrid_keywords = [
            "hybrid", "flexible", "flex", "mixed",
            "partial remote", "partially remote",
        ]
        onsite_keywords = [
            "onsite", "on-site", "in-office", "in office",
            "on campus", "at office", "office based",
        ]

        for keyword in remote_keywords:
            if keyword in value_lower:
                return "remote"

        for keyword in hybrid_keywords:
            if keyword in value_lower:
                return "hybrid"

        for keyword in onsite_keywords:
            if keyword in value_lower:
                return "onsite"

        return value_lower

    def normalize_experience_level(self, value: str) -> str:
        """Standardize experience level.

        Args:
            value: Experience level string.

        Returns:
            Standardized experience level.
        """
        if not value:
            return ""

        value_lower = value.lower().strip()

        level_mapping = {
            "junior": "junior",
            "entry level": "junior",
            "entry-level": "junior",
            "associate": "junior",
            "graduate": "junior",
            "intern": "junior",
            "trainee": "junior",
            "mid": "mid",
            "mid level": "mid",
            "mid-level": "mid",
            "intermediate": "mid",
            "experienced": "mid",
            "senior": "senior",
            "sr.": "senior",
            "sr": "senior",
            "seasoned": "senior",
            "lead": "lead",
            "tech lead": "lead",
            "technical lead": "lead",
            "team lead": "lead",
            "engineering lead": "lead",
            "staff": "staff",
            "staff engineer": "staff",
            "principal": "principal",
            "principal engineer": "principal",
            "director": "director",
            "engineering director": "director",
            "director of engineering": "director",
            "vp": "executive",
            "vice president": "executive",
            "cto": "executive",
            "ceo": "executive",
            "executive": "executive",
            "chief": "executive",
        }

        return level_mapping.get(value_lower, value_lower)
