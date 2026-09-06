"""Metrics domain repository.

Data access layer for SystemMetric entities.
"""
from datetime import datetime
from typing import List, Tuple

from sqlalchemy import func

from ..models.metric import SystemMetric
from .base import BaseRepository


class MetricRepository(BaseRepository[SystemMetric]):
    """Repository for SystemMetric entity."""

    def __init__(self, db):
        super().__init__(SystemMetric, db)

    def get_by_name_and_range(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        page: int = 1,
        limit: int = 100,
    ) -> Tuple[List[SystemMetric], int]:
        """Get metrics by name and time range with pagination."""
        # Strip timezone info for SQLite compatibility
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)

        query = (
            self.db.query(SystemMetric)
            .filter(
                SystemMetric.metric_name == metric_name,
                SystemMetric.recorded_at >= start_time,
                SystemMetric.recorded_at <= end_time,
            )
            .order_by(SystemMetric.recorded_at.desc())
        )
        total = query.count()
        items = query.offset((page - 1) * limit).limit(limit).all()
        return items, total

    def delete_older_than(self, cutoff_date: datetime) -> int:
        """Hard delete metrics older than cutoff_date. Returns count deleted."""
        count = (
            self.db.query(SystemMetric)
            .filter(SystemMetric.recorded_at < cutoff_date)
            .delete()
        )
        self.db.commit()
        return count

    def count_by_name_and_range(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        """Count metrics by name and time range."""
        # Strip timezone info for SQLite compatibility
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)

        return (
            self.db.query(SystemMetric)
            .filter(
                SystemMetric.metric_name == metric_name,
                SystemMetric.recorded_at >= start_time,
                SystemMetric.recorded_at <= end_time,
            )
            .count()
        )

    def sum_value_by_name_and_range(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> float:
        """Sum metric values by name and time range."""
        # Strip timezone info for SQLite compatibility
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
        if end_time.tzinfo is not None:
            end_time = end_time.replace(tzinfo=None)

        result = (
            self.db.query(func.sum(SystemMetric.metric_value))
            .filter(
                SystemMetric.metric_name == metric_name,
                SystemMetric.recorded_at >= start_time,
                SystemMetric.recorded_at <= end_time,
            )
            .scalar()
        )
        return float(result) if result else 0.0

    def create_many(self, items: List[dict]) -> int:
        """Bulk insert metric samples. Returns count inserted."""
        if not items:
            return 0
        objects = [SystemMetric(**item) for item in items]
        self.db.add_all(objects)
        self.db.commit()
        return len(objects)
