"""Language Extractor.

Extracts programming and spoken languages from resume sections.
"""
import re
from typing import Any, Dict, List

PROGRAMMING_LANGUAGES = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    "haskell", "elixir", "clojure", "f#", "groovy", "lua", "objective-c",
    "dart", "zig", "ocaml", "erlang", "fortran", "cobol", "assembly",
    "sql", "html", "css", "scss", "sass", "bash", "powershell", "zsh",
]


class LanguageExtractor:
    """Extracts languages from resume sections."""

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        all_text = "\n".join(sections.values()).lower()

        for lang in PROGRAMMING_LANGUAGES:
            if len(lang) <= 3:
                pattern = r"\b" + re.escape(lang) + r"\b"
                if re.search(pattern, all_text):
                    entities.append({
                        "entity_type": "language",
                        "entity_value": lang,
                    })
            else:
                if lang in all_text:
                    entities.append({
                        "entity_type": "language",
                        "entity_value": lang,
                    })

        return {"entities": entities}
