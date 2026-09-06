"""Resume Knowledge Builder.

Assembles extracted entities into a structured Resume Knowledge representation.
No AI involved.
"""
from typing import Any, Dict, List, Optional


class ResumeKnowledgeBuilder:
    """Builds structured Resume Knowledge from extracted entities and parsed data."""

    def build(
        self,
        entities: List[Dict[str, Any]],
        parsed_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build Resume Knowledge from entities and parsed data.

        Args:
            entities: List of extracted entities.
            parsed_data: Parsed resume data.

        Returns:
            Structured Resume Knowledge dictionary.
        """
        knowledge = {
            "personal_info": self._build_personal_info(entities, parsed_data),
            "contact_info": self._build_contact_info(entities, parsed_data),
            "summary": parsed_data.get("summary", ""),
            "skills": self._build_skills(entities),
            "technologies": self._build_technologies(entities),
            "experience_summary": self._build_experience_summary(entities, parsed_data),
            "education_summary": self._build_education_summary(entities, parsed_data),
            "certifications": self._build_certifications(entities),
            "projects": self._build_projects(entities, parsed_data),
            "achievements": self._build_achievements(entities),
            "total_experience_years": self._estimate_experience_years(entities, parsed_data),
        }

        return knowledge

    def _build_personal_info(self, entities: List[Dict], parsed_data: Dict) -> Dict[str, Any]:
        personal = {}
        for e in entities:
            if e["entity_type"] == "personal_info":
                metadata = e.get("entity_metadata", {})
                if metadata.get("field") == "name":
                    personal["name"] = e["entity_value"]
        return personal

    def _build_contact_info(self, entities: List[Dict], parsed_data: Dict) -> Dict[str, Any]:
        contact = {}
        for e in entities:
            if e["entity_type"] == "contact":
                metadata = e.get("entity_metadata", {})
                contact_type = metadata.get("contact_type", "")
                if contact_type:
                    contact[contact_type] = e["entity_value"]
        return contact

    def _build_skills(self, entities: List[Dict]) -> List[str]:
        return list(set(
            e["entity_value"] for e in entities
            if e["entity_type"] == "skill"
        ))

    def _build_technologies(self, entities: List[Dict]) -> Dict[str, List[str]]:
        tech_map = {}
        for e in entities:
            if e["entity_type"] in ("technology", "framework", "library", "database",
                                     "cloud_platform", "devops_tool", "ai_ml"):
                tech_type = e["entity_type"]
                if tech_type not in tech_map:
                    tech_map[tech_type] = []
                tech_map[tech_type].append(e["entity_value"])
        for key in tech_map:
            tech_map[key] = list(set(tech_map[key]))
        return tech_map

    def _build_experience_summary(self, entities: List[Dict], parsed_data: Dict) -> List[Dict]:
        entries = parsed_data.get("experience_entries", [])
        summary = []
        for entry in entries:
            summary.append({
                "role": entry.get("role", ""),
                "company": entry.get("company", ""),
                "start_date": entry.get("start_date", ""),
                "end_date": entry.get("end_date", ""),
                "bullet_count": len(entry.get("bullets", [])),
            })
        return summary

    def _build_education_summary(self, entities: List[Dict], parsed_data: Dict) -> List[Dict]:
        degrees = [
            e["entity_value"] for e in entities
            if e["entity_type"] == "degree"
        ]
        fields = [
            e["entity_value"] for e in entities
            if e["entity_type"] == "field_of_study"
        ]
        institutions = parsed_data.get("institutions", [])

        summary = []
        if degrees or fields or institutions:
            summary.append({
                "degrees": degrees,
                "fields_of_study": fields,
                "institutions": institutions,
            })
        return summary

    def _build_certifications(self, entities: List[Dict]) -> List[str]:
        return list(set(
            e["entity_value"] for e in entities
            if e["entity_type"] == "certification"
        ))

    def _build_projects(self, entities: List[Dict], parsed_data: Dict) -> List[Dict]:
        projects = parsed_data.get("projects", [])
        if not projects:
            projects = []
            for e in entities:
                if e["entity_type"] == "project":
                    metadata = e.get("entity_metadata", {})
                    projects.append({
                        "name": e["entity_value"],
                        "description": metadata.get("description", ""),
                        "technologies": metadata.get("technologies", []),
                    })
        return projects

    def _build_achievements(self, entities: List[Dict]) -> List[str]:
        return list(set(
            e["entity_value"] for e in entities
            if e["entity_type"] == "achievement"
        ))

    def _estimate_experience_years(self, entities: List[Dict], parsed_data: Dict) -> Optional[int]:
        entries = parsed_data.get("experience_entries", [])
        if not entries:
            return None

        total_months = 0
        for entry in entries:
            start = entry.get("start_date", "")
            end = entry.get("end_date", "")
            months = self._estimate_months(start, end)
            total_months += months

        if total_months > 0:
            return max(1, total_months // 12)
        return None

    def _estimate_months(self, start: str, end: str) -> int:
        month_names = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }

        start_months = 0
        for name, num in month_names.items():
            if name in start.lower():
                start_months = num
                break

        end_months = 12
        if "present" in end.lower() or "current" in end.lower() or "now" in end.lower():
            end_months = 12
        else:
            for name, num in month_names.items():
                if name in end.lower():
                    end_months = num
                    break

        start_year = 0
        for part in start.split():
            if part.isdigit() and len(part) == 4:
                start_year = int(part)
                break

        end_year = 2026
        for part in end.split():
            if part.isdigit() and len(part) == 4:
                end_year = int(part)
                break

        return max(0, (end_year - start_year) * 12 + (end_months - start_months))
