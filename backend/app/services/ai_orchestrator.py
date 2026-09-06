"""AI Orchestrator for the Career Intelligence Engine.

Coordinates the full pipeline:
Knowledge -> Context -> Prompt -> AI -> Rules -> Validation -> DB

The LLM is only the writing engine. Knowledge is the source of truth.
"""
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .ai_service import (
    UniversalAIService,
    ProviderResponse,
    ProviderType,
    get_ai_service,
)
# DEPRECATED: PromptBuilder is a legacy stub. PromptContext, PromptMessage,
# PromptRole are used as data containers for backward compatibility with
# run_pipeline(). Actual prompt construction uses PromptBuilderV2.
from .prompt_builder import PromptBuilder, PromptContext, PromptMessage, PromptRole
from .prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from .prompt_intelligence_v2.types import PromptRequest
from .rules_engine import RulesEngine, ValidationResult

logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """AI task types."""
    RESUME_BULLETS = "resume_bullets"
    RESUME_SUMMARY = "resume_summary"
    COVER_LETTER = "cover_letter"
    BULLET_FEEDBACK = "bullet_feedback"
    ATS_OPTIMIZATION = "ats_optimization"


# TaskType → Prompt Intelligence v2 prompt_type mapping
_TASK_TYPE_MAP = {
    TaskType.RESUME_BULLETS: "resume_bullets",
    TaskType.RESUME_SUMMARY: "resume_summary",
    TaskType.COVER_LETTER: "cover_letter",
    TaskType.BULLET_FEEDBACK: "bullet_feedback",
    TaskType.ATS_OPTIMIZATION: "ats_optimization",
}


@dataclass
class PipelineResult:
    """Result from the AI pipeline."""
    task_type: TaskType
    content: Any
    validation: Optional[ValidationResult] = None
    ai_response: Optional[ProviderResponse] = None
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "task_type": self.task_type.value,
            "content": self.content,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
            "success": self.success,
        }
        if self.validation:
            result["validation"] = self.validation.to_dict()
        if self.ai_response:
            result["usage"] = {
                "prompt_tokens": self.ai_response.prompt_tokens,
                "completion_tokens": self.ai_response.completion_tokens,
                "total_tokens": self.ai_response.total_tokens,
                "model": self.ai_response.model,
            }
        if self.error:
            result["error"] = self.error
        return result


class AIOrchestrator:
    """Coordinates Knowledge -> Prompt -> AI -> Rules -> Validation pipeline.

    The orchestrator ensures:
    1. Knowledge is retrieved BEFORE generation
    2. LLM only writes; knowledge is the source of truth
    3. Output is validated against rules
    4. All operations are logged for audit

    Knowledge is provided via a callable that returns knowledge rules.
    This decouples the orchestrator from the specific knowledge source
    (legacy KnowledgeEngine or new KnowledgeIntelligenceService).
    """

    def __init__(
        self,
        provider: Optional[UniversalAIService] = None,
        knowledge_retriever: Optional[callable] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        rules_engine: Optional[RulesEngine] = None,
        prompt_builder_v2: Optional[PromptBuilderV2] = None,
    ):
        if provider is None:
            try:
                self.provider = get_ai_service()
            except Exception:
                logger.warning("Failed to get AI service, using mock")
                self.provider = UniversalAIService()
        else:
            self.provider = provider

        self.knowledge_retriever = knowledge_retriever
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.prompt_builder_v2 = prompt_builder_v2 or PromptBuilderV2()
        self.rules_engine = rules_engine or RulesEngine()

    @classmethod
    def from_config(
        cls,
        provider_type: Optional[ProviderType] = None,
        knowledge_retriever: Optional[callable] = None,
    ) -> "AIOrchestrator":
        """Create orchestrator from configuration using the universal service."""
        provider = get_ai_service()
        return cls(provider=provider, knowledge_retriever=knowledge_retriever)

    async def run_pipeline(
        self,
        task_type: TaskType,
        input_data: Dict[str, Any],
        validate: bool = True,
        knowledge_domains: Optional[List[str]] = None,
    ) -> PipelineResult:
        """Run the full AI pipeline for a given task.

        Args:
            task_type: Type of task to run
            input_data: Task-specific input parameters
            validate: Whether to validate output with Rules Engine
            knowledge_domains: Specific domains to retrieve knowledge from

        Returns:
            PipelineResult with content, validation, and metadata
        """
        start = time.time()

        try:
            # Step 1: Retrieve knowledge context
            knowledge_chunks = self._retrieve_knowledge(
                task_type, input_data, knowledge_domains
            )

            # Step 2: Build prompt with knowledge context
            prompt = self._build_prompt(task_type, input_data, knowledge_chunks)

            # Step 3: Call AI provider (universal service handles routing)
            messages = self.prompt_builder.to_api_messages(prompt)
            ai_response = await self.provider.generate(messages)

            # Step 4: Parse response
            content = self._parse_response(task_type, ai_response.content)

            # Step 5: Validate with rules engine
            validation = None
            if validate:
                validation = self._validate_output(task_type, content)

            latency_ms = (time.time() - start) * 1000

            return PipelineResult(
                task_type=task_type,
                content=content,
                validation=validation,
                ai_response=ai_response,
                latency_ms=latency_ms,
                metadata={
                    "knowledge_chunks_used": len(knowledge_chunks),
                    "provider": self.provider.provider_name,
                    "validated": validate,
                },
                success=True,
            )

        except Exception as e:
            latency_ms = (time.time() - start) * 1000
            logger.error(f"Pipeline failed for {task_type.value}: {str(e)}")
            return PipelineResult(
                task_type=task_type,
                content=None,
                latency_ms=latency_ms,
                error=str(e),
                success=False,
            )

    def _retrieve_knowledge(
        self,
        task_type: TaskType,
        input_data: Dict[str, Any],
        domains: Optional[List[str]] = None,
    ) -> List[str]:
        """Retrieve relevant knowledge chunks as strings.

        Uses the injected knowledge_retriever callable. If no retriever
        is configured, returns an empty list (graceful degradation).
        """
        if self.knowledge_retriever is None:
            logger.warning("No knowledge_retriever configured, returning empty context")
            return []

        search_parts = []
        if "responsibilities" in input_data:
            search_parts.append(input_data["responsibilities"])
        if "technologies" in input_data:
            search_parts.append(input_data["technologies"])
        if "job_description" in input_data:
            search_parts.append(input_data["job_description"])
        if "target_role" in input_data:
            search_parts.append(input_data["target_role"])

        job_description = " ".join(search_parts) if search_parts else ""

        try:
            return self.knowledge_retriever(
                task_type=task_type.value,
                job_description=job_description,
                domains=domains,
            )
        except Exception as e:
            logger.warning("Knowledge retrieval failed: %s", e)
            return []

    def _build_prompt(
        self,
        task_type: TaskType,
        input_data: Dict[str, Any],
        knowledge_chunks: List[str],
    ) -> PromptContext:
        """Build the appropriate prompt for the task type.

        Uses Prompt Intelligence v2 PromptBuilder for prompt construction,
        then wraps the result in a PromptContext for backward compatibility
        with the existing run_pipeline() flow.

        Knowledge is injected via knowledge_rules in the PromptRequest context
        (dicts with 'instruction', 'section_name', 'source', 'category' keys).
        """
        prompt_type = _TASK_TYPE_MAP.get(task_type)
        if prompt_type is None:
            raise ValueError(f"Unknown task type: {task_type}")

        # Build context: merge input_data with knowledge as knowledge_rules
        context = dict(input_data)
        if knowledge_chunks:
            # Convert string chunks to knowledge_rule dicts for PromptBuilderV2
            knowledge_rules = []
            for chunk in knowledge_chunks:
                if isinstance(chunk, dict):
                    knowledge_rules.append(chunk)
                else:
                    # Wrap string chunks as knowledge rules
                    knowledge_rules.append({
                        "instruction": str(chunk),
                        "section_name": "general",
                        "source": "knowledge_retriever",
                        "category": "General",
                    })
            context["knowledge_rules"] = knowledge_rules

        request = PromptRequest(
            prompt_type=prompt_type,
            context=context,
        )

        # Use v2 builder to get messages (knowledge_rules are composed into instructions)
        messages = self.prompt_builder_v2.build_messages(request)

        # Wrap in PromptContext for backward compatibility with run_pipeline()
        prompt_messages = [
            PromptMessage(role=PromptRole(m["role"]), content=m["content"])
            for m in messages
        ]
        return PromptContext(
            messages=prompt_messages,
            metadata={"task": prompt_type, "prompt_engine": "v2"},
        )

    def _parse_response(self, task_type: TaskType, content: str) -> Any:
        """Parse AI response into structured format."""
        try:
            parsed = json.loads(content)
            return parsed
        except (json.JSONDecodeError, TypeError):
            pass

        if task_type in (TaskType.RESUME_BULLETS,):
            lines = [
                line.strip().lstrip("0123456789.-) ")
                for line in content.split("\n")
                if line.strip() and not line.strip().startswith("{")
            ]
            if lines:
                return lines

        return content

    def _validate_output(
        self, task_type: TaskType, content: Any
    ) -> ValidationResult:
        """Validate output using the Rules Engine."""
        if task_type == TaskType.RESUME_BULLETS and isinstance(content, list):
            return self.rules_engine.validate_bullets(content)
        elif task_type == TaskType.RESUME_SUMMARY and isinstance(content, str):
            return self.rules_engine._validate_summary(content)
        elif task_type == TaskType.BULLET_FEEDBACK and isinstance(content, dict):
            if "improved" in content:
                return self.rules_engine.validate_bullet(content["improved"])
            return ValidationResult(is_valid=True)

        return ValidationResult(is_valid=True)
