"""Certification Extractor.

Extracts certifications from resume sections.
"""
import json
import re
from pathlib import Path
from typing import Any, Dict, List


class CertificationExtractor:
    """Extracts certifications from resume sections."""

    def __init__(self):
        self.cert_data = self._load_data("certifications.json")
        self.all_certs = self._build_cert_index()

    def _load_data(self, filename: str) -> Dict[str, Any]:
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        with open(data_dir / filename, "r") as f:
            return json.load(f)

    def _build_cert_index(self) -> List[str]:
        all_certs = []
        for category, certs in self.cert_data.items():
            if isinstance(certs, list):
                all_certs.extend(certs)
        return list(set(all_certs))

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        cert_text = sections.get("certifications", "")
        all_text = "\n".join(sections.values()).lower()

        for cert in self.all_certs:
            if cert.lower() in all_text:
                entities.append({
                    "entity_type": "certification",
                    "entity_value": cert,
                })

        return {"entities": entities}
