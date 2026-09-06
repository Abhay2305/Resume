"""Knowledge Document Service.

Manages knowledge document registration, versioning, and metadata.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.knowledge_intelligence import KnowledgeDocument
from app.repositories.knowledge_intelligence import KnowledgeDocumentRepository
from app.services.audit_service import AuditService


class KnowledgeDocumentService:
    """Service for knowledge document operations."""

    def __init__(self, db: Session):
        self.db = db
        self.repo = KnowledgeDocumentRepository(db)
        self.audit_service = AuditService(db)

    def register(
        self,
        document_key: str,
        name: str,
        source: str,
        document_type: str,
        version: str = "1.0",
        description: Optional[str] = None,
        confidence: float = 0.8,
        user_id: Optional[str] = None,
    ) -> KnowledgeDocument:
        """Register a new knowledge document."""
        existing = self.repo.get_by_key(document_key)
        if existing:
            raise ValueError(f"Document with key '{document_key}' already exists")

        doc = self.repo.create({
            "document_key": document_key,
            "name": name,
            "source": source,
            "document_type": document_type,
            "version": version,
            "description": description,
            "confidence": confidence,
        })

        if user_id:
            self.audit_service.log_create(
                user_id=user_id,
                entity_type="knowledge_document",
                entity_id=doc.id,
                details={"document_key": document_key, "name": name, "source": source},
            )

        return doc

    def get_by_id(self, document_id: str) -> Optional[KnowledgeDocument]:
        """Get document by ID."""
        return self.repo.get_by_id(document_id)

    def get_by_key(self, document_key: str) -> Optional[KnowledgeDocument]:
        """Get document by key."""
        return self.repo.get_by_key(document_key)

    def get_all(self, *, skip: int = 0, limit: int = 100) -> Tuple[List[KnowledgeDocument], int]:
        """Get all documents."""
        return self.repo.get_all(skip=skip, limit=limit)

    def get_active(self) -> List[KnowledgeDocument]:
        """Get all active documents."""
        return self.repo.get_active()

    def search(self, q: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[KnowledgeDocument], int]:
        """Search documents."""
        return self.repo.search(q, skip=skip, limit=limit)

    def update(
        self,
        document_id: str,
        name: Optional[str] = None,
        version: Optional[str] = None,
        description: Optional[str] = None,
        confidence: Optional[float] = None,
        is_active: Optional[bool] = None,
        user_id: Optional[str] = None,
    ) -> Optional[KnowledgeDocument]:
        """Update a knowledge document."""
        data = {}
        if name is not None:
            data["name"] = name
        if version is not None:
            data["version"] = version
        if description is not None:
            data["description"] = description
        if confidence is not None:
            data["confidence"] = confidence
        if is_active is not None:
            data["is_active"] = is_active

        doc = self.repo.update(document_id, data)
        if doc and user_id:
            self.audit_service.log_create(
                user_id=user_id,
                entity_type="knowledge_document_updated",
                entity_id=document_id,
                details=data,
            )

        return doc

    def delete(self, document_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a knowledge document."""
        doc = self.repo.get_by_id(document_id)
        if not doc:
            return False

        self.repo.delete(document_id)

        if user_id:
            self.audit_service.log_create(
                user_id=user_id,
                entity_type="knowledge_document_deleted",
                entity_id=document_id,
                details={"deleted_at": datetime.utcnow().isoformat()},
            )

        return True

    def get_by_source(self, source: str) -> List[KnowledgeDocument]:
        """Get documents by source."""
        return self.repo.get_by_source(source)

    def get_by_type(self, document_type: str) -> List[KnowledgeDocument]:
        """Get documents by type."""
        return self.repo.get_by_type(document_type)
