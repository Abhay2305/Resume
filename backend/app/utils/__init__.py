"""Shared API utilities.

Standard response format, pagination, filtering, sorting, and common validators
for the Prompt Resume ecosystem. These utilities ensure consistency across all
API endpoints and comply with the three governing documents.

Usage:
    from app.utils import PaginatedResponse, paginate_query, parse_sort_params
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import asc, desc, text
from sqlalchemy.orm import Query, Session

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Standard API Response Format
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    """Individual error detail for validation errors."""
    field: str
    message: str


class ErrorInfo(BaseModel):
    """Error response structure per PROCS_Implementation.md Section 14.2."""
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None


class MetaInfo(BaseModel):
    """Pagination metadata for paginated responses."""
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    total: int = Field(ge=0)
    totalPages: int = Field(ge=0)


class APIResponse(BaseModel):
    """Standard API response wrapper.
    
    Follows the response format defined in PROCS_Implementation.md Section 14.2:
    {
        "success": true/false,
        "data": { ... },
        "meta": { "page": 1, "limit": 20, "total": 150, "totalPages": 8 }
    }
    """
    success: bool = True
    data: Optional[Any] = None
    meta: Optional[MetaInfo] = None
    error: Optional[ErrorInfo] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Standard paginated response with items and metadata."""
    success: bool = True
    items: List[Any] = []
    meta: MetaInfo
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None


def success_response(
    data: Any,
    request_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standard success response.
    
    Args:
        data: The response data
        request_id: Optional request ID for tracing
        correlation_id: Optional correlation ID for tracing
    
    Returns:
        Standard success response dict
    """
    return {
        "success": True,
        "data": data,
        "request_id": request_id,
        "correlation_id": correlation_id,
    }


def error_response(
    code: str,
    message: str,
    details: Optional[List[Dict[str, str]]] = None,
    request_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standard error response.
    
    Args:
        code: Error code (e.g., VALIDATION_ERROR, NOT_FOUND)
        message: Human-readable error message
        details: Optional list of field-level errors
        request_id: Optional request ID for tracing
        correlation_id: Optional correlation ID for tracing
    
    Returns:
        Standard error response dict
    """
    error_detail = ErrorInfo(code=code, message=message)
    if details:
        error_detail.details = [ErrorDetail(**d) for d in details]
    
    return {
        "success": False,
        "error": error_detail.model_dump(),
        "request_id": request_id,
        "correlation_id": correlation_id,
    }


# ---------------------------------------------------------------------------
# Pagination Utilities
# ---------------------------------------------------------------------------

def paginate_query(
    query: Query,
    page: int = 1,
    limit: int = 20,
    max_limit: int = 100,
) -> Dict[str, Any]:
    """Apply pagination to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        limit: Items per page
        max_limit: Maximum allowed items per page
    
    Returns:
        Dict with 'items', 'total', 'page', 'limit', 'totalPages'
    """
    # Enforce limits
    page = max(1, page)
    limit = max(1, min(limit, max_limit))
    
    # Get total count
    total = query.count()
    
    # Calculate total pages
    total_pages = max(1, (total + limit - 1) // limit)
    
    # Apply pagination
    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "totalPages": total_pages,
    }


def get_pagination_params(
    page: Optional[int] = None,
    limit: Optional[int] = None,
    default_page: int = 1,
    default_limit: int = 20,
    max_limit: int = 100,
) -> tuple[int, int]:
    """Extract and validate pagination parameters.
    
    Args:
        page: Page number (optional)
        limit: Items per page (optional)
        default_page: Default page number
        default_limit: Default items per page
        max_limit: Maximum allowed items per page
    
    Returns:
        Tuple of (page, limit) validated
    """
    page = page if page is not None else default_page
    limit = limit if limit is not None else default_limit
    
    page = max(1, page)
    limit = max(1, min(limit, max_limit))
    
    return page, limit


# ---------------------------------------------------------------------------
# Filtering Utilities
# ---------------------------------------------------------------------------

def apply_filters(
    query: Query,
    filters: Optional[Dict[str, Any]] = None,
    model: Optional[Type] = None,
) -> Query:
    """Apply dynamic filters to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        filters: Dict of field_name: value pairs to filter by
        model: SQLAlchemy model class (for column lookup)
    
    Returns:
        Filtered query
    
    Supported filter formats:
        - {"field": value}  ->  exact match
        - {"field__contains": value}  ->  LIKE %value%
        - {"field__startswith": value}  ->  LIKE value%
        - {"field__gte": value}  ->  >= value
        - {"field__lte": value}  ->  <= value
        - {"field__in": [values]}  ->  IN (values)
        - {"field__is_null": True}  ->  IS NULL
    """
    if not filters:
        return query
    
    for key, value in filters.items():
        # Parse operator
        if "__" in key:
            field_name, operator = key.rsplit("__", 1)
        else:
            field_name = key
            operator = "eq"
        
        # Get column
        if model and hasattr(model, field_name):
            column = getattr(model, field_name)
        else:
            # Try to get column from query's entity
            try:
                column = getattr(query.column_descriptions[0]["entity"], field_name)
            except (AttributeError, IndexError):
                continue
        
        # Apply filter
        if operator == "eq":
            query = query.filter(column == value)
        elif operator == "contains":
            query = query.filter(column.like(f"%{value}%"))
        elif operator == "startswith":
            query = query.filter(column.like(f"{value}%"))
        elif operator == "gte":
            query = query.filter(column >= value)
        elif operator == "lte":
            query = query.filter(column <= value)
        elif operator == "in":
            query = query.filter(column.in_(value))
        elif operator == "is_null" and value is True:
            query = query.filter(column.is_(None))
        elif operator == "is_null" and value is False:
            query = query.filter(column.isnot(None))
    
    return query


def parse_filter_params(
    params: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Parse filter parameters from query string.
    
    Args:
        params: Query parameter dict (e.g., from request.query_params)
    
    Returns:
        Parsed filter dict
    """
    if not params:
        return {}
    
    filters = {}
    for key, value in params.items():
        if key.startswith("filter_"):
            field_name = key[7:]  # Remove "filter_" prefix
            filters[field_name] = value
    
    return filters


# ---------------------------------------------------------------------------
# Sorting Utilities
# ---------------------------------------------------------------------------

def apply_sorting(
    query: Query,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    model: Optional[Type] = None,
    default_sort: Optional[str] = None,
    default_order: str = "desc",
) -> Query:
    """Apply sorting to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        sort_by: Field name to sort by
        sort_order: Sort direction ('asc' or 'desc')
        model: SQLAlchemy model class (for column lookup)
        default_sort: Default sort field if sort_by is None
        default_order: Default sort direction if sort_order is None
    
    Returns:
        Sorted query
    """
    # Use defaults if not provided
    if not sort_by and default_sort:
        sort_by = default_sort
    if not sort_order:
        sort_order = default_order
    
    if not sort_by:
        return query
    
    # Get column
    if model and hasattr(model, sort_by):
        column = getattr(model, sort_by)
    else:
        try:
            column = getattr(query.column_descriptions[0]["entity"], sort_by)
        except (AttributeError, IndexError):
            return query
    
    # Apply sorting
    if sort_order.lower() == "desc":
        return query.order_by(desc(column))
    else:
        return query.order_by(asc(column))


def parse_sort_params(
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None,
    allowed_fields: Optional[List[str]] = None,
    default_sort: str = "created_at",
    default_order: str = "desc",
) -> tuple[str, str]:
    """Parse and validate sorting parameters.
    
    Args:
        sort_by: Field name to sort by
        sort_order: Sort direction ('asc' or 'desc')
        allowed_fields: List of allowed sort fields (None = all)
        default_sort: Default sort field
        default_order: Default sort direction
    
    Returns:
        Tuple of (sort_by, sort_order) validated
    
    Raises:
        ValueError: If sort_by is not in allowed_fields
    """
    # Use defaults
    sort_by = sort_by or default_sort
    sort_order = (sort_order or default_order).lower()
    
    # Validate sort order
    if sort_order not in ("asc", "desc"):
        sort_order = "desc"
    
    # Validate sort field
    if allowed_fields and sort_by not in allowed_fields:
        sort_by = default_sort
    
    return sort_by, sort_order


# ---------------------------------------------------------------------------
# Common Validators
# ---------------------------------------------------------------------------

def validate_string_field(
    value: str,
    min_length: int = 0,
    max_length: int = 1000,
    pattern: Optional[str] = None,
    field_name: str = "field",
) -> str:
    """Validate a string field.
    
    Args:
        value: String value to validate
        min_length: Minimum length
        max_length: Maximum length
        pattern: Regex pattern to match
        field_name: Field name for error messages
    
    Returns:
        Validated string
    
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    
    value = value.strip()
    
    if len(value) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters")
    
    if len(value) > max_length:
        raise ValueError(f"{field_name} must be at most {max_length} characters")
    
    if pattern:
        import re
        if not re.match(pattern, value):
            raise ValueError(f"{field_name} format is invalid")
    
    return value


def validate_email(email: str) -> str:
    """Validate an email address.
    
    Args:
        email: Email address to validate
    
    Returns:
        Normalized email (lowercase, trimmed)
    
    Raises:
        ValueError: If email is invalid
    """
    import re
    
    if not email:
        raise ValueError("Email is required")
    
    email = email.strip().lower()
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    
    return email


def validate_uuid(value: str, field_name: str = "id") -> str:
    """Validate a UUID string.
    
    Args:
        value: UUID string to validate
        field_name: Field name for error messages
    
    Returns:
        Validated UUID string
    
    Raises:
        ValueError: If UUID is invalid
    """
    import uuid
    
    if not value:
        raise ValueError(f"{field_name} is required")
    
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        raise ValueError(f"{field_name} must be a valid UUID")


def validate_pagination(
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> tuple[int, int]:
    """Validate pagination parameters.
    
    Args:
        page: Page number
        limit: Items per page
    
    Returns:
        Tuple of (page, limit) validated
    """
    page = max(1, page if page is not None else 1)
    limit = max(1, min(limit if limit is not None else 20, 100))
    return page, limit


def validate_sort_order(order: Optional[str] = None) -> str:
    """Validate sort order.
    
    Args:
        order: Sort order string
    
    Returns:
        Validated sort order ('asc' or 'desc')
    """
    if not order:
        return "desc"
    
    order = order.lower()
    if order not in ("asc", "desc"):
        return "desc"
    
    return order
