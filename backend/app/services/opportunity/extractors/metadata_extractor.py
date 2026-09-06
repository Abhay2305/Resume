"""Metadata Extractor.

Extracts responsibilities, benefits, ATS keywords, and other metadata.
"""
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


class MetadataExtractor:
    """Extracts metadata from opportunity sections."""

    def __init__(self):
        self.section_headers = self._load_data("section_headers.json")
        self.stop_words = self._get_stop_words()

    def _load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def _get_stop_words(self) -> set:
        """Get common stop words to filter out."""
        return {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can", "need",
            "dare", "ought", "used", "this", "that", "these", "those", "i", "you",
            "he", "she", "it", "we", "they", "what", "which", "who", "whom",
            "whose", "where", "when", "why", "how", "all", "each", "every",
            "both", "few", "more", "most", "other", "some", "such", "no", "not",
            "only", "own", "same", "so", "than", "too", "very", "just", "because",
            "if", "then", "else", "while", "about", "up", "out", "off", "over",
            "under", "again", "further", "once", "here", "there", "also",
        }

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract metadata from sections.

        Args:
            sections: Detected sections from parser.

        Returns:
            Dictionary with 'entities' list and 'parsed_data' dict.
        """
        entities = []
        parsed_data = {}

        # Extract responsibilities
        responsibilities = self._extract_list_items(sections.get("responsibilities", ""))
        if responsibilities:
            parsed_data["responsibilities"] = responsibilities

        # Extract benefits
        benefits = self._extract_list_items(sections.get("benefits", ""))
        if benefits:
            parsed_data["benefits"] = benefits

        # Extract ATS keywords
        all_text = "\n".join(sections.values())
        ats_keywords = self._extract_ats_keywords(all_text)
        if ats_keywords:
            parsed_data["ats_keywords"] = ats_keywords

        # Store raw sections for debugging
        parsed_data["raw_sections"] = sections

        return {"entities": entities, "parsed_data": parsed_data}

    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text (bullet points, numbered items).

        Args:
            text: Text to extract from.

        Returns:
            List of extracted items.
        """
        if not text:
            return []

        items = []

        # Match bullet points (-, *, •, ▪, ▸)
        bullet_pattern = r"^[\s]*[-*•▪▸]\s+(.+)$"
        for match in re.finditer(bullet_pattern, text, re.MULTILINE):
            item = match.group(1).strip()
            if item:
                items.append(item)

        # Match numbered items (1., 2., etc.)
        number_pattern = r"^[\s]*\d+[\.\)]\s+(.+)$"
        for match in re.finditer(number_pattern, text, re.MULTILINE):
            item = match.group(1).strip()
            if item:
                items.append(item)

        # If no list items found, split by newlines
        if not items:
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            items = lines

        return items

    def _extract_ats_keywords(self, text: str) -> List[str]:
        """Extract ATS-friendly keywords from text.

        Args:
            text: Text to extract from.

        Returns:
            List of important keywords.
        """
        if not text:
            return []

        # Tokenize and count word frequencies
        words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
        word_freq = Counter(words)

        # Filter out stop words and get top keywords
        keywords = [
            word for word, count in word_freq.most_common(50)
            if word not in self.stop_words and count >= 2
        ]

        return keywords[:20]  # Return top 20 keywords
