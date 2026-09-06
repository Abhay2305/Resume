"""Knowledge Intelligence Engine repository.

Data access layer for the Knowledge Intelligence Engine.
"""
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_

from app.models.knowledge_intelligence import (
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeRetrieval,
    KnowledgeRule,
    KnowledgeSection,
)
from app.repositories.base import BaseRepository


class KnowledgeDocumentRepository(BaseRepository[KnowledgeDocument]):
    """Repository for KnowledgeDocument CRUD operations."""

    def __init__(self, db):
        super().__init__(KnowledgeDocument, db)

    def get_by_id(self, id: str) -> Optional[KnowledgeDocument]:
        """Get knowledge document by ID."""
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.id == id).first()

    def get_by_key(self, document_key: str) -> Optional[KnowledgeDocument]:
        """Get knowledge document by document key."""
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.document_key == document_key).first()

    def get_by_source(self, source: str) -> List[KnowledgeDocument]:
        """Get knowledge documents by source."""
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.source == source).all()

    def get_by_type(self, document_type: str) -> List[KnowledgeDocument]:
        """Get knowledge documents by type."""
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.document_type == document_type).all()

    def get_active(self) -> List[KnowledgeDocument]:
        """Get all active knowledge documents."""
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.is_active == True).all()

    def get_all(self, *, skip: int = 0, limit: int = 100) -> Tuple[List[KnowledgeDocument], int]:
        """Get all knowledge documents with pagination."""
        query = self.db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def search(self, q: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[KnowledgeDocument], int]:
        """Search knowledge documents by name or source."""
        query = self.db.query(KnowledgeDocument).filter(
            (KnowledgeDocument.name.contains(q)) | (KnowledgeDocument.source.contains(q))
        ).order_by(KnowledgeDocument.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, data: dict) -> KnowledgeDocument:
        """Create a knowledge document."""
        doc = KnowledgeDocument(**data)
        self.db.add(doc)
        self.db.flush()
        return doc

    def update(self, id: str, data: dict) -> Optional[KnowledgeDocument]:
        """Update a knowledge document."""
        doc = self.get_by_id(id)
        if doc:
            for key, value in data.items():
                if hasattr(doc, key) and value is not None:
                    setattr(doc, key, value)
            self.db.flush()
        return doc

    def delete(self, id: str) -> bool:
        """Delete a knowledge document."""
        doc = self.get_by_id(id)
        if doc:
            self.db.delete(doc)
            self.db.flush()
            return True
        return False


class KnowledgeSectionRepository(BaseRepository[KnowledgeSection]):
    """Repository for KnowledgeSection CRUD operations."""

    def __init__(self, db):
        super().__init__(KnowledgeSection, db)

    def get_by_id(self, id: str) -> Optional[KnowledgeSection]:
        """Get knowledge section by ID."""
        return self.db.query(KnowledgeSection).filter(KnowledgeSection.id == id).first()

    def get_by_document_id(self, document_id: str) -> List[KnowledgeSection]:
        """Get all sections for a document."""
        return self.db.query(KnowledgeSection).filter(
            KnowledgeSection.document_id == document_id
        ).order_by(KnowledgeSection.sort_order).all()

    def get_by_category(self, category: str) -> List[KnowledgeSection]:
        """Get sections by category."""
        return self.db.query(KnowledgeSection).filter(
            KnowledgeSection.category == category
        ).all()

    def get_by_key(self, document_id: str, section_key: str) -> Optional[KnowledgeSection]:
        """Get section by document and key."""
        return self.db.query(KnowledgeSection).filter(
            KnowledgeSection.document_id == document_id,
            KnowledgeSection.section_key == section_key,
        ).first()

    def create(self, data: dict) -> KnowledgeSection:
        """Create a knowledge section."""
        section = KnowledgeSection(**data)
        self.db.add(section)
        self.db.flush()
        return section

    def create_many(self, sections: List[dict]) -> List[KnowledgeSection]:
        """Create multiple knowledge sections."""
        created = []
        for data in sections:
            section = KnowledgeSection(**data)
            self.db.add(section)
            created.append(section)
        self.db.flush()
        return created

    def delete_by_document_id(self, document_id: str) -> bool:
        """Delete all sections for a document."""
        self.db.query(KnowledgeSection).filter(
            KnowledgeSection.document_id == document_id
        ).delete()
        self.db.flush()
        return True


class KnowledgeRuleRepository(BaseRepository[KnowledgeRule]):
    """Repository for KnowledgeRule CRUD operations."""

    def __init__(self, db):
        super().__init__(KnowledgeRule, db)

    def get_by_id(self, id: str) -> Optional[KnowledgeRule]:
        """Get knowledge rule by ID."""
        return self.db.query(KnowledgeRule).filter(KnowledgeRule.id == id).first()

    def get_by_key(self, rule_key: str) -> Optional[KnowledgeRule]:
        """Get knowledge rule by rule key."""
        return self.db.query(KnowledgeRule).filter(KnowledgeRule.rule_key == rule_key).first()

    def get_by_document_id(self, document_id: str) -> List[KnowledgeRule]:
        """Get all rules for a document."""
        return self.db.query(KnowledgeRule).filter(
            KnowledgeRule.document_id == document_id
        ).order_by(KnowledgeRule.priority, KnowledgeRule.category).all()

    def get_by_section_name(self, section_name: str) -> List[KnowledgeRule]:
        """Get rules by section name."""
        return self.db.query(KnowledgeRule).filter(
            KnowledgeRule.section_name == section_name,
            KnowledgeRule.is_active == True,
        ).order_by(KnowledgeRule.priority).all()

    def get_by_category(self, category: str) -> List[KnowledgeRule]:
        """Get rules by category."""
        return self.db.query(KnowledgeRule).filter(
            KnowledgeRule.category == category,
            KnowledgeRule.is_active == True,
        ).order_by(KnowledgeRule.priority).all()

    def get_by_priority(self, priority: str) -> List[KnowledgeRule]:
        """Get rules by priority."""
        return self.db.query(KnowledgeRule).filter(
            KnowledgeRule.priority == priority,
            KnowledgeRule.is_active == True,
        ).all()

    def get_active(self) -> List[KnowledgeRule]:
        """Get all active knowledge rules.

        Requires both state=ACTIVE and is_active=True (defense-in-depth).
        """
        return self.db.query(KnowledgeRule).filter(
            KnowledgeRule.state == 'ACTIVE',
            KnowledgeRule.is_active == True,
        ).order_by(KnowledgeRule.priority, KnowledgeRule.category).all()

    def get_by_state(self, state: str, *, skip: int = 0, limit: int = 100) -> Tuple[List[KnowledgeRule], int]:
        """Get rules by governance state with pagination.

        Args:
            state: Governance state (e.g., 'VERIFIED', 'APPROVED', 'ACTIVE').
            skip: Offset for pagination.
            limit: Maximum number of rules to return.

        Returns:
            Tuple of (rules, total_count).
        """
        query = self.db.query(KnowledgeRule).filter(
            KnowledgeRule.state == state
        ).order_by(KnowledgeRule.source_document, KnowledgeRule.priority)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_state_and_active(self, state: str, is_active: bool) -> List[KnowledgeRule]:
        """Get rules by governance state and active status.

        Args:
            state: Governance state.
            is_active: Active status filter.

        Returns:
            List of matching rules.
        """
        return self.db.query(KnowledgeRule).filter(
            KnowledgeRule.state == state,
            KnowledgeRule.is_active == is_active,
        ).order_by(KnowledgeRule.source_document, KnowledgeRule.priority).all()

    def count_by_state(self) -> Dict[str, int]:
        """Count rules grouped by governance state.

        Returns:
            Dictionary mapping state to count.
        """
        from sqlalchemy import func
        results = self.db.query(
            KnowledgeRule.state, func.count(KnowledgeRule.id)
        ).group_by(KnowledgeRule.state).all()
        return {state: count for state, count in results}

    def get_all(self, *, skip: int = 0, limit: int = 100) -> Tuple[List[KnowledgeRule], int]:
        """Get all knowledge rules with pagination."""
        query = self.db.query(KnowledgeRule).order_by(KnowledgeRule.priority, KnowledgeRule.category)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def search(self, q: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[KnowledgeRule], int]:
        """Search knowledge rules by instruction or category."""
        query = self.db.query(KnowledgeRule).filter(
            (KnowledgeRule.instruction.contains(q)) | (KnowledgeRule.category.contains(q))
        ).order_by(KnowledgeRule.priority)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, data: dict) -> KnowledgeRule:
        """Create a knowledge rule."""
        rule = KnowledgeRule(**data)
        self.db.add(rule)
        self.db.flush()
        return rule

    def create_many(self, rules: List[dict]) -> List[KnowledgeRule]:
        """Create multiple knowledge rules."""
        created = []
        for data in rules:
            rule = KnowledgeRule(**data)
            self.db.add(rule)
            created.append(rule)
        self.db.flush()
        return created

    def count(self, document_id: Optional[str] = None) -> int:
        """Count knowledge rules, optionally filtered by document."""
        query = self.db.query(KnowledgeRule)
        if document_id:
            query = query.filter(KnowledgeRule.document_id == document_id)
        return query.count()


class KnowledgeRetrievalRepository(BaseRepository[KnowledgeRetrieval]):
    """Repository for KnowledgeRetrieval CRUD operations."""

    def __init__(self, db):
        super().__init__(KnowledgeRetrieval, db)

    def get_by_id(self, id: str) -> Optional[KnowledgeRetrieval]:
        """Get knowledge retrieval by ID."""
        return self.db.query(KnowledgeRetrieval).filter(KnowledgeRetrieval.id == id).first()

    def get_by_gap_analysis_id(self, gap_analysis_id: str) -> Optional[KnowledgeRetrieval]:
        """Get knowledge retrieval by gap analysis ID."""
        return self.db.query(KnowledgeRetrieval).filter(
            KnowledgeRetrieval.gap_analysis_id == gap_analysis_id
        ).first()

    def get_by_user_id(self, user_id: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[KnowledgeRetrieval], int]:
        """Get knowledge retrievals for a user."""
        query = self.db.query(KnowledgeRetrieval).filter(
            KnowledgeRetrieval.user_id == user_id
        ).order_by(KnowledgeRetrieval.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, data: dict) -> KnowledgeRetrieval:
        """Create a knowledge retrieval."""
        retrieval = KnowledgeRetrieval(**data)
        self.db.add(retrieval)
        self.db.flush()
        return retrieval


class KnowledgeContextRepository(BaseRepository[KnowledgeContext]):
    """Repository for KnowledgeContext CRUD operations."""

    def __init__(self, db):
        super().__init__(KnowledgeContext, db)

    def get_by_id(self, id: str) -> Optional[KnowledgeContext]:
        """Get knowledge context by ID."""
        return self.db.query(KnowledgeContext).filter(KnowledgeContext.id == id).first()

    def get_by_retrieval_id(self, retrieval_id: str) -> Optional[KnowledgeContext]:
        """Get knowledge context by retrieval ID."""
        return self.db.query(KnowledgeContext).filter(
            KnowledgeContext.retrieval_id == retrieval_id
        ).first()

    def get_by_gap_analysis_id(self, gap_analysis_id: str) -> Optional[KnowledgeContext]:
        """Get knowledge context by gap analysis ID."""
        return self.db.query(KnowledgeContext).filter(
            KnowledgeContext.gap_analysis_id == gap_analysis_id
        ).first()

    def create(self, data: dict) -> KnowledgeContext:
        """Create a knowledge context."""
        context = KnowledgeContext(**data)
        self.db.add(context)
        self.db.flush()
        return context

    def update(self, id: str, data: dict) -> Optional[KnowledgeContext]:
        """Update a knowledge context."""
        context = self.get_by_id(id)
        if context:
            for key, value in data.items():
                if hasattr(context, key) and value is not None:
                    setattr(context, key, value)
            self.db.flush()
        return context
