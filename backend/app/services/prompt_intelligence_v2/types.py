"""Type definitions for the Prompt Intelligence Engine.

Defines the prompt contract: PromptRequest (input) → PromptPackage (output).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PromptRequest:
    """Input to Prompt Intelligence Engine.

    Caller provides prompt type + context variables.
    The engine produces a PromptPackage ready for Universal AI Engine.
    """
    prompt_type: str
    context: Dict[str, Any]
    template_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptPackage:
    """Output from Prompt Intelligence Engine.

    Structured prompt ready for execution by Universal AI Engine.
    Contains messages list compatible with UniversalAIService.generate().
    """
    prompt_type: str
    system_prompt: str
    user_prompt: str
    messages: List[Dict[str, str]]
    instructions: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    output_schema: Optional[Dict[str, Any]]
    token_estimate: int
    template_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptTemplateMeta:
    """Metadata for a prompt template type.

    Describes what a prompt type requires and produces.
    """
    type: str
    name: str
    version: str
    category: str
    required_variables: List[str]
    optional_variables: List[str]
    output_format: str
    output_schema: Optional[Dict[str, Any]] = None
    max_tokens: Optional[int] = None
    system_prompt_version: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of prompt validation.

    Errors block execution; warnings are informational.
    """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    token_estimate: int = 0
