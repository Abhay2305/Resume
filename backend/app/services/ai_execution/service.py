"""AI Execution Engine service.

Executes validated prompt packages against AI providers and stores execution metadata.
Does NOT modify resumes or apply AI changes.
"""
import json
import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.ai_execution import AIExecution
from app.models.prompt_intelligence import PromptPackage
from app.repositories.ai_execution import AIExecutionRepository
from app.repositories.prompt_intelligence import PromptPackageRepository
from app.services.ai_execution.response_parser import ResponseParser
from app.services.ai_service import (
    AuthenticationError,
    ProviderError,
    ProviderResponse,
    ProviderType,
    RateLimitError,
    TimeoutError,
    ProviderUnavailableError,
    InvalidResponseError,
    ResponseParsingError,
    get_ai_service,
    run_async,
)

logger = logging.getLogger(__name__)


class AIExecutionService:
    """Service for executing prompt packages against AI providers.

    Handles execution, retry logic, latency tracking, token counting,
    cost estimation, and execution metadata storage.
    """

    def __init__(self, db: Session):
        self.db = db
        self.execution_repo = AIExecutionRepository(db)
        self.package_repo = PromptPackageRepository(db)
        self.parser = ResponseParser()

    def execute_prompt_package(
        self,
        user_id: str,
        prompt_package_id: str,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute a prompt package against an AI provider.

        Args:
            user_id: The user executing the prompt.
            prompt_package_id: ID of the prompt package to execute.
            provider: Optional provider override (gemini, openai, anthropic, mock).

        Returns:
            Dictionary with execution result and metadata.

        Raises:
            ValueError: If prompt package not found or invalid.
            ProviderError: If AI execution fails.
        """
        # Load prompt package
        package = self.package_repo.get_by_id(prompt_package_id)
        if not package:
            raise ValueError(f"Prompt package not found: {prompt_package_id}")

        if package.user_id != user_id:
            raise ValueError("Prompt package does not belong to user")

        # Create execution record
        execution_data = {
            "prompt_package_id": prompt_package_id,
            "user_id": user_id,
            "provider": provider or "unknown",
            "model": "pending",
            "status": "pending",
        }
        execution = self.execution_repo.create(execution_data)
        self.db.commit()

        try:
            # Build messages from prompt package
            messages = self._build_messages(package)

            # Get AI service (optionally with provider override)
            ai_service = get_ai_service()
            if provider:
                from app.services.ai_service import ProviderConfig, _load_config
                provider_type_map = {
                    "gemini": ProviderType.GEMINI,
                    "openai": ProviderType.OPENAI,
                    "anthropic": ProviderType.ANTHROPIC,
                }
                if provider.lower() in provider_type_map:
                    config = _load_config()
                    config.provider_type = provider_type_map[provider.lower()]
                    ai_service = __import__('app.services.ai_service', fromlist=['UniversalAIService']).UniversalAIService(config)

            # Update execution with provider info
            self.execution_repo.update(execution.id, {
                "provider": ai_service.provider_name,
                "model": ai_service.model,
            })
            self.db.commit()

            # Execute with timing
            start_time = time.time()
            try:
                response = run_async(ai_service.generate(messages))
            except Exception as e:
                logger.error("AI execution failed: %s\n%s", e, traceback.format_exc())
                raise

            latency_ms = int((time.time() - start_time) * 1000)

            # Parse response
            parsed_response = None
            try:
                parsed_response = self.parser.parse_to_dict(response.content)
            except ResponseParsingError:
                # Store as text if not valid JSON
                parsed_response = {"text": self.parser.parse_to_text(response.content)}

            # Update execution record
            update_data = {
                "status": "completed",
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens,
                "estimated_cost": ai_service.config.model and self._estimate_cost(
                    ai_service.model, response.prompt_tokens, response.completion_tokens
                ),
                "execution_time_ms": latency_ms,
                "raw_response": response.content[:10000] if response.content else None,
                "parsed_response": parsed_response,
                "retry_count": 0,
            }
            execution = self.execution_repo.update(execution.id, update_data)
            self.db.commit()

            return {
                "execution_id": execution.id,
                "status": "completed",
                "provider": ai_service.provider_name,
                "model": ai_service.model,
                "prompt_tokens": response.prompt_tokens,
                "completion_tokens": response.completion_tokens,
                "total_tokens": response.total_tokens,
                "estimated_cost": update_data["estimated_cost"],
                "execution_time_ms": latency_ms,
                "parsed_response": parsed_response,
            }

        except (AuthenticationError, RateLimitError, TimeoutError, ProviderUnavailableError) as e:
            # Non-retryable or already retried errors
            self.execution_repo.update(execution.id, {
                "status": "failed",
                "error_message": str(e),
                "error_code": e.error_code,
            })
            self.db.commit()
            raise

        except ProviderError as e:
            self.execution_repo.update(execution.id, {
                "status": "failed",
                "error_message": str(e),
                "error_code": e.error_code,
            })
            self.db.commit()
            raise

        except Exception as e:
            self.execution_repo.update(execution.id, {
                "status": "failed",
                "error_message": str(e),
                "error_code": "unknown_error",
            })
            self.db.commit()
            raise

    def get_execution(self, execution_id: str) -> Optional[AIExecution]:
        """Get an execution by ID."""
        return self.execution_repo.get_by_id(execution_id)

    def get_executions_by_user(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[AIExecution], int]:
        """Get executions for a user with pagination."""
        return self.execution_repo.get_by_user_id(user_id, skip=skip, limit=limit)

    def get_executions_by_package(self, prompt_package_id: str) -> List[AIExecution]:
        """Get all executions for a prompt package."""
        return self.execution_repo.get_by_prompt_package_id(prompt_package_id)

    def get_execution_response(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the parsed response from an execution."""
        execution = self.execution_repo.get_by_id(execution_id)
        if not execution:
            return None

        return {
            "execution_id": execution.id,
            "status": execution.status,
            "parsed_response": execution.parsed_response,
            "raw_response": execution.raw_response,
            "provider": execution.provider,
            "model": execution.model,
            "prompt_tokens": execution.prompt_tokens,
            "completion_tokens": execution.completion_tokens,
            "total_tokens": execution.total_tokens,
            "execution_time_ms": execution.execution_time_ms,
        }

    def _build_messages(self, package: PromptPackage) -> List[Dict[str, str]]:
        """Build AI messages from a prompt package.

        Args:
            package: The prompt package.

        Returns:
            List of message dictionaries.
        """
        messages = []

        # System prompt
        if package.system_prompt:
            messages.append({"role": "system", "content": package.system_prompt})

        # Build user message from contexts
        user_parts = []

        if package.resume_context:
            user_parts.append(f"Resume Context:\n{json.dumps(package.resume_context, indent=2)}")

        if package.opportunity_context:
            user_parts.append(f"Opportunity Context:\n{json.dumps(package.opportunity_context, indent=2)}")

        if package.gap_context:
            user_parts.append(f"Gap Analysis:\n{json.dumps(package.gap_context, indent=2)}")

        if package.knowledge_context:
            user_parts.append(f"Knowledge Context:\n{json.dumps(package.knowledge_context, indent=2)}")

        if package.instructions:
            user_parts.append(f"Instructions:\n{json.dumps(package.instructions, indent=2)}")

        if package.constraints:
            user_parts.append(f"Constraints:\n{json.dumps(package.constraints, indent=2)}")

        if package.output_schema:
            user_parts.append(f"Expected Output Format:\n{json.dumps(package.output_schema, indent=2)}")

        if user_parts:
            messages.append({"role": "user", "content": "\n\n".join(user_parts)})

        return messages

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for a request."""
        from app.services.ai_service import estimate_cost
        return estimate_cost(model, prompt_tokens, completion_tokens)
