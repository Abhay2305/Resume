"""Unit tests for UserManagementService."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

from app.services.user_management_service import UserManagementService
from app.models.identity import User, Profile, UserRole, Role


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = "test-user-id"
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.is_active = True
    user.is_verified = True
    user.is_superuser = False
    user.avatar_url = None
    user.timezone = "UTC"
    user.language = "en"
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = "127.0.0.1"
    user.failed_login_attempts = 0
    user.locked_until = None
    user.password_changed_at = None
    user.email_verified_at = datetime.utcnow()
    user.created_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()
    user.deleted_at = None
    user.profile = None
    return user


@pytest.fixture
def service(mock_db):
    return UserManagementService(mock_db)


class TestGetUsers:
    def test_returns_paginated_users(self, service, mock_db, mock_user):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_user]

        result = service.get_users(page=1, limit=20)

        assert result["total"] == 1
        assert result["page"] == 1
        assert result["limit"] == 20
        assert result["totalPages"] == 1
        assert len(result["items"]) == 1

    def test_applies_search_filter(self, service, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        service.get_users(search="test")

        assert mock_query.filter.call_count >= 1

    def test_applies_active_filter(self, service, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        service.get_users(is_active=True)

        assert mock_query.filter.call_count >= 1

    def test_handles_empty_results(self, service, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = service.get_users()

        assert result["items"] == []
        assert result["total"] == 0


class TestGetUserDetail:
    def test_returns_user_when_found(self, service, mock_db, mock_user):
        service.users.get = MagicMock(return_value=mock_user)

        result = service.get_user_detail("test-user-id")

        assert result == mock_user

    def test_returns_none_when_not_found(self, service, mock_db):
        service.users.get = MagicMock(return_value=None)

        result = service.get_user_detail("nonexistent-id")

        assert result is None

    def test_returns_none_when_soft_deleted(self, service, mock_db, mock_user):
        mock_user.deleted_at = datetime.utcnow()
        service.users.get = MagicMock(return_value=mock_user)

        result = service.get_user_detail("test-user-id")

        assert result is None


class TestGetUserRoles:
    def test_returns_user_roles(self, service, mock_db):
        mock_role = MagicMock(spec=Role)
        mock_role.id = "role-id"
        mock_role.name = "admin"

        mock_user_role = MagicMock(spec=UserRole)
        mock_user_role.id = "user-role-id"
        mock_user_role.user_id = "test-user-id"
        mock_user_role.role_id = "role-id"
        mock_user_role.is_active = True
        mock_user_role.created_at = datetime.utcnow()

        mock_result = MagicMock()
        mock_result.UserRole = mock_user_role
        mock_result.Role = mock_role

        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_result]

        result = service.get_user_roles("test-user-id")

        assert len(result) == 1
        assert result[0]["role_name"] == "admin"

    def test_returns_empty_list_when_no_roles(self, service, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        result = service.get_user_roles("test-user-id")

        assert result == []


class TestUpdateUser:
    def test_updates_user_fields(self, service, mock_db, mock_user):
        service.users.get = MagicMock(return_value=mock_user)
        service.audit = MagicMock()

        result = service.update_user(
            "test-user-id",
            {"full_name": "Updated Name"},
            "admin-id"
        )

        assert mock_user.full_name == "Updated Name"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_returns_none_when_user_not_found(self, service, mock_db):
        service.users.get = MagicMock(return_value=None)

        result = service.update_user(
            "nonexistent-id",
            {"full_name": "Updated Name"},
            "admin-id"
        )

        assert result is None

    def test_logs_audit_on_update(self, service, mock_db, mock_user):
        service.users.get = MagicMock(return_value=mock_user)
        service.audit = MagicMock()

        service.update_user(
            "test-user-id",
            {"full_name": "Updated Name"},
            "admin-id"
        )

        service.audit.log_update.assert_called_once()


class TestSoftDeleteUser:
    def test_soft_deletes_user(self, service, mock_db, mock_user):
        service.users.get = MagicMock(return_value=mock_user)
        service.audit = MagicMock()

        result = service.soft_delete_user("test-user-id", "admin-id")

        assert result is True
        assert mock_user.deleted_at is not None
        assert mock_user.is_active is False
        mock_db.commit.assert_called_once()

    def test_returns_false_when_user_not_found(self, service, mock_db):
        service.users.get = MagicMock(return_value=None)

        result = service.soft_delete_user("nonexistent-id", "admin-id")

        assert result is False

    def test_logs_audit_on_delete(self, service, mock_db, mock_user):
        service.users.get = MagicMock(return_value=mock_user)
        service.audit = MagicMock()

        service.soft_delete_user("test-user-id", "admin-id")

        service.audit.log_delete.assert_called_once()


class TestGetUserStats:
    def test_returns_user_statistics(self, service, mock_db):
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = 10

        result = service.get_user_stats()

        assert "total_users" in result
        assert "active_users" in result
        assert "verified_users" in result
        assert "superuser_count" in result
        assert "new_users_today" in result
        assert "new_users_this_week" in result
        assert "new_users_this_month" in result

    def test_handles_database_errors(self, service, mock_db):
        mock_db.query.side_effect = Exception("Database error")

        result = service.get_user_stats()

        assert result["total_users"] == 0
        assert result["active_users"] == 0
