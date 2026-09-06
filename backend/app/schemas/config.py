"""Configuration domain schemas.

Pydantic schemas for SystemConfig and FeatureFlag API endpoints.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================================
# SystemConfig Schemas
# ============================================================================

class ConfigCreate(BaseModel):
    """Schema for creating a new configuration."""
    key: str = Field(..., min_length=1, max_length=200, description="Configuration key")
    value: str = Field(..., min_length=1, description="Configuration value")
    category: Optional[str] = Field(None, max_length=100, description="Configuration category")
    description: Optional[str] = Field(None, description="Configuration description")
    is_public: bool = Field(False, description="Whether config is publicly accessible")


class ConfigUpdate(BaseModel):
    """Schema for updating an existing configuration."""
    value: Optional[str] = Field(None, min_length=1, description="Configuration value")
    category: Optional[str] = Field(None, max_length=100, description="Configuration category")
    description: Optional[str] = Field(None, description="Configuration description")
    is_public: Optional[bool] = Field(None, description="Whether config is publicly accessible")


class ConfigOut(BaseModel):
    """Schema for configuration output."""
    id: str
    key: str
    value: str
    category: Optional[str] = None
    description: Optional[str] = None
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConfigListResponse(BaseModel):
    """Paginated configuration list response."""
    items: List[ConfigOut]
    total: int
    page: int
    size: int


# ============================================================================
# FeatureFlag Schemas
# ============================================================================

class FeatureFlagCreate(BaseModel):
    """Schema for creating a new feature flag."""
    name: str = Field(..., min_length=1, max_length=200, description="Feature flag name")
    description: Optional[str] = Field(None, description="Feature flag description")
    is_enabled: bool = Field(False, description="Whether flag is enabled")
    rollout_percentage: int = Field(100, ge=0, le=100, description="Rollout percentage (0-100)")
    allowed_tiers: Optional[List[str]] = Field(None, description="Allowed user tiers")
    environment: str = Field("all", max_length=50, description="Target environment")


class FeatureFlagUpdate(BaseModel):
    """Schema for updating an existing feature flag."""
    description: Optional[str] = Field(None, description="Feature flag description")
    is_enabled: Optional[bool] = Field(None, description="Whether flag is enabled")
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100, description="Rollout percentage (0-100)")
    allowed_tiers: Optional[List[str]] = Field(None, description="Allowed user tiers")
    environment: Optional[str] = Field(None, max_length=50, description="Target environment")


class FeatureFlagOut(BaseModel):
    """Schema for feature flag output."""
    id: str
    name: str
    description: Optional[str] = None
    is_enabled: bool
    rollout_percentage: int
    allowed_tiers: Optional[List[str]] = None
    environment: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator('allowed_tiers', mode='before')
    @classmethod
    def parse_allowed_tiers(cls, v):
        """Parse allowed_tiers from JSON string if needed."""
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return None
        return v


class FeatureFlagListResponse(BaseModel):
    """Paginated feature flag list response."""
    items: List[FeatureFlagOut]
    total: int
    page: int
    size: int


class FeatureFlagEvaluateResponse(BaseModel):
    """Feature flag evaluation response."""
    name: str
    enabled: bool
    tier: Optional[str] = None
