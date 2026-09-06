"""Achievement Extractor.

Extracts achievements and quantified metrics from resume sections.
"""
import re
from typing import Any, Dict, List

METRIC_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*%",
    r"\$\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:K|M|B|k|m|b)?",
    r"(\d+(?:,\d{3})*)\+?\s*(?:users|customers|clients|requests|calls|transactions)",
    r"(\d+(?:\.\d+)?)\s*x\b",
    r"reduced\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%",
    r"increased\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%",
    r"improved\s+(?:by\s+)?(\d+(?:\.\d+)?)\s*%",
    r"saved\s+\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)",
    r"(\d+(?:\.\d+)?)\s*(?:hours?|days?|weeks?|months?)\s*(?:per\s+\w+)?",
]


class AchievementExtractor:
    """Extracts achievements from resume sections."""

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        all_text = "\n".join(sections.values())

        bullets = re.split(r"\n", all_text)
        for bullet in bullets:
            bullet = bullet.strip()
            if not bullet or not bullet.startswith(("-", "•", "*", "–")):
                continue

            content = bullet.lstrip("-•*– ").strip()
            metrics = self._extract_metrics(content)

            if metrics:
                entities.append({
                    "entity_type": "achievement",
                    "entity_value": content,
                    "entity_metadata": {"metrics": metrics},
                })
                for metric in metrics:
                    entities.append({
                        "entity_type": "metric",
                        "entity_value": metric,
                        "entity_metadata": {"source": content},
                    })

        return {"entities": entities}

    def _extract_metrics(self, text: str) -> List[str]:
        metrics = []
        text_lower = text.lower()

        has_impact_keyword = any(kw in text_lower for kw in [
            "increased", "reduced", "improved", "saved", "achieved",
            "delivered", "completed", "managed", "led", "designed",
            "built", "launched", "scaled", "optimized",
        ])

        if not has_impact_keyword:
            return metrics

        for pattern in METRIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    metrics.append(match[0] if match else "")
                else:
                    metrics.append(match)

        return list(set(metrics))
