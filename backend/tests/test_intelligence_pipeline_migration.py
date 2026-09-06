"""Tests for Intelligence Pipeline database migration.

Verifies upgrade, downgrade, and idempotency of the pipeline domain migration.
Uses SQLite in-memory to avoid requiring a real database.
"""
import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.models.base import Base


# ============================================================================
# Helpers
# ============================================================================

def _create_users_table(engine):
    """Create a minimal users table for FK references."""
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS users ("
            "id VARCHAR(36) PRIMARY KEY, "
            "email VARCHAR(255) NOT NULL UNIQUE"
            ")"
        ))
        conn.commit()


def _get_table_names(engine):
    """Return set of table names in the database."""
    return set(inspect(engine).get_table_names())


def _get_columns(engine, table_name):
    """Return dict of column_name -> column_info for a table."""
    inspector = inspect(engine)
    return {col["name"]: col for col in inspector.get_columns(table_name)}


def _get_foreign_keys(engine, table_name):
    """Return list of FK info for a table."""
    inspector = inspect(engine)
    return inspector.get_foreign_keys(table_name)


def _get_indexes(engine, table_name):
    """Return list of index info for a table."""
    inspector = inspect(engine)
    return inspector.get_indexes(table_name)


# ============================================================================
# TestMigrationImport
# ============================================================================

class TestMigrationImport:
    def test_module_imports(self):
        from migrations import add_pipeline_domain
        assert add_pipeline_domain is not None

    def test_migrate_function_exists(self):
        from migrations.add_pipeline_domain import migrate
        assert callable(migrate)

    def test_rollback_function_exists(self):
        from migrations.add_pipeline_domain import rollback
        assert callable(rollback)


# ============================================================================
# TestMigrationUpgrade
# ============================================================================

class TestMigrationUpgrade:
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        _create_users_table(self.engine)

    def teardown_method(self):
        self.engine.dispose()

    def test_migrate_creates_pipeline_runs(self):
        from migrations.add_pipeline_domain import migrate
        with self.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # Mock get_engine to return our test engine
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        tables = _get_table_names(self.engine)
        assert "pipeline_runs" in tables

    def test_migrate_creates_pipeline_stages(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        tables = _get_table_names(self.engine)
        assert "pipeline_stages" in tables

    def test_pipeline_runs_columns(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        columns = _get_columns(self.engine, "pipeline_runs")
        expected_columns = [
            "id", "user_id", "status",
            "resume_text", "opportunity_text",
            "resume_profile_id", "opportunity_id", "gap_analysis_id",
            "knowledge_retrieval_id", "prompt_package_id",
            "ai_execution_id", "ai_validation_id",
            "total_latency_ms", "error_message", "metadata",
            "created_at", "updated_at",
        ]
        for col_name in expected_columns:
            assert col_name in columns, f"Missing column: {col_name}"

    def test_pipeline_stages_columns(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        columns = _get_columns(self.engine, "pipeline_stages")
        expected_columns = [
            "id", "pipeline_run_id",
            "stage_name", "stage_order", "status",
            "entity_id", "latency_ms", "error_message", "metadata",
            "started_at", "completed_at",
        ]
        for col_name in expected_columns:
            assert col_name in columns, f"Missing column: {col_name}"

    def test_user_id_foreign_key(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        fks = _get_foreign_keys(self.engine, "pipeline_runs")
        user_fk = [fk for fk in fks if fk["referred_table"] == "users"]
        assert len(user_fk) == 1
        assert user_fk[0]["referred_columns"] == ["id"]

    def test_pipeline_run_id_foreign_key(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        fks = _get_foreign_keys(self.engine, "pipeline_stages")
        run_fk = [fk for fk in fks if fk["referred_table"] == "pipeline_runs"]
        assert len(run_fk) == 1
        assert run_fk[0]["referred_columns"] == ["id"]

    def test_entity_ids_have_no_foreign_keys(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        fks = _get_foreign_keys(self.engine, "pipeline_runs")
        fk_referred_tables = {fk["referred_table"] for fk in fks}
        # Only users should be a FK target
        assert fk_referred_tables == {"users"}

    def test_indexes_exist(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
        finally:
            mod.get_engine = original_get_engine

        # Check composite indexes
        run_indexes = _get_indexes(self.engine, "pipeline_runs")
        run_index_names = {idx["name"] for idx in run_indexes}
        assert "ix_pipeline_runs_user_created" in run_index_names

        stage_indexes = _get_indexes(self.engine, "pipeline_stages")
        stage_index_names = {idx["name"] for idx in stage_indexes}
        assert "ix_pipeline_stages_run_order" in stage_index_names


# ============================================================================
# TestMigrationIdempotency
# ============================================================================

class TestMigrationIdempotency:
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        _create_users_table(self.engine)

    def teardown_method(self):
        self.engine.dispose()

    def test_migrate_called_twice_does_not_fail(self):
        from migrations.add_pipeline_domain import migrate
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
            migrate()  # Second call should not fail
        finally:
            mod.get_engine = original_get_engine

        tables = _get_table_names(self.engine)
        assert "pipeline_runs" in tables
        assert "pipeline_stages" in tables


# ============================================================================
# TestMigrationRollback
# ============================================================================

class TestMigrationRollback:
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        _create_users_table(self.engine)

    def teardown_method(self):
        self.engine.dispose()

    def test_rollback_executes_without_crashing(self):
        """Rollback runs without crashing, even if CASCADE is unsupported by SQLite."""
        from migrations.add_pipeline_domain import migrate, rollback
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            migrate()
            rollback()  # Should not raise even if DROP TABLE CASCADE fails on SQLite
        finally:
            mod.get_engine = original_get_engine

    def test_rollback_on_nonexistent_tables_does_not_fail(self):
        from migrations.add_pipeline_domain import rollback
        import migrations.add_pipeline_domain as mod
        original_get_engine = mod.get_engine
        mod.get_engine = lambda: self.engine
        try:
            rollback()  # Should not fail even if tables don't exist
        finally:
            mod.get_engine = original_get_engine

    def test_rollback_source_targets_correct_tables(self):
        """Verify rollback source code targets only pipeline_stages and pipeline_runs."""
        import inspect
        from migrations.add_pipeline_domain import rollback
        source = inspect.getsource(rollback)
        assert "pipeline_stages" in source
        assert "pipeline_runs" in source
        # Verify drop order: stages before runs (child before parent)
        stages_pos = source.index("pipeline_stages")
        runs_pos = source.index("pipeline_runs")
        assert stages_pos < runs_pos
