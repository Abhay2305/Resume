"""Dashboard Service.

Business logic layer for dashboard operations.
Assembles aggregated data from multiple repositories into dashboard responses.
"""
import logging
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from ..repositories.dashboard import DashboardRepository

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for PROCS dashboard operations.

    Aggregates data from DashboardRepository into dashboard-specific responses.
    """

    def __init__(self, db: Session):
        self.db = db
        self.repo = DashboardRepository(db)

    def get_stats(self) -> Dict[str, Any]:
        """Get all dashboard statistics in a single call.

        Returns aggregated stats from users, resumes, cover letters,
        AI requests, errors, subscriptions, opportunities, and ATS.
        """
        try:
            users = self.repo.get_user_stats()
            resumes = self.repo.get_resume_stats()
            cover_letters = self.repo.get_cover_letter_stats()
            ai_requests = self.repo.get_ai_request_stats()
            errors = self.repo.get_error_stats()
            subscriptions = self.repo.get_subscription_stats()
            opportunities = self.repo.get_opportunity_stats()
            ats = self.repo.get_ats_stats()

            return {
                "users": users,
                "resumes": resumes,
                "cover_letters": cover_letters,
                "ai_requests": ai_requests,
                "errors": errors,
                "subscriptions": subscriptions,
                "opportunities": opportunities,
                "ats": ats,
            }
        except Exception as e:
            logger.error("Failed to get dashboard stats: %s", e)
            raise

    def get_activity(self, limit: int = 10, cursor: str = None) -> Dict[str, Any]:
        """Get recent activity feed with cursor pagination."""
        try:
            return self.repo.get_recent_activity(limit=limit, cursor=cursor)
        except Exception as e:
            logger.error("Failed to get dashboard activity: %s", e)
            raise

    def get_health(self) -> Dict[str, Any]:
        """Get system health status."""
        try:
            return self.repo.get_health_status()
        except Exception as e:
            logger.error("Failed to get dashboard health: %s", e)
            raise

    def get_recent(self, limit: int = 5) -> Dict[str, Any]:
        """Get recent items (errors, activity)."""
        try:
            activity_result = self.repo.get_recent_activity(limit=limit)
            return {
                "errors": self.repo.get_recent_errors(limit=limit),
                "activity": activity_result.get("activity", []),
            }
        except Exception as e:
            logger.error("Failed to get dashboard recent: %s", e)
            raise

    def get_metrics(self, period: str = "24h") -> Dict[str, Any]:
        """Get metric cards data with trend calculations.

        Args:
            period: Time period for trend calculation ('24h', '7d', '30d').
        """
        try:
            metrics = self.repo.get_metrics_with_trends(period=period)
            return {
                "metrics": metrics,
                "period": period,
            }
        except Exception as e:
            logger.error("Failed to get dashboard metrics: %s", e)
            raise

    def get_request_chart(self, period: str = "24h") -> Dict[str, Any]:
        """Get request volume time-series for charts."""
        try:
            return self.repo.get_request_timeseries(period=period)
        except Exception as e:
            logger.error("Failed to get request chart: %s", e)
            raise

    def get_error_chart(self, period: str = "24h") -> Dict[str, Any]:
        """Get error count time-series for charts."""
        try:
            return self.repo.get_error_timeseries(period=period)
        except Exception as e:
            logger.error("Failed to get error chart: %s", e)
            raise

    def get_ai_cost_chart(self, period: str = "24h") -> Dict[str, Any]:
        """Get AI cost time-series for charts."""
        try:
            return self.repo.get_ai_cost_timeseries(period=period)
        except Exception as e:
            logger.error("Failed to get AI cost chart: %s", e)
            raise
