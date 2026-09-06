"""Prompt Intelligence Engine repository.

Data access layer for the Prompt Intelligence Engine.
"""
from typing import List, Optional, Tuple

from app.models.prompt_intelligence import (
    PromptExecution,
    PromptPackage,
    PromptTemplate,
    PromptVariable,
    PromptVersion,
)
from app.repositories.base import BaseRepository


class PromptTemplateRepository(BaseRepository[PromptTemplate]):
    """Repository for PromptTemplate CRUD operations."""

    def __init__(self, db):
        super().__init__(PromptTemplate, db)

    def get_by_id(self, id: str) -> Optional[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(PromptTemplate.id == id).first()

    def get_by_key(self, template_key: str) -> Optional[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(PromptTemplate.template_key == template_key).first()

    def get_by_type(self, prompt_type: str) -> List[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.prompt_type == prompt_type,
            PromptTemplate.is_active == True,
        ).all()

    def get_active(self) -> List[PromptTemplate]:
        return self.db.query(PromptTemplate).filter(PromptTemplate.is_active == True).all()

    def get_all(self, *, skip: int = 0, limit: int = 100) -> Tuple[List[PromptTemplate], int]:
        query = self.db.query(PromptTemplate).order_by(PromptTemplate.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, data: dict) -> PromptTemplate:
        template = PromptTemplate(**data)
        self.db.add(template)
        self.db.flush()
        return template

    def update(self, id: str, data: dict) -> Optional[PromptTemplate]:
        template = self.get_by_id(id)
        if template:
            for key, value in data.items():
                if hasattr(template, key) and value is not None:
                    setattr(template, key, value)
            self.db.flush()
        return template

    def delete(self, id: str) -> bool:
        template = self.get_by_id(id)
        if template:
            self.db.delete(template)
            self.db.flush()
            return True
        return False


class PromptPackageRepository(BaseRepository[PromptPackage]):
    """Repository for PromptPackage CRUD operations."""

    def __init__(self, db):
        super().__init__(PromptPackage, db)

    def get_by_id(self, id: str) -> Optional[PromptPackage]:
        return self.db.query(PromptPackage).filter(PromptPackage.id == id).first()

    def get_by_user_id(self, user_id: str, *, skip: int = 0, limit: int = 20) -> Tuple[List[PromptPackage], int]:
        query = self.db.query(PromptPackage).filter(
            PromptPackage.user_id == user_id
        ).order_by(PromptPackage.created_at.desc())
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_gap_analysis_id(self, gap_analysis_id: str) -> Optional[PromptPackage]:
        return self.db.query(PromptPackage).filter(
            PromptPackage.gap_analysis_id == gap_analysis_id
        ).first()

    def create(self, data: dict) -> PromptPackage:
        package = PromptPackage(**data)
        self.db.add(package)
        self.db.flush()
        return package

    def update(self, id: str, data: dict) -> Optional[PromptPackage]:
        package = self.get_by_id(id)
        if package:
            for key, value in data.items():
                if hasattr(package, key) and value is not None:
                    setattr(package, key, value)
            self.db.flush()
        return package

    def delete(self, id: str) -> bool:
        package = self.get_by_id(id)
        if package:
            self.db.delete(package)
            self.db.flush()
            return True
        return False


class PromptVariableRepository(BaseRepository[PromptVariable]):
    """Repository for PromptVariable CRUD operations."""

    def __init__(self, db):
        super().__init__(PromptVariable, db)

    def get_by_id(self, id: str) -> Optional[PromptVariable]:
        return self.db.query(PromptVariable).filter(PromptVariable.id == id).first()

    def get_by_key(self, variable_key: str) -> Optional[PromptVariable]:
        return self.db.query(PromptVariable).filter(PromptVariable.variable_key == variable_key).first()

    def get_by_source(self, source: str) -> List[PromptVariable]:
        return self.db.query(PromptVariable).filter(PromptVariable.source == source).all()

    def get_all(self) -> List[PromptVariable]:
        return self.db.query(PromptVariable).order_by(PromptVariable.source, PromptVariable.name).all()

    def create(self, data: dict) -> PromptVariable:
        variable = PromptVariable(**data)
        self.db.add(variable)
        self.db.flush()
        return variable

    def create_many(self, variables: List[dict]) -> List[PromptVariable]:
        created = []
        for data in variables:
            variable = PromptVariable(**data)
            self.db.add(variable)
            created.append(variable)
        self.db.flush()
        return created


class PromptExecutionRepository(BaseRepository[PromptExecution]):
    """Repository for PromptExecution CRUD operations."""

    def __init__(self, db):
        super().__init__(PromptExecution, db)

    def get_by_id(self, id: str) -> Optional[PromptExecution]:
        return self.db.query(PromptExecution).filter(PromptExecution.id == id).first()

    def get_by_package_id(self, package_id: str) -> List[PromptExecution]:
        return self.db.query(PromptExecution).filter(
            PromptExecution.package_id == package_id
        ).order_by(PromptExecution.created_at.desc()).all()

    def create(self, data: dict) -> PromptExecution:
        execution = PromptExecution(**data)
        self.db.add(execution)
        self.db.flush()
        return execution

    def update(self, id: str, data: dict) -> Optional[PromptExecution]:
        execution = self.get_by_id(id)
        if execution:
            for key, value in data.items():
                if hasattr(execution, key) and value is not None:
                    setattr(execution, key, value)
            self.db.flush()
        return execution


class PromptVersionRepository(BaseRepository[PromptVersion]):
    """Repository for PromptVersion CRUD operations."""

    def __init__(self, db):
        super().__init__(PromptVersion, db)

    def get_by_id(self, id: str) -> Optional[PromptVersion]:
        return self.db.query(PromptVersion).filter(PromptVersion.id == id).first()

    def get_by_template_id(self, template_id: str) -> List[PromptVersion]:
        return self.db.query(PromptVersion).filter(
            PromptVersion.template_id == template_id
        ).order_by(PromptVersion.created_at.desc()).all()

    def get_by_version(self, template_id: str, version: str) -> Optional[PromptVersion]:
        return self.db.query(PromptVersion).filter(
            PromptVersion.template_id == template_id,
            PromptVersion.version == version,
        ).first()

    def create(self, data: dict) -> PromptVersion:
        version = PromptVersion(**data)
        self.db.add(version)
        self.db.flush()
        return version

    def get_latest(self, template_id: str) -> Optional[PromptVersion]:
        return self.db.query(PromptVersion).filter(
            PromptVersion.template_id == template_id,
            PromptVersion.is_active == True,
        ).order_by(PromptVersion.created_at.desc()).first()
