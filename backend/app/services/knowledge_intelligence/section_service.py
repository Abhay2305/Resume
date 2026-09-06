"""Knowledge Section Service.

Manages knowledge sections within documents.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.knowledge_intelligence import KnowledgeSection
from app.repositories.knowledge_intelligence import KnowledgeSectionRepository


class KnowledgeSectionService:
    """Service for knowledge section operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = KnowledgeSectionRepository(db)

    def create(
        self,
        document_id: str,
        section_key: str,
        name: str,
        category: str,
        description: Optional[str] = None,
        content_summary: Optional[str] = None,
        sort_order: int = 0,
    ) -> KnowledgeSection:
        """Create a knowledge section."""
        existing = self.repo.get_by_key(document_id, section_key)
        if existing:
            raise ValueError(f"Section '{section_key}' already exists for this document")

        return self.repo.create({
            "document_id": document_id,
            "section_key": section_key,
            "name": name,
            "category": category,
            "description": description,
            "content_summary": content_summary,
            "sort_order": sort_order,
        })

    def create_many(self, sections: List[dict]) -> List[KnowledgeSection]:
        """Create multiple sections."""
        return self.repo.create_many(sections)

    def get_by_id(self, section_id: str) -> Optional[KnowledgeSection]:
        """Get section by ID."""
        return self.repo.get_by_id(section_id)

    def get_by_document_id(self, document_id: str) -> List[KnowledgeSection]:
        """Get all sections for a document."""
        return self.repo.get_by_document_id(document_id)

    def get_by_category(self, category: str) -> List[KnowledgeSection]:
        """Get sections by category."""
        return self.repo.get_by_category(category)

    def get_by_key(self, document_id: str, section_key: str) -> Optional[KnowledgeSection]:
        """Get section by document and key."""
        return self.repo.get_by_key(document_id, section_key)

    def delete_by_document_id(self, document_id: str) -> bool:
        """Delete all sections for a document."""
        return self.repo.delete_by_document_id(document_id)

    def initialize_default_sections(self, document_id: str) -> List[KnowledgeSection]:
        """Initialize default sections for a knowledge document."""
        default_sections = [
            {"section_key": "summary", "name": "Summary", "category": "summary", "sort_order": 1},
            {"section_key": "experience", "name": "Experience", "category": "experience", "sort_order": 2},
            {"section_key": "skills", "name": "Skills", "category": "skills", "sort_order": 3},
            {"section_key": "education", "name": "Education", "category": "education", "sort_order": 4},
            {"section_key": "projects", "name": "Projects", "category": "projects", "sort_order": 5},
            {"section_key": "certifications", "name": "Certifications", "category": "certifications", "sort_order": 6},
            {"section_key": "achievements", "name": "Achievements", "category": "achievements", "sort_order": 7},
            {"section_key": "formatting", "name": "Formatting", "category": "formatting", "sort_order": 8},
            {"section_key": "ats", "name": "ATS Optimization", "category": "ats", "sort_order": 9},
            {"section_key": "cover_letter", "name": "Cover Letter", "category": "cover_letter", "sort_order": 10},
        ]

        sections_to_create = []
        for section in default_sections:
            existing = self.repo.get_by_key(document_id, section["section_key"])
            if not existing:
                sections_to_create.append({
                    "document_id": document_id,
                    **section,
                })

        if sections_to_create:
            return self.repo.create_many(sections_to_create)
        return []
