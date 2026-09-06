"""Critical error notification hooks.

Provides an extensible notification mechanism for critical (5xx) exceptions.
Designed for future integration with Slack, Email, PagerDuty, etc.

Usage:
    from app.notifications import notify_critical_error
    notify_critical_error(error_code="DATABASE_ERROR", message="Connection pool exhausted")
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NotificationProvider(ABC):
    """Base class for notification providers."""

    @abstractmethod
    def send(self, event: Dict[str, Any]) -> bool:
        """Send a notification. Returns True if successful."""
        ...


class LogNotificationProvider(NotificationProvider):
    """Default provider that logs critical errors."""

    def send(self, event: Dict[str, Any]) -> bool:
        logger.critical(
            "CRITICAL ERROR [%s] %s - %s (request_id=%s)",
            event.get("error_code"),
            event.get("message"),
            event.get("endpoint"),
            event.get("request_id"),
        )
        return True


_notification_providers: List[NotificationProvider] = [LogNotificationProvider()]


def register_provider(provider: NotificationProvider) -> None:
    """Register a notification provider for critical error alerts."""
    _notification_providers.append(provider)


def notify_critical_error(
    *,
    error_code: str,
    message: str,
    endpoint: Optional[str] = None,
    http_method: Optional[str] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    status_code: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Trigger notification hooks for critical (5xx) exceptions.

    This is a fire-and-forget function. Provider failures are logged and ignored.
    """
    event = {
        "error_code": error_code,
        "message": message,
        "endpoint": endpoint,
        "http_method": http_method,
        "request_id": request_id,
        "user_id": user_id,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **(extra or {}),
    }

    for provider in _notification_providers:
        try:
            provider.send(event)
        except Exception as exc:
            logger.warning(
                "Notification provider %s failed: %s",
                type(provider).__name__,
                exc,
            )
