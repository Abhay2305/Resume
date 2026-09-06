"""Opportunity Parser.

Responsible for reading raw opportunity text, detecting sections,
and basic preprocessing.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


class OpportunityParser:
    """Parses raw opportunity text into structured sections."""

    def __init__(self):
        self.section_headers = self._load_data("section_headers.json")

    def _load_data(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def parse(self, raw_text: str) -> Dict[str, Any]:
        """Parse raw opportunity text into structured sections.

        Args:
            raw_text: The raw opportunity description text.

        Returns:
            Dictionary containing:
            - raw_text: The original text
            - sections: Detected sections (requirements, responsibilities, etc.)
            - metadata: Basic metadata about the text
        """
        if not raw_text or not raw_text.strip():
            return {"raw_text": raw_text, "sections": {}, "metadata": {}}

        preprocessed = self._preprocess(raw_text)
        sections = self._detect_sections(preprocessed)
        metadata = self._extract_metadata(preprocessed)

        return {
            "raw_text": raw_text,
            "sections": sections,
            "metadata": metadata,
        }

    def _preprocess(self, text: str) -> str:
        """Clean and preprocess the text.

        Args:
            text: Raw text to preprocess.

        Returns:
            Cleaned text.
        """
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Normalize unicode characters
        text = text.replace("\u2019", "'").replace("\u2018", "'")
        text = text.replace("\u201c", '"').replace("\u201d", '"')
        text = text.replace("\u2013", "-").replace("\u2014", "-")
        text = text.replace("\u2022", "-").replace("\u2023", "-")
        text = text.replace("\u25cf", "-").replace("\u25cb", "-")
        text = text.replace("\u2026", "...")

        # Normalize whitespace (preserve newlines for section detection)
        text = re.sub(r"[^\S\n]+", " ", text)  # Replace non-newline whitespace with single space
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Normalize multiple newlines to double newline
        text = re.sub(r"\n ", "\n", text)  # Remove leading spaces after newlines

        return text.strip()

    def _detect_sections(self, text: str) -> Dict[str, str]:
        """Detect and extract sections from the text.

        Args:
            text: Preprocessed text.

        Returns:
            Dictionary mapping section names to their content.
        """
        sections = {}

        # Split text into lines for section detection
        lines = text.split("\n")
        current_section = "general"
        current_content = []

        for line in lines:
            stripped_line = line.strip().lower()

            # Check if this line is a section header
            detected_section = self._match_section_header(stripped_line)

            if detected_section:
                # Save previous section if it has content
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = detected_section
                current_content = []
            else:
                current_content.append(line)

        # Save the last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _match_section_header(self, line: str) -> Optional[str]:
        """Check if a line matches a section header.

        Args:
            line: Lowercased line to check.

        Returns:
            Section name if matched, None otherwise.
        """
        for section_name, headers in self.section_headers.items():
            for header in headers:
                # Check for exact match or line starting with header
                if line == header or line.startswith(header + ":") or line.startswith(header + "s:"):
                    return section_name
                # Check for patterns like "What You'll Do:" or "Requirements:"
                if re.match(rf"^{re.escape(header)}[\s:]*$", line):
                    return section_name
        return None

    def _extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract basic metadata from the text.

        Args:
            text: Preprocessed text.

        Returns:
            Dictionary with metadata.
        """
        metadata = {
            "word_count": len(text.split()),
            "line_count": len(text.split("\n")),
            "has_bullet_points": bool(re.search(r"^[\s]*[-*•]\s", text, re.MULTILINE)),
            "has_numbers": bool(re.search(r"\d+", text)),
        }
        return metadata
