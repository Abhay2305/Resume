"""Configuration domain router.

API endpoints for system configuration and feature flag management.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..schemas.config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigOut,
    ConfigListResponse,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagOut,
    FeatureFlagListResponse,
    FeatureFlagEvaluateResponse,
)
from ..services.config_service import ConfigService

router = APIRouter(prefix="/config", tags=["Configuration"])


# ============================================================================
# System Configuration Endpoints (static routes before /{key})
# ============================================================================

@router.get("", response_model=ConfigListResponse)
def list_configs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """List all configurations with pagination and optional category filter."""
    service = ConfigService(db)

    if category:
        configs = service.get_configs_by_category(category)
        return ConfigListResponse(
            items=[ConfigOut.model_validate(c) for c in configs],
            total=len(configs),
            page=1,
            size=len(configs),
        )

    from ..repositories.config import ConfigRepository
    repo = ConfigRepository(db)
    skip = (page - 1) * size
    configs = repo.get_multi(skip=skip, limit=size)
    total = repo.count()

    return ConfigListResponse(
        items=[ConfigOut.model_validate(c) for c in configs],
        total=total,
        page=page,
        size=size,
    )


@router.get("/public", response_model=list[ConfigOut])
def get_public_configs(
    db: Session = Depends(get_db),
):
    """Get all public configurations (no auth required)."""
    service = ConfigService(db)
    configs = service.get_public_configs()
    return [ConfigOut.model_validate(c) for c in configs]


@router.post("", response_model=ConfigOut, status_code=201)
def create_config(
    data: ConfigCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create a new configuration."""
    service = ConfigService(db)
    try:
        config = service.create_config(data.model_dump())
        return ConfigOut.model_validate(config)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ============================================================================
# Feature Flag Endpoints (static /flags before /{key})
# ============================================================================

@router.get("/flags", response_model=FeatureFlagListResponse)
def list_feature_flags(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """List all feature flags with pagination."""
    service = ConfigService(db)
    flags, total = service.list_feature_flags(page=page, size=size)
    return FeatureFlagListResponse(
        items=[FeatureFlagOut.model_validate(f) for f in flags],
        total=total,
        page=page,
        size=size,
    )


@router.post("/flags", response_model=FeatureFlagOut, status_code=201)
def create_feature_flag(
    data: FeatureFlagCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create a new feature flag."""
    service = ConfigService(db)
    try:
        flag = service.create_feature_flag(data.model_dump())
        return FeatureFlagOut.model_validate(flag)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


# ============================================================================
# Dynamic parameter routes (after all static routes)
# ============================================================================

@router.get("/{key}", response_model=ConfigOut)
def get_config(
    key: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get configuration by key."""
    service = ConfigService(db)
    config = service.get_config(key)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return ConfigOut.model_validate(config)


@router.put("/{key}", response_model=ConfigOut)
def update_config(
    key: str,
    data: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Update an existing configuration."""
    service = ConfigService(db)
    try:
        update_data = data.model_dump(exclude_unset=True)
        config = service.update_config(key, update_data)
        return ConfigOut.model_validate(config)
    except KeyError:
        raise HTTPException(status_code=404, detail="Configuration not found")


@router.delete("/{key}")
def delete_config(
    key: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Delete a configuration."""
    service = ConfigService(db)
    try:
        deleted = service.delete_config(key)
        if not deleted:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return {"message": "Configuration deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Configuration not found")


# ============================================================================
# Feature Flag Dynamic Routes
# ============================================================================

@router.get("/flags/{name}", response_model=FeatureFlagOut)
def get_feature_flag(
    name: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get feature flag by name."""
    service = ConfigService(db)
    flag = service.get_feature_flag(name)
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")
    return FeatureFlagOut.model_validate(flag)


@router.put("/flags/{name}", response_model=FeatureFlagOut)
def update_feature_flag(
    name: str,
    data: FeatureFlagUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Update an existing feature flag."""
    service = ConfigService(db)
    try:
        update_data = data.model_dump(exclude_unset=True)
        flag = service.update_feature_flag(name, update_data)
        return FeatureFlagOut.model_validate(flag)
    except KeyError:
        raise HTTPException(status_code=404, detail="Feature flag not found")


@router.delete("/flags/{name}")
def delete_feature_flag(
    name: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Delete a feature flag."""
    service = ConfigService(db)
    try:
        deleted = service.delete_feature_flag(name)
        if not deleted:
            raise HTTPException(status_code=404, detail="Feature flag not found")
        return {"message": "Feature flag deleted successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Feature flag not found")


@router.get("/flags/{name}/evaluate", response_model=FeatureFlagEvaluateResponse)
def evaluate_feature_flag(
    name: str,
    tier: Optional[str] = Query(None, description="User tier for evaluation"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Evaluate if a feature flag is enabled for a tier."""
    service = ConfigService(db)
    enabled = service.evaluate_feature_flag(name, tier=tier)
    return FeatureFlagEvaluateResponse(
        name=name,
        enabled=enabled,
        tier=tier,
    )
