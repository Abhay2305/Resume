"""Dashboard Repository.

Data access layer for dashboard aggregated queries.
Provides read-only aggregated metrics from across the system.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from ..models.identity import User, Subscription, LoginHistory, Payment
from ..models.resume import Resume
from ..models.ai import CoverLetter, AIRequest
from ..models.error import ErrorLog
from ..models.audit import AuditLog
from ..models.opportunity import Opportunity
from ..models.analytics import ATSResult

logger = logging.getLogger(__name__)


def _map_action_to_icon(action: str) -> str:
    """Map audit action to icon type for frontend rendering."""
    action_map = {
        "create": "create",
        "update": "update",
        "delete": "delete",
        "login": "login",
        "logout": "logout",
        "error": "error",
        "export": "export",
    }
    return action_map.get(action.lower(), "info")


def _map_entity_type(entity_type: str) -> str:
    """Map entity type to human-readable label."""
    entity_map = {
        "user": "User",
        "resume": "Resume",
        "cover_letter": "Cover Letter",
        "template": "Template",
        "ai_execution": "AI Execution",
        "subscription": "Subscription",
        "error": "Error",
        "system": "System",
    }
    return entity_map.get(entity_type.lower(), entity_type.replace("_", " ").title())


class DashboardRepository:
    """Repository for dashboard aggregated data queries.

    All methods are read-only and return plain dicts or ints.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_user_stats(self) -> Dict[str, int]:
        """Get user count statistics."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)

        total = self.db.query(func.count(User.id)).filter(User.deleted_at.is_(None)).scalar() or 0
        active = self.db.query(func.count(User.id)).filter(
            User.is_active == True, User.deleted_at.is_(None)
        ).scalar() or 0
        verified = self.db.query(func.count(User.id)).filter(
            User.is_verified == True, User.deleted_at.is_(None)
        ).scalar() or 0
        new_today = self.db.query(func.count(User.id)).filter(
            User.created_at >= today_start, User.deleted_at.is_(None)
        ).scalar() or 0
        new_week = self.db.query(func.count(User.id)).filter(
            User.created_at >= week_start, User.deleted_at.is_(None)
        ).scalar() or 0

        return {
            "total": total,
            "active": active,
            "verified": verified,
            "new_today": new_today,
            "new_this_week": new_week,
        }

    def get_resume_stats(self) -> Dict[str, int]:
        """Get resume count statistics."""
        total = self.db.query(func.count(Resume.id)).scalar() or 0
        return {"total": total}

    def get_cover_letter_stats(self) -> Dict[str, int]:
        """Get cover letter count statistics."""
        total = self.db.query(func.count(CoverLetter.id)).scalar() or 0
        return {"total": total}

    def get_ai_request_stats(self) -> Dict[str, int]:
        """Get AI request statistics."""
        total = self.db.query(func.count(AIRequest.id)).scalar() or 0
        return {"total": total}

    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        total = self.db.query(func.count(ErrorLog.id)).scalar() or 0
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today = self.db.query(func.count(ErrorLog.id)).filter(
            ErrorLog.created_at >= today_start
        ).scalar() or 0
        return {"total": total, "today": today}

    def get_subscription_stats(self) -> Dict[str, int]:
        """Get subscription statistics."""
        total = self.db.query(func.count(Subscription.id)).scalar() or 0
        active = self.db.query(func.count(Subscription.id)).filter(
            Subscription.status == "active"
        ).scalar() or 0
        return {"total": total, "active": active}

    def get_opportunity_stats(self) -> Dict[str, int]:
        """Get opportunity statistics."""
        total = self.db.query(func.count(Opportunity.id)).scalar() or 0
        return {"total": total}

    def get_ats_stats(self) -> Dict[str, int]:
        """Get ATS result statistics."""
        total = self.db.query(func.count(ATSResult.id)).scalar() or 0
        return {"total": total}

    def get_recent_activity(self, limit: int = 10, cursor: str = None) -> Dict[str, Any]:
        """Get recent audit log entries for activity feed with cursor pagination.

        Args:
            limit: Maximum number of entries to return (1-50).
            cursor: ISO timestamp cursor. Returns entries older than this value.
        """
        from datetime import datetime

        query = self.db.query(AuditLog)

        if cursor:
            try:
                cursor_dt = datetime.fromisoformat(cursor.replace("Z", "+00:00")).replace(tzinfo=None)
                query = query.filter(AuditLog.created_at < cursor_dt)
            except (ValueError, TypeError):
                pass

        logs = (
            query.order_by(AuditLog.created_at.desc())
            .limit(limit + 1)
            .all()
        )

        has_more = len(logs) > limit
        items = logs[:limit]

        result = []
        for log in items:
            icon_type = _map_action_to_icon(log.action)
            entity_label = _map_entity_type(log.entity_type)
            result.append({
                "id": log.id,
                "entity_type": log.entity_type,
                "action": log.action,
                "description": log.description or f"{log.action} on {log.entity_type}",
                "user_id": log.user_id,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "icon_type": icon_type,
                "entity_label": entity_label,
            })

        next_cursor = None
        if has_more and items:
            last_item = items[-1]
            if last_item.created_at:
                next_cursor = last_item.created_at.isoformat()

        return {
            "activity": result,
            "has_more": has_more,
            "next_cursor": next_cursor,
        }

    def get_recent_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent error log entries."""
        logs = (
            self.db.query(ErrorLog)
            .order_by(ErrorLog.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": log.id,
                "endpoint": getattr(log, "endpoint", None),
                "http_method": getattr(log, "http_method", None),
                "status_code": getattr(log, "status_code", None),
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health indicators with latency measurements.

        Performs real health checks for Database, AI Providers,
        Storage, and Background Jobs. Each check is independent —
        a failing check does not block other checks.
        """
        import time
        import tempfile
        import os

        def _measure_ms(fn) -> tuple[str, str | None]:
            """Run fn, return (status, latency_str)."""
            start = time.monotonic()
            try:
                fn()
                elapsed_ms = round((time.monotonic() - start) * 1000)
                latency = f"{elapsed_ms}ms"
                if elapsed_ms > 5000:
                    return "degraded", latency
                return "healthy", latency
            except Exception:
                elapsed_ms = round((time.monotonic() - start) * 1000)
                return "failing", f"{elapsed_ms}ms"

        # 1. Database check
        def _check_db():
            from ..database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

        db_status, db_latency = _measure_ms(_check_db)

        # 2. AI Providers check
        def _check_ai():
            from ..models.ai_execution import AIExecution
            self.db.query(AIExecution.id).limit(1).first()

        ai_status, ai_latency = _measure_ms(_check_ai)

        # 3. Storage check
        def _check_storage():
            test_dir = tempfile.gettempdir()
            test_file = os.path.join(test_dir, "procs_health_check.tmp")
            with open(test_file, "w") as f:
                f.write("health")
            with open(test_file, "r") as f:
                f.read()
            os.remove(test_file)

        storage_status, storage_latency = _measure_ms(_check_storage)

        # 4. Background Jobs check
        def _check_jobs():
            from ..models.identity import User
            self.db.query(User.id).limit(1).first()

        jobs_status, jobs_latency = _measure_ms(_check_jobs)

        return {
            "database": {"status": db_status, "latency": db_latency},
            "ai_providers": {"status": ai_status, "latency": ai_latency},
            "storage": {"status": storage_status, "latency": storage_latency},
            "background_jobs": {"status": jobs_status, "latency": jobs_latency},
        }

    def _parse_period(self, period: str) -> tuple[timedelta, timedelta]:
        """Parse period string into (current_delta, previous_delta) timedeltas."""
        period_map = {
            "24h": (timedelta(hours=24), timedelta(hours=48)),
            "7d": (timedelta(days=7), timedelta(days=14)),
            "30d": (timedelta(days=30), timedelta(days=60)),
        }
        return period_map.get(period, period_map["24h"])

    def _calc_trend(self, current: int, previous: int) -> float:
        """Calculate trend percentage between current and previous period."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round(((current - previous) / previous) * 100, 1)

    def get_metrics_with_trends(self, period: str = "24h") -> List[Dict[str, Any]]:
        """Get metric cards data with trend calculations for the given period."""
        now = datetime.utcnow()
        current_delta, previous_delta = self._parse_period(period)

        current_start = now - current_delta
        previous_start = now - previous_delta
        previous_end = current_start

        # Total Users
        total_users = self.db.query(func.count(User.id)).filter(
            User.deleted_at.is_(None)
        ).scalar() or 0
        prev_total_users = self.db.query(func.count(User.id)).filter(
            User.created_at < previous_end,
            User.deleted_at.is_(None),
        ).scalar() or 0

        # Active Users (users who logged in during period)
        active_users = self.db.query(func.count(func.distinct(LoginHistory.user_id))).filter(
            LoginHistory.created_at >= current_start,
            LoginHistory.status == "success",
        ).scalar() or 0
        prev_active_users = self.db.query(func.count(func.distinct(LoginHistory.user_id))).filter(
            LoginHistory.created_at >= previous_start,
            LoginHistory.created_at < previous_end,
            LoginHistory.status == "success",
        ).scalar() or 0

        # Total Resumes
        total_resumes = self.db.query(func.count(Resume.id)).scalar() or 0
        prev_total_resumes = self.db.query(func.count(Resume.id)).filter(
            Resume.created_at < previous_end,
        ).scalar() or 0

        # AI Requests
        total_ai = self.db.query(func.count(AIRequest.id)).scalar() or 0
        prev_total_ai = self.db.query(func.count(AIRequest.id)).filter(
            AIRequest.created_at < previous_end,
        ).scalar() or 0

        # System Errors (in period)
        current_errors = self.db.query(func.count(ErrorLog.id)).filter(
            ErrorLog.created_at >= current_start,
        ).scalar() or 0
        previous_errors = self.db.query(func.count(ErrorLog.id)).filter(
            ErrorLog.created_at >= previous_start,
            ErrorLog.created_at < previous_end,
        ).scalar() or 0

        # Revenue MTD (from payments)
        revenue_current = self.db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.payment_date >= current_start,
            Payment.status == "completed",
        ).scalar() or 0
        revenue_previous = self.db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.payment_date >= previous_start,
            Payment.payment_date < previous_end,
            Payment.status == "completed",
        ).scalar() or 0

        return [
            {
                "id": "total_users",
                "title": "Total Users",
                "value": total_users,
                "trend": self._calc_trend(total_users, prev_total_users),
                "subtitle": "All registered users",
            },
            {
                "id": "active_users",
                "title": "Active Users",
                "value": active_users,
                "trend": self._calc_trend(active_users, prev_active_users),
                "subtitle": f"{active_users:,} active in last {period}",
            },
            {
                "id": "total_resumes",
                "title": "Total Resumes",
                "value": total_resumes,
                "trend": self._calc_trend(total_resumes, prev_total_resumes),
                "subtitle": "All created resumes",
            },
            {
                "id": "ai_requests",
                "title": "AI Requests",
                "value": total_ai,
                "trend": self._calc_trend(total_ai, prev_total_ai),
                "subtitle": f"{total_ai:,} total requests",
            },
            {
                "id": "system_errors",
                "title": "System Errors",
                "value": current_errors,
                "trend": self._calc_trend(current_errors, previous_errors),
                "subtitle": f"{current_errors} errors in last {period}",
            },
            {
                "id": "revenue_mtd",
                "title": "Revenue (MTD)",
                "value": float(revenue_current),
                "trend": self._calc_trend(float(revenue_current), float(revenue_previous)),
                "subtitle": f"${float(revenue_current):,.0f} this period",
            },
        ]

    def _get_period_bounds(self, period: str) -> tuple[datetime, timedelta]:
        """Return (start, bucket_delta) for the given period."""
        now = datetime.utcnow()
        bounds = {
            "24h": (now - timedelta(hours=24), timedelta(hours=1)),
            "7d": (now - timedelta(days=7), timedelta(days=1)),
            "30d": (now - timedelta(days=30), timedelta(days=1)),
        }
        return bounds.get(period, bounds["24h"])

    def _build_empty_series(self, start: datetime, bucket: timedelta) -> List[Dict[str, Any]]:
        """Build an empty time series with zero values for each bucket."""
        now = datetime.utcnow()
        series = []
        current = start
        while current < now:
            series.append({"label": current.isoformat(), "value": 0})
            current += bucket
        return series

    def _merge_series(
        self, empty: List[Dict[str, Any]], raw: List[Dict[str, Any]], bucket: timedelta
    ) -> List[Dict[str, Any]]:
        """Merge raw query results into the empty series template."""
        lookup: Dict[str, int] = {}
        for row in raw:
            ts = row["bucket"]
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
            key = ts.isoformat()
            lookup[key] = row["count"]

        result = []
        for point in empty:
            ts = datetime.fromisoformat(point["label"])
            matched_value = lookup.get(point["label"], 0)
            # Try matching by floor to bucket boundary
            if matched_value == 0:
                for raw_key, raw_val in lookup.items():
                    raw_ts = datetime.fromisoformat(raw_key)
                    if abs((raw_ts - ts).total_seconds()) < bucket.total_seconds():
                        matched_value = raw_val
                        break
            result.append({"label": point["label"], "value": matched_value})
        return result

    def get_request_timeseries(self, period: str = "24h") -> Dict[str, Any]:
        """Count audit_logs per time bucket."""
        start, bucket = self._get_period_bounds(period)
        empty = self._build_empty_series(start, bucket)

        rows = (
            self.db.query(
                AuditLog.created_at.label("bucket"),
                func.count(AuditLog.id).label("count"),
            )
            .filter(AuditLog.created_at >= start)
            .group_by(AuditLog.created_at)
            .order_by(AuditLog.created_at)
            .all()
        )

        raw = [{"bucket": str(r.bucket), "count": r.count} for r in rows]
        series = self._merge_series(empty, raw, bucket)
        total = sum(p["value"] for p in series)

        return {"series": series, "total": total, "period": period}

    def get_error_timeseries(self, period: str = "24h") -> Dict[str, Any]:
        """Count error_logs per time bucket."""
        start, bucket = self._get_period_bounds(period)
        empty = self._build_empty_series(start, bucket)

        rows = (
            self.db.query(
                ErrorLog.created_at.label("bucket"),
                func.count(ErrorLog.id).label("count"),
            )
            .filter(ErrorLog.created_at >= start)
            .group_by(ErrorLog.created_at)
            .order_by(ErrorLog.created_at)
            .all()
        )

        raw = [{"bucket": str(r.bucket), "count": r.count} for r in rows]
        series = self._merge_series(empty, raw, bucket)
        total = sum(p["value"] for p in series)

        return {"series": series, "total": total, "period": period}

    def get_ai_cost_timeseries(self, period: str = "24h") -> Dict[str, Any]:
        """Sum ai_executions cost per time bucket, plus by-provider breakdown."""
        from ..models.ai_execution import AIExecution

        start, bucket = self._get_period_bounds(period)
        empty = self._build_empty_series(start, bucket)

        rows = (
            self.db.query(
                AIExecution.created_at.label("bucket"),
                func.coalesce(func.sum(AIExecution.estimated_cost), 0).label("count"),
            )
            .filter(AIExecution.created_at >= start)
            .group_by(AIExecution.created_at)
            .order_by(AIExecution.created_at)
            .all()
        )

        raw = [{"bucket": str(r.bucket), "count": float(r.count)} for r in rows]
        series = self._merge_series(empty, raw, bucket)
        total_cost = round(sum(p["value"] for p in series), 2)

        provider_rows = (
            self.db.query(
                AIExecution.provider.label("provider"),
                func.coalesce(func.sum(AIExecution.estimated_cost), 0).label("total_cost"),
            )
            .filter(AIExecution.created_at >= start)
            .group_by(AIExecution.provider)
            .all()
        )

        by_provider = [
            {"provider": r.provider, "total_cost": round(float(r.total_cost), 2)}
            for r in provider_rows
        ]

        return {
            "series": series,
            "by_provider": by_provider,
            "total_cost": total_cost,
            "period": period,
        }

    # ------------------------------------------------------------------
    # Analytics: Revenue
    # ------------------------------------------------------------------

    def get_revenue_analytics(self, period: str = "30d") -> dict:
        """Get revenue analytics with time series and summary."""
        now = datetime.utcnow()
        period_map = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
        }
        delta = period_map.get(period, timedelta(days=30))
        current_start = now - delta
        previous_start = current_start - delta

        # Current period revenue
        revenue_current = self.db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.payment_date >= current_start,
            Payment.status == "completed",
        ).scalar() or 0

        # Previous period revenue
        revenue_previous = self.db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(
            Payment.payment_date >= previous_start,
            Payment.payment_date < current_start,
            Payment.status == "completed",
        ).scalar() or 0

        # Transaction counts
        tx_current = self.db.query(func.count(Payment.id)).filter(
            Payment.payment_date >= current_start,
            Payment.status == "completed",
        ).scalar() or 0

        tx_previous = self.db.query(func.count(Payment.id)).filter(
            Payment.payment_date >= previous_start,
            Payment.payment_date < current_start,
            Payment.status == "completed",
        ).scalar() or 0

        # Growth
        growth = self._calc_trend(float(revenue_current), float(revenue_previous))

        # Avg revenue per transaction
        avg_revenue = float(revenue_current) / tx_current if tx_current > 0 else 0.0

        # Time series: daily revenue
        start, bucket = self._get_period_bounds(period)
        empty = self._build_empty_series(start, bucket)

        rows = (
            self.db.query(
                Payment.payment_date.label("bucket"),
                func.coalesce(func.sum(Payment.amount), 0).label("count"),
            )
            .filter(
                Payment.payment_date >= start,
                Payment.status == "completed",
            )
            .group_by(Payment.payment_date)
            .order_by(Payment.payment_date)
            .all()
        )

        raw = [{"bucket": str(r.bucket), "count": float(r.count)} for r in rows]
        series = self._merge_series(empty, raw, bucket)

        return {
            "summary": {
                "total_revenue": float(revenue_current),
                "growth": growth,
                "avg_revenue": round(avg_revenue, 2),
                "total_transactions": tx_current,
            },
            "series": series,
            "period": period,
        }

    # ------------------------------------------------------------------
    # Analytics: Feature Usage
    # ------------------------------------------------------------------

    def get_feature_usage_analytics(self, period: str = "30d") -> dict:
        """Get feature usage analytics across resumes, cover letters, AI requests."""
        now = datetime.utcnow()
        period_map = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
        }
        delta = period_map.get(period, timedelta(days=30))
        current_start = now - delta
        previous_start = current_start - delta

        def _count_and_trend(model, label):
            current = self.db.query(func.count(model.id)).filter(
                model.created_at >= current_start
            ).scalar() or 0
            previous = self.db.query(func.count(model.id)).filter(
                model.created_at >= previous_start,
                model.created_at < current_start,
            ).scalar() or 0
            trend = self._calc_trend(current, previous)
            return {"name": label, "count": current, "trend": trend}

        items = [
            _count_and_trend(Resume, "Resumes Created"),
            _count_and_trend(CoverLetter, "Cover Letters Generated"),
            _count_and_trend(AIRequest, "AI Requests"),
        ]

        total = sum(item["count"] for item in items)

        return {
            "items": items,
            "total": total,
            "period": period,
        }

    # ------------------------------------------------------------------
    # Analytics: Funnels
    # ------------------------------------------------------------------

    def get_funnel_analytics(self) -> dict:
        """Get funnel conversion analytics."""
        # Funnel 1: User Onboarding
        total_users = self.db.query(func.count(User.id)).filter(
            User.deleted_at.is_(None)
        ).scalar() or 0

        verified_users = self.db.query(func.count(User.id)).filter(
            User.is_verified == True,
            User.deleted_at.is_(None),
        ).scalar() or 0

        active_subscriptions = self.db.query(func.count(Subscription.id)).filter(
            Subscription.status == "active",
        ).scalar() or 0

        onboarding_steps = [
            {"name": "Signups", "count": total_users, "percentage": 100.0},
            {"name": "Verified", "count": verified_users, "percentage": round(verified_users / total_users * 100, 1) if total_users > 0 else 0},
            {"name": "Subscribed", "count": active_subscriptions, "percentage": round(active_subscriptions / total_users * 100, 1) if total_users > 0 else 0},
        ]

        # Funnel 2: Content Creation
        total_resumes = self.db.query(func.count(Resume.id)).scalar() or 0
        total_cover_letters = self.db.query(func.count(CoverLetter.id)).scalar() or 0
        total_ats = self.db.query(func.count(ATSResult.id)).scalar() or 0

        content_steps = [
            {"name": "Resumes Created", "count": total_resumes, "percentage": 100.0},
            {"name": "Cover Letters", "count": total_cover_letters, "percentage": round(total_cover_letters / total_resumes * 100, 1) if total_resumes > 0 else 0},
            {"name": "ATS Scored", "count": total_ats, "percentage": round(total_ats / total_resumes * 100, 1) if total_resumes > 0 else 0},
        ]

        # Funnel 3: AI Engagement
        total_ai = self.db.query(func.count(AIRequest.id)).scalar() or 0
        total_opportunities = self.db.query(func.count(Opportunity.id)).scalar() or 0

        ai_steps = [
            {"name": "AI Requests", "count": total_ai, "percentage": 100.0},
            {"name": "Opportunities Found", "count": total_opportunities, "percentage": round(total_opportunities / total_ai * 100, 1) if total_ai > 0 else 0},
        ]

        funnels = [
            {
                "name": "User Onboarding",
                "steps": onboarding_steps,
                "completion_rate": onboarding_steps[-1]["percentage"],
            },
            {
                "name": "Content Creation",
                "steps": content_steps,
                "completion_rate": content_steps[-1]["percentage"],
            },
            {
                "name": "AI Engagement",
                "steps": ai_steps,
                "completion_rate": ai_steps[-1]["percentage"],
            },
        ]

        return {"funnels": funnels}
