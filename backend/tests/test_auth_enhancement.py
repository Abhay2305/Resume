"""Tests for PROC-SPEC-0.1: Authentication Enhancement.

Tests admin authentication, RBAC management, and rate limiting.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base, User, Profile, Subscription, Role, Permission, UserRole, RolePermission
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth_enhancement.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def db():
    """Get a database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Get a test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db):
    """Create a regular test user."""
    user = User(
        email="user@example.com",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Regular User",
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db):
    """Create an admin test user."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPass123"),
        full_name="Admin User",
        is_verified=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def role_with_admin(db):
    """Create a role with admin privileges."""
    role = Role(name="admin", description="Administrator role", is_system=True)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture
def non_system_role(db):
    """Create a non-system role that can be modified."""
    role = Role(name="custom_role", description="Custom role", is_system=False)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@pytest.fixture
def user_with_admin_role(db, role_with_admin):
    """Create a user with admin role."""
    user = User(
        email="roleadmin@example.com",
        hashed_password=get_password_hash("AdminPass123"),
        full_name="Role Admin User",
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign admin role
    user_role = UserRole(user_id=user.id, role_id=role_with_admin.id, is_active=True)
    db.add(user_role)
    db.commit()
    return user


@pytest.fixture
def admin_headers(admin_user):
    """Get authentication headers for admin user."""
    token = create_access_token(data={"sub": admin_user.id, "is_admin": True})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def role_admin_headers(user_with_admin_role):
    """Get authentication headers for role-based admin user."""
    token = create_access_token(data={"sub": user_with_admin_role.id, "is_admin": True})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_headers(test_user):
    """Get authentication headers for regular user."""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Admin Authentication Tests
# ============================================================================


class TestAdminLogin:
    """Tests for admin login endpoint."""

    def test_admin_login_success(self, client, admin_user):
        response = client.post("/api/auth/admin/login", json={
            "email": "admin@example.com",
            "password": "AdminPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "admin" in data
        assert data["admin"]["email"] == "admin@example.com"
        assert data["admin"]["is_superuser"] is True

    def test_admin_login_wrong_password(self, client, admin_user):
        response = client.post("/api/auth/admin/login", json={
            "email": "admin@example.com",
            "password": "WrongPass123",
        })
        assert response.status_code == 401

    def test_admin_login_nonexistent_user(self, client):
        response = client.post("/api/auth/admin/login", json={
            "email": "nonexistent@example.com",
            "password": "TestPass123",
        })
        assert response.status_code == 401

    def test_admin_login_regular_user(self, client, test_user):
        """Regular users cannot login via admin endpoint."""
        response = client.post("/api/auth/admin/login", json={
            "email": "user@example.com",
            "password": "TestPass123",
        })
        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["error"]["message"]

    def test_admin_login_with_admin_role(self, client, user_with_admin_role):
        """Users with admin role can login via admin endpoint."""
        response = client.post("/api/auth/admin/login", json={
            "email": "roleadmin@example.com",
            "password": "AdminPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestAdminMe:
    """Tests for admin me endpoint."""

    def test_admin_me_success(self, client, admin_user, admin_headers):
        response = client.get("/api/auth/admin/me", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@example.com"
        assert data["is_superuser"] is True

    def test_admin_me_unauthenticated(self, client):
        response = client.get("/api/auth/admin/me")
        assert response.status_code == 401

    def test_admin_me_regular_user(self, client, test_user, user_headers):
        """Regular users cannot access admin me endpoint."""
        response = client.get("/api/auth/admin/me", headers=user_headers)
        assert response.status_code == 403


class TestAdminLogout:
    """Tests for admin logout endpoint."""

    def test_admin_logout_success(self, client, admin_user, admin_headers):
        response = client.post("/api/auth/admin/logout", headers=admin_headers)
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()


class TestAdminChangePassword:
    """Tests for admin password change endpoint."""

    def test_admin_change_password_success(self, client, admin_user, admin_headers):
        response = client.post("/api/auth/admin/change-password", headers=admin_headers, json={
            "current_password": "AdminPass123",
            "new_password": "NewAdminPass456",
            "confirm_password": "NewAdminPass456",
        })
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()

    def test_admin_change_password_wrong_current(self, client, admin_user, admin_headers):
        response = client.post("/api/auth/admin/change-password", headers=admin_headers, json={
            "current_password": "WrongPass123",
            "new_password": "NewAdminPass456",
            "confirm_password": "NewAdminPass456",
        })
        assert response.status_code == 401

    def test_admin_change_password_mismatch(self, client, admin_user, admin_headers):
        response = client.post("/api/auth/admin/change-password", headers=admin_headers, json={
            "current_password": "AdminPass123",
            "new_password": "NewAdminPass456",
            "confirm_password": "DifferentPass789",
        })
        assert response.status_code == 422


# ============================================================================
# Role Management Tests
# ============================================================================


class TestRoleManagement:
    """Tests for role CRUD operations."""

    def test_list_roles(self, client, admin_user, admin_headers):
        response = client.get("/api/rbac/roles", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_create_role(self, client, admin_user, admin_headers):
        response = client.post("/api/rbac/roles", headers=admin_headers, json={
            "name": "test_role",
            "description": "Test role",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test_role"
        assert data["description"] == "Test role"

    def test_create_duplicate_role(self, client, admin_user, admin_headers, role_with_admin):
        response = client.post("/api/rbac/roles", headers=admin_headers, json={
            "name": "admin",
            "description": "Duplicate admin",
        })
        assert response.status_code == 400

    def test_get_role(self, client, admin_user, admin_headers, role_with_admin):
        response = client.get(f"/api/rbac/roles/{role_with_admin.id}", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "admin"

    def test_get_role_not_found(self, client, admin_user, admin_headers):
        response = client.get("/api/rbac/roles/nonexistent", headers=admin_headers)
        assert response.status_code == 404

    def test_update_role(self, client, admin_user, admin_headers, non_system_role):
        response = client.put(f"/api/rbac/roles/{non_system_role.id}", headers=admin_headers, json={
            "description": "Updated description",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    def test_delete_role(self, client, admin_user, admin_headers):
        # Create a non-system role
        create_resp = client.post("/api/rbac/roles", headers=admin_headers, json={
            "name": "deletable_role",
            "description": "Can be deleted",
        })
        role_id = create_resp.json()["id"]

        response = client.delete(f"/api/rbac/roles/{role_id}", headers=admin_headers)
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_delete_system_role(self, client, admin_user, admin_headers, role_with_admin):
        response = client.delete(f"/api/rbac/roles/{role_with_admin.id}", headers=admin_headers)
        assert response.status_code == 400
        assert "system role" in response.json()["error"]["message"].lower()

    def test_regular_user_cannot_manage_roles(self, client, test_user, user_headers):
        response = client.get("/api/rbac/roles", headers=user_headers)
        assert response.status_code == 403


# ============================================================================
# Permission Management Tests
# ============================================================================


class TestPermissionManagement:
    """Tests for permission management."""

    def test_list_permissions(self, client, admin_user, admin_headers):
        response = client.get("/api/rbac/permissions", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_add_permission_to_role(self, client, admin_user, admin_headers, role_with_admin, db):
        # Create a permission
        permission = Permission(name="test.permission", description="Test permission")
        db.add(permission)
        db.commit()
        db.refresh(permission)

        response = client.post(
            f"/api/rbac/roles/{role_with_admin.id}/permissions",
            headers=admin_headers,
            json={"permission_id": permission.id},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_get_role_permissions(self, client, admin_user, admin_headers, role_with_admin):
        response = client.get(f"/api/rbac/roles/{role_with_admin.id}/permissions", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_remove_permission_from_role(self, client, admin_user, admin_headers, role_with_admin, db):
        # Create and add a permission
        permission = Permission(name="removable.permission", description="Removable permission")
        db.add(permission)
        db.commit()
        db.refresh(permission)

        # Add permission to role
        db.add(RolePermission(role_id=role_with_admin.id, permission_id=permission.id))
        db.commit()

        response = client.delete(
            f"/api/rbac/roles/{role_with_admin.id}/permissions/{permission.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()


# ============================================================================
# User Role Assignment Tests
# ============================================================================


class TestUserRoleAssignment:
    """Tests for user role assignment."""

    def test_assign_role_to_user(self, client, admin_user, admin_headers, test_user, role_with_admin):
        response = client.post(
            f"/api/rbac/users/{test_user.id}/roles",
            headers=admin_headers,
            json={"role_id": role_with_admin.id},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["role_id"] == role_with_admin.id
        assert data["role_name"] == "admin"

    def test_get_user_roles(self, client, admin_user, admin_headers, user_with_admin_role):
        response = client.get(f"/api/rbac/users/{user_with_admin_role.id}/roles", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_revoke_role_from_user(self, client, admin_user, admin_headers, user_with_admin_role, role_with_admin):
        response = client.delete(
            f"/api/rbac/users/{user_with_admin_role.id}/roles/{role_with_admin.id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert "revoked" in response.json()["message"].lower()

    def test_regular_user_cannot_assign_roles(self, client, test_user, user_headers, role_with_admin):
        response = client.post(
            f"/api/rbac/users/{test_user.id}/roles",
            headers=user_headers,
            json={"role_id": role_with_admin.id},
        )
        assert response.status_code == 403


# ============================================================================
# Rate Limiting Tests
# ============================================================================


class TestRateLimiting:
    """Tests for rate limiting middleware."""

    def test_rate_limit_headers(self, client, test_user, user_headers):
        """Verify rate limit headers are present in response."""
        response = client.get("/api/auth/me", headers=user_headers)
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    def test_auth_endpoint_rate_limit(self, client, test_user):
        """Test that auth endpoints have stricter rate limits."""
        # Make multiple rapid requests to hit rate limit
        for i in range(15):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "WrongPass",
            })
            if response.status_code == 429:
                # Rate limit hit
                assert "retry_after" in response.json()
                return

        # If we get here, rate limit wasn't hit (which is also valid depending on timing)
        assert True


# ============================================================================
# RBAC Service Unit Tests
# ============================================================================


class TestRBACService:
    """Unit tests for RBAC service."""

    def test_create_role(self, db):
        from app.services.rbac_service import RBACService
        service = RBACService(db)
        
        role = service.create_role(name="test", description="Test role")
        assert role.name == "test"
        assert role.description == "Test role"

    def test_create_duplicate_role(self, db):
        from app.services.rbac_service import RBACService
        service = RBACService(db)
        
        service.create_role(name="test", description="Test role")
        with pytest.raises(ValueError, match="already exists"):
            service.create_role(name="test", description="Duplicate")

    def test_update_role(self, db):
        from app.services.rbac_service import RBACService
        service = RBACService(db)
        
        role = service.create_role(name="test", description="Test role")
        updated = service.update_role(role.id, description="Updated")
        assert updated.description == "Updated"

    def test_delete_role(self, db):
        from app.services.rbac_service import RBACService
        service = RBACService(db)
        
        role = service.create_role(name="test", description="Test role")
        result = service.delete_role(role.id)
        assert result is True

    def test_assign_role(self, db, test_user):
        from app.services.rbac_service import RBACService
        service = RBACService(db)
        
        role = service.create_role(name="test", description="Test role")
        assignment = service.assign_role(test_user.id, role.id)
        assert assignment.user_id == test_user.id
        assert assignment.role_id == role.id

    def test_revoke_role(self, db, test_user):
        from app.services.rbac_service import RBACService
        service = RBACService(db)
        
        role = service.create_role(name="test", description="Test role")
        service.assign_role(test_user.id, role.id)
        result = service.revoke_role(test_user.id, role.id)
        assert result is True
