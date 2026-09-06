"""AI Response Intelligence Engine repository.

Data access layer for AI response validation, diffs, change sets,
validation reports, and confidence scores.
"""
from typing import List, Optional, Tuple

from app.models.ai_response_intelligence import (
    AIResponseValidation,
    ChangeSet,
    ConfidenceScore,
    ResumeDiff,
    ValidationReport,
)
from app.repositories.base import BaseRepository


class AIResponseValidationRepository(BaseRepository[AIResponseValidation]):
    """Repository for AIResponseValidation CRUD operations."""

    def __init__(self, db):
        super().__init__(AIResponseValidation, db)

    def get_by_id(self, id: str) -> Optional[AIResponseValidation]:
        return self.db.query(AIResponseValidation).filter(AIResponseValidation.id == id).first()

    def get_by_user_id(self, user_id: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[AIResponseValidation], int]:
        query = self.db.query(AIResponseValidation).filter(
            AIResponseValidation.user_id == user_id
        ).order_by(AIResponseValidation.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_ai_execution_id(self, ai_execution_id: str) -> Optional[AIResponseValidation]:
        return self.db.query(AIResponseValidation).filter(
            AIResponseValidation.ai_execution_id == ai_execution_id
        ).first()

    def get_by_prompt_package_id(self, prompt_package_id: str) -> List[AIResponseValidation]:
        return self.db.query(AIResponseValidation).filter(
            AIResponseValidation.prompt_package_id == prompt_package_id
        ).order_by(AIResponseValidation.created_at.desc()).all()

    def create(self, data: dict) -> AIResponseValidation:
        validation = AIResponseValidation(**data)
        self.db.add(validation)
        self.db.flush()
        return validation

    def update(self, id: str, data: dict) -> Optional[AIResponseValidation]:
        validation = self.get_by_id(id)
        if validation:
            for key, value in data.items():
                if hasattr(validation, key) and value is not None:
                    setattr(validation, key, value)
            self.db.flush()
        return validation


class ResumeDiffRepository(BaseRepository[ResumeDiff]):
    """Repository for ResumeDiff CRUD operations."""

    def __init__(self, db):
        super().__init__(ResumeDiff, db)

    def get_by_id(self, id: str) -> Optional[ResumeDiff]:
        return self.db.query(ResumeDiff).filter(ResumeDiff.id == id).first()

    def get_by_validation_id(self, validation_id: str) -> List[ResumeDiff]:
        return self.db.query(ResumeDiff).filter(
            ResumeDiff.validation_id == validation_id
        ).order_by(ResumeDiff.created_at).all()

    def get_by_validation_and_section(self, validation_id: str, section: str) -> List[ResumeDiff]:
        return self.db.query(ResumeDiff).filter(
            ResumeDiff.validation_id == validation_id,
            ResumeDiff.section == section,
        ).all()

    def create(self, data: dict) -> ResumeDiff:
        diff = ResumeDiff(**data)
        self.db.add(diff)
        self.db.flush()
        return diff

    def create_many(self, diffs: List[dict]) -> List[ResumeDiff]:
        created = []
        for data in diffs:
            diff = ResumeDiff(**data)
            self.db.add(diff)
            created.append(diff)
        self.db.flush()
        return created


class ChangeSetRepository(BaseRepository[ChangeSet]):
    """Repository for ChangeSet CRUD operations."""

    def __init__(self, db):
        super().__init__(ChangeSet, db)

    def get_by_id(self, id: str) -> Optional[ChangeSet]:
        return self.db.query(ChangeSet).filter(ChangeSet.id == id).first()

    def get_by_validation_id(self, validation_id: str) -> List[ChangeSet]:
        return self.db.query(ChangeSet).filter(
            ChangeSet.validation_id == validation_id
        ).order_by(ChangeSet.created_at).all()

    def get_by_validation_and_category(self, validation_id: str, category: str) -> List[ChangeSet]:
        return self.db.query(ChangeSet).filter(
            ChangeSet.validation_id == validation_id,
            ChangeSet.category == category,
        ).all()

    def create(self, data: dict) -> ChangeSet:
        change = ChangeSet(**data)
        self.db.add(change)
        self.db.flush()
        return change

    def create_many(self, changes: List[dict]) -> List[ChangeSet]:
        created = []
        for data in changes:
            change = ChangeSet(**data)
            self.db.add(change)
            created.append(change)
        self.db.flush()
        return created


class ValidationReportRepository(BaseRepository[ValidationReport]):
    """Repository for ValidationReport CRUD operations."""

    def __init__(self, db):
        super().__init__(ValidationReport, db)

    def get_by_id(self, id: str) -> Optional[ValidationReport]:
        return self.db.query(ValidationReport).filter(ValidationReport.id == id).first()

    def get_by_validation_id(self, validation_id: str) -> List[ValidationReport]:
        return self.db.query(ValidationReport).filter(
            ValidationReport.validation_id == validation_id
        ).order_by(ValidationReport.created_at).all()

    def get_by_validation_and_validator(self, validation_id: str, validator_name: str) -> Optional[ValidationReport]:
        return self.db.query(ValidationReport).filter(
            ValidationReport.validation_id == validation_id,
            ValidationReport.validator_name == validator_name,
        ).first()

    def create(self, data: dict) -> ValidationReport:
        report = ValidationReport(**data)
        self.db.add(report)
        self.db.flush()
        return report


class ConfidenceScoreRepository(BaseRepository[ConfidenceScore]):
    """Repository for ConfidenceScore CRUD operations."""

    def __init__(self, db):
        super().__init__(ConfidenceScore, db)

    def get_by_id(self, id: str) -> Optional[ConfidenceScore]:
        return self.db.query(ConfidenceScore).filter(ConfidenceScore.id == id).first()

    def get_by_validation_id(self, validation_id: str) -> List[ConfidenceScore]:
        return self.db.query(ConfidenceScore).filter(
            ConfidenceScore.validation_id == validation_id
        ).order_by(ConfidenceScore.score.desc()).all()

    def get_by_change_set_id(self, change_set_id: str) -> Optional[ConfidenceScore]:
        return self.db.query(ConfidenceScore).filter(
            ConfidenceScore.change_set_id == change_set_id
        ).first()

    def create(self, data: dict) -> ConfidenceScore:
        score = ConfidenceScore(**data)
        self.db.add(score)
        self.db.flush()
        return score

    def create_many(self, scores: List[dict]) -> List[ConfidenceScore]:
        created = []
        for data in scores:
            score = ConfidenceScore(**data)
            self.db.add(score)
            created.append(score)
        self.db.flush()
        return created
