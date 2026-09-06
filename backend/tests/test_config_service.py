"""Tests for Configuration Service (PROC-SPEC-0.8).

Unit tests for repository, service, and schema validation.
Integration tests for API endpoints.
Error handling and validation tests.
"""
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db
from app.auth import require_admin
from app.models import Base
from app.models.config import SystemConfig, FeatureFlag
from app.repositories.config import ConfigRepository, FeatureFlagRepository
from app.services.config_service import ConfigService
from app.schemas.config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigOut,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagOut,
)


# ============================================================================
# Test Database Setup
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_config.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


class _FakeAdminUser:
    """Minimal fake admin user for dependency override."""
    def __init__(self):
        self.id = "admin-test-id"
        self.email = "admin@test.com"
        self.is_superuser = True
        self.is_active = True


def override_require_admin():
    return _FakeAdminUser()


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[require_admin] = override_require_admin
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(require_admin, None)


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
def config_repo(db):
    """Get a config repository."""
    return ConfigRepository(db)


@pytest.fixture
def flag_repo(db):
    """Get a feature flag repository."""
    return FeatureFlagRepository(db)


@pytest.fixture
def config_service(db):
    """Get a config service."""
    return ConfigService(db)


@pytest.fixture
def sample_config(db):
    """Create a sample configuration."""
    config = SystemConfig(
        key="test.config",
        value="test_value",
        category="test",
        description="Test configuration",
        is_public=True,
        version=1,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@pytest.fixture
def sample_flag(db):
    """Create a sample feature flag."""
    flag = FeatureFlag(
        name="test.flag",
        description="Test feature flag",
        is_enabled=True,
        rollout_percentage=50,
        allowed_tiers=json.dumps(["free", "pro"]),
        environment="all",
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag


# ============================================================================
# Repository Tests
# ============================================================================


class TestConfigRepository:
    """Tests for ConfigRepository."""

    def test_create_config(self, config_repo, db):
        """Test creating a configuration."""
        data = {"key": "new.config", "value": "new_value", "category": "test"}
        config = config_repo.create(data)
        
        assert config is not None
        assert config.key == "new.config"
        assert config.value == "new_value"
        assert config.category == "test"

    def test_get_by_key(self, config_repo, sample_config):
        """Test getting config by key."""
        config = config_repo.get_by_key("test.config")
        
        assert config is not None
        assert config.key == "test.config"
        assert config.value == "test_value"

    def test_get_by_key_not_found(self, config_repo):
        """Test getting config by key when not found."""
        config = config_repo.get_by_key("nonexistent.key")
        
        assert config is None

    def test_get_by_category(self, config_repo, sample_config):
        """Test getting configs by category."""
        configs = config_repo.get_by_category("test")
        
        assert len(configs) == 1
        assert configs[0].key == "test.config"

    def test_get_public_configs(self, config_repo, sample_config):
        """Test getting public configs."""
        configs = config_repo.get_public_configs()
        
        assert len(configs) == 1
        assert configs[0].is_public is True

    def test_upsert_create(self, config_repo):
        """Test upsert creating new config."""
        config = config_repo.upsert("upsert.key", "upsert_value", category="test")
        
        assert config.key == "upsert.key"
        assert config.value == "upsert_value"

    def test_upsert_update(self, config_repo, sample_config):
        """Test upsert updating existing config."""
        config = config_repo.upsert("test.config", "updated_value")
        
        assert config.key == "test.config"
        assert config.value == "updated_value"

    def test_key_exists(self, config_repo, sample_config):
        """Test checking if key exists."""
        exists = config_repo.key_exists("test.config")
        
        assert exists is True

    def test_key_not_exists(self, config_repo):
        """Test checking if key exists when it doesn't."""
        exists = config_repo.key_exists("nonexistent.key")
        
        assert exists is False

    def test_update_config(self, config_repo, sample_config):
        """Test updating a configuration."""
        updated = config_repo.update(sample_config, {"value": "new_value"})
        
        assert updated.value == "new_value"

    def test_delete_config(self, config_repo, sample_config):
        """Test deleting a configuration."""
        deleted = config_repo.delete(sample_config.id)
        
        assert deleted is True
        assert config_repo.get_by_key("test.config") is None


class TestFeatureFlagRepository:
    """Tests for FeatureFlagRepository."""

    def test_create_flag(self, flag_repo, db):
        """Test creating a feature flag."""
        data = {
            "name": "new.flag",
            "description": "New flag",
            "is_enabled": True,
            "rollout_percentage": 100,
            "environment": "all",
        }
        flag = flag_repo.create(data)
        
        assert flag is not None
        assert flag.name == "new.flag"
        assert flag.is_enabled is True

    def test_get_by_name(self, flag_repo, sample_flag):
        """Test getting flag by name."""
        flag = flag_repo.get_by_name("test.flag")
        
        assert flag is not None
        assert flag.name == "test.flag"

    def test_get_by_name_not_found(self, flag_repo):
        """Test getting flag by name when not found."""
        flag = flag_repo.get_by_name("nonexistent.flag")
        
        assert flag is None

    def test_get_enabled_flags(self, flag_repo, sample_flag):
        """Test getting enabled flags."""
        flags = flag_repo.get_enabled_flags()
        
        assert len(flags) == 1
        assert flags[0].is_enabled is True

    def test_get_flags_for_tier(self, flag_repo, sample_flag):
        """Test getting flags for a specific tier."""
        flags = flag_repo.get_flags_for_tier("free")
        
        assert len(flags) == 1
        assert flags[0].name == "test.flag"

    def test_get_flags_for_tier_no_match(self, flag_repo, sample_flag):
        """Test getting flags for a tier with no matching flags."""
        flags = flag_repo.get_flags_for_tier("enterprise")
        
        assert len(flags) == 0

    def test_name_exists(self, flag_repo, sample_flag):
        """Test checking if name exists."""
        exists = flag_repo.name_exists("test.flag")
        
        assert exists is True

    def test_name_not_exists(self, flag_repo):
        """Test checking if name exists when it doesn't."""
        exists = flag_repo.name_exists("nonexistent.flag")
        
        assert exists is False

    def test_update_flag(self, flag_repo, sample_flag):
        """Test updating a feature flag."""
        updated = flag_repo.update(sample_flag, {"is_enabled": False})
        
        assert updated.is_enabled is False

    def test_delete_flag(self, flag_repo, sample_flag):
        """Test deleting a feature flag."""
        deleted = flag_repo.delete(sample_flag.id)
        
        assert deleted is True
        assert flag_repo.get_by_name("test.flag") is None


# ============================================================================
# Service Tests
# ============================================================================


class TestConfigService:
    """Tests for ConfigService."""

    def test_get_config(self, config_service, sample_config):
        """Test getting configuration by key."""
        config = config_service.get_config("test.config")
        
        assert config is not None
        assert config.key == "test.config"

    def test_get_config_not_found(self, config_service):
        """Test getting configuration when not found."""
        config = config_service.get_config("nonexistent.key")
        
        assert config is None

    def test_get_configs_by_category(self, config_service, sample_config):
        """Test getting configurations by category."""
        configs = config_service.get_configs_by_category("test")
        
        assert len(configs) == 1

    def test_get_public_configs(self, config_service, sample_config):
        """Test getting public configurations."""
        configs = config_service.get_public_configs()
        
        assert len(configs) == 1

    def test_create_config(self, config_service):
        """Test creating a configuration."""
        data = {"key": "new.config", "value": "new_value", "category": "test"}
        config = config_service.create_config(data, user_id="test-user")
        
        assert config.key == "new.config"
        assert config.value == "new_value"

    def test_create_config_duplicate(self, config_service, sample_config):
        """Test creating a configuration with duplicate key."""
        data = {"key": "test.config", "value": "duplicate"}
        
        with pytest.raises(ValueError, match="already exists"):
            config_service.create_config(data)

    def test_update_config(self, config_service, sample_config):
        """Test updating a configuration."""
        updated = config_service.update_config(
            "test.config", {"value": "updated_value"}, user_id="test-user"
        )
        
        assert updated.value == "updated_value"

    def test_update_config_not_found(self, config_service):
        """Test updating a configuration when not found."""
        with pytest.raises(KeyError, match="not found"):
            config_service.update_config("nonexistent.key", {"value": "new"})

    def test_delete_config(self, config_service, sample_config):
        """Test deleting a configuration."""
        deleted = config_service.delete_config("test.config", user_id="test-user")
        
        assert deleted is True

    def test_delete_config_not_found(self, config_service):
        """Test deleting a configuration when not found."""
        with pytest.raises(KeyError, match="not found"):
            config_service.delete_config("nonexistent.key")

    def test_get_feature_flag(self, config_service, sample_flag):
        """Test getting feature flag by name."""
        flag = config_service.get_feature_flag("test.flag")
        
        assert flag is not None
        assert flag.name == "test.flag"

    def test_get_feature_flag_not_found(self, config_service):
        """Test getting feature flag when not found."""
        flag = config_service.get_feature_flag("nonexistent.flag")
        
        assert flag is None

    def test_create_feature_flag(self, config_service):
        """Test creating a feature flag."""
        data = {
            "name": "new.flag",
            "description": "New flag",
            "is_enabled": True,
            "rollout_percentage": 100,
            "environment": "all",
        }
        flag = config_service.create_feature_flag(data, user_id="test-user")
        
        assert flag.name == "new.flag"
        assert flag.is_enabled is True

    def test_create_feature_flag_duplicate(self, config_service, sample_flag):
        """Test creating a feature flag with duplicate name."""
        data = {"name": "test.flag", "is_enabled": True}
        
        with pytest.raises(ValueError, match="already exists"):
            config_service.create_feature_flag(data)

    def test_update_feature_flag(self, config_service, sample_flag):
        """Test updating a feature flag."""
        updated = config_service.update_feature_flag(
            "test.flag", {"is_enabled": False}, user_id="test-user"
        )
        
        assert updated.is_enabled is False

    def test_update_feature_flag_not_found(self, config_service):
        """Test updating a feature flag when not found."""
        with pytest.raises(KeyError, match="not found"):
            config_service.update_feature_flag("nonexistent.flag", {"is_enabled": True})

    def test_delete_feature_flag(self, config_service, sample_flag):
        """Test deleting a feature flag."""
        deleted = config_service.delete_feature_flag("test.flag", user_id="test-user")
        
        assert deleted is True

    def test_delete_feature_flag_not_found(self, config_service):
        """Test deleting a feature flag when not found."""
        with pytest.raises(KeyError, match="not found"):
            config_service.delete_feature_flag("nonexistent.flag")

    def test_evaluate_feature_flag_enabled(self, config_service, sample_flag):
        """Test evaluating an enabled feature flag."""
        result = config_service.evaluate_feature_flag("test.flag", tier="free")
        
        assert result is True

    def test_evaluate_feature_flag_disabled(self, config_service, sample_flag):
        """Test evaluating a disabled feature flag."""
        sample_flag.is_enabled = False
        config_service.db.commit()
        
        result = config_service.evaluate_feature_flag("test.flag", tier="free")
        
        assert result is False

    def test_evaluate_feature_flag_not_found(self, config_service):
        """Test evaluating a feature flag that doesn't exist."""
        result = config_service.evaluate_feature_flag("nonexistent.flag")
        
        assert result is False

    def test_evaluate_feature_flag_tier_restriction(self, config_service, sample_flag):
        """Test evaluating a feature flag with tier restriction."""
        result = config_service.evaluate_feature_flag("test.flag", tier="enterprise")
        
        assert result is False

    def test_list_feature_flags(self, config_service, sample_flag):
        """Test listing feature flags."""
        flags, total = config_service.list_feature_flags()
        
        assert total == 1
        assert len(flags) == 1

    def test_cache_invalidation(self, config_service, sample_config):
        """Test cache invalidation on update."""
        # Get config (should be cached)
        config1 = config_service.get_config("test.config")
        
        # Update config
        config_service.update_config("test.config", {"value": "new_value"})
        
        # Get config again (should be updated)
        config2 = config_service.get_config("test.config")
        
        assert config2.value == "new_value"


# ============================================================================
# Schema Validation Tests
# ============================================================================


class TestConfigSchemas:
    """Tests for Configuration schemas."""

    def test_config_create_valid(self):
        """Test valid ConfigCreate schema."""
        data = ConfigCreate(key="test.key", value="test_value")
        
        assert data.key == "test.key"
        assert data.value == "test_value"
        assert data.is_public is False

    def test_config_create_empty_key(self):
        """Test ConfigCreate with empty key."""
        with pytest.raises(Exception):
            ConfigCreate(key="", value="test_value")

    def test_config_create_key_too_long(self):
        """Test ConfigCreate with key too long."""
        with pytest.raises(Exception):
            ConfigCreate(key="x" * 201, value="test_value")

    def test_config_create_empty_value(self):
        """Test ConfigCreate with empty value."""
        with pytest.raises(Exception):
            ConfigCreate(key="test.key", value="")

    def test_config_update_valid(self):
        """Test valid ConfigUpdate schema."""
        data = ConfigUpdate(value="new_value")
        
        assert data.value == "new_value"

    def test_config_out_valid(self):
        """Test valid ConfigOut schema."""
        data = ConfigOut(
            id="test-id",
            key="test.key",
            value="test_value",
            is_public=False,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert data.id == "test-id"
        assert data.key == "test.key"

    def test_feature_flag_create_valid(self):
        """Test valid FeatureFlagCreate schema."""
        data = FeatureFlagCreate(name="test.flag")
        
        assert data.name == "test.flag"
        assert data.is_enabled is False
        assert data.rollout_percentage == 100

    def test_feature_flag_create_empty_name(self):
        """Test FeatureFlagCreate with empty name."""
        with pytest.raises(Exception):
            FeatureFlagCreate(name="")

    def test_feature_flag_create_name_too_long(self):
        """Test FeatureFlagCreate with name too long."""
        with pytest.raises(Exception):
            FeatureFlagCreate(name="x" * 201)

    def test_feature_flag_create_invalid_rollout(self):
        """Test FeatureFlagCreate with invalid rollout percentage."""
        with pytest.raises(Exception):
            FeatureFlagCreate(name="test.flag", rollout_percentage=101)

    def test_feature_flag_create_negative_rollout(self):
        """Test FeatureFlagCreate with negative rollout percentage."""
        with pytest.raises(Exception):
            FeatureFlagCreate(name="test.flag", rollout_percentage=-1)

    def test_feature_flag_update_valid(self):
        """Test valid FeatureFlagUpdate schema."""
        data = FeatureFlagUpdate(is_enabled=True)
        
        assert data.is_enabled is True

    def test_feature_flag_out_valid(self):
        """Test valid FeatureFlagOut schema."""
        data = FeatureFlagOut(
            id="test-id",
            name="test.flag",
            is_enabled=True,
            rollout_percentage=50,
            environment="all",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert data.id == "test-id"
        assert data.name == "test.flag"

    def test_feature_flag_out_with_allowed_tiers(self):
        """Test FeatureFlagOut with allowed_tiers as list."""
        data = FeatureFlagOut(
            id="test-id",
            name="test.flag",
            is_enabled=True,
            rollout_percentage=50,
            allowed_tiers=["free", "pro"],
            environment="all",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert data.allowed_tiers == ["free", "pro"]

    def test_feature_flag_out_with_allowed_tiers_json(self):
        """Test FeatureFlagOut with allowed_tiers as JSON string."""
        data = FeatureFlagOut(
            id="test-id",
            name="test.flag",
            is_enabled=True,
            rollout_percentage=50,
            allowed_tiers='["free", "pro"]',
            environment="all",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        
        assert data.allowed_tiers == ["free", "pro"]


# ============================================================================
# API Integration Tests
# ============================================================================


class TestConfigAPI:
    """Tests for Configuration API endpoints."""

    def test_list_configs(self, client, sample_config):
        """Test listing configurations."""
        response = client.get("/api/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_get_config(self, client, sample_config):
        """Test getting configuration by key."""
        response = client.get("/api/config/test.config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "test.config"
        assert data["value"] == "test_value"

    def test_get_config_not_found(self, client):
        """Test getting configuration when not found."""
        response = client.get("/api/config/nonexistent.key")
        
        assert response.status_code == 404

    def test_create_config(self, client):
        """Test creating a configuration."""
        data = {"key": "new.config", "value": "new_value", "category": "test"}
        response = client.post("/api/config", json=data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["key"] == "new.config"
        assert result["value"] == "new_value"

    def test_create_config_duplicate(self, client, sample_config):
        """Test creating a configuration with duplicate key."""
        data = {"key": "test.config", "value": "duplicate"}
        response = client.post("/api/config", json=data)
        
        assert response.status_code == 409

    def test_update_config(self, client, sample_config):
        """Test updating a configuration."""
        data = {"value": "updated_value"}
        response = client.put("/api/config/test.config", json=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["value"] == "updated_value"

    def test_update_config_not_found(self, client):
        """Test updating a configuration when not found."""
        data = {"value": "new_value"}
        response = client.put("/api/config/nonexistent.key", json=data)
        
        assert response.status_code == 404

    def test_delete_config(self, client, sample_config):
        """Test deleting a configuration."""
        response = client.delete("/api/config/test.config")
        
        assert response.status_code == 200

    def test_delete_config_not_found(self, client):
        """Test deleting a configuration when not found."""
        response = client.delete("/api/config/nonexistent.key")
        
        assert response.status_code == 404

    def test_get_public_configs(self, client, sample_config):
        """Test getting public configurations."""
        response = client.get("/api/config/public")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1


class TestFeatureFlagAPI:
    """Tests for Feature Flag API endpoints."""

    def test_list_feature_flags(self, client, sample_flag):
        """Test listing feature flags."""
        response = client.get("/api/config/flags")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_get_feature_flag(self, client, sample_flag):
        """Test getting feature flag by name."""
        response = client.get("/api/config/flags/test.flag")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test.flag"

    def test_get_feature_flag_not_found(self, client):
        """Test getting feature flag when not found."""
        response = client.get("/api/config/flags/nonexistent.flag")
        
        assert response.status_code == 404

    def test_create_feature_flag(self, client):
        """Test creating a feature flag."""
        data = {
            "name": "new.flag",
            "description": "New flag",
            "is_enabled": True,
            "rollout_percentage": 100,
            "environment": "all",
        }
        response = client.post("/api/config/flags", json=data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "new.flag"
        assert result["is_enabled"] is True

    def test_create_feature_flag_duplicate(self, client, sample_flag):
        """Test creating a feature flag with duplicate name."""
        data = {"name": "test.flag", "is_enabled": True}
        response = client.post("/api/config/flags", json=data)
        
        assert response.status_code == 409

    def test_update_feature_flag(self, client, sample_flag):
        """Test updating a feature flag."""
        data = {"is_enabled": False}
        response = client.put("/api/config/flags/test.flag", json=data)
        
        assert response.status_code == 200
        result = response.json()
        assert result["is_enabled"] is False

    def test_update_feature_flag_not_found(self, client):
        """Test updating a feature flag when not found."""
        data = {"is_enabled": True}
        response = client.put("/api/config/flags/nonexistent.flag", json=data)
        
        assert response.status_code == 404

    def test_delete_feature_flag(self, client, sample_flag):
        """Test deleting a feature flag."""
        response = client.delete("/api/config/flags/test.flag")
        
        assert response.status_code == 200

    def test_delete_feature_flag_not_found(self, client):
        """Test deleting a feature flag when not found."""
        response = client.delete("/api/config/flags/nonexistent.flag")
        
        assert response.status_code == 404

    def test_evaluate_feature_flag(self, client, sample_flag):
        """Test evaluating a feature flag."""
        response = client.get("/api/config/flags/test.flag/evaluate?tier=free")
        
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is True
        assert data["tier"] == "free"

    def test_evaluate_feature_flag_disabled(self, client, sample_flag):
        """Test evaluating a disabled feature flag."""
        # Disable the flag
        client.put("/api/config/flags/test.flag", json={"is_enabled": False})
        
        response = client.get("/api/config/flags/test.flag/evaluate?tier=free")
        
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False

    def test_evaluate_feature_flag_not_found(self, client):
        """Test evaluating a feature flag that doesn't exist."""
        response = client.get("/api/config/flags/nonexistent.flag/evaluate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] is False


# ============================================================================
# Validation Tests
# ============================================================================


class TestValidation:
    """Tests for input validation."""

    def test_config_create_invalid_payload(self, client):
        """Test creating config with invalid payload."""
        response = client.post("/api/config", json={})
        
        assert response.status_code == 422

    def test_config_create_missing_value(self, client):
        """Test creating config with missing value."""
        data = {"key": "test.key"}
        response = client.post("/api/config", json=data)
        
        assert response.status_code == 422

    def test_config_update_invalid_payload(self, client, sample_config):
        """Test updating config with invalid payload."""
        response = client.put("/api/config/test.config", json={"value": ""})
        
        assert response.status_code == 422

    def test_feature_flag_create_invalid_payload(self, client):
        """Test creating feature flag with invalid payload."""
        response = client.post("/api/config/flags", json={})
        
        assert response.status_code == 422

    def test_feature_flag_create_invalid_rollout(self, client):
        """Test creating feature flag with invalid rollout percentage."""
        data = {"name": "test.flag", "rollout_percentage": 150}
        response = client.post("/api/config/flags", json=data)
        
        assert response.status_code == 422

    def test_feature_flag_create_negative_rollout(self, client):
        """Test creating feature flag with negative rollout percentage."""
        data = {"name": "test.flag", "rollout_percentage": -10}
        response = client.post("/api/config/flags", json=data)
        
        assert response.status_code == 422


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling."""

    def test_config_not_found_error_response(self, client):
        """Test error response for config not found."""
        response = client.get("/api/config/nonexistent.key")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "HTTP_404"

    def test_flag_not_found_error_response(self, client):
        """Test error response for flag not found."""
        response = client.get("/api/config/flags/nonexistent.flag")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "HTTP_404"

    def test_duplicate_config_error_response(self, client, sample_config):
        """Test error response for duplicate config."""
        data = {"key": "test.config", "value": "duplicate"}
        response = client.post("/api/config", json=data)
        
        assert response.status_code == 409
        result = response.json()
        assert result["success"] is False
        assert result["error"]["code"] == "HTTP_409"

    def test_duplicate_flag_error_response(self, client, sample_flag):
        """Test error response for duplicate flag."""
        data = {"name": "test.flag", "is_enabled": True}
        response = client.post("/api/config/flags", json=data)
        
        assert response.status_code == 409
        result = response.json()
        assert result["success"] is False
        assert result["error"]["code"] == "HTTP_409"


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Tests for performance requirements."""

    def test_config_read_response_time(self, client, sample_config):
        """Test config read response time is within acceptable limits."""
        import time
        
        start = time.time()
        response = client.get("/api/config/test.config")
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 0.2  # Should be under 200ms

    def test_config_create_response_time(self, client):
        """Test config create response time is within acceptable limits."""
        import time
        
        data = {"key": "perf.test", "value": "perf_value"}
        start = time.time()
        response = client.post("/api/config", json=data)
        end = time.time()
        
        assert response.status_code == 201
        assert (end - start) < 0.5  # Should be under 500ms

    def test_feature_flag_evaluate_response_time(self, client, sample_flag):
        """Test feature flag evaluate response time is within acceptable limits."""
        import time
        
        start = time.time()
        response = client.get("/api/config/flags/test.flag/evaluate")
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 0.2  # Should be under 200ms


# ============================================================================
# Security Tests
# ============================================================================


class TestSecurity:
    """Tests for security requirements."""

    def test_config_create_sql_injection(self, client):
        """Test SQL injection prevention in config creation."""
        data = {"key": "test'; DROP TABLE system_config;--", "value": "test"}
        response = client.post("/api/config", json=data)
        
        # Should either succeed or fail with validation error, not SQL error
        assert response.status_code in [201, 422]

    def test_feature_flag_create_sql_injection(self, client):
        """Test SQL injection prevention in flag creation."""
        data = {"name": "test'; DROP TABLE feature_flags;--", "is_enabled": True}
        response = client.post("/api/config/flags", json=data)
        
        # Should either succeed or fail with validation error, not SQL error
        assert response.status_code in [201, 422]

    def test_config_create_xss_prevention(self, client):
        """Test XSS prevention in config values."""
        data = {"key": "xss.test", "value": "<script>alert('xss')</script>"}
        response = client.post("/api/config", json=data)
        
        # Should succeed, value will be stored as-is but rendered safely by frontend
        assert response.status_code == 201


# ============================================================================
# Regression Tests
# ============================================================================


class TestRegression:
    """Regression tests to ensure existing functionality isn't broken."""

    def test_existing_config_operations(self, client):
        """Test that existing config operations still work."""
        # Create
        data = {"key": "regression.test", "value": "original"}
        create_response = client.post("/api/config", json=data)
        assert create_response.status_code == 201
        
        # Read
        read_response = client.get("/api/config/regression.test")
        assert read_response.status_code == 200
        
        # Update
        update_response = client.put(
            "/api/config/regression.test", json={"value": "updated"}
        )
        assert update_response.status_code == 200
        
        # Delete
        delete_response = client.delete("/api/config/regression.test")
        assert delete_response.status_code == 200

    def test_existing_flag_operations(self, client):
        """Test that existing flag operations still work."""
        # Create
        data = {"name": "regression.flag", "is_enabled": True}
        create_response = client.post("/api/config/flags", json=data)
        assert create_response.status_code == 201
        
        # Read
        read_response = client.get("/api/config/flags/regression.flag")
        assert read_response.status_code == 200
        
        # Update
        update_response = client.put(
            "/api/config/flags/regression.flag", json={"is_enabled": False}
        )
        assert update_response.status_code == 200
        
        # Delete
        delete_response = client.delete("/api/config/flags/regression.flag")
        assert delete_response.status_code == 200
