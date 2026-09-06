"""Tests for Intelligence Pipeline repositories.

Verifies CRUD operations for PipelineRunRepository and PipelineStageRepository.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.base import Base
from app.models.pipeline import PipelineRun, PipelineStage
from app.repositories.pipeline import PipelineRunRepository, PipelineStageRepository


class TestPipelineRunRepository:
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def teardown_method(self):
        self.db.close()

    def test_create_run(self):
        repo = PipelineRunRepository(self.db)
        run = repo.create({
            "user_id": "user-1",
            "status": "pending",
            "resume_text": "resume content",
            "opportunity_text": "job description",
        })
        self.db.commit()

        assert run.id is not None
        assert run.user_id == "user-1"
        assert run.status == "pending"
        assert run.resume_text == "resume content"
        assert run.opportunity_text == "job description"

    def test_get_by_id(self):
        repo = PipelineRunRepository(self.db)
        run = repo.create({
            "user_id": "user-1",
            "status": "pending",
            "resume_text": "r",
            "opportunity_text": "o",
        })
        self.db.commit()

        found = repo.get_by_id(run.id)
        assert found is not None
        assert found.id == run.id

    def test_get_by_id_not_found(self):
        repo = PipelineRunRepository(self.db)
        found = repo.get_by_id("nonexistent-id")
        assert found is None

    def test_get_by_user_id(self):
        repo = PipelineRunRepository(self.db)
        repo.create({
            "user_id": "user-1",
            "status": "pending",
            "resume_text": "r1",
            "opportunity_text": "o1",
        })
        repo.create({
            "user_id": "user-1",
            "status": "completed",
            "resume_text": "r2",
            "opportunity_text": "o2",
        })
        repo.create({
            "user_id": "user-2",
            "status": "pending",
            "resume_text": "r3",
            "opportunity_text": "o3",
        })
        self.db.commit()

        items, total = repo.get_by_user_id("user-1")
        assert total == 2
        assert all(run.user_id == "user-1" for run in items)

    def test_get_by_user_id_pagination(self):
        repo = PipelineRunRepository(self.db)
        for i in range(5):
            repo.create({
                "user_id": "user-1",
                "status": "pending",
                "resume_text": f"r{i}",
                "opportunity_text": f"o{i}",
            })
        self.db.commit()

        items, total = repo.get_by_user_id("user-1", skip=0, limit=2)
        assert total == 5
        assert len(items) == 2

    def test_update_status(self):
        repo = PipelineRunRepository(self.db)
        run = repo.create({
            "user_id": "user-1",
            "status": "pending",
            "resume_text": "r",
            "opportunity_text": "o",
        })
        self.db.commit()

        updated = repo.update_status(run.id, "running")
        self.db.commit()

        assert updated.status == "running"

    def test_update_status_with_kwargs(self):
        repo = PipelineRunRepository(self.db)
        run = repo.create({
            "user_id": "user-1",
            "status": "running",
            "resume_text": "r",
            "opportunity_text": "o",
        })
        self.db.commit()

        updated = repo.update_status(
            run.id,
            "completed",
            total_latency_ms=1500.0,
            error_message=None,
        )
        self.db.commit()

        assert updated.status == "completed"
        assert updated.total_latency_ms == 1500.0


class TestPipelineStageRepository:
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def teardown_method(self):
        self.db.close()

    def _create_run(self):
        repo = PipelineRunRepository(self.db)
        run = repo.create({
            "user_id": "user-1",
            "status": "running",
            "resume_text": "r",
            "opportunity_text": "o",
        })
        self.db.commit()
        return run

    def test_create_batch(self):
        run = self._create_run()
        repo = PipelineStageRepository(self.db)

        stages = repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "resume_intelligence", "stage_order": 1, "status": "pending"},
            {"pipeline_run_id": run.id, "stage_name": "opportunity", "stage_order": 2, "status": "pending"},
            {"pipeline_run_id": run.id, "stage_name": "gap_analysis", "stage_order": 3, "status": "pending"},
        ])
        self.db.commit()

        assert len(stages) == 3
        assert all(s.id is not None for s in stages)
        assert all(s.pipeline_run_id == run.id for s in stages)

    def test_get_by_id(self):
        run = self._create_run()
        repo = PipelineStageRepository(self.db)

        stages = repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "test", "stage_order": 1, "status": "pending"},
        ])
        self.db.commit()

        found = repo.get_by_id(stages[0].id)
        assert found is not None
        assert found.id == stages[0].id

    def test_get_by_run_id_ordering(self):
        run = self._create_run()
        repo = PipelineStageRepository(self.db)

        repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "stage_c", "stage_order": 3, "status": "pending"},
            {"pipeline_run_id": run.id, "stage_name": "stage_a", "stage_order": 1, "status": "pending"},
            {"pipeline_run_id": run.id, "stage_name": "stage_b", "stage_order": 2, "status": "pending"},
        ])
        self.db.commit()

        stages = repo.get_by_run_id(run.id)
        assert len(stages) == 3
        assert [s.stage_order for s in stages] == [1, 2, 3]
        assert [s.stage_name for s in stages] == ["stage_a", "stage_b", "stage_c"]

    def test_update_status(self):
        run = self._create_run()
        repo = PipelineStageRepository(self.db)

        stages = repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "test", "stage_order": 1, "status": "pending"},
        ])
        self.db.commit()

        updated = repo.update_status(stages[0].id, "running")
        self.db.commit()

        assert updated.status == "running"

    def test_update_status_with_kwargs(self):
        run = self._create_run()
        repo = PipelineStageRepository(self.db)

        stages = repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "test", "stage_order": 1, "status": "running"},
        ])
        self.db.commit()

        from datetime import datetime
        updated = repo.update_status(
            stages[0].id,
            "completed",
            entity_id="entity-1",
            latency_ms=500.0,
            started_at=datetime(2026, 1, 1),
            completed_at=datetime(2026, 1, 1, 0, 0, 1),
        )
        self.db.commit()

        assert updated.status == "completed"
        assert updated.entity_id == "entity-1"
        assert updated.latency_ms == 500.0

    def test_update_status_skipped(self):
        run = self._create_run()
        repo = PipelineStageRepository(self.db)

        stages = repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "validation", "stage_order": 7, "status": "pending"},
        ])
        self.db.commit()

        updated = repo.update_status(stages[0].id, "skipped")
        self.db.commit()

        assert updated.status == "skipped"

    def test_run_stages_relationship(self):
        run = self._create_run()
        stage_repo = PipelineStageRepository(self.db)

        stage_repo.create_batch([
            {"pipeline_run_id": run.id, "stage_name": "s1", "stage_order": 1, "status": "completed"},
            {"pipeline_run_id": run.id, "stage_name": "s2", "stage_order": 2, "status": "completed"},
        ])
        self.db.commit()

        run_repo = PipelineRunRepository(self.db)
        found_run = run_repo.get_by_id(run.id)
        assert len(found_run.stages) == 2
        assert found_run.stages[0].stage_name == "s1"
        assert found_run.stages[1].stage_name == "s2"
