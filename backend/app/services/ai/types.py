"""Type definitions for the AI provider abstraction layer."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import uuid
from datetime import datetime


class ProviderType(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class ProviderConfig:
    provider_type: ProviderType
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    timeout: int = 60
    max_retries: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 30.0
    base_url: Optional[str] = None
    priority: int = 0
    enabled: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderResponse:
    content: str
    model: str
    provider: ProviderType
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: str = ""
    raw_response: Any = None
    latency_ms: float = 0.0
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def prompt_tokens(self) -> int:
        return self.usage.get("prompt_tokens", 0)

    @property
    def completion_tokens(self) -> int:
        return self.usage.get("completion_tokens", 0)

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


@dataclass
class ProviderMetrics:
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = ""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: float = 0.0
    success: bool = False
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider": self.provider,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error_code": self.error_code,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "timestamp": self.timestamp,
        }
