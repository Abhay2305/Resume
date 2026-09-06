"""Error domain schemas.

Pydantic models for error API request/response validation.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# ---------------------------------------------------------------------------
# Error Output Schema
# ---------------------------------------------------------------------------

class ErrorOut(BaseModel):
    """Error log output schema."""
    id: str
    error_type: str
    error_message: str
    error_fingerprint: Optional[str] = None
    severity: str
    status: str
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    response_status: Optional[int] = None
    module: Optional[str] = None
    function: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    router: Optional[str] = None
    stack_trace: Optional[str] = None
    request_payload: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    processing_time_ms: Optional[int] = None
    environment: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    retry_count: int = 0
    occurrence_count: int = 1
    first_occurrence_at: Optional[datetime] = None
    last_occurrence_at: Optional[datetime] = None
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Error List Response
# ---------------------------------------------------------------------------

class ErrorListResponse(BaseModel):
    """Paginated error list response."""
    items: List[ErrorOut] = []
    total: int = 0
    page: int = 1
    size: int = 20
    totalPages: int = 1


# ---------------------------------------------------------------------------
# Error Stats Response
# ---------------------------------------------------------------------------

class ErrorStatsResponse(BaseModel):
    """Error statistics response."""
    total: int = 0
    by_severity: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    top_types: List[Dict[str, Any]] = []
    resolution_rate: float = 0.0


# ---------------------------------------------------------------------------
# Error Acknowledge/Resolve Response
# ---------------------------------------------------------------------------

class ErrorActionResponse(BaseModel):
    """Response from error action endpoints."""
    success: bool = True
    error: Optional[ErrorOut] = None
    message: str = ""
