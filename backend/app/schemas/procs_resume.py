"""PROCS Resume Management Schemas.

Pydantic schemas for PROCS resume management endpoints.
Follows the response format defined in PROCS_Implementation.md Section 14.2.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Resume List Schemas
# ---------------------------------------------------------------------------

class ResumeListOut(BaseModel):
    """Resume list item schema for PROCS resume management."""
    id: str
    user_id: str
    title: str
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeListResponse(BaseModel):
    """Paginated resume list response."""
    success: bool = True
    items: List[ResumeListOut] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    totalPages: int = 1


# ---------------------------------------------------------------------------
# Resume Detail Schemas
# ---------------------------------------------------------------------------

class ResumeSectionOut(BaseModel):
    """Resume section schema."""
    id: str
    section_type: str
    content: Any
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeVersionOut(BaseModel):
    """Resume version schema."""
    id: str
    version_number: int
    content: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailOut(BaseModel):
    """Full resume detail schema for PROCS resume inspector."""
    id: str
    user_id: str
    title: str
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Sections
    sections: List[ResumeSectionOut] = []

    # Version history
    versions: List[ResumeVersionOut] = []

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(BaseModel):
    """Resume detail response."""
    success: bool = True
    data: ResumeDetailOut


# ---------------------------------------------------------------------------
# Resume Update Schemas
# ---------------------------------------------------------------------------

class ResumeUpdateRequest(BaseModel):
    """Resume update request schema."""
    title: Optional[str] = None
    template_id: Optional[str] = None


class ResumeUpdateResponse(BaseModel):
    """Resume update response schema."""
    success: bool = True
    data: ResumeDetailOut


# ---------------------------------------------------------------------------
# Resume Action Schemas
# ---------------------------------------------------------------------------

class ResumeActionResponse(BaseModel):
    """Generic resume action response."""
    success: bool = True
    message: str


# ---------------------------------------------------------------------------
# Resume Stats Schema
# ---------------------------------------------------------------------------

class ResumeStatsOut(BaseModel):
    """Resume statistics schema."""
    total_resumes: int = 0
    new_resumes_today: int = 0
    new_resumes_this_week: int = 0
    new_resumes_this_month: int = 0
    total_templates: int = 0


class ResumeStatsResponse(BaseModel):
    """Resume stats response."""
    success: bool = True
    data: ResumeStatsOut


# ---------------------------------------------------------------------------
# Template Schemas
# ---------------------------------------------------------------------------

class TemplateOut(BaseModel):
    """Template schema."""
    id: str
    name: str
    category: str
    preview_image: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Template list response."""
    success: bool = True
    items: List[TemplateOut] = []
    total: int = 0


class TemplateStatsOut(BaseModel):
    """Template usage statistics schema."""
    id: str
    name: str
    category: str
    usage_count: int = 0


class TemplateStatsResponse(BaseModel):
    """Template stats response."""
    success: bool = True
    items: List[TemplateStatsOut] = []
