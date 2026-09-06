"""Prompt Intelligence Snapshot/Regression Tests.

Detects unintended prompt drift by comparing build output against stored
snapshots for all 16 prompt types. When a prompt intentionally changes,
update the snapshot with the new expected output.

Task 3.2 — SPEC-002 Prompt Intelligence Engine.
"""
import pytest

from app.services.prompt_intelligence_v2.builder import PromptBuilder
from app.services.prompt_intelligence_v2.registry import create_default_registry
from app.services.prompt_intelligence_v2.types import PromptRequest, PromptPackage


# ------------------------------------------------------------------
# Canonical input contexts for all 16 prompt types
# ------------------------------------------------------------------

CANONICAL_CONTEXTS = {
    "resume_bullets": {
        "role_title": "Software Engineer",
        "company": "Acme Corp",
        "responsibilities": "Designed and implemented microservices architecture",
        "technologies": "Python, FastAPI, PostgreSQL, Docker",
        "achievements": "Reduced API latency by 40%",
        "num_bullets": 5,
    },
    "resume_summary": {
        "target_role": "Senior Software Engineer",
        "experience_years": 8,
        "skills": "Python, Go, Kubernetes, AWS",
        "achievements": "Led migration of monolith to microservices serving 10M requests/day",
    },
    "cover_letter": {
        "company": "TechCorp",
        "role_title": "Staff Engineer",
        "job_description": "Lead the backend team to build scalable distributed systems",
        "my_experience": "10 years building high-throughput distributed systems at scale",
    },
    "resume_generation": {
        "resume_knowledge": {
            "skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience": [
                {"role": "Software Engineer", "company": "Acme Corp", "years": 5}
            ],
            "summary": "Backend engineer specializing in high-performance APIs",
        },
    },
    "resume_tailoring": {
        "resume_knowledge": {
            "summary": "Backend engineer specializing in high-performance APIs",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "experience": [
                {"role": "Software Engineer", "company": "Acme Corp", "years": 5}
            ],
        },
        "opportunity": {
            "responsibilities": [
                "Build and maintain microservices",
                "Optimize system performance",
                "Mentor junior engineers",
            ],
        },
        "gap_analysis": {
            "overall_match_score": 78,
            "matching_skills": ["Python", "FastAPI", "PostgreSQL"],
            "missing_skills": ["Kubernetes", "Terraform"],
        },
    },
    "ats_optimization": {
        "content": "Experienced software engineer with expertise in Python and cloud infrastructure",
        "job_description": "Senior Python Developer with AWS and Docker experience",
    },
    "ats_optimization_pi": {
        "resume_knowledge": {
            "summary": "Backend engineer",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        },
        "opportunity": {
            "responsibilities": ["Build microservices", "Optimize performance"],
        },
    },
    "text_improve": {
        "text_content": "I built some APIs that work pretty well and handle lots of requests",
    },
    "text_shorten": {
        "text_content": "I was responsible for the design and implementation of various backend services that handled a significant volume of requests on a daily basis",
    },
    "text_expand": {
        "text_content": "Built APIs",
    },
    "text_professional": {
        "text_content": "I made the code better and fixed a bunch of bugs",
    },
    "text_autofix": {
        "text_content": "i did the api development work and it was really good",
    },
    "bullet_feedback": {
        "bullet": "Responsible for handling various backend tasks and responsibilities",
    },
    "chat": {
        "user_message": "What skills should I highlight for a senior backend role?",
    },
    "structured_resume": {
        "archetype": "experienced",
        "prompt": "John Doe, Senior Software Engineer. 8 years building distributed systems. Skills: Python, Go, Kubernetes, AWS.",
    },
    "cover_letter_direct": {
        "job_role": "Senior Backend Engineer",
        "company_name": "TechCorp",
        "company_summary": "Leading fintech company building next-gen payment infrastructure",
        "role_summary": "Design and build high-throughput payment processing microservices",
        "requirements": "5+ years backend development, distributed systems experience",
    },
}


# ------------------------------------------------------------------
# Snapshot comparison helpers
# ------------------------------------------------------------------

def _normalize_instructions(instructions):
    """Sort instructions by id for deterministic comparison."""
    return sorted(instructions, key=lambda x: x.get("id", ""))


def _normalize_constraints(constraints):
    """Sort constraints by id for deterministic comparison."""
    return sorted(constraints, key=lambda x: x.get("id", ""))


def assert_snapshot_matches(package, expected):
    """Compare a PromptPackage against expected snapshot values."""
    assert package.system_prompt == expected["system_prompt"], (
        f"system_prompt changed for {package.prompt_type}. "
        f"Update snapshot if intentional."
    )
    assert package.user_prompt == expected["user_prompt"], (
        f"user_prompt changed for {package.prompt_type}. "
        f"Update snapshot if intentional."
    )
    assert _normalize_instructions(package.instructions) == _normalize_instructions(expected["instructions"]), (
        f"instructions changed for {package.prompt_type}. "
        f"Update snapshot if intentional."
    )
    assert _normalize_constraints(package.constraints) == _normalize_constraints(expected["constraints"]), (
        f"constraints changed for {package.prompt_type}. "
        f"Update snapshot if intentional."
    )
    assert package.output_schema == expected["output_schema"], (
        f"output_schema changed for {package.prompt_type}. "
        f"Update snapshot if intentional."
    )


# ------------------------------------------------------------------
# Build snapshots for all 16 types
# ------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_snapshots():
    """Build all 16 prompt types once and store as snapshots."""
    builder = PromptBuilder()
    snapshots = {}
    for prompt_type, context in CANONICAL_CONTEXTS.items():
        request = PromptRequest(prompt_type=prompt_type, context=context)
        package = builder.build(request)
        snapshots[prompt_type] = {
            "system_prompt": package.system_prompt,
            "user_prompt": package.user_prompt,
            "instructions": package.instructions,
            "constraints": package.constraints,
            "output_schema": package.output_schema,
        }
    return snapshots


# ------------------------------------------------------------------
# Snapshot tests for each prompt type
# ------------------------------------------------------------------

class TestSnapshotResumeBullets:
    """Snapshot test for resume_bullets type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_bullets", context=CANONICAL_CONTEXTS["resume_bullets"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["resume_bullets"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_bullets", context=CANONICAL_CONTEXTS["resume_bullets"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["resume_bullets"]["user_prompt"]

    def test_instructions_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_bullets", context=CANONICAL_CONTEXTS["resume_bullets"])
        package = builder.build(request)
        assert _normalize_instructions(package.instructions) == _normalize_instructions(all_snapshots["resume_bullets"]["instructions"])

    def test_constraints_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_bullets", context=CANONICAL_CONTEXTS["resume_bullets"])
        package = builder.build(request)
        assert _normalize_constraints(package.constraints) == _normalize_constraints(all_snapshots["resume_bullets"]["constraints"])


class TestSnapshotResumeSummary:
    """Snapshot test for resume_summary type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_summary", context=CANONICAL_CONTEXTS["resume_summary"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["resume_summary"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_summary", context=CANONICAL_CONTEXTS["resume_summary"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["resume_summary"]["user_prompt"]


class TestSnapshotCoverLetter:
    """Snapshot test for cover_letter type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="cover_letter", context=CANONICAL_CONTEXTS["cover_letter"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["cover_letter"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="cover_letter", context=CANONICAL_CONTEXTS["cover_letter"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["cover_letter"]["user_prompt"]


class TestSnapshotResumeGeneration:
    """Snapshot test for resume_generation type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_generation", context=CANONICAL_CONTEXTS["resume_generation"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["resume_generation"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_generation", context=CANONICAL_CONTEXTS["resume_generation"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["resume_generation"]["user_prompt"]


class TestSnapshotResumeTailoring:
    """Snapshot test for resume_tailoring type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_tailoring", context=CANONICAL_CONTEXTS["resume_tailoring"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["resume_tailoring"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_tailoring", context=CANONICAL_CONTEXTS["resume_tailoring"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["resume_tailoring"]["user_prompt"]

    def test_instructions_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_tailoring", context=CANONICAL_CONTEXTS["resume_tailoring"])
        package = builder.build(request)
        assert _normalize_instructions(package.instructions) == _normalize_instructions(all_snapshots["resume_tailoring"]["instructions"])

    def test_output_schema_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="resume_tailoring", context=CANONICAL_CONTEXTS["resume_tailoring"])
        package = builder.build(request)
        assert package.output_schema == all_snapshots["resume_tailoring"]["output_schema"]


class TestSnapshotAtsOptimization:
    """Snapshot test for ats_optimization type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="ats_optimization", context=CANONICAL_CONTEXTS["ats_optimization"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["ats_optimization"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="ats_optimization", context=CANONICAL_CONTEXTS["ats_optimization"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["ats_optimization"]["user_prompt"]


class TestSnapshotAtsOptimizationPi:
    """Snapshot test for ats_optimization_pi type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="ats_optimization_pi", context=CANONICAL_CONTEXTS["ats_optimization_pi"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["ats_optimization_pi"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="ats_optimization_pi", context=CANONICAL_CONTEXTS["ats_optimization_pi"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["ats_optimization_pi"]["user_prompt"]


class TestSnapshotTextImprove:
    """Snapshot test for text_improve type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_improve", context=CANONICAL_CONTEXTS["text_improve"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["text_improve"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_improve", context=CANONICAL_CONTEXTS["text_improve"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["text_improve"]["user_prompt"]


class TestSnapshotTextShorten:
    """Snapshot test for text_shorten type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_shorten", context=CANONICAL_CONTEXTS["text_shorten"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["text_shorten"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_shorten", context=CANONICAL_CONTEXTS["text_shorten"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["text_shorten"]["user_prompt"]


class TestSnapshotTextExpand:
    """Snapshot test for text_expand type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_expand", context=CANONICAL_CONTEXTS["text_expand"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["text_expand"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_expand", context=CANONICAL_CONTEXTS["text_expand"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["text_expand"]["user_prompt"]


class TestSnapshotTextProfessional:
    """Snapshot test for text_professional type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_professional", context=CANONICAL_CONTEXTS["text_professional"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["text_professional"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_professional", context=CANONICAL_CONTEXTS["text_professional"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["text_professional"]["user_prompt"]


class TestSnapshotTextAutofix:
    """Snapshot test for text_autofix type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_autofix", context=CANONICAL_CONTEXTS["text_autofix"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["text_autofix"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="text_autofix", context=CANONICAL_CONTEXTS["text_autofix"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["text_autofix"]["user_prompt"]


class TestSnapshotBulletFeedback:
    """Snapshot test for bullet_feedback type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="bullet_feedback", context=CANONICAL_CONTEXTS["bullet_feedback"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["bullet_feedback"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="bullet_feedback", context=CANONICAL_CONTEXTS["bullet_feedback"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["bullet_feedback"]["user_prompt"]


class TestSnapshotChat:
    """Snapshot test for chat type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="chat", context=CANONICAL_CONTEXTS["chat"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["chat"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="chat", context=CANONICAL_CONTEXTS["chat"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["chat"]["user_prompt"]


class TestSnapshotStructuredResume:
    """Snapshot test for structured_resume type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="structured_resume", context=CANONICAL_CONTEXTS["structured_resume"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["structured_resume"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="structured_resume", context=CANONICAL_CONTEXTS["structured_resume"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["structured_resume"]["user_prompt"]


class TestSnapshotCoverLetterDirect:
    """Snapshot test for cover_letter_direct type."""

    def test_system_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="cover_letter_direct", context=CANONICAL_CONTEXTS["cover_letter_direct"])
        package = builder.build(request)
        assert package.system_prompt == all_snapshots["cover_letter_direct"]["system_prompt"]

    def test_user_prompt_stable(self, all_snapshots):
        builder = PromptBuilder()
        request = PromptRequest(prompt_type="cover_letter_direct", context=CANONICAL_CONTEXTS["cover_letter_direct"])
        package = builder.build(request)
        assert package.user_prompt == all_snapshots["cover_letter_direct"]["user_prompt"]


# ------------------------------------------------------------------
# Cross-cutting snapshot tests
# ------------------------------------------------------------------

class TestSnapshotCrossCutting:
    """Cross-cutting tests that verify snapshot behavior across all types."""

    def test_all_types_have_snapshots(self, all_snapshots):
        """Every registered type must have a snapshot entry."""
        registry = create_default_registry()
        all_types = registry.list_types()
        for prompt_type in all_types:
            assert prompt_type in all_snapshots, f"Missing snapshot for {prompt_type}"

    def test_all_snapshots_build_successfully(self):
        """Every snapshot can be built without error."""
        builder = PromptBuilder()
        for prompt_type, context in CANONICAL_CONTEXTS.items():
            request = PromptRequest(prompt_type=prompt_type, context=context)
            package = builder.build(request)
            assert isinstance(package, PromptPackage), f"Failed to build {prompt_type}"

    def test_message_format_for_all_types(self, all_snapshots):
        """Messages are always [system, user] with correct role keys."""
        builder = PromptBuilder()
        for prompt_type, context in CANONICAL_CONTEXTS.items():
            request = PromptRequest(prompt_type=prompt_type, context=context)
            package = builder.build(request)
            assert len(package.messages) == 2, f"{prompt_type} should have 2 messages"
            assert package.messages[0]["role"] == "system", f"{prompt_type} first message should be system"
            assert package.messages[1]["role"] == "user", f"{prompt_type} second message should be user"
            assert "content" in package.messages[0], f"{prompt_type} system message missing content"
            assert "content" in package.messages[1], f"{prompt_type} user message missing content"

    def test_system_prompt_nonempty_for_all_types(self, all_snapshots):
        """System prompt is non-empty for all types."""
        for prompt_type, snapshot in all_snapshots.items():
            assert snapshot["system_prompt"], f"{prompt_type} has empty system_prompt"

    def test_user_prompt_nonempty_for_all_types(self, all_snapshots):
        """User prompt is non-empty for all types."""
        for prompt_type, snapshot in all_snapshots.items():
            assert snapshot["user_prompt"], f"{prompt_type} has empty user_prompt"

    def test_full_snapshot_match_for_all_types(self, all_snapshots):
        """Full snapshot comparison for all 16 types."""
        builder = PromptBuilder()
        for prompt_type, context in CANONICAL_CONTEXTS.items():
            request = PromptRequest(prompt_type=prompt_type, context=context)
            package = builder.build(request)
            assert_snapshot_matches(package, all_snapshots[prompt_type])
