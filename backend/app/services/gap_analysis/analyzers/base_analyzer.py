"""Base analyzer for gap analysis.

Provides common matching logic for all analyzers.
"""
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple


class BaseAnalyzer:
    """Base class for gap analyzers."""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data")
        self._synonyms = None
        self._normalized_cache = {}

    def _load_synonyms(self, filename: str) -> Dict[str, Any]:
        """Load synonym dictionary from JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def normalize_item(self, item: str) -> str:
        """Normalize an item for comparison."""
        normalized = item.lower().strip()
        normalized = normalized.replace("-", " ").replace("_", " ")
        normalized = " ".join(normalized.split())
        return normalized

    def normalize_items(self, items: List[str]) -> Set[str]:
        """Normalize a list of items for comparison."""
        return {self.normalize_item(item) for item in items if item}

    def find_synonym_groups(self, item: str, synonym_data: Dict) -> List[str]:
        """Find all synonyms for an item."""
        normalized = self.normalize_item(item)
        for group_name, synonyms in synonym_data.items():
            all_names = [self.normalize_item(s) for s in synonyms]
            if normalized in all_names or normalized == self.normalize_item(group_name):
                return [self.normalize_item(s) for s in synonyms] + [self.normalize_item(group_name)]
        return [normalized]

    def exact_match(self, required: Set[str], available: Set[str]) -> Tuple[Set[str], Set[str]]:
        """Find exact matches and missing items."""
        matched = required & available
        missing = required - available
        return matched, missing

    def synonym_match(
        self, required: Set[str], available: Set[str], synonym_data: Dict
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """Find matches using synonym matching."""
        matched = set()
        missing = set()
        partial = set()

        for req_item in required:
            req_synonyms = set()
            for group_name, synonyms in synonym_data.items():
                group_normalized = self.normalize_item(group_name)
                syn_normalized = {self.normalize_item(s) for s in synonyms}
                if req_item in syn_normalized or req_item == group_normalized:
                    req_synonyms = syn_normalized | {group_normalized}
                    break

            if not req_synonyms:
                req_synonyms = {req_item}

            found = False
            for avail_item in available:
                if avail_item in req_synonyms:
                    matched.add(req_item)
                    found = True
                    break

            if not found:
                missing.add(req_item)

        return matched, missing, partial

    def calculate_match_score(self, matched: Set[str], total: Set[str]) -> float:
        """Calculate match score as percentage."""
        if not total:
            return 1.0
        return len(matched) / len(total)

    def analyze(
        self,
        required_items: List[str],
        available_items: List[str],
        preferred_items: Optional[List[str]] = None,
        synonym_data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Analyze gap between required and available items.

        Args:
            required_items: Items required by the opportunity.
            available_items: Items the candidate has.
            preferred_items: Items preferred but not required.
            synonym_data: Synonym dictionary for matching.

        Returns:
            Dictionary with matched, missing, partial, score.
        """
        required_norm = self.normalize_items(required_items)
        available_norm = self.normalize_items(available_items)
        preferred_norm = self.normalize_items(preferred_items or [])

        matched_exact, missing_exact = self.exact_match(required_norm, available_norm)

        if synonym_data:
            matched_syn, missing_syn, partial_syn = self.synonym_match(
                missing_exact, available_norm, synonym_data
            )
        else:
            matched_syn, missing_syn, partial_syn = set(), missing_exact, set()

        all_matched = matched_exact | matched_syn
        all_missing = missing_syn

        preferred_matched, preferred_missing = self.exact_match(preferred_norm, available_norm)

        score = self.calculate_match_score(all_matched, required_norm)

        extra = available_norm - required_norm - preferred_norm

        return {
            "matched": sorted(list(all_matched)),
            "missing": sorted(list(all_missing)),
            "partial": sorted(list(partial_syn)),
            "extra": sorted(list(extra)),
            "preferred_matched": sorted(list(preferred_matched)),
            "preferred_missing": sorted(list(preferred_missing)),
            "score": round(score, 2),
        }
