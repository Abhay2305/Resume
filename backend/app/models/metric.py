"""Metrics domain model.

Stores raw metric samples flushed from in-memory counters.
"""
from sqlalchemy import Column, DateTime, Numeric, String, JSON

from .base import Base
from .mixins import UUIDPrimaryKeyMixin


class SystemMetric(UUIDPrimaryKeyMixin, Base):
    """Raw metric sample stored in the system_metrics table."""

    __tablename__ = "system_metrics"

    metric_name = Column(String(200), nullable=False, index=True)
    metric_value = Column(Numeric(20, 4), nullable=False)
    dimensions = Column(JSON, nullable=True)
    recorded_at = Column(DateTime, nullable=False)
