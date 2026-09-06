"""PROCS Template CMS Schemas.

Pydantic schemas for the dynamic template management system.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Template CRUD Schemas
# ---------------------------------------------------------------------------

class TemplateCreate(BaseModel):
    """Create a new template."""
    id: str = Field(..., min_length=1, max_length=100, description="Unique template ID (e.g., 'modern-blue')")
    name: str = Field(..., min_length=1, max_length=100)
    slug: Optional[str] = None
    description: Optional[str] = None
    category: str = Field(..., min_length=1, max_length=50)
    color_scheme: Dict[str, Any] = Field(default_factory=dict)
    layout_schema: Dict[str, Any] = Field(default_factory=dict)
    template_definition: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    fonts: Optional[Dict[str, str]] = None
    colors: Optional[Dict[str, str]] = None
    author: Optional[str] = None
    is_default: bool = False
    sort_order: int = 0
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.fullmatch(r"[a-z0-9-]+", v):
            raise ValueError("Slug must contain only lowercase letters, digits, and hyphens")
        return v


class TemplateUpdate(BaseModel):
    """Update an existing template."""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    thumbnail_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    color_scheme: Optional[Dict[str, Any]] = None
    layout_schema: Optional[Dict[str, Any]] = None
    template_definition: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    fonts: Optional[Dict[str, str]] = None
    colors: Optional[Dict[str, str]] = None
    status: Optional[str] = None
    author: Optional[str] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata_json: Optional[Dict[str, Any]] = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.fullmatch(r"[a-z0-9-]+", v):
            raise ValueError("Slug must contain only lowercase letters, digits, and hyphens")
        return v


class TemplateOut(BaseModel):
    """Full template output schema."""
    id: str
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    category: str
    thumbnail_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    color_scheme: Dict[str, Any]
    layout_schema: Dict[str, Any]
    template_definition: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    fonts: Optional[Dict[str, str]] = None
    colors: Optional[Dict[str, str]] = None
    status: str = "draft"
    version: int = 1
    author: Optional[str] = None
    is_default: bool = False
    sort_order: int = 0
    tags: Optional[List[str]] = None
    usage_count: int = 0
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Paginated template list response."""
    success: bool = True
    items: List[TemplateOut] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    totalPages: int = 1


class TemplateDetailResponse(BaseModel):
    """Single template detail response."""
    success: bool = True
    data: TemplateOut


class TemplateActionResponse(BaseModel):
    """Generic template action response."""
    success: bool = True
    message: str


class TemplatePublishRequest(BaseModel):
    """Publish a template."""
    status: str = "published"


class TemplateReorderRequest(BaseModel):
    """Reorder templates."""
    template_ids: List[str]


class TemplateDuplicateRequest(BaseModel):
    """Duplicate a template."""
    new_id: str = Field(..., min_length=1, max_length=100)
    new_name: Optional[str] = None


# ---------------------------------------------------------------------------
# File Upload Schemas
# ---------------------------------------------------------------------------

class UploadResponse(BaseModel):
    """File upload response."""
    success: bool = True
    url: str
    filename: str
    size: int


class DefinitionUploadResponse(BaseModel):
    """Template definition upload response (stored in DB, not filesystem)."""
    success: bool = True
    definition_stored: bool = True
    filename: str
    size: int


# ---------------------------------------------------------------------------
# Template Version Schemas
# ---------------------------------------------------------------------------

class TemplateVersionOut(BaseModel):
    """Template version history entry."""
    id: str
    template_id: str
    version: int
    snapshot: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateVersionListResponse(BaseModel):
    """Template version list response."""
    success: bool = True
    items: List[TemplateVersionOut] = []
    total: int = 0
