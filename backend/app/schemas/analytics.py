"""PROCS Analytics Schemas.

Pydantic schemas for PROCS analytics endpoints.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class RevenueDataPoint(BaseModel):
    label: str
    value: float


class RevenueSummary(BaseModel):
    total_revenue: float = 0.0
    growth: float = 0.0
    avg_revenue: float = 0.0
    total_transactions: int = 0


class RevenueResponse(BaseModel):
    success: bool = True
    summary: RevenueSummary
    series: List[RevenueDataPoint] = []
    period: str = "30d"


class FeatureUsageItem(BaseModel):
    name: str
    count: int
    trend: float = 0.0


class FeatureUsageResponse(BaseModel):
    success: bool = True
    items: List[FeatureUsageItem] = []
    total: int = 0
    period: str = "30d"


class FunnelStep(BaseModel):
    name: str
    count: int
    percentage: float = 0.0


class FunnelData(BaseModel):
    name: str
    steps: List[FunnelStep] = []
    completion_rate: float = 0.0


class FunnelsResponse(BaseModel):
    success: bool = True
    funnels: List[FunnelData] = []
