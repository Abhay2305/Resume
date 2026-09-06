"""Prompt Builder for the Career Intelligence Engine.

.. deprecated::
    This module is deprecated. Use ``app.services.prompt_intelligence_v2`` instead.

Data classes and utilities used by legacy code paths.
All prompt template content has been migrated to ``prompt_intelligence_v2.templates``.
"""
import warnings
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PromptRole(str, Enum):
    """Prompt roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class PromptMessage:
    """A single prompt message."""
    role: PromptRole
    content: str


@dataclass
class PromptContext:
    """Assembled context for a prompt."""
    messages: List[PromptMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptBuilder:
    """Backward-compatible PromptBuilder stub.

    .. deprecated::
        Use ``app.services.prompt_intelligence_v2.builder.PromptBuilder`` instead.
        All prompt content has been migrated to ``prompt_intelligence_v2.templates``.
    """

    def __init__(self):
        warnings.warn(
            "app.services.prompt_builder.PromptBuilder is deprecated. "
            "Use app.services.prompt_intelligence_v2.builder.PromptBuilder instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def to_api_messages(self, context: PromptContext) -> List[Dict[str, str]]:
        """Convert PromptContext to API-compatible message format."""
        return [{"role": m.role.value, "content": m.content} for m in context.messages]
