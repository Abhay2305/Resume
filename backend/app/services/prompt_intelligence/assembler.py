"""Prompt Assembler.

Assembles complete prompt packages from all components.
"""
import json
from typing import Any, Dict, List, Optional

from app.services.prompt_intelligence.context_builders import (
    GapContextBuilder,
    KnowledgeContextBuilder,
    OpportunityContextBuilder,
    ResumeContextBuilder,
)
from app.services.prompt_intelligence.instruction_builder import ConstraintBuilder, InstructionBuilder
from app.services.prompt_intelligence.output_schema_builder import OutputSchemaBuilder
from app.services.prompt_intelligence.system_prompt_builder import SystemPromptBuilder


class PromptAssembler:
    """Assembles complete prompt packages."""

    def __init__(self):
        self.system_builder = SystemPromptBuilder()
        self.resume_builder = ResumeContextBuilder()
        self.opportunity_builder = OpportunityContextBuilder()
        self.gap_builder = GapContextBuilder()
        self.knowledge_builder = KnowledgeContextBuilder()
        self.instruction_builder = InstructionBuilder()
        self.constraint_builder = ConstraintBuilder()
        self.output_builder = OutputSchemaBuilder()

    def assemble(
        self,
        prompt_type: str,
        resume_knowledge: Optional[Dict[str, Any]] = None,
        opportunity_entities: Optional[List[Dict[str, Any]]] = None,
        opportunity_parsed_data: Optional[Dict[str, Any]] = None,
        gap_analysis_data: Optional[Dict[str, Any]] = None,
        knowledge_context_data: Optional[Dict[str, Any]] = None,
        template_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        system_prompt = self.system_builder.build(prompt_type)
        resume_ctx = self.resume_builder.build(resume_knowledge or {})
        opportunity_ctx = self.opportunity_builder.build(opportunity_entities or [], opportunity_parsed_data)
        gap_ctx = self.gap_builder.build(gap_analysis_data or {})
        knowledge_ctx = self.knowledge_builder.build(knowledge_context_data or {})
        instructions = self.instruction_builder.build(prompt_type)
        constraints = self.constraint_builder.build(prompt_type)
        output_schema = self.output_builder.build(prompt_type)

        return {
            "system_prompt": system_prompt,
            "resume_context": resume_ctx,
            "opportunity_context": opportunity_ctx,
            "gap_context": gap_ctx,
            "knowledge_context": knowledge_ctx,
            "instructions": instructions,
            "constraints": constraints,
            "output_schema": output_schema,
            "metadata": {
                "prompt_type": prompt_type,
                "template_id": template_id,
                "total_sections": 7,
            },
        }

    def estimate_tokens(self, package: Dict[str, Any]) -> int:
        total_text = package.get("system_prompt", "")
        for key in ["resume_context", "opportunity_context", "gap_context", "knowledge_context"]:
            ctx = package.get(key, {})
            if isinstance(ctx, dict):
                total_text += json.dumps(ctx)
        for key in ["instructions", "constraints"]:
            items = package.get(key, [])
            if isinstance(items, list):
                total_text += json.dumps(items)
        schema = package.get("output_schema", {})
        total_text += json.dumps(schema)
        return len(total_text) // 4
