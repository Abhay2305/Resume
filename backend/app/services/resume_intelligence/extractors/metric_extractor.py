"""Metric Extractor.

Extracts quantified metrics and numbers from resume sections.
"""
import re
from typing import Any, Dict, List


class MetricExtractor:
    """Extracts metrics from resume sections."""

    METRIC_PATTERNS = [
        (r"(\d+(?:\.\d+)?)\s*%", "percentage"),
        (r"\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:K|M|B|k|m|b)?", "currency"),
        (r"(\d+(?:,\d{3})*)\+?\s*(?:users|customers|clients)", "count"),
        (r"(\d+(?:\.\d+)?)\s*x\b", "multiplier"),
        (r"(\d+(?:\.\d+)?)\s*(?:hours?|days?|weeks?|months?)", "time"),
        (r"(\d+(?:,\d{3})*)\s*(?:requests|calls|transactions|events)", "volume"),
        (r"(?:latency|response time|load time)[:\s]*(\d+(?:\.\d+)?)\s*(?:ms|sec|s)\b", "performance"),
        (r"(?:uptime|availability)[:\s]*(\d+(?:\.\d+)?)\s*%", "availability"),
    ]

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        all_text = "\n".join(sections.values())

        for pattern, metric_type in self.METRIC_PATTERNS:
            matches = re.finditer(pattern, all_text, re.IGNORECASE)
            for match in matches:
                value = match.group(0).strip()
                context = self._get_context(all_text, match.start(), match.end())
                entities.append({
                    "entity_type": "metric",
                    "entity_value": value,
                    "entity_metadata": {
                        "metric_type": metric_type,
                        "context": context,
                    },
                })

        seen = set()
        unique = []
        for e in entities:
            if e["entity_value"] not in seen:
                seen.add(e["entity_value"])
                unique.append(e)

        return {"entities": unique}

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end].strip()
