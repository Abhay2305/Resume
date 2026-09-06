"""Pipeline Intelligence Engine repository.

Data access layer for pipeline execution runs and stages.
"""
from typing import List, Optional, Tuple

from app.models.pipeline import PipelineRun, PipelineStage
from app.repositories.base import BaseRepository


class PipelineRunRepository(BaseRepository[PipelineRun]):
    """Repository for PipelineRun CRUD operations."""

    def __init__(self, db):
        super().__init__(PipelineRun, db)

    def get_by_id(self, id: str) -> Optional[PipelineRun]:
        """Get pipeline run by ID."""
        return self.db.query(PipelineRun).filter(PipelineRun.id == id).first()

    def get_by_user_id(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[PipelineRun], int]:
        """Get pipeline runs for a specific user with pagination."""
        query = (
            self.db.query(PipelineRun)
            .filter(PipelineRun.user_id == user_id)
            .order_by(PipelineRun.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, data: dict) -> PipelineRun:
        """Create a new pipeline run."""
        run = PipelineRun(**data)
        self.db.add(run)
        self.db.flush()
        return run

    def update_status(self, id: str, status: str, **kwargs) -> Optional[PipelineRun]:
        """Update pipeline run status and optional fields."""
        run = self.get_by_id(id)
        if run:
            run.status = status
            for key, value in kwargs.items():
                if hasattr(run, key) and value is not None:
                    setattr(run, key, value)
            self.db.flush()
        return run


class PipelineStageRepository(BaseRepository[PipelineStage]):
    """Repository for PipelineStage CRUD operations."""

    def __init__(self, db):
        super().__init__(PipelineStage, db)

    def get_by_id(self, id: str) -> Optional[PipelineStage]:
        """Get pipeline stage by ID."""
        return self.db.query(PipelineStage).filter(PipelineStage.id == id).first()

    def get_by_run_id(self, run_id: str) -> List[PipelineStage]:
        """Get all stages for a pipeline run, ordered by stage_order."""
        return (
            self.db.query(PipelineStage)
            .filter(PipelineStage.pipeline_run_id == run_id)
            .order_by(PipelineStage.stage_order)
            .all()
        )

    def create_batch(self, stages: List[dict]) -> List[PipelineStage]:
        """Create multiple pipeline stages in a batch."""
        created = []
        for data in stages:
            stage = PipelineStage(**data)
            self.db.add(stage)
            created.append(stage)
        self.db.flush()
        return created

    def update_status(
        self, id: str, status: str, **kwargs
    ) -> Optional[PipelineStage]:
        """Update pipeline stage status and optional fields."""
        stage = self.get_by_id(id)
        if stage:
            stage.status = status
            for key, value in kwargs.items():
                if hasattr(stage, key) and value is not None:
                    setattr(stage, key, value)
            self.db.flush()
        return stage
