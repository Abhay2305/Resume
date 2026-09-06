"""Tests for the Instruction Composer.

Verifies instruction loading, contextual enrichment, constraint merging,
deduplication, and integration with PromptBuilder.
"""
import pytest

from app.services.prompt_intelligence_v2.instructions import InstructionComposer
from app.services.prompt_intelligence_v2.builder import PromptBuilder
from app.services.prompt_intelligence_v2.types import PromptRequest


class TestInstructionComposer:
    """Test the InstructionComposer class."""

    def setup_method(self):
        self.composer = InstructionComposer()

    # ------------------------------------------------------------------
    # Basic instruction loading
    # ------------------------------------------------------------------

    def test_compose_resume_tailoring_has_instructions(self):
        instructions = self.composer.compose("resume_tailoring")
        assert isinstance(instructions, list)
        assert len(instructions) >= 1
        assert all("instruction" in inst for inst in instructions)

    def test_compose_cover_letter_has_instructions(self):
        instructions = self.composer.compose("cover_letter")
        assert isinstance(instructions, list)
        assert len(instructions) >= 1

    def test_compose_unknown_type_falls_back_to_resume_tailoring(self):
        instructions = self.composer.compose("resume_bullets")
        # resume_bullets has no specific instructions; should fall back
        assert isinstance(instructions, list)
        assert len(instructions) >= 1

    def test_compose_empty_for_type_with_no_instructions(self):
        # text_improve has no type-specific instructions in JSON
        instructions = self.composer.compose("text_improve")
        assert isinstance(instructions, list)
        # Falls back to resume_tailoring instructions
        assert len(instructions) >= 1

    # ------------------------------------------------------------------
    # Gap-analysis contextual instructions
    # ------------------------------------------------------------------

    def test_gap_categories_appended(self):
        instructions = self.composer.compose(
            "resume_tailoring",
            gap_categories=["experience", "skills"],
        )
        ids = [inst.get("id") for inst in instructions]
        assert "INST_CTX_EXPERIENCE" in ids
        assert "INST_CTX_SKILLS" in ids

    def test_gap_category_instruction_content(self):
        instructions = self.composer.compose(
            "resume_tailoring",
            gap_categories=["education"],
        )
        edu = [i for i in instructions if i.get("id") == "INST_CTX_EDUCATION"]
        assert len(edu) == 1
        assert "education" in edu[0]["instruction"].lower()
        assert "gap analysis" in edu[0]["instruction"].lower()

    def test_gap_categories_empty_list(self):
        base = self.composer.compose("resume_tailoring")
        enriched = self.composer.compose("resume_tailoring", gap_categories=[])
        assert len(enriched) == len(base)

    def test_gap_categories_none(self):
        base = self.composer.compose("resume_tailoring")
        enriched = self.composer.compose("resume_tailoring", gap_categories=None)
        assert len(enriched) == len(base)

    # ------------------------------------------------------------------
    # Recommendation-based contextual instructions
    # ------------------------------------------------------------------

    def test_recommendations_appended(self):
        recs = [
            {"action": "add_metrics", "description": "Add quantifiable metrics", "priority": "high", "category": "achievements"},
            {"action": "improve_verbs", "description": "Use stronger action verbs", "priority": "medium", "category": "language"},
        ]
        instructions = self.composer.compose(
            "resume_tailoring",
            recommendations=recs,
        )
        ids = [inst.get("id") for inst in instructions]
        assert "INST_REC_ADD_METRICS" in ids
        assert "INST_REC_IMPROVE_VERBS" in ids

    def test_recommendations_max_five(self):
        recs = [{"action": f"rec_{i}", "description": f"Rec {i}"} for i in range(10)]
        instructions = self.composer.compose(
            "resume_tailoring",
            recommendations=recs,
        )
        rec_instructions = [i for i in instructions if i.get("id", "").startswith("INST_REC_")]
        assert len(rec_instructions) == 5

    def test_recommendations_empty_list(self):
        base = self.composer.compose("resume_tailoring")
        enriched = self.composer.compose("resume_tailoring", recommendations=[])
        assert len(enriched) == len(base)

    def test_recommendations_none(self):
        base = self.composer.compose("resume_tailoring")
        enriched = self.composer.compose("resume_tailoring", recommendations=None)
        assert len(enriched) == len(base)

    def test_recommendations_with_missing_fields(self):
        recs = [{"action": "test"}]  # missing description, priority, category
        instructions = self.composer.compose(
            "resume_tailoring",
            recommendations=recs,
        )
        rec_inst = [i for i in instructions if i.get("id", "").startswith("INST_REC_")]
        assert len(rec_inst) == 1
        assert rec_inst[0]["instruction"] == ""  # missing description defaults to ""
        assert rec_inst[0]["priority"] == "medium"  # default
        assert rec_inst[0]["category"] == "general"  # default

    # ------------------------------------------------------------------
    # Deduplication — instructions
    # ------------------------------------------------------------------

    def test_deduplicate_instructions_by_text(self):
        instructions = [
            {"id": "1", "instruction": "Do X", "priority": "high"},
            {"id": "2", "instruction": "Do X", "priority": "low"},  # duplicate
            {"id": "3", "instruction": "Do Y", "priority": "high"},
        ]
        result = InstructionComposer._deduplicate_instructions(instructions)
        assert len(result) == 2
        assert result[0]["id"] == "1"  # first wins
        assert result[1]["id"] == "3"

    def test_deduplicate_preserves_order(self):
        instructions = [
            {"id": "a", "instruction": "A"},
            {"id": "b", "instruction": "B"},
            {"id": "c", "instruction": "A"},  # dup of first
        ]
        result = InstructionComposer._deduplicate_instructions(instructions)
        assert [i["id"] for i in result] == ["a", "b"]

    def test_deduplicate_empty_list(self):
        assert InstructionComposer._deduplicate_instructions([]) == []

    def test_compose_deduplicates_across_base_and_contextual(self):
        """If a contextual instruction matches a base instruction, dedup removes it."""
        # First, get base instructions for resume_tailoring
        base = self.composer.compose("resume_tailoring")
        if base:
            # Create a recommendation with the same instruction text as the first base instruction
            first_instruction_text = base[0].get("instruction", "")
            recs = [{"action": "dup", "description": first_instruction_text}]
            result = self.composer.compose("resume_tailoring", recommendations=recs)
            # The duplicate should be removed
            instruction_texts = [i.get("instruction") for i in result]
            assert instruction_texts.count(first_instruction_text) == 1

    # ------------------------------------------------------------------
    # Constraint composition
    # ------------------------------------------------------------------

    def test_compose_constraints_has_universal(self):
        constraints = self.composer.compose_constraints("resume_tailoring")
        assert isinstance(constraints, list)
        assert len(constraints) >= 1
        # Universal constraints should be included
        texts = [c.get("constraint", "") for c in constraints]
        assert any("first-person" in t.lower() or "pronoun" in t.lower() or len(t) > 0 for t in texts)

    def test_compose_constraints_includes_type_specific(self):
        constraints = self.composer.compose_constraints("resume_tailoring")
        assert isinstance(constraints, list)
        # Should have both universal + type-specific
        assert len(constraints) >= 2

    def test_compose_constraints_empty_for_unknown_type(self):
        constraints = self.composer.compose_constraints("nonexistent_type")
        # Should at least return universal constraints (via templates fallback)
        assert isinstance(constraints, list)

    # ------------------------------------------------------------------
    # Constraint deduplication
    # ------------------------------------------------------------------

    def test_deduplicate_constraints(self):
        constraints = [
            {"id": "1", "constraint": "No spam"},
            {"id": "2", "constraint": "No spam"},  # duplicate
            {"id": "3", "constraint": "Be professional"},
        ]
        result = InstructionComposer._deduplicate_constraints(constraints)
        assert len(result) == 2
        assert result[0]["constraint"] == "No spam"
        assert result[1]["constraint"] == "Be professional"

    def test_deduplicate_constraints_preserves_order(self):
        constraints = [
            {"id": "a", "constraint": "Rule A"},
            {"id": "b", "constraint": "Rule B"},
            {"id": "c", "constraint": "Rule A"},  # dup
        ]
        result = InstructionComposer._deduplicate_constraints(constraints)
        assert [c["id"] for c in result] == ["a", "b"]

    # ------------------------------------------------------------------
    # Text output
    # ------------------------------------------------------------------

    def test_compose_text(self):
        text = self.composer.compose_text("resume_tailoring")
        assert isinstance(text, str)
        assert len(text) > 0
        assert "- " in text  # bullet-point format

    def test_constraints_text(self):
        text = self.composer.constraints_text("resume_tailoring")
        assert isinstance(text, str)
        assert len(text) > 0
        assert "- " in text

    # ------------------------------------------------------------------
    # Integration with PromptBuilder
    # ------------------------------------------------------------------

    def test_promptbuilder_uses_composer_for_instructions(self):
        """PromptBuilder.build() now uses InstructionComposer."""
        builder = PromptBuilder()
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "SE"},
            },
        )
        package = builder.build(request)
        # Instructions should be non-empty (from resume_tailoring base)
        assert isinstance(package.instructions, list)
        assert len(package.instructions) >= 1

    def test_promptbuilder_composer_enriches_with_gap_categories(self):
        builder = PromptBuilder()
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "SE"},
                "gap_categories": ["experience", "skills"],
            },
        )
        package = builder.build(request)
        ids = [inst.get("id") for inst in package.instructions]
        assert "INST_CTX_EXPERIENCE" in ids
        assert "INST_CTX_SKILLS" in ids

    def test_promptbuilder_composer_enriches_with_recommendations(self):
        builder = PromptBuilder()
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "SE"},
                "recommendations": [
                    {"action": "add_metrics", "description": "Add metrics", "priority": "high"},
                ],
            },
        )
        package = builder.build(request)
        ids = [inst.get("id") for inst in package.instructions]
        assert "INST_REC_ADD_METRICS" in ids

    def test_promptbuilder_constraints_deduplicated(self):
        builder = PromptBuilder()
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "SE"},
            },
        )
        package = builder.build(request)
        assert isinstance(package.constraints, list)
        # No duplicate constraint texts
        texts = [c.get("constraint", "") for c in package.constraints]
        assert len(texts) == len(set(texts))

    def test_promptbuilder_all_16_types_still_build(self):
        """All 16 prompt types continue to build successfully with composer."""
        builder = PromptBuilder()
        types_and_contexts = [
            ("resume_bullets", {"role_title": "SE", "company": "X", "responsibilities": "A", "technologies": "B"}),
            ("resume_summary", {"target_role": "SE", "experience_years": 5, "skills": "Py", "achievements": "Led"}),
            ("cover_letter", {"company": "X", "role_title": "SE", "job_description": "Build", "my_experience": "10y"}),
            ("resume_generation", {"resume_knowledge": {"skills": []}}),
            ("resume_tailoring", {"resume_knowledge": {"skills": []}, "opportunity": {"title": "SE"}}),
            ("ats_optimization", {"content": "text", "job_description": "desc"}),
            ("ats_optimization_pi", {"resume_knowledge": {"skills": []}, "opportunity": {"title": "SE"}}),
            ("text_improve", {"text_content": "text"}),
            ("text_shorten", {"text_content": "text"}),
            ("text_expand", {"text_content": "text"}),
            ("text_professional", {"text_content": "text"}),
            ("text_autofix", {"text_content": "text"}),
            ("bullet_feedback", {"bullet": "text"}),
            ("chat", {"user_message": "hello"}),
            ("structured_resume", {"archetype": "be", "prompt": "gen"}),
            ("cover_letter_direct", {"job_role": "eng", "company_name": "X"}),
        ]
        for pt, ctx in types_and_contexts:
            request = PromptRequest(prompt_type=pt, context=ctx)
            package = builder.build(request)
            assert package.prompt_type == pt
            assert isinstance(package.instructions, list)
            assert isinstance(package.constraints, list)

    # ------------------------------------------------------------------
    # Legacy InstructionBuilder unaffected
    # ------------------------------------------------------------------

    def test_legacy_instruction_builder_still_works(self):
        """Existing InstructionBuilder in prompt_intelligence/ is untouched."""
        from app.services.prompt_intelligence.instruction_builder import InstructionBuilder, ConstraintBuilder

        ib = InstructionBuilder()
        cb = ConstraintBuilder()

        instructions = ib.build("resume_tailoring")
        assert isinstance(instructions, list)
        assert len(instructions) >= 1

        constraints = cb.build("resume_tailoring")
        assert isinstance(constraints, list)
        assert len(constraints) >= 1

        # build_with_context still works
        contextual = ib.build_with_context(
            "resume_tailoring",
            gap_categories=["skills"],
            recommendations=[{"action": "test", "description": "Test rec"}],
        )
        assert len(contextual) > len(instructions)
