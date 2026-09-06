"""Tests for Error domain models, repositories, services, and middleware."""
import json
import sys
import os
import unittest
from datetime import datetime, timedelta

from sqlalchemy import text

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.models import Base
from app.models.error import ErrorArchive, ErrorCategory, ErrorLog, ErrorOccurrence, ErrorResolution
from app.repositories.error import (
    ErrorArchiveRepository,
    ErrorCategoryRepository,
    ErrorLogRepository,
    ErrorOccurrenceRepository,
    ErrorResolutionRepository,
)
from app.services.error_service import ErrorService


ERROR_TABLES = [
    "error_resolutions",
    "error_occurrences",
    "error_logs",
    "error_categories",
    "error_archive",
]


def _clean_error_tables():
    """Delete rows from error tables in FK-safe order."""
    with engine.begin() as conn:
        for table in ERROR_TABLES:
            try:
                conn.execute(text(f"DELETE FROM {table}"))
            except Exception:
                pass


class TestErrorModels(unittest.TestCase):
    """Test Error domain models."""

    def setUp(self):
        """Set up test database."""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        _clean_error_tables()

    def test_error_log_creation(self):
        """Test ErrorLog creation."""
        error = ErrorLog(
            error_type="TestError",
            error_message="Test error message",
            error_fingerprint="test-fingerprint-123",
            severity="medium",
            environment="test",
        )
        self.db.add(error)
        self.db.commit()
        self.db.refresh(error)

        self.assertIsNotNone(error.id)
        self.assertEqual(error.error_type, "TestError")
        self.assertEqual(error.severity, "medium")

    def test_error_category_creation(self):
        """Test ErrorCategory creation."""
        category = ErrorCategory(
            name="TestCategory",
            description="Test category",
            default_severity="medium",
        )
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)

        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "TestCategory")

    def test_error_resolution_creation(self):
        """Test ErrorResolution creation."""
        resolution = ErrorResolution(
            resolution_type="fixed",
            title="Fixed the bug",
            description="Applied a patch",
        )
        self.db.add(resolution)
        self.db.commit()
        self.db.refresh(resolution)

        self.assertIsNotNone(resolution.id)
        self.assertEqual(resolution.resolution_type, "fixed")

    def test_error_occurrence_creation(self):
        """Test ErrorOccurrence creation."""
        # Create parent error
        error = ErrorLog(
            error_type="TestError",
            error_message="Test message",
            error_fingerprint="fp-123",
            severity="low",
            environment="test",
        )
        self.db.add(error)
        self.db.commit()

        # Create occurrence
        occurrence = ErrorOccurrence(
            error_log_id=error.id,
            error_fingerprint="fp-123",
            endpoint="/test",
        )
        self.db.add(occurrence)
        self.db.commit()
        self.db.refresh(occurrence)

        self.assertIsNotNone(occurrence.id)
        self.assertEqual(occurrence.error_log_id, error.id)

    def test_error_archive_creation(self):
        """Test ErrorArchive creation."""
        archive = ErrorArchive(
            original_id="original-123",
            error_type="TestError",
            error_message="Test message",
            error_fingerprint="fp-123",
            severity="low",
            environment="test",
            status="new",
            first_occurrence_at=datetime.utcnow(),
            last_occurrence_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        self.db.add(archive)
        self.db.commit()
        self.db.refresh(archive)

        self.assertIsNotNone(archive.id)
        self.assertEqual(archive.original_id, "original-123")


class TestErrorRepositories(unittest.TestCase):
    """Test Error domain repositories."""

    def setUp(self):
        """Set up test database and repositories."""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        self.logs = ErrorLogRepository(self.db)
        self.categories = ErrorCategoryRepository(self.db)
        self.resolutions = ErrorResolutionRepository(self.db)
        self.occurrences = ErrorOccurrenceRepository(self.db)
        self.archives = ErrorArchiveRepository(self.db)

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        _clean_error_tables()

    def test_log_error(self):
        """Test logging an error."""
        error = self.logs.log(
            error_type="TestError",
            error_message="Test error message",
            severity="medium",
            environment="test",
        )

        self.assertIsNotNone(error.id)
        self.assertEqual(error.error_type, "TestError")
        self.assertIsNotNone(error.error_fingerprint)

    def test_fingerprint_deduplication(self):
        """Test that same error type/message creates fingerprint."""
        error1 = self.logs.log(
            error_type="DuplicateError",
            error_message="Same message",
            severity="low",
            environment="test",
        )
        error2 = self.logs.log(
            error_type="DuplicateError",
            error_message="Same message",
            severity="low",
            environment="test",
        )

        # Same fingerprint
        self.assertEqual(error1.error_fingerprint, error2.error_fingerprint)
        # Second occurrence increments count
        self.assertEqual(error2.occurrence_count, 2)

    def test_get_by_severity(self):
        """Test getting errors by severity."""
        self.logs.log(error_type="E1", error_message="M1", severity="high", environment="test")
        self.logs.log(error_type="E2", error_message="M2", severity="low", environment="test")
        self.logs.log(error_type="E3", error_message="M3", severity="high", environment="test")

        high_errors = self.logs.get_by_severity("high")
        self.assertEqual(len(high_errors), 2)

    def test_get_by_status(self):
        """Test getting errors by status."""
        e1 = self.logs.log(error_type="E1", error_message="M1", severity="low", environment="test")
        e2 = self.logs.log(error_type="E2", error_message="M2", severity="low", environment="test")

        self.logs.update_status(e1.id, "acknowledged")

        new_errors = self.logs.get_by_status("new")
        ack_errors = self.logs.get_by_status("acknowledged")

        self.assertEqual(len(new_errors), 1)
        self.assertEqual(len(ack_errors), 1)

    def test_count_by_severity(self):
        """Test counting errors by severity."""
        self.logs.log(error_type="E1", error_message="M1", severity="high", environment="test")
        self.logs.log(error_type="E2", error_message="M2", severity="low", environment="test")
        self.logs.log(error_type="E3", error_message="M3", severity="high", environment="test")

        counts = self.logs.count_by_severity()
        self.assertEqual(counts["high"], 2)
        self.assertEqual(counts["low"], 1)

    def test_create_category(self):
        """Test creating a category."""
        category = self.categories.create({
            "name": "TestCategory",
            "description": "Test",
            "default_severity": "medium",
        })

        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "TestCategory")

    def test_create_resolution(self):
        """Test creating a resolution."""
        resolution = self.resolutions.create({
            "resolution_type": "fixed",
            "title": "Fixed it",
        })

        self.assertIsNotNone(resolution.id)
        self.assertEqual(resolution.resolution_type, "fixed")

    def test_archive_error(self):
        """Test archiving an error."""
        error = self.logs.log(
            error_type="ArchiveTest",
            error_message="Archive me",
            severity="low",
            environment="test",
        )

        archive = self.archives.archive_error(error)

        self.assertIsNotNone(archive.id)
        self.assertEqual(archive.original_id, error.id)


class TestErrorService(unittest.TestCase):
    """Test Error domain service."""

    def setUp(self):
        """Set up test database and service."""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        self.service = ErrorService(self.db)

    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        _clean_error_tables()

    def test_log_exception(self):
        """Test logging an exception."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            error = self.service.log_exception(
                e,
                endpoint="/test",
                http_method="GET",
                environment="test",
            )

        self.assertIsNotNone(error.id)
        self.assertEqual(error.error_type, "ValueError")

    def test_log_error(self):
        """Test logging a handled error."""
        error = self.service.log_error(
            error_type="HandledError",
            error_message="Something went wrong",
            severity="medium",
            environment="test",
        )

        self.assertIsNotNone(error.id)

    def test_log_api_error(self):
        """Test logging an API error."""
        error = self.service.log_api_error(
            status_code=404,
            detail="Not found",
            endpoint="/api/test",
            http_method="GET",
        )

        self.assertIsNotNone(error.id)
        self.assertEqual(error.response_status, 404)

    def test_get_error_history(self):
        """Test getting error history."""
        self.service.log_error(
            error_type="E1", error_message="M1", severity="low", environment="test"
        )
        self.service.log_error(
            error_type="E2", error_message="M2", severity="high", environment="test"
        )

        history = self.service.get_error_history()
        self.assertEqual(len(history), 2)

    def test_get_unresolved_errors(self):
        """Test getting unresolved errors."""
        e1 = self.service.log_error(
            error_type="E1", error_message="M1", severity="low", environment="test"
        )
        e2 = self.service.log_error(
            error_type="E2", error_message="M2", severity="low", environment="test"
        )

        # Acknowledge e1
        self.service.acknowledge_error(e1.id)
        
        # Verify e1 is now acknowledged
        e1_updated = self.service.get_error(e1.id)
        self.assertEqual(e1_updated.status, "acknowledged")
        
        # Get unresolved errors
        unresolved = self.service.get_unresolved_errors()
        # Only e2 should be "new"
        new_errors = [e for e in unresolved if e.status == "new"]
        self.assertEqual(len(new_errors), 1)
        self.assertEqual(new_errors[0].id, e2.id)

    def test_resolve_error(self):
        """Test resolving an error."""
        error = self.service.log_error(
            error_type="ResolvableError",
            error_message="Fix me",
            severity="medium",
            environment="test",
        )

        resolved = self.service.resolve_error(
            error.id,
            resolution_type="fixed",
            title="Applied fix",
            description="Fixed the issue",
        )

        self.assertEqual(resolved.status, "resolved")
        self.assertIsNotNone(resolved.resolution_id)

    def test_wont_fix_error(self):
        """Test marking an error as won't fix."""
        error = self.service.log_error(
            error_type="WontFixError",
            error_message="By design",
            severity="low",
            environment="test",
        )

        wont_fix = self.service.wont_fix_error(error.id, "Intentional behavior")

        self.assertEqual(wont_fix.status, "wont_fix")

    def test_get_error_statistics(self):
        """Test getting error statistics."""
        self.service.log_error(
            error_type="E1", error_message="M1", severity="low", environment="test"
        )
        self.service.log_error(
            error_type="E2", error_message="M2", severity="high", environment="test"
        )

        stats = self.service.get_error_statistics()

        self.assertEqual(stats["total_count"], 2)
        self.assertIn("by_severity", stats)
        self.assertIn("by_status", stats)

    def test_search_errors(self):
        """Test searching errors."""
        self.service.log_error(
            error_type="SearchableError",
            error_message="Unique search term",
            severity="low",
            environment="test",
        )

        results = self.service.search_errors("Unique")
        self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
