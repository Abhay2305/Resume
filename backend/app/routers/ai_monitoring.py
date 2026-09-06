"""AI Monitoring Router.

Admin-only endpoints for AI monitoring: executions, stats, tokens, providers.
Reuses existing services — no duplicate business logic.
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models.ai_execution import AIExecution
from ..schemas import AIExecutionListOut
from ..schemas.ai_monitoring import (
    AiExecutionStatsResponse,
    AiProviderDetail,
    AiProviderModelStats,
    AiProviderStatsResponse,
    AiTokenModelBreakdown,
    AiTokenResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/admin", tags=["AI Monitoring"])


def _parse_period_bounds(period: str):
    """Return (start, bucket_delta) for the given period."""
    now = datetime.utcnow()
    bounds = {
        "24h": (now - timedelta(hours=24), timedelta(hours=1)),
        "7d": (now - timedelta(days=7), timedelta(days=1)),
        "30d": (now - timedelta(days=30), timedelta(days=1)),
    }
    return bounds.get(period, bounds["24h"])


def _build_empty_series(start: datetime, bucket: timedelta):
    """Build an empty time series with zero values."""
    now = datetime.utcnow()
    series = []
    current = start
    while current < now:
        series.append({"label": current.isoformat(), "value": 0})
        current += bucket
    return series


def _merge_count_series(empty, raw_rows, bucket):
    """Merge raw count query results into empty series."""
    lookup = {}
    for row in raw_rows:
        ts = row["bucket"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        key = ts.isoformat()
        lookup[key] = row["count"]

    result = []
    for point in empty:
        ts = datetime.fromisoformat(point["label"])
        matched_value = lookup.get(point["label"], 0)
        if matched_value == 0:
            for raw_key, raw_val in lookup.items():
                raw_ts = datetime.fromisoformat(raw_key)
                if abs((raw_ts - ts).total_seconds()) < bucket.total_seconds():
                    matched_value = raw_val
                    break
        result.append({"label": point["label"], "value": matched_value})
    return result


def _merge_cost_series(empty, raw_rows, bucket):
    """Merge raw cost query results into empty series."""
    lookup = {}
    for row in raw_rows:
        ts = row["bucket"]
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
        key = ts.isoformat()
        lookup[key] = row["cost"]

    result = []
    for point in empty:
        ts = datetime.fromisoformat(point["label"])
        matched_value = lookup.get(point["label"], 0.0)
        if matched_value == 0.0:
            for raw_key, raw_val in lookup.items():
                raw_ts = datetime.fromisoformat(raw_key)
                if abs((raw_ts - ts).total_seconds()) < bucket.total_seconds():
                    matched_value = raw_val
                    break
        result.append({"label": point["label"], "value": matched_value})
    return result


# ---------------------------------------------------------------------------
# GET /api/ai/admin/executions
# ---------------------------------------------------------------------------

@router.get("/executions")
async def list_admin_executions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    provider: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """List all AI executions (admin-only, cross-user, filterable)."""
    query = db.query(AIExecution)

    if provider:
        query = query.filter(AIExecution.provider == provider)
    if status:
        query = query.filter(AIExecution.status == status)
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(AIExecution.created_at >= start_dt)
        except ValueError:
            pass
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(AIExecution.created_at <= end_dt)
        except ValueError:
            pass

    total = query.count()
    items = (
        query.order_by(AIExecution.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return {
        "items": [AIExecutionListOut.model_validate(i) for i in items],
        "total": total,
        "page": page,
        "size": size,
    }


# ---------------------------------------------------------------------------
# GET /api/ai/admin/executions/stats
# ---------------------------------------------------------------------------

@router.get("/executions/stats")
async def get_admin_execution_stats(
    period: str = Query("24h", pattern="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get aggregated execution statistics."""
    start, bucket = _parse_period_bounds(period)
    empty = _build_empty_series(start, bucket)

    # Base query for the period
    base = db.query(AIExecution).filter(AIExecution.created_at >= start)

    total_executions = base.count()
    completed = base.filter(AIExecution.status == "completed").count()
    failed = base.filter(AIExecution.status == "failed").count()

    success_rate = round((completed / total_executions * 100), 2) if total_executions else 0.0
    failure_rate = round((failed / total_executions * 100), 2) if total_executions else 0.0

    # Average latency from completed executions
    avg_latency_row = (
        db.query(func.avg(AIExecution.execution_time_ms))
        .filter(AIExecution.created_at >= start, AIExecution.status == "completed")
        .scalar()
    )
    avg_latency_ms = round(float(avg_latency_row or 0), 2)

    # Total retries
    total_retries = (
        db.query(func.coalesce(func.sum(AIExecution.retry_count), 0))
        .filter(AIExecution.created_at >= start)
        .scalar()
    )

    # By status
    status_rows = (
        db.query(AIExecution.status, func.count(AIExecution.id))
        .filter(AIExecution.created_at >= start)
        .group_by(AIExecution.status)
        .all()
    )
    by_status = {row[0]: row[1] for row in status_rows}

    # Daily trend (count per bucket)
    trend_rows = (
        db.query(
            AIExecution.created_at.label("bucket"),
            func.count(AIExecution.id).label("count"),
        )
        .filter(AIExecution.created_at >= start)
        .group_by(AIExecution.created_at)
        .order_by(AIExecution.created_at)
        .all()
    )
    raw = [{"bucket": str(r.bucket), "count": r.count} for r in trend_rows]
    daily_trend = _merge_count_series(empty, raw, bucket)

    return {
        "total_executions": total_executions,
        "success_rate": success_rate,
        "failure_rate": failure_rate,
        "avg_latency_ms": avg_latency_ms,
        "total_retries": int(total_retries),
        "by_status": by_status,
        "daily_trend": daily_trend,
    }


# ---------------------------------------------------------------------------
# GET /api/ai/admin/tokens
# ---------------------------------------------------------------------------

@router.get("/tokens")
async def get_admin_token_stats(
    period: str = Query("24h", pattern="^(24h|7d|30d)$"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get token usage analytics (by model, daily trend)."""
    start, bucket = _parse_period_bounds(period)
    empty = _build_empty_series(start, bucket)

    base = db.query(AIExecution).filter(AIExecution.created_at >= start)

    # Total tokens
    total_tokens = int(
        db.query(func.coalesce(func.sum(AIExecution.total_tokens), 0))
        .filter(AIExecution.created_at >= start)
        .scalar()
    )

    # By model
    model_rows = (
        db.query(
            AIExecution.model,
            func.coalesce(func.sum(AIExecution.total_tokens), 0).label("tokens"),
        )
        .filter(AIExecution.created_at >= start)
        .group_by(AIExecution.model)
        .all()
    )
    by_model = [
        {
            "model": r.model,
            "tokens": int(r.tokens),
            "percentage": round((int(r.tokens) / total_tokens * 100), 2) if total_tokens else 0.0,
        }
        for r in model_rows
    ]
    by_model.sort(key=lambda x: x["tokens"], reverse=True)

    # Daily trend
    trend_rows = (
        db.query(
            AIExecution.created_at.label("bucket"),
            func.coalesce(func.sum(AIExecution.total_tokens), 0).label("count"),
        )
        .filter(AIExecution.created_at >= start)
        .group_by(AIExecution.created_at)
        .order_by(AIExecution.created_at)
        .all()
    )
    raw = [{"bucket": str(r.bucket), "count": int(r.count)} for r in trend_rows]
    daily_trend = _merge_count_series(empty, raw, bucket)

    # Avg tokens per request
    total_executions = base.count()
    avg_tokens_per_request = round(total_tokens / total_executions, 1) if total_executions else 0.0

    return {
        "total_tokens": total_tokens,
        "by_model": by_model,
        "daily_trend": daily_trend,
        "avg_tokens_per_request": avg_tokens_per_request,
        "period": period,
    }


# ---------------------------------------------------------------------------
# GET /api/ai/admin/providers
# ---------------------------------------------------------------------------

def _check_provider_health(provider_name: str) -> bool:
    """Check if a specific provider has a configured API key."""
    env_key_map = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }
    env_key = env_key_map.get(provider_name)
    if not env_key:
        return False
    api_key = os.getenv(env_key, "").strip()
    return bool(api_key)


@router.get("/providers")
async def get_admin_provider_stats(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get per-provider health and aggregated stats."""
    providers = ["gemini", "openai", "anthropic"]
    result = []

    for provider_name in providers:
        healthy = _check_provider_health(provider_name)

        # Aggregate from AIExecution table
        base = db.query(AIExecution).filter(AIExecution.provider == provider_name)
        total_executions = base.count()
        completed = base.filter(AIExecution.status == "completed").count()
        success_rate = round((completed / total_executions * 100), 2) if total_executions else 0.0

        avg_latency_row = (
            db.query(func.avg(AIExecution.execution_time_ms))
            .filter(AIExecution.provider == provider_name, AIExecution.status == "completed")
            .scalar()
        )
        avg_latency_ms = round(float(avg_latency_row or 0), 2)

        total_cost = float(
            db.query(func.coalesce(func.sum(AIExecution.estimated_cost), 0))
            .filter(AIExecution.provider == provider_name)
            .scalar()
        )
        total_tokens = int(
            db.query(func.coalesce(func.sum(AIExecution.total_tokens), 0))
            .filter(AIExecution.provider == provider_name)
            .scalar()
        )

        # Per-model stats
        model_rows = (
            db.query(
                AIExecution.model,
                func.count(AIExecution.id).label("executions"),
                func.coalesce(func.sum(AIExecution.total_tokens), 0).label("tokens"),
            )
            .filter(AIExecution.provider == provider_name)
            .group_by(AIExecution.model)
            .all()
        )
        models = [
            {"model": r.model, "executions": r.executions, "tokens": int(r.tokens)}
            for r in model_rows
        ]

        result.append({
            "name": provider_name,
            "healthy": healthy,
            "total_executions": total_executions,
            "success_rate": success_rate,
            "avg_latency_ms": avg_latency_ms,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "models": models,
        })

    return {"providers": result}
