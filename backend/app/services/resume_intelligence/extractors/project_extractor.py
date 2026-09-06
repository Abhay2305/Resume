"""Project Extractor.

Extracts project entries from resume sections.
"""
import re
from typing import Any, Dict, List


class ProjectExtractor:
    """Extracts projects from resume sections."""

    def extract(self, sections: Dict[str, str]) -> Dict[str, Any]:
        entities = []
        parsed_data = {}

        proj_text = sections.get("projects", "")
        if not proj_text:
            return {"entities": entities, "parsed_data": parsed_data}

        projects = self._parse_projects(proj_text)
        parsed_data["projects"] = projects

        for project in projects:
            entities.append({
                "entity_type": "project",
                "entity_value": project.get("name", "Unknown"),
                "entity_metadata": {
                    "description": project.get("description", ""),
                    "technologies": project.get("technologies", []),
                },
            })

        return {"entities": entities, "parsed_data": parsed_data}

    def _parse_projects(self, text: str) -> List[Dict[str, Any]]:
        projects = []
        blocks = re.split(r"\n\s*\n", text)

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            lines = block.split("\n")
            name = lines[0].strip().rstrip(":")
            description_parts = []
            technologies = []

            for line in lines[1:]:
                line = line.strip()
                if line.startswith(("-", "•", "*", "–")):
                    content = line.lstrip("-•*– ").strip()
                    if any(tech in content.lower() for tech in ["built with", "using", "technologies", "stack"]):
                        techs = re.split(r",\s*|\s+and\s+", content)
                        technologies.extend([t.strip() for t in techs if t.strip()])
                    else:
                        description_parts.append(content)
                elif re.match(r"^[Tt]echnologies?:", line):
                    techs = re.split(r",\s*|\s+and\s+", line.split(":", 1)[1])
                    technologies.extend([t.strip() for t in techs if t.strip()])

            projects.append({
                "name": name,
                "description": " ".join(description_parts),
                "technologies": technologies,
            })

        return projects
