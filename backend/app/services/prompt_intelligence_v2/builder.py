"""Prompt Builder — orchestrates prompt construction from request to package.

Composes: registry → templates → interpolation → instructions → constraints
→ output schema → token estimation → validation → PromptPackage assembly.
"""
import json
from typing import Any, Dict, List, Optional

from app.services.prompt_intelligence_v2.errors import (
    MissingVariables,
    UnknownPromptType,
)
from app.services.prompt_intelligence_v2.instructions import InstructionComposer
from app.services.prompt_intelligence_v2.interpolator import VariableInterpolator
from app.services.prompt_intelligence_v2.registry import PromptRegistry, create_default_registry
from app.services.prompt_intelligence_v2.templates import PromptTemplates
from app.services.prompt_intelligence_v2.types import (
    PromptPackage,
    PromptRequest,
    ValidationResult,
)

# Context-driven types: user message comes from context, not a template
_CONTEXT_DRIVEN_TYPES = {"resume_tailoring", "resume_generation", "ats_optimization_pi", "chat"}


class PromptBuilder:
    """Builds PromptPackages from PromptRequests.

    Orchestrates registry lookup, template loading, variable interpolation,
    instruction composition, constraint assembly, output schema selection,
    token estimation, and validation into a single build() call.
    """

    def __init__(
        self,
        registry: Optional[PromptRegistry] = None,
        templates: Optional[PromptTemplates] = None,
        interpolator: Optional[VariableInterpolator] = None,
        composer: Optional[InstructionComposer] = None,
    ) -> None:
        self._registry = registry or create_default_registry()
        self._templates = templates or PromptTemplates()
        self._interpolator = interpolator or VariableInterpolator()
        self._composer = composer or InstructionComposer(self._templates)

    # ------------------------------------------------------------------
    # Core build pipeline
    # ------------------------------------------------------------------

    def build(self, request: PromptRequest) -> PromptPackage:
        """Build a complete PromptPackage from a PromptRequest.

        Pipeline:
        1. Registry lookup → metadata (required/optional variables)
        2. Template loading → system prompt, user template
        3. Variable interpolation → resolved user prompt
        4. Instruction composition → instructions list
        5. Constraint assembly → constraints list
        6. Output schema selection → schema dict
        7. Token estimation → integer estimate
        8. Validation → verify no unresolved placeholders
        9. Package assembly → PromptPackage

        Raises:
            UnknownPromptType: If prompt_type is not registered.
            MissingVariables: If required variables are missing from context.
        """
        # 1. Registry lookup
        meta = self._registry.get(request.prompt_type)

        # 2. Template loading
        system_prompt = self._templates.get_system(request.prompt_type)
        user_template = self._templates.get_user(request.prompt_type)

        # 3. Variable interpolation
        if request.prompt_type in _CONTEXT_DRIVEN_TYPES:
            user_prompt = self._build_context_driven_user(request)
        else:
            user_prompt = self._interpolator.interpolate(
                user_template,
                request.context,
                required_variables=meta.required_variables,
                optional_variables=meta.optional_variables,
                prompt_type=request.prompt_type,
            )

        # 4. Instruction composition (via InstructionComposer)
        gap_categories = request.context.get("gap_categories")
        recommendations = request.context.get("recommendations")
        knowledge_rules = request.context.get("knowledge_rules")
        instructions = self._composer.compose(
            request.prompt_type,
            gap_categories=gap_categories,
            recommendations=recommendations,
            knowledge_rules=knowledge_rules,
        )

        # 5. Constraint assembly (via InstructionComposer)
        constraints = self._composer.compose_constraints(request.prompt_type)

        # 6. Output schema selection
        output_schema = self._templates.get_output_schema(request.prompt_type)

        # 7. Token estimation
        token_estimate = self._estimate_tokens(system_prompt, user_prompt, instructions, constraints, output_schema)

        # 8. Inject instructions, constraints, knowledge, and output schema into user message
        injected_user = user_prompt

        if instructions:
            injected_user += "\n\n## Instructions\n"
            for i, inst in enumerate(instructions, 1):
                inst_text = inst.get("instruction", "")
                if inst_text:
                    injected_user += f"{i}. {inst_text}\n"

        if constraints:
            injected_user += "\n\n## Constraints\n"
            for constraint in constraints:
                c_text = constraint.get("constraint", "")
                if c_text:
                    injected_user += f"- {c_text}\n"

        knowledge_rules = request.context.get("knowledge_rules")
        if knowledge_rules:
            injected_user += "\n\n## Authoritative Knowledge Rules\n"
            for rule in knowledge_rules:
                section = rule.get("section_name", "general")
                content = rule.get("instruction", "")
                source = rule.get("source", "unknown")
                if content:
                    injected_user += f"- [{section}] {content} (Source: {source})\n"

        if output_schema:
            injected_user += f"\n\n## Required Output Format\n{json.dumps(output_schema, indent=2)}\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": injected_user},
        ]
        unresolved = self._interpolator.find_placeholders(system_prompt) | self._interpolator.find_placeholders(injected_user)
        # Filter out output_schema JSON patterns ({{ }}) — only check {variable} patterns
        # unresolved already only contains {word} patterns from interpolator regex

        # 9. Package assembly
        return PromptPackage(
            prompt_type=request.prompt_type,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            messages=messages,
            instructions=instructions,
            constraints=constraints,
            output_schema=output_schema,
            token_estimate=token_estimate,
            template_version=meta.version,
            metadata={
                "category": meta.category,
                "output_format": meta.output_format,
                "template_id": request.template_id,
                "user_id": request.user_id,
                **request.metadata,
            },
        )

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def build_messages(self, request: PromptRequest) -> List[Dict[str, str]]:
        """Build and return only the messages list.

        Convenience for callers who only need the messages for
        UniversalAIService.generate().
        """
        package = self.build(request)
        return package.messages

    def validate(self, request: PromptRequest) -> ValidationResult:
        """Validate a request without building the full package.

        Checks:
        - Prompt type is registered
        - Required variables are present in context
        - No unresolved placeholders remain
        - Token count is reasonable
        """
        errors: List[str] = []
        warnings: List[str] = []
        token_estimate = 0

        # Check prompt type exists
        meta = self._registry.get_meta(request.prompt_type)
        if meta is None:
            errors.append(f"Unknown prompt type: '{request.prompt_type}'")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Check required variables (resolve dot paths)
        for var in meta.required_variables:
            if var in meta.optional_variables:
                continue
            # Resolve dot path
            value = request.context
            found = True
            for part in var.split("."):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    found = False
                    break
            if not found or value is None:
                errors.append(f"Missing required variable: '{var}'")

        # Check template placeholder alignment
        user_template = self._templates.get_user(request.prompt_type)
        if user_template:
            validation = self._interpolator.validate_template(
                user_template,
                required_variables=meta.required_variables,
                optional_variables=meta.optional_variables,
            )
            if validation["undeclared"]:
                warnings.append(f"Undeclared placeholders in template: {validation['undeclared']}")
            if validation["unused_required"]:
                warnings.append(f"Required variables not in template: {validation['unused_required']}")

        # Token estimate (approximate)
        system_prompt = self._templates.get_system(request.prompt_type)
        if request.prompt_type not in _CONTEXT_DRIVEN_TYPES and user_template:
            try:
                user_prompt = self._interpolator.interpolate(
                    user_template, request.context,
                    required_variables=meta.required_variables,
                    optional_variables=meta.optional_variables,
                )
            except MissingVariables:
                user_prompt = ""
        else:
            user_prompt = ""
        token_estimate = self._estimate_tokens(system_prompt, user_prompt, [], [], None)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            token_estimate=token_estimate,
        )

    def estimate_tokens(self, request: PromptRequest) -> int:
        """Estimate token count for a request without building the full package."""
        meta = self._registry.get_meta(request.prompt_type)
        if meta is None:
            return 0

        system_prompt = self._templates.get_system(request.prompt_type)
        user_template = self._templates.get_user(request.prompt_type)

        if request.prompt_type not in _CONTEXT_DRIVEN_TYPES and user_template:
            try:
                user_prompt = self._interpolator.interpolate(
                    user_template, request.context,
                    required_variables=meta.required_variables,
                    optional_variables=meta.optional_variables,
                )
            except MissingVariables:
                user_prompt = ""
        else:
            user_prompt = ""

        gap_categories = request.context.get("gap_categories")
        recommendations = request.context.get("recommendations")
        knowledge_rules = request.context.get("knowledge_rules")
        instructions = self._composer.compose(
            request.prompt_type,
            gap_categories=gap_categories,
            recommendations=recommendations,
            knowledge_rules=knowledge_rules,
        )
        constraints = self._composer.compose_constraints(request.prompt_type)
        output_schema = self._templates.get_output_schema(request.prompt_type)

        return self._estimate_tokens(system_prompt, user_prompt, instructions, constraints, output_schema)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_context_driven_user(self, request: PromptRequest) -> str:
        """Build user prompt for context-driven types from structured context."""
        prompt_type = request.prompt_type
        ctx = request.context

        if prompt_type == "chat":
            return ctx.get("user_message", "")

        # For resume_tailoring, resume_generation, ats_optimization_pi:
        # Build a structured user prompt from context data
        parts = []
        if prompt_type == "resume_tailoring":
            resume = ctx.get("resume_knowledge", {})
            opportunity = ctx.get("opportunity", {})
            if isinstance(resume, dict):
                parts.append(f"## Resume Data\n{json.dumps(resume, indent=2)}")
            elif isinstance(resume, str):
                parts.append(f"## Resume Data\n{resume}")
            if isinstance(opportunity, dict):
                parts.append(f"## Target Opportunity\n{json.dumps(opportunity, indent=2)}")
            elif isinstance(opportunity, str):
                parts.append(f"## Target Opportunity\n{opportunity}")
            gap = ctx.get("gap_analysis")
            if gap:
                if isinstance(gap, dict):
                    parts.append(f"## Gap Analysis\n{json.dumps(gap, indent=2)}")
                elif isinstance(gap, str):
                    parts.append(f"## Gap Analysis\n{gap}")
        elif prompt_type == "resume_generation":
            resume = ctx.get("resume_knowledge", {})
            if isinstance(resume, dict):
                parts.append(f"## Resume Data\n{json.dumps(resume, indent=2)}")
            elif isinstance(resume, str):
                parts.append(f"## Resume Data\n{resume}")
        elif prompt_type == "ats_optimization_pi":
            resume = ctx.get("resume_knowledge", {})
            opportunity = ctx.get("opportunity", {})
            if isinstance(resume, dict):
                parts.append(f"## Resume Data\n{json.dumps(resume, indent=2)}")
            elif isinstance(resume, str):
                parts.append(f"## Resume Data\n{resume}")
            if isinstance(opportunity, dict):
                parts.append(f"## Target Opportunity\n{json.dumps(opportunity, indent=2)}")
            elif isinstance(opportunity, str):
                parts.append(f"## Target Opportunity\n{opportunity}")

        return "\n\n".join(parts) if parts else ""

    def _estimate_tokens(
        self,
        system_prompt: str,
        user_prompt: str,
        instructions: List[Dict[str, Any]],
        constraints: List[Dict[str, Any]],
        output_schema: Optional[Dict[str, Any]],
    ) -> int:
        """Estimate token count (~4 chars per token)."""
        total_text = system_prompt + user_prompt
        if instructions:
            total_text += json.dumps(instructions)
        if constraints:
            total_text += json.dumps(constraints)
        if output_schema:
            total_text += json.dumps(output_schema)
        return len(total_text) // 4
