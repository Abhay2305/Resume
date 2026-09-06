"""Configuration domain service.

Provides high-level configuration and feature flag management operations.
Integrates with the repository layer and provides caching, validation,
and audit logging.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..models.config import SystemConfig, FeatureFlag
from ..repositories.config import ConfigRepository, FeatureFlagRepository
from .audit_service import AuditService
from .error_service import ErrorService


class ConfigService:
    """Service for configuration and feature flag operations.

    Usage:
        service = ConfigService(db)
        config = service.get_config("app.name")
        flag = service.evaluate_feature_flag("new.feature", tier="pro")
    """

    def __init__(self, db: Session):
        self.db = db
        self.config_repo = ConfigRepository(db)
        self.flag_repo = FeatureFlagRepository(db)
        self.audit = AuditService(db)
        self.error = ErrorService(db)
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = 300  # 5 minutes
        self._cache_timestamps: Dict[str, datetime] = {}

    # -----------------------------------------------------------------------
    # Cache methods
    # -----------------------------------------------------------------------

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if valid."""
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key)
            if timestamp:
                elapsed = (datetime.utcnow() - timestamp).total_seconds()
                if elapsed < self._cache_ttl:
                    return self._cache[key]
                else:
                    # Cache expired
                    del self._cache[key]
                    del self._cache_timestamps[key]
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.utcnow()

    def _invalidate_cache(self, key: Optional[str] = None) -> None:
        """Invalidate cache for a key or all keys."""
        if key:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()

    # -----------------------------------------------------------------------
    # Configuration methods
    # -----------------------------------------------------------------------

    def get_config(self, key: str) -> Optional[SystemConfig]:
        """Get configuration by key."""
        try:
            # Check cache first
            cache_key = f"config:{key}"
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached

            config = self.config_repo.get_by_key(key)
            if config:
                self._set_cache(cache_key, config)
            return config
        except Exception as e:
            self.error.log_exception(e, context={"key": key})
            return None

    def get_configs_by_category(self, category: str) -> List[SystemConfig]:
        """Get all configurations in a category."""
        try:
            return self.config_repo.get_by_category(category)
        except Exception as e:
            self.error.log_exception(e, context={"category": category})
            return []

    def get_public_configs(self) -> List[SystemConfig]:
        """Get all public configurations."""
        try:
            # Check cache first
            cache_key = "config:public"
            cached = self._get_from_cache(cache_key)
            if cached is not None:
                return cached

            configs = self.config_repo.get_public_configs()
            self._set_cache(cache_key, configs)
            return configs
        except Exception as e:
            self.error.log_exception(e, context={})
            return []

    def create_config(
        self, data: Dict[str, Any], user_id: Optional[str] = None
    ) -> SystemConfig:
        """Create a new configuration."""
        try:
            # Check if key already exists
            if self.config_repo.key_exists(data.get("key")):
                raise ValueError(f"Configuration with key '{data.get('key')}' already exists")

            config = self.config_repo.create(data)

            # Audit logging
            self.audit.log_create(
                entity_type="SystemConfig",
                entity_id=config.id,
                new_state={"key": config.key, "value": config.value},
                description=f"Created configuration: {config.key}",
            )

            # Invalidate cache
            self._invalidate_cache()

            return config
        except ValueError:
            raise
        except Exception as e:
            self.error.log_exception(e, context={"data": data})
            raise

    def update_config(
        self, key: str, data: Dict[str, Any], user_id: Optional[str] = None
    ) -> SystemConfig:
        """Update an existing configuration."""
        try:
            config = self.config_repo.get_by_key(key)
            if not config:
                raise KeyError(f"Configuration with key '{key}' not found")

            old_value = config.value
            updated = self.config_repo.update(config, data)

            # Audit logging
            self.audit.log_update(
                entity_type="SystemConfig",
                entity_id=updated.id,
                previous_state={"value": old_value},
                new_state={"value": updated.value},
                description=f"Updated configuration: {key}",
            )

            # Invalidate cache
            self._invalidate_cache()
            self._invalidate_cache(f"config:{key}")

            return updated
        except KeyError:
            raise
        except Exception as e:
            self.error.log_exception(e, context={"key": key, "data": data})
            raise

    def delete_config(self, key: str, user_id: Optional[str] = None) -> bool:
        """Delete a configuration."""
        try:
            config = self.config_repo.get_by_key(key)
            if not config:
                raise KeyError(f"Configuration with key '{key}' not found")

            config_id = config.id
            deleted = self.config_repo.delete(config_id)

            if deleted:
                # Audit logging
                self.audit.log_delete(
                    entity_type="SystemConfig",
                    entity_id=config_id,
                    previous_state={"key": key},
                    description=f"Deleted configuration: {key}",
                )

                # Invalidate cache
                self._invalidate_cache()
                self._invalidate_cache(f"config:{key}")

            return deleted
        except KeyError:
            raise
        except Exception as e:
            self.error.log_exception(e, context={"key": key})
            raise

    # -----------------------------------------------------------------------
    # Feature Flag methods
    # -----------------------------------------------------------------------

    def get_feature_flag(self, name: str) -> Optional[FeatureFlag]:
        """Get feature flag by name."""
        try:
            return self.flag_repo.get_by_name(name)
        except Exception as e:
            self.error.log_exception(e, context={"name": name})
            return None

    def create_feature_flag(
        self, data: Dict[str, Any], user_id: Optional[str] = None
    ) -> FeatureFlag:
        """Create a new feature flag."""
        try:
            # Check if name already exists
            if self.flag_repo.name_exists(data.get("name")):
                raise ValueError(f"Feature flag with name '{data.get('name')}' already exists")

            # Serialize allowed_tiers if it's a list
            if "allowed_tiers" in data and isinstance(data["allowed_tiers"], list):
                data["allowed_tiers"] = json.dumps(data["allowed_tiers"])

            flag = self.flag_repo.create(data)

            # Audit logging
            self.audit.log_create(
                entity_type="FeatureFlag",
                entity_id=flag.id,
                new_state={"name": flag.name, "is_enabled": flag.is_enabled},
                description=f"Created feature flag: {flag.name}",
            )

            return flag
        except ValueError:
            raise
        except Exception as e:
            self.error.log_exception(e, context={"data": data})
            raise

    def update_feature_flag(
        self, name: str, data: Dict[str, Any], user_id: Optional[str] = None
    ) -> FeatureFlag:
        """Update an existing feature flag."""
        try:
            flag = self.flag_repo.get_by_name(name)
            if not flag:
                raise KeyError(f"Feature flag with name '{name}' not found")

            previous_state = {
                "is_enabled": flag.is_enabled,
                "rollout_percentage": flag.rollout_percentage,
            }

            # Serialize allowed_tiers if it's a list
            if "allowed_tiers" in data and isinstance(data["allowed_tiers"], list):
                data["allowed_tiers"] = json.dumps(data["allowed_tiers"])

            updated = self.flag_repo.update(flag, data)

            new_state = {
                "is_enabled": updated.is_enabled,
                "rollout_percentage": updated.rollout_percentage,
            }

            # Audit logging
            self.audit.log_update(
                entity_type="FeatureFlag",
                entity_id=updated.id,
                previous_state=previous_state,
                new_state=new_state,
                description=f"Updated feature flag: {name}",
            )

            return updated
        except KeyError:
            raise
        except Exception as e:
            self.error.log_exception(e, context={"name": name, "data": data})
            raise

    def delete_feature_flag(self, name: str, user_id: Optional[str] = None) -> bool:
        """Delete a feature flag."""
        try:
            flag = self.flag_repo.get_by_name(name)
            if not flag:
                raise KeyError(f"Feature flag with name '{name}' not found")

            flag_id = flag.id
            deleted = self.flag_repo.delete(flag_id)

            if deleted:
                # Audit logging
                self.audit.log_delete(
                    entity_type="FeatureFlag",
                    entity_id=flag_id,
                    previous_state={"name": name},
                    description=f"Deleted feature flag: {name}",
                )

            return deleted
        except KeyError:
            raise
        except Exception as e:
            self.error.log_exception(e, context={"name": name})
            raise

    def evaluate_feature_flag(
        self, name: str, tier: Optional[str] = None
    ) -> bool:
        """Evaluate if a feature flag is enabled for a tier."""
        try:
            flag = self.flag_repo.get_by_name(name)
            if not flag:
                return False

            if not flag.is_enabled:
                return False

            # Check tier restriction
            if tier and flag.allowed_tiers:
                try:
                    allowed_tiers = json.loads(flag.allowed_tiers)
                    if tier not in allowed_tiers:
                        return False
                except (json.JSONDecodeError, TypeError):
                    # Invalid JSON, allow access
                    pass

            # Check rollout percentage (simplified - in production would use user hash)
            if flag.rollout_percentage < 100:
                # For now, always allow - implement proper rollout logic later
                pass

            return True
        except Exception as e:
            self.error.log_exception(e, context={"name": name, "tier": tier})
            return False

    def list_feature_flags(
        self, page: int = 1, size: int = 20
    ) -> Tuple[List[FeatureFlag], int]:
        """List all feature flags with pagination."""
        try:
            skip = (page - 1) * size
            flags = self.flag_repo.get_multi(skip=skip, limit=size)
            total = self.flag_repo.count()
            return flags, total
        except Exception as e:
            self.error.log_exception(e, context={"page": page, "size": size})
            return [], 0
