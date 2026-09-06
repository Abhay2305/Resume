"""Unit tests for ResumeManagementService."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from app.services.resume_management_service import ResumeManagementService
from app.models.resume import Resume, ResumeSection, ResumeVersion, Template


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_resume():
    resume = MagicMock(spec=Resume)
    resume.id = "test-resume-id"
    resume.user_id = "test-user-id"
    resume.title = "Test Resume"
    resume.template_id = "harvard"
    resume.created_at = datetime.utcnow()
    resume.updated_at = datetime.utcnow()
    return resume


@pytest.fixture
def mock_section():
    section = MagicMock(spec=ResumeSection)
    section.id = "test-section-id"
    section.resume_id = "test-resume-id"
    section.section_type = "experience"
    section.content = []
    section.position = 0
    section.created_at = datetime.utcnow()
    section.updated_at = datetime.utcnow()
    return section


@pytest.fixture
def mock_version():
    version = MagicMock(spec=ResumeVersion)
    version.id = "test-version-id"
    version.resume_id = "test-resume-id"
    version.version_number = 1
    version.content = {"experience": []}
    version.created_at = datetime.utcnow()
    return version


@pytest.fixture
def service(mock_db):
    return ResumeManagementService(mock_db)


class TestGetResumes:
    def test_returns_paginated_resumes(self, service, mock_db, mock_resume):
        service.resumes.get_resumes_with_filters = MagicMock(return_value=[mock_resume])
        service.resumes.count_with_filters = MagicMock(return_value=1)

        result = service.get_resumes(page=1, limit=20)

        assert result["total"] == 1
        assert result["page"] == 1
        assert result["limit"] == 20
        assert result["totalPages"] == 1
        assert len(result["items"]) == 1

    def test_applies_search_filter(self, service, mock_db):
        service.resumes.get_resumes_with_filters = MagicMock(return_value=[])
        service.resumes.count_with_filters = MagicMock(return_value=0)

        service.get_resumes(search="test")

        service.resumes.get_resumes_with_filters.assert_called_once()

    def test_handles_empty_results(self, service, mock_db):
        service.resumes.get_resumes_with_filters = MagicMock(return_value=[])
        service.resumes.count_with_filters = MagicMock(return_value=0)

        result = service.get_resumes()

        assert result["items"] == []
        assert result["total"] == 0


class TestGetResumeDetail:
    def test_returns_resume_when_found(self, service, mock_db, mock_resume):
        service.resumes.get = MagicMock(return_value=mock_resume)

        result = service.get_resume_detail("test-resume-id")

        assert result == mock_resume

    def test_returns_none_when_not_found(self, service, mock_db):
        service.resumes.get = MagicMock(return_value=None)

        result = service.get_resume_detail("nonexistent-id")

        assert result is None


class TestGetResumeSections:
    def test_returns_sections(self, service, mock_db, mock_section):
        service.sections.get_by_resume = MagicMock(return_value=[mock_section])

        result = service.get_resume_sections("test-resume-id")

        assert len(result) == 1
        assert result[0] == mock_section

    def test_returns_empty_list_when_no_sections(self, service, mock_db):
        service.sections.get_by_resume = MagicMock(return_value=[])

        result = service.get_resume_sections("test-resume-id")

        assert result == []


class TestGetResumeVersions:
    def test_returns_versions(self, service, mock_db, mock_version):
        service.versions.get_by_resume = MagicMock(return_value=[mock_version])

        result = service.get_resume_versions("test-resume-id")

        assert len(result) == 1
        assert result[0] == mock_version

    def test_returns_empty_list_when_no_versions(self, service, mock_db):
        service.versions.get_by_resume = MagicMock(return_value=[])

        result = service.get_resume_versions("test-resume-id")

        assert result == []


class TestUpdateResume:
    def test_updates_resume_fields(self, service, mock_db, mock_resume):
        service.resumes.get = MagicMock(return_value=mock_resume)
        service.audit = MagicMock()

        result = service.update_resume(
            "test-resume-id",
            {"title": "Updated Title"},
            "admin-id"
        )

        assert mock_resume.title == "Updated Title"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_returns_none_when_resume_not_found(self, service, mock_db):
        service.resumes.get = MagicMock(return_value=None)

        result = service.update_resume(
            "nonexistent-id",
            {"title": "Updated Title"},
            "admin-id"
        )

        assert result is None

    def test_logs_audit_on_update(self, service, mock_db, mock_resume):
        service.resumes.get = MagicMock(return_value=mock_resume)
        service.audit = MagicMock()

        service.update_resume(
            "test-resume-id",
            {"title": "Updated Title"},
            "admin-id"
        )

        service.audit.log_update.assert_called_once()


class TestSoftDeleteResume:
    def test_deletes_resume(self, service, mock_db, mock_resume):
        service.resumes.get = MagicMock(return_value=mock_resume)
        service.audit = MagicMock()

        result = service.soft_delete_resume("test-resume-id", "admin-id")

        assert result is True
        mock_db.delete.assert_called_once_with(mock_resume)
        mock_db.commit.assert_called_once()

    def test_returns_false_when_resume_not_found(self, service, mock_db):
        service.resumes.get = MagicMock(return_value=None)

        result = service.soft_delete_resume("nonexistent-id", "admin-id")

        assert result is False

    def test_logs_audit_on_delete(self, service, mock_db, mock_resume):
        service.resumes.get = MagicMock(return_value=mock_resume)
        service.audit = MagicMock()

        service.soft_delete_resume("test-resume-id", "admin-id")

        service.audit.log_delete.assert_called_once()


class TestGetResumeStats:
    def test_returns_resume_statistics(self, service, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10

        result = service.get_resume_stats()

        assert "total_resumes" in result
        assert "new_resumes_today" in result
        assert "new_resumes_this_week" in result
        assert "new_resumes_this_month" in result
        assert "total_templates" in result

    def test_handles_database_errors(self, service, mock_db):
        mock_db.query.side_effect = Exception("Database error")

        result = service.get_resume_stats()

        assert result["total_resumes"] == 0
        assert result["new_resumes_today"] == 0


class TestGetTemplateStats:
    def test_returns_template_statistics(self, service, mock_db):
        mock_template = MagicMock(spec=Template)
        mock_template.id = "harvard"
        mock_template.name = "Harvard"
        mock_template.category = "professional"

        service.templates.get_all_templates = MagicMock(return_value=[mock_template])
        service.resumes.count_by_template = MagicMock(return_value=5)

        result = service.get_template_stats()

        assert len(result) == 1
        assert result[0]["id"] == "harvard"
        assert result[0]["usage_count"] == 5

    def test_handles_empty_templates(self, service, mock_db):
        service.templates.get_all_templates = MagicMock(return_value=[])

        result = service.get_template_stats()

        assert result == []
