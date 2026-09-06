"""Tests for authentication features.

Tests email verification, change password, delete account, remember me,
and session management flows.
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.models import Base, User, Profile, Subscription
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_verification_token,
    create_verification_token,
    verify_verification_token,
)


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
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
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Test User",
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(user_id=user.id)
    db.add(profile)

    sub = Subscription(user_id=user.id, plan_type="free", status="active")
    db.add(sub)
    db.commit()

    return user


@pytest.fixture
def verified_user(db):
    """Create a verified test user."""
    user = User(
        email="verified@example.com",
        hashed_password=get_password_hash("TestPass123"),
        full_name="Verified User",
        is_verified=True,
        email_verified_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = Profile(user_id=user.id)
    db.add(profile)

    sub = Subscription(user_id=user.id, plan_type="free", status="active")
    db.add(sub)
    db.commit()

    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers for test user."""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def verified_auth_headers(verified_user):
    """Get authentication headers for verified test user."""
    token = create_access_token(data={"sub": verified_user.id})
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# Registration Tests
# ============================================================================


class TestRegistration:
    def test_register_success(self, client, db):
        response = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "StrongPass123",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "id" in data

        # Verify user was created with verification token
        user = db.query(User).filter(User.email == "new@example.com").first()
        assert user is not None
        assert user.is_verified is False
        assert user.verification_token is not None

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "StrongPass123",
            "full_name": "Duplicate User",
        })
        assert response.status_code == 400
        assert "already registered" in response.json()["error"]["message"]

    def test_register_weak_password(self, client):
        response = client.post("/api/auth/register", json={
            "email": "weak@example.com",
            "password": "weak",
            "full_name": "Weak User",
        })
        assert response.status_code == 422


# ============================================================================
# Login Tests
# ============================================================================


class TestLogin:
    def test_login_success(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_remember_me(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123",
            "remember_me": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPass123",
        })
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["error"]["message"]

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "TestPass123",
        })
        assert response.status_code == 401


# ============================================================================
# Email Verification Tests
# ============================================================================


class TestEmailVerification:
    def test_send_verification_success(self, client, test_user, auth_headers):
        response = client.post("/api/auth/send-verification", headers=auth_headers)
        assert response.status_code == 200
        assert "sent" in response.json()["message"].lower() or "already" in response.json()["message"].lower()

    def test_send_verification_already_verified(self, client, verified_user, verified_auth_headers):
        response = client.post("/api/auth/send-verification", headers=verified_auth_headers)
        assert response.status_code == 200
        assert "already verified" in response.json()["message"].lower()

    def test_verify_email_success(self, client, test_user, db):
        # Generate a verification token
        token = generate_verification_token()
        test_user.verification_token = token
        test_user.verification_token_expires_at = datetime.utcnow() + timedelta(hours=24)
        db.commit()

        response = client.get(f"/api/auth/verify-email?token={token}")
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()

        # Verify user is now verified
        db.refresh(test_user)
        assert test_user.is_verified is True
        assert test_user.email_verified_at is not None

    def test_verify_email_invalid_token(self, client):
        response = client.get("/api/auth/verify-email?token=invalid_token")
        assert response.status_code == 400
        assert "invalid" in response.json()["error"]["message"].lower()

    def test_verify_email_expired_token(self, client, test_user, db):
        token = generate_verification_token()
        test_user.verification_token = token
        test_user.verification_token_expires_at = datetime.utcnow() - timedelta(hours=1)
        db.commit()

        response = client.get(f"/api/auth/verify-email?token={token}")
        assert response.status_code == 400
        assert "expired" in response.json()["error"]["message"].lower()


# ============================================================================
# Change Password Tests
# ============================================================================


class TestChangePassword:
    def test_change_password_success(self, client, test_user, auth_headers):
        response = client.post("/api/auth/change-password", headers=auth_headers, json={
            "current_password": "TestPass123",
            "new_password": "NewStrongPass456",
            "confirm_password": "NewStrongPass456",
        })
        assert response.status_code == 200
        assert "successfully" in response.json()["message"].lower()

    def test_change_password_wrong_current(self, client, test_user, auth_headers):
        response = client.post("/api/auth/change-password", headers=auth_headers, json={
            "current_password": "WrongPass123",
            "new_password": "NewStrongPass456",
            "confirm_password": "NewStrongPass456",
        })
        assert response.status_code == 401
        assert "incorrect" in response.json()["error"]["message"].lower()

    def test_change_password_mismatch(self, client, test_user, auth_headers):
        response = client.post("/api/auth/change-password", headers=auth_headers, json={
            "current_password": "TestPass123",
            "new_password": "NewStrongPass456",
            "confirm_password": "DifferentPass789",
        })
        assert response.status_code == 422
        assert "do not match" in response.json()["error"]["message"].lower()

    def test_change_password_weak_new(self, client, test_user, auth_headers):
        response = client.post("/api/auth/change-password", headers=auth_headers, json={
            "current_password": "TestPass123",
            "new_password": "weak",
            "confirm_password": "weak",
        })
        assert response.status_code == 422

    def test_change_password_same_as_current(self, client, test_user, auth_headers):
        response = client.post("/api/auth/change-password", headers=auth_headers, json={
            "current_password": "TestPass123",
            "new_password": "TestPass123",
            "confirm_password": "TestPass123",
        })
        assert response.status_code == 422
        assert "different" in response.json()["error"]["message"].lower()


# ============================================================================
# Delete Account Tests
# ============================================================================


class TestDeleteAccount:
    def test_delete_account_success(self, client, test_user, auth_headers):
        response = client.request(
            "DELETE",
            "/api/auth/account",
            headers=auth_headers,
            json={
                "password": "TestPass123",
                "confirmation": "DELETE",
            },
        )
        assert response.status_code == 200
        assert "deactivated" in response.json()["message"].lower()

    def test_delete_account_wrong_password(self, client, test_user, auth_headers):
        response = client.request(
            "DELETE",
            "/api/auth/account",
            headers=auth_headers,
            json={
                "password": "WrongPass123",
                "confirmation": "DELETE",
            },
        )
        assert response.status_code == 401

    def test_delete_account_wrong_confirmation(self, client, test_user, auth_headers):
        response = client.request(
            "DELETE",
            "/api/auth/account",
            headers=auth_headers,
            json={
                "password": "TestPass123",
                "confirmation": "WRONG",
            },
        )
        assert response.status_code == 422
        assert "DELETE" in response.json()["error"]["message"]


# ============================================================================
# Auth Settings Tests
# ============================================================================


class TestAuthSettings:
    def test_get_settings_success(self, client, test_user, auth_headers):
        response = client.get("/api/auth/settings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "is_verified" in data
        assert "login_provider" in data
        assert "has_password" in data

    def test_get_settings_unauthenticated(self, client):
        response = client.get("/api/auth/settings")
        assert response.status_code == 401


# ============================================================================
# Token Utility Tests
# ============================================================================


class TestTokenUtilities:
    def test_verification_token_create_verify(self):
        email = "test@example.com"
        token = create_verification_token(email)
        verified_email = verify_verification_token(token)
        assert verified_email == email

    def test_verification_token_invalid(self):
        result = verify_verification_token("invalid_token")
        assert result is None

    def test_verification_token_wrong_type(self):
        # Create a reset token instead of verification
        from app.auth import create_reset_token
        token = create_reset_token("test@example.com")
        result = verify_verification_token(token)
        assert result is None

    def test_generate_verification_token(self):
        token1 = generate_verification_token()
        token2 = generate_verification_token()
        assert token1 != token2
        assert len(token1) > 0


# ============================================================================
# Password Utility Tests
# ============================================================================


class TestPasswordUtilities:
    def test_password_hash_verify(self):
        password = "TestPass123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPass", hashed) is False

    def test_password_strength_valid(self):
        from app.auth import validate_password_strength
        result = validate_password_strength("StrongPass123")
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_password_strength_too_short(self):
        from app.auth import validate_password_strength
        result = validate_password_strength("Short1")
        assert result["valid"] is False
        assert any("8 characters" in e for e in result["errors"])

    def test_password_strength_no_uppercase(self):
        from app.auth import validate_password_strength
        result = validate_password_strength("nouppercase123")
        assert result["valid"] is False
        assert any("uppercase" in e for e in result["errors"])

    def test_password_strength_no_lowercase(self):
        from app.auth import validate_password_strength
        result = validate_password_strength("NOLOWERCASE123")
        assert result["valid"] is False
        assert any("lowercase" in e for e in result["errors"])

    def test_password_strength_no_number(self):
        from app.auth import validate_password_strength
        result = validate_password_strength("NoNumbersHere")
        assert result["valid"] is False
        assert any("number" in e for e in result["errors"])


# ============================================================================
# Email Template Tests
# ============================================================================


class TestEmailTemplates:
    def test_verification_email_template(self):
        from app.services.email_templates import verification_email
        template = verification_email("Test User", "http://example.com/verify?token=abc123")
        assert "subject" in template
        assert "html" in template
        assert "Test User" in template["html"]
        assert "abc123" in template["html"]

    def test_password_reset_email_template(self):
        from app.services.email_templates import password_reset_email
        template = password_reset_email("Test User", "http://example.com/reset?token=xyz789")
        assert "subject" in template
        assert "html" in template
        assert "Test User" in template["html"]
        assert "xyz789" in template["html"]

    def test_welcome_email_template(self):
        from app.services.email_templates import welcome_email
        template = welcome_email("Test User")
        assert "subject" in template
        assert "html" in template
        assert "Test User" in template["html"]

    def test_account_deletion_email_template(self):
        from app.services.email_templates import account_deletion_email
        template = account_deletion_email("Test User")
        assert "subject" in template
        assert "html" in template


# ============================================================================
# Password Handling Fix Tests (bcrypt/passlib compatibility)
# ============================================================================


class TestPasswordHandlingFix:
    """Tests for bcrypt/passlib compatibility fix.

    Validates that:
    - verify_password returns True/False without leaking exceptions
    - get_password_hash raises ValueError for bad input
    - Password hashing works with bcrypt 4.x
    - 72-byte boundary is handled correctly
    """

    def test_verify_password_correct(self):
        password = "TestPass123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "TestPass123"
        hashed = get_password_hash(password)
        assert verify_password("WrongPass456", hashed) is False

    def test_verify_password_none_hash(self):
        assert verify_password("anything", None) is False

    def test_verify_password_empty_hash(self):
        assert verify_password("anything", "") is False

    def test_verify_password_malformed_hash(self):
        assert verify_password("anything", "not_a_real_hash") is False

    def test_get_password_hash_normal(self):
        hashed = get_password_hash("TestPass123")
        assert hashed.startswith("$2b$")
        assert len(hashed) > 0

    def test_get_password_hash_72_bytes_boundary(self):
        password_72 = "A" * 72
        hashed = get_password_hash(password_72)
        assert hashed is not None
        assert verify_password(password_72, hashed) is True

    def test_get_password_hash_exceeds_72_bytes(self):
        password_73 = "A" * 73
        hashed = get_password_hash(password_73)
        assert hashed is not None
        assert verify_password(password_73, hashed) is True

    def test_get_password_hash_long_password(self):
        password_255 = "B" * 255
        hashed = get_password_hash(password_255)
        assert hashed is not None

    def test_get_password_hash_empty_string(self):
        hashed = get_password_hash("")
        assert hashed is not None

    def test_get_password_hash_unicode(self):
        hashed = get_password_hash("Pässwörd123")
        assert hashed is not None
        assert verify_password("Pässwörd123", hashed) is True

    def test_verify_returns_false_not_exception(self):
        """verify_password must return False on any error, never raise."""
        assert verify_password("anything", None) is False
        assert verify_password("anything", "") is False
        assert verify_password("anything", "corrupt") is False

    def test_access_token_generation(self):
        from app.auth import create_access_token, verify_token
        token = create_access_token(data={"sub": "user-123"})
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"

    def test_access_token_remember_me(self):
        from app.auth import create_access_token, verify_token
        token = create_access_token(data={"sub": "user-123"}, remember_me=True)
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user-123"
