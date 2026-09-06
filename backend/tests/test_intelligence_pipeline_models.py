"""Tests for Intelligence Pipeline models: PipelineRun, PipelineStage.

Verifies model structure, relationships, defaults, and contract compliance.
"""
import pytest
from app.models.pipeline import PipelineRun, PipelineStage


class TestPipelineRun:
    def test_import(self):
        assert PipelineRun is not None

    def test_tablename(self):
        assert PipelineRun.__tablename__ == "pipeline_runs"

    def test_required_columns(self):
        cols = {c.name for c in PipelineRun.__table__.columns}
        required = {
            "id", "user_id", "status",
            "resume_text", "opportunity_text",
            "total_latency_ms", "error_message", "metadata",
            "created_at", "updated_at",
        }
        assert required.issubset(cols)

    def test_entity_id_columns(self):
        cols = {c.name for c in PipelineRun.__table__.columns}
        entity_ids = {
            "resume_profile_id", "opportunity_id", "gap_analysis_id",
            "knowledge_retrieval_id", "prompt_package_id",
            "ai_execution_id", "ai_validation_id",
        }
        assert entity_ids.issubset(cols)

    def test_status_default(self):
        status_col = PipelineRun.__table__.c.status
        assert status_col.default.arg == "pending"

    def test_metadata_column_name(self):
        metadata_col = PipelineRun.__table__.c.metadata
        assert metadata_col.name == "metadata"

    def test_nullable_entity_ids(self):
        entity_ids = [
            "resume_profile_id", "opportunity_id", "gap_analysis_id",
            "knowledge_retrieval_id", "prompt_package_id",
            "ai_execution_id", "ai_validation_id",
        ]
        for col_name in entity_ids:
            col = getattr(PipelineRun, col_name)
            assert col.property.columns[0].nullable is True

    def test_user_id_foreign_key(self):
        fk = PipelineRun.__table__.c.user_id.foreign_keys
        assert len(fk) == 1
        fk_obj = list(fk)[0]
        assert fk_obj.column.table.name == "users"

    def test_relationships(self):
        rels = {r.key for r in PipelineRun.__mapper__.relationships}
        assert "stages" in rels


class TestPipelineStage:
    def test_import(self):
        assert PipelineStage is not None

    def test_tablename(self):
        assert PipelineStage.__tablename__ == "pipeline_stages"

    def test_required_columns(self):
        cols = {c.name for c in PipelineStage.__table__.columns}
        required = {
            "id", "pipeline_run_id",
            "stage_name", "stage_order", "status",
            "entity_id", "latency_ms", "error_message", "metadata",
            "started_at", "completed_at",
        }
        assert required.issubset(cols)

    def test_status_default(self):
        status_col = PipelineStage.__table__.c.status
        assert status_col.default.arg == "pending"

    def test_metadata_column_name(self):
        metadata_col = PipelineStage.__table__.c.metadata
        assert metadata_col.name == "metadata"

    def test_entity_id_nullable(self):
        col = PipelineStage.__table__.c.entity_id
        assert col.nullable is True

    def test_pipeline_run_id_foreign_key(self):
        fk = PipelineStage.__table__.c.pipeline_run_id.foreign_keys
        assert len(fk) == 1
        fk_obj = list(fk)[0]
        assert fk_obj.column.table.name == "pipeline_runs"

    def test_relationships(self):
        rels = {r.key for r in PipelineStage.__mapper__.relationships}
        assert "pipeline_run" in rels

    def test_stage_order_is_integer(self):
        col = PipelineStage.__table__.c.stage_order
        assert str(col.type) == "INTEGER"


class TestPipelineRelationship:
    def test_run_has_stages(self):
        from sqlalchemy.orm import RelationshipProperty
        rel = PipelineRun.__mapper__.relationships.get("stages")
        assert rel is not None
        assert rel.mapper.class_ is PipelineStage

    def test_stage_has_pipeline_run(self):
        from sqlalchemy.orm import RelationshipProperty
        rel = PipelineStage.__mapper__.relationships.get("pipeline_run")
        assert rel is not None
        assert rel.mapper.class_ is PipelineRun

    def test_back_populates_consistent(self):
        run_rel = PipelineRun.__mapper__.relationships["stages"]
        stage_rel = PipelineStage.__mapper__.relationships["pipeline_run"]
        assert run_rel.back_populates == "pipeline_run"
        assert stage_rel.back_populates == "stages"
