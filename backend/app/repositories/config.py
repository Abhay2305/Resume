"""Configuration domain repositories.

Data access layer for SystemConfig and FeatureFlag entities.
"""
import json
from typing import Dict, List, Optional, Any

from sqlalchemy import and_

from ..models.config import SystemConfig, FeatureFlag
from .base import BaseRepository


# ---------------------------------------------------------------------------
# SystemConfig Repository
# ---------------------------------------------------------------------------

class ConfigRepository(BaseRepository[SystemConfig]):
    """Repository for SystemConfig entity."""

    def __init__(self, db):
        super().__init__(SystemConfig, db)

    def get_by_key(self, key: str) -> Optional[SystemConfig]:
        """Get config by key."""
        return self.db.query(SystemConfig).filter(SystemConfig.key == key).first()

    def get_by_category(self, category: str) -> List[SystemConfig]:
        """Get all configs in a category."""
        return (
            self.db.query(SystemConfig)
            .filter(SystemConfig.category == category)
            .all()
        )

    def get_public_configs(self) -> List[SystemConfig]:
        """Get all public configs."""
        return (
            self.db.query(SystemConfig)
            .filter(SystemConfig.is_public == True)
            .all()
        )

    def upsert(
        self, key: str, value: str, **kwargs: Any
    ) -> SystemConfig:
        """Create or update config by key."""
        existing = self.get_by_key(key)
        if existing:
            existing.value = value
            for field, val in kwargs.items():
                if hasattr(existing, field):
                    setattr(existing, field, val)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            data = {"key": key, "value": value, **kwargs}
            return self.create(data)

    def key_exists(self, key: str) -> bool:
        """Check if config key exists."""
        return (
            self.db.query(SystemConfig)
            .filter(SystemConfig.key == key)
            .first()
            is not None
        )


# ---------------------------------------------------------------------------
# FeatureFlag Repository
# ---------------------------------------------------------------------------

class FeatureFlagRepository(BaseRepository[FeatureFlag]):
    """Repository for FeatureFlag entity."""

    def __init__(self, db):
        super().__init__(FeatureFlag, db)

    def get_by_name(self, name: str) -> Optional[FeatureFlag]:
        """Get flag by name."""
        return self.db.query(FeatureFlag).filter(FeatureFlag.name == name).first()

    def get_enabled_flags(self) -> List[FeatureFlag]:
        """Get all enabled flags."""
        return (
            self.db.query(FeatureFlag)
            .filter(FeatureFlag.is_enabled == True)
            .all()
        )

    def get_flags_for_tier(self, tier: str) -> List[FeatureFlag]:
        """Get flags enabled for a specific tier."""
        flags = self.get_enabled_flags()
        result = []
        for flag in flags:
            if flag.allowed_tiers is None:
                # No tier restriction
                result.append(flag)
            else:
                try:
                    allowed = json.loads(flag.allowed_tiers)
                    if tier in allowed:
                        result.append(flag)
                except (json.JSONDecodeError, TypeError):
                    # Invalid JSON, include flag
                    result.append(flag)
        return result

    def name_exists(self, name: str) -> bool:
        """Check if flag name exists."""
        return (
            self.db.query(FeatureFlag)
            .filter(FeatureFlag.name == name)
            .first()
            is not None
        )
