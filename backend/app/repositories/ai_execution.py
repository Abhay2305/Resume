"""AI Execution Engine repository.

Data access layer for AI execution records.
"""
from typing import List, Optional, Tuple

from app.models.ai_execution import AIExecution
from app.repositories.base import BaseRepository


class AIExecutionRepository(BaseRepository[AIExecution]):
    """Repository for AIExecution CRUD operations."""

    def __init__(self, db):
        super().__init__(AIExecution, db)

    def get_by_id(self, id: str) -> Optional[AIExecution]:
        return self.db.query(AIExecution).filter(AIExecution.id == id).first()

    def get_by_user_id(self, user_id: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[AIExecution], int]:
        query = self.db.query(AIExecution).filter(
            AIExecution.user_id == user_id
        ).order_by(AIExecution.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_prompt_package_id(self, prompt_package_id: str) -> List[AIExecution]:
        return self.db.query(AIExecution).filter(
            AIExecution.prompt_package_id == prompt_package_id
        ).order_by(AIExecution.created_at.desc()).all()

    def create(self, data: dict) -> AIExecution:
        execution = AIExecution(**data)
        self.db.add(execution)
        self.db.flush()
        return execution

    def update(self, id: str, data: dict) -> Optional[AIExecution]:
        execution = self.get_by_id(id)
        if execution:
            for key, value in data.items():
                if hasattr(execution, key) and value is not None:
                    setattr(execution, key, value)
            self.db.flush()
        return execution

    def get_by_status(self, status: str) -> List[AIExecution]:
        return self.db.query(AIExecution).filter(
            AIExecution.status == status
        ).order_by(AIExecution.created_at.desc()).all()
