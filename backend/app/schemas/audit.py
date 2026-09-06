"""Audit System Schemas.

Pydantic schemas for audit logging endpoints.
Provides request/response models for audit log queries and exports.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Audit Log Schemas
# ---------------------------------------------------------------------------

class AuditLogOut(BaseModel):
    """Audit log item schema."""
    id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    description: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    request_body: Optional[str] = None
    response_status: Optional[int] = None
    response_body_summary: Optional[str] = None
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    metadata_json: Optional[str] = None
    tags: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""
    success: bool = True
    items: List[AuditLogOut] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    totalPages: int = 1


# ---------------------------------------------------------------------------
# Audit Summary Schemas
# ---------------------------------------------------------------------------

class AuditActionSummary(BaseModel):
    """Action summary item."""
    action: str
    count: int


class AuditEntitySummary(BaseModel):
    """Entity type summary item."""
    entity_type: str
    count: int


class AuditSummaryResponse(BaseModel):
    """Audit summary response."""
    success: bool = True
    action_summary: List[AuditActionSummary] = []
    entity_summary: List[AuditEntitySummary] = []
    total_errors: int = 0
    total_logs: int = 0


# ---------------------------------------------------------------------------
# Audit Export Schemas
# ---------------------------------------------------------------------------

class AuditExportRequest(BaseModel):
    """Audit export request schema."""
    entity_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditExportResponse(BaseModel):
    """Audit export response schema."""
    success: bool = True
    export_id: str
    status: str = "pending"
    message: str = "Export job created"
