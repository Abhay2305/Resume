"""Error hierarchy for the Prompt Intelligence Engine.

All prompt intelligence errors inherit from PromptIntelligenceError.
"""
from typing import List, Optional


class PromptIntelligenceError(Exception):
    """Base error for all prompt intelligence failures."""

    def __init__(self, message: str, prompt_type: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.prompt_type = prompt_type

    def to_dict(self) -> dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "prompt_type": self.prompt_type,
        }


class UnknownPromptType(PromptIntelligenceError):
    """Raised when a requested prompt type is not registered."""

    def __init__(self, prompt_type: str):
        super().__init__(
            f"Unknown prompt type: '{prompt_type}'",
            prompt_type=prompt_type,
        )


class MissingVariables(PromptIntelligenceError):
    """Raised when required variables are missing from context."""

    def __init__(self, missing: List[str], prompt_type: Optional[str] = None):
        self.missing = missing
        super().__init__(
            f"Missing required variables: {', '.join(missing)}",
            prompt_type=prompt_type,
        )

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["missing"] = self.missing
        return d


class InvalidTemplate(PromptIntelligenceError):
    """Raised when a template is malformed or contains invalid content."""

    def __init__(self, message: str, prompt_type: Optional[str] = None):
        super().__init__(message, prompt_type=prompt_type)


class TokenLimitExceeded(PromptIntelligenceError):
    """Raised when estimated tokens exceed the provider limit."""

    def __init__(
        self,
        estimated: int,
        limit: int,
        prompt_type: Optional[str] = None,
    ):
        self.estimated = estimated
        self.limit = limit
        super().__init__(
            f"Token estimate ({estimated}) exceeds limit ({limit})",
            prompt_type=prompt_type,
        )

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["estimated"] = self.estimated
        d["limit"] = self.limit
        return d
