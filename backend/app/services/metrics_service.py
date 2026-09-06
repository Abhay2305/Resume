"""Metrics domain service.

Collects in-memory counters for requests, response times, error rates,
AI token/cost usage, and background job metrics. Periodically flushes
to the system_metrics database table.
"""
import logging
import threading
import time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from ..repositories.metric import MetricRepository
from ..schemas.metric import MetricSummary, VALID_METRIC_NAMES

logger = logging.getLogger(__name__)

# Maximum unique endpoint keys to track (LRU eviction beyond this)
MAX_ENDPOINT_KEYS = 1000

# Maximum response time samples per endpoint
MAX_RESPONSE_SAMPLES = 1000


class MetricsService:
    """Service for collecting, aggregating, and reporting metrics.

    Usage:
        service = MetricsService(db, metric_repository)
        service.record_request("/api/users", "GET", 200, 12.5)
        service.flush()
    """

    def __init__(self, db: Session, metric_repository: MetricRepository):
        self.db = db
        self.repo = metric_repository
        self._lock = threading.Lock()

        # In-memory buffers (protected by _lock)
        self._request_counts: Dict[str, int] = {}
        self._response_times: "OrderedDict[str, list[float]]" = OrderedDict()
        self._error_counts: Dict[str, int] = {}
        self._ai_tokens: Dict[str, int] = {}
        self._ai_costs: Dict[str, float] = {}
        self._job_metrics: Dict[str, Dict[str, int]] = {}

        # Flush thread control
        self._flush_interval = 60
        self._shutdown_flag = threading.Event()
        self._flush_thread: threading.Thread | None = None
        self._last_cleanup_date: datetime | None = None

    # -------------------------------------------------------------------
    # Recording methods (called from middleware / services)
    # -------------------------------------------------------------------

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
    ) -> None:
        """Record an HTTP request metric. Thread-safe, fire-and-forget."""
        with self._lock:
            # Request count
            self._request_counts[endpoint] = self._request_counts.get(endpoint, 0) + 1

            # Response times (with LRU cap per endpoint)
            if endpoint not in self._response_times:
                if len(self._response_times) >= MAX_ENDPOINT_KEYS:
                    self._response_times.popitem(last=False)
                self._response_times[endpoint] = []
            samples = self._response_times[endpoint]
            if len(samples) >= MAX_RESPONSE_SAMPLES:
                samples.pop(0)
            samples.append(response_time_ms)

            # Error count (4xx and 5xx)
            if status_code >= 400:
                key = f"{endpoint}:{method}:{status_code}"
                self._error_counts[key] = self._error_counts.get(key, 0) + 1

    def record_ai_usage(self, model_name: str, tokens: int, cost: float) -> None:
        """Record AI token usage and cost. Thread-safe, fire-and-forget."""
        with self._lock:
            self._ai_tokens[model_name] = self._ai_tokens.get(model_name, 0) + tokens
            self._ai_costs[model_name] = self._ai_costs.get(model_name, 0.0) + cost

    def record_job(self, job_name: str, status: str, duration_ms: float) -> None:
        """Record background job execution. Thread-safe, fire-and-forget."""
        with self._lock:
            if job_name not in self._job_metrics:
                self._job_metrics[job_name] = {"count": 0, "total_ms": 0}
            self._job_metrics[job_name]["count"] += 1
            self._job_metrics[job_name]["total_ms"] += duration_ms

    # -------------------------------------------------------------------
    # Query methods (called from router)
    # -------------------------------------------------------------------

    def get_metrics(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        page: int = 1,
        limit: int = 100,
    ) -> Tuple[List, int]:
        """Retrieve metric samples by name and time range."""
        if metric_name not in VALID_METRIC_NAMES:
            raise ValueError(f"Invalid metric name: {metric_name}")
        return self.repo.get_by_name_and_range(metric_name, start_time, end_time, page, limit)

    def get_metrics_summary(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> MetricSummary:
        """Retrieve aggregated metrics summary for a time period."""
        request_count = self.repo.count_by_name_and_range("request_count", start_time, end_time)
        error_count = self.repo.count_by_name_and_range("error_count", start_time, end_time)
        ai_tokens = int(self.repo.sum_value_by_name_and_range("ai_tokens", start_time, end_time))
        ai_cost = self.repo.sum_value_by_name_and_range("ai_cost", start_time, end_time)

        # Average response time from response_time samples
        response_count = self.repo.count_by_name_and_range("response_time", start_time, end_time)
        response_sum = self.repo.sum_value_by_name_and_range("response_time", start_time, end_time)
        avg_response_time = response_sum / response_count if response_count > 0 else 0.0

        error_rate = error_count / request_count if request_count > 0 else 0.0

        return MetricSummary(
            request_count=request_count,
            avg_response_time_ms=round(avg_response_time, 2),
            error_rate=round(error_rate, 4),
            ai_tokens_total=ai_tokens,
            ai_cost_total=round(ai_cost, 4),
            period_start=start_time,
            period_end=end_time,
        )

    # -------------------------------------------------------------------
    # Flush and cleanup
    # -------------------------------------------------------------------

    def flush(self) -> int:
        """Flush in-memory buffers to database. Returns rows inserted."""
        samples = []
        now = datetime.now(timezone.utc)

        with self._lock:
            # Flush request counts
            for endpoint, count in self._request_counts.items():
                samples.append({
                    "metric_name": "request_count",
                    "metric_value": count,
                    "dimensions": {"endpoint": endpoint},
                    "recorded_at": now,
                })
            self._request_counts.clear()

            # Flush response times (as individual samples)
            for endpoint, times in self._response_times.items():
                for t in times:
                    samples.append({
                        "metric_name": "response_time",
                        "metric_value": t,
                        "dimensions": {"endpoint": endpoint},
                        "recorded_at": now,
                    })
            self._response_times.clear()

            # Flush error counts
            for key, count in self._error_counts.items():
                endpoint, method, status = key.rsplit(":", 2)
                samples.append({
                    "metric_name": "error_count",
                    "metric_value": count,
                    "dimensions": {"endpoint": endpoint, "method": method, "status": status},
                    "recorded_at": now,
                })
            self._error_counts.clear()

            # Flush AI tokens
            for model, tokens in self._ai_tokens.items():
                samples.append({
                    "metric_name": "ai_tokens",
                    "metric_value": tokens,
                    "dimensions": {"model_name": model},
                    "recorded_at": now,
                })
            self._ai_tokens.clear()

            # Flush AI costs
            for model, cost in self._ai_costs.items():
                samples.append({
                    "metric_name": "ai_cost",
                    "metric_value": cost,
                    "dimensions": {"model_name": model},
                    "recorded_at": now,
                })
            self._ai_costs.clear()

            # Flush job metrics
            for job_name, metrics in self._job_metrics.items():
                samples.append({
                    "metric_name": "job_execution",
                    "metric_value": metrics["count"],
                    "dimensions": {"job_name": job_name},
                    "recorded_at": now,
                })
                samples.append({
                    "metric_name": "job_duration",
                    "metric_value": metrics["total_ms"],
                    "dimensions": {"job_name": job_name},
                    "recorded_at": now,
                })
            self._job_metrics.clear()

        if not samples:
            return 0

        try:
            count = self.repo.create_many(samples)
            logger.info("Flushed %d metric samples", count)
            return count
        except Exception as e:
            logger.error("Failed to flush metrics: %s (buffer_size=%d)", e, len(samples))
            return 0

    def cleanup_retention(self) -> int:
        """Delete metrics older than 90 days. Returns count deleted."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        try:
            count = self.repo.delete_older_than(cutoff)
            logger.info("Retention cleanup deleted %d old metrics", count)
            return count
        except Exception as e:
            logger.error("Retention cleanup failed: %s", e)
            return 0

    # -------------------------------------------------------------------
    # Background flush thread lifecycle
    # -------------------------------------------------------------------

    def start_flush_thread(self) -> None:
        """Start the background flush thread. Called once at startup."""
        if self._flush_thread is not None and self._flush_thread.is_alive():
            logger.warning("Flush thread already running")
            return

        self._shutdown_flag.clear()
        self._flush_thread = threading.Thread(
            target=self._flush_loop,
            name="metrics-flush",
            daemon=True,
        )
        self._flush_thread.start()
        logger.info("Metrics flush thread started (interval=%ds)", self._flush_interval)

    def stop_flush_thread(self) -> None:
        """Stop the background flush thread gracefully. Called at shutdown."""
        if self._flush_thread is None:
            return

        self._shutdown_flag.set()
        self._flush_thread.join(timeout=5)
        if self._flush_thread.is_alive():
            logger.warning("Flush thread did not stop within 5s")

        # Final flush
        remaining = self.flush()
        if remaining:
            logger.info("Final flush: %d samples", remaining)

        logger.info("Metrics flush thread stopped")

    def _flush_loop(self) -> None:
        """Background loop: flush every 60s, cleanup once per day."""
        while not self._shutdown_flag.is_set():
            self._shutdown_flag.wait(timeout=self._flush_interval)
            if self._shutdown_flag.is_set():
                break

            try:
                self.flush()
            except Exception as e:
                logger.error("Flush cycle error: %s", e)

            # Daily retention cleanup
            today = datetime.now(timezone.utc).date()
            if self._last_cleanup_date != today:
                try:
                    self.cleanup_retention()
                    self._last_cleanup_date = today
                except Exception as e:
                    logger.error("Daily cleanup error: %s", e)
