"""Token budget enforcement for per-request and per-user limits."""
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from app.services.ai.error_classifier import TokenBudgetExceeded

logger = logging.getLogger(__name__)


class TokenBudget:
    """Enforces token limits per request and per user (daily/monthly)."""

    def __init__(self):
        self._max_input_tokens = int(os.getenv("AI_MAX_INPUT_TOKENS", "0"))
        self._max_output_tokens = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "0"))
        self._user_daily_limit = int(os.getenv("AI_USER_DAILY_TOKEN_LIMIT", "0"))
        self._user_monthly_limit = int(os.getenv("AI_USER_MONTHLY_TOKEN_LIMIT", "0"))

        self._user_daily: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._user_monthly: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def check_input(self, messages_text: str) -> None:
        if self._max_input_tokens <= 0:
            return
        estimated = self.estimate_tokens(messages_text)
        if estimated > self._max_input_tokens:
            logger.warning(
                "Budget rejection: input tokens %d exceeds limit %d",
                estimated, self._max_input_tokens,
            )
            raise TokenBudgetExceeded(
                f"Input token estimate ({estimated}) exceeds limit ({self._max_input_tokens})"
            )

    def check_user_daily(self, user_id: str, tokens_used: int) -> None:
        if self._user_daily_limit <= 0 or not user_id:
            return
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        current = self._user_daily[user_id][today]
        if current + tokens_used > self._user_daily_limit:
            logger.warning(
                "Budget rejection: user=%s daily tokens %d (+%d) exceeds limit %d",
                user_id, current, tokens_used, self._user_daily_limit,
            )
            raise TokenBudgetExceeded(
                f"User {user_id} daily token limit ({self._user_daily_limit}) would be exceeded. "
                f"Current: {current}, requested: {tokens_used}"
            )

    def check_user_monthly(self, user_id: str, tokens_used: int) -> None:
        if self._user_monthly_limit <= 0 or not user_id:
            return
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        current = self._user_monthly[user_id][month]
        if current + tokens_used > self._user_monthly_limit:
            logger.warning(
                "Budget rejection: user=%s monthly tokens %d (+%d) exceeds limit %d",
                user_id, current, tokens_used, self._user_monthly_limit,
            )
            raise TokenBudgetExceeded(
                f"User {user_id} monthly token limit ({self._user_monthly_limit}) would be exceeded. "
                f"Current: {current}, requested: {tokens_used}"
            )

    def record_usage(self, user_id: str, tokens: int) -> None:
        if not user_id:
            return
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        self._user_daily[user_id][today] += tokens
        self._user_monthly[user_id][month] += tokens

    def get_budget_status(self, user_id: Optional[str] = None) -> Dict[str, any]:
        result: Dict[str, any] = {
            "max_input_tokens": self._max_input_tokens,
            "max_output_tokens": self._max_output_tokens,
            "user_daily_limit": self._user_daily_limit,
            "user_monthly_limit": self._user_monthly_limit,
        }
        if user_id:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            month = datetime.now(timezone.utc).strftime("%Y-%m")
            daily_used = self._user_daily[user_id].get(today, 0)
            monthly_used = self._user_monthly[user_id].get(month, 0)
            result["user_daily_used"] = daily_used
            result["user_daily_remaining"] = max(0, self._user_daily_limit - daily_used) if self._user_daily_limit > 0 else -1
            result["user_monthly_used"] = monthly_used
            result["user_monthly_remaining"] = max(0, self._user_monthly_limit - monthly_used) if self._user_monthly_limit > 0 else -1
        return result

    def get_budget_usage(self, user_id: Optional[str] = None) -> Dict[str, int]:
        if not user_id:
            return {}
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        return {
            "daily_tokens": self._user_daily[user_id].get(today, 0),
            "monthly_tokens": self._user_monthly[user_id].get(month, 0),
        }
