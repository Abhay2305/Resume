"""Instruction Composer — assembles instructions and constraints for prompts.

Replaces and consolidates InstructionBuilder + ConstraintBuilder from
prompt_intelligence/instruction_builder.py with deduplication support.
"""
from typing import Any, Dict, List, Optional

from app.services.prompt_intelligence_v2.templates import PromptTemplates


class InstructionComposer:
    """Composes instructions and constraints for a prompt type.

    Loads base instructions from PromptTemplates, generates contextual
    instructions from gap analysis and recommendations, merges universal
    and type-specific constraints, and deduplicates everything.
    """

    def __init__(self, templates: Optional[PromptTemplates] = None) -> None:
        self._templates = templates or PromptTemplates()

    def compose(
        self,
        prompt_type: str,
        gap_categories: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        knowledge_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """Compose instructions for a prompt type with contextual enrichment.

        Pipeline:
        1. Load type-specific instructions from templates
        2. Append gap-analysis contextual instructions
        3. Append recommendation-based contextual instructions
        4. Append knowledge rule-based instructions
        5. Deduplicate by instruction text

        Args:
            prompt_type: The prompt type key.
            gap_categories: Categories from gap analysis to generate
                contextual instructions for.
            recommendations: Recommendation dicts with 'action',
                'description', 'priority', 'category' keys.
            knowledge_rules: Knowledge rule dicts with 'instruction',
                'section_name', 'source', 'category' keys.

        Returns:
            Deduplicated list of instruction dicts.
        """
        # 1. Load base instructions
        base = self._templates.get_instructions(prompt_type)
        # Fallback to resume_tailoring if type has no specific instructions
        if not base and prompt_type != "resume_tailoring":
            base = self._templates.get_instructions("resume_tailoring")

        instructions = list(base)

        # 2. Gap-analysis contextual instructions
        if gap_categories:
            for category in gap_categories:
                instructions.append({
                    "id": f"INST_CTX_{category.upper()}",
                    "instruction": f"Focus on improving {category} section based on gap analysis.",
                    "priority": "high",
                    "category": category,
                })

        # 3. Recommendation-based contextual instructions (max 5)
        if recommendations:
            for rec in recommendations[:5]:
                instructions.append({
                    "id": f"INST_REC_{rec.get('action', 'unknown').upper()}",
                    "instruction": rec.get("description", ""),
                    "priority": rec.get("priority", "medium"),
                    "category": rec.get("category", "general"),
                })

        # 4. Knowledge rule-based instructions
        if knowledge_rules:
            for rule in knowledge_rules[:15]:  # Cap at 15 rules
                section = rule.get("section_name", "general")
                source = rule.get("source", "unknown")
                instructions.append({
                    "id": f"INST_KR_{section.upper()}_{source.upper()}",
                    "instruction": rule.get("instruction", ""),
                    "priority": "high",
                    "category": rule.get("category", section),
                    "source": source,
                })

        # 5. Deduplicate by instruction text
        return self._deduplicate_instructions(instructions)

    def compose_constraints(
        self,
        prompt_type: str,
    ) -> List[Dict[str, Any]]:
        """Merge universal and type-specific constraints without duplicates.

        Args:
            prompt_type: The prompt type key.

        Returns:
            Merged, deduplicated list of constraint dicts.
        """
        all_constraints = self._templates.get_constraints(prompt_type)
        return self._deduplicate_constraints(all_constraints)

    def compose_text(
        self,
        prompt_type: str,
        gap_categories: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None,
        knowledge_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Compose instructions as a single text block.

        Convenience for callers who need instructions as a string
        rather than structured dicts.
        """
        instructions = self.compose(prompt_type, gap_categories, recommendations, knowledge_rules)
        return "\n".join(
            f"- {inst.get('instruction', '')}" for inst in instructions
            if inst.get("instruction")
        )

    def constraints_text(self, prompt_type: str) -> str:
        """Render constraints as a single text block."""
        constraints = self.compose_constraints(prompt_type)
        return "\n".join(
            f"- {c.get('constraint', '')}" for c in constraints
            if c.get("constraint")
        )

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_instructions(instructions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate instructions by instruction text.

        First occurrence wins. Preserves order.
        """
        seen: set = set()
        result: List[Dict[str, Any]] = []
        for inst in instructions:
            text = inst.get("instruction", "")
            if text and text not in seen:
                seen.add(text)
                result.append(inst)
            elif not text:
                # Keep instructions without text (e.g., structural placeholders)
                result.append(inst)
        return result

    @staticmethod
    def _deduplicate_constraints(constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate constraints by constraint text.

        First occurrence wins. Preserves order.
        """
        seen: set = set()
        result: List[Dict[str, Any]] = []
        for constraint in constraints:
            text = constraint.get("constraint", "")
            if text and text not in seen:
                seen.add(text)
                result.append(constraint)
            elif not text:
                result.append(constraint)
        return result
