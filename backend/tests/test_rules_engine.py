"""Comprehensive tests for the Rules Engine.

Tests all 9 rules, edge cases, score calculation, and integration.
Covers: bullet_starts_with_verb, no_weak_verbs, mentions_technology,
has_quantifiable_impact, no_vague_phrases, no_generic_phrases,
bullet_concise, no_special_characters, no_first_person.
"""
import pytest

from app.services.rules_engine import (
    GENERIC_PHRASES,
    STRONG_ACTION_VERBS,
    VAGUE_PHRASES,
    WEAK_VERBS,
    RuleCategory,
    RulesEngine,
    RuleViolation,
    Severity,
    ValidationResult,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def engine():
    """Create a fresh RulesEngine instance."""
    return RulesEngine()


# ============================================================================
# ValidationResult Tests
# ============================================================================

class TestValidationResult:
    def test_initial_state(self):
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.violations == []
        assert result.score == 100.0
        assert result.passed_rules == 0
        assert result.failed_rules == 0

    def test_add_error_violation(self):
        result = ValidationResult(is_valid=True)
        violation = RuleViolation(
            rule_name="test_rule",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.ERROR,
            message="Test error",
        )
        result.add_violation(violation)
        assert result.is_valid is False
        assert result.score == 90.0
        assert len(result.violations) == 1

    def test_add_warning_violation(self):
        result = ValidationResult(is_valid=True)
        violation = RuleViolation(
            rule_name="test_rule",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.WARNING,
            message="Test warning",
        )
        result.add_violation(violation)
        assert result.is_valid is True
        assert result.score == 97.0

    def test_add_info_violation(self):
        result = ValidationResult(is_valid=True)
        violation = RuleViolation(
            rule_name="test_rule",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.INFO,
            message="Test info",
        )
        result.add_violation(violation)
        assert result.is_valid is True
        assert result.score == 99.0

    def test_score_decreases_with_violations(self):
        result = ValidationResult(is_valid=True, score=5.0)
        for _ in range(3):
            violation = RuleViolation(
                rule_name="test",
                category=RuleCategory.ACTION_VERB,
                severity=Severity.WARNING,
                message="test",
            )
            result.add_violation(violation)
        assert result.score < 5.0
        # Note: ValidationResult does NOT clamp score to 0.
        # Score can go negative when many violations accumulate.

    def test_to_dict(self):
        result = ValidationResult(is_valid=True, score=85.0)
        result.passed_rules = 5
        result.failed_rules = 2
        violation = RuleViolation(
            rule_name="test_rule",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.WARNING,
            message="Test message",
            field_path="bullets[0]",
            suggestion="Fix this",
        )
        result.add_violation(violation)
        d = result.to_dict()
        assert d["is_valid"] is True
        assert d["score"] == 82.0
        assert len(d["violations"]) == 1
        assert d["violations"][0]["rule"] == "test_rule"
        assert d["violations"][0]["category"] == "action_verb"
        assert d["violations"][0]["severity"] == "warning"
        assert d["passed_rules"] == 5
        assert d["failed_rules"] == 2


# ============================================================================
# Strong Action Verbs Tests
# ============================================================================

class TestStrongActionVerbs:
    def test_developed_is_strong(self):
        assert "developed" in STRONG_ACTION_VERBS

    def test_implemented_is_strong(self):
        assert "implemented" in STRONG_ACTION_VERBS

    def test_led_is_strong(self):
        assert "led" in STRONG_ACTION_VERBS

    def test_managed_is_strong(self):
        assert "managed" in STRONG_ACTION_VERBS

    def test_optimized_is_strong(self):
        assert "optimized" in STRONG_ACTION_VERBS

    def test_reduced_is_strong(self):
        assert "reduced" in STRONG_ACTION_VERBS

    def test_increased_is_strong(self):
        assert "increased" in STRONG_ACTION_VERBS

    def test_improved_is_strong(self):
        assert "improved" in STRONG_ACTION_VERBS

    def test_designed_is_strong(self):
        assert "designed" in STRONG_ACTION_VERBS

    def test_architected_is_strong(self):
        assert "architected" in STRONG_ACTION_VERBS


# ============================================================================
# Weak Verbs Tests
# ============================================================================

class TestWeakVerbs:
    def test_helped_is_weak(self):
        assert "helped" in WEAK_VERBS

    def test_worked_is_weak(self):
        assert "worked" in WEAK_VERBS

    def test_responsible_for_is_weak(self):
        assert "responsible for" in WEAK_VERBS

    def test_assisted_with_is_weak(self):
        assert "assisted with" in WEAK_VERBS

    def test_involved_in_is_weak(self):
        assert "involved in" in WEAK_VERBS


# ============================================================================
# Rule: bullet_starts_with_verb Tests
# ============================================================================

class TestBulletStartsWithVerb:
    def test_starts_with_developed(self, engine):
        result = engine.validate_bullet("Developed a new system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 0

    def test_starts_with_implemented(self, engine):
        result = engine.validate_bullet("Implemented feature X")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 0

    def test_starts_with_weak_verb(self, engine):
        result = engine.validate_bullet("Helped the team with project")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR

    def test_starts_with_responsible_for(self, engine):
        result = engine.validate_bullet("Responsible for managing team")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_single_word_verb(self, engine):
        result = engine.validate_bullet("Built")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 0

    def test_starts_with_number(self, engine):
        result = engine.validate_bullet("5 years of experience")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_article(self, engine):
        result = engine.validate_bullet("The project was successful")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_case_insensitive(self, engine):
        result = engine.validate_bullet("DEVELOPED new system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 0

    def test_starts_with_leading_dash_fails_verb_check(self, engine):
        # The engine strips trailing punctuation from the first word,
        # but leading punctuation like '-' is not stripped before splitting.
        # "- Developed" splits to ["-", "Developed", ...] and "-" is not a verb.
        result = engine.validate_bullet("- Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_leading_comma_fails_verb_check(self, engine):
        result = engine.validate_bullet(", Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_leading_period_fails_verb_check(self, engine):
        result = engine.validate_bullet(". Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_leading_colon_fails_verb_check(self, engine):
        result = engine.validate_bullet(": Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_leading_semicolon_fails_verb_check(self, engine):
        result = engine.validate_bullet("; Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_leading_exclamation_fails_verb_check(self, engine):
        result = engine.validate_bullet("! Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_leading_question_mark_fails_verb_check(self, engine):
        result = engine.validate_bullet("? Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_long_bullet(self, engine):
        bullet = "Designed and implemented a comprehensive microservices architecture " * 5
        result = engine.validate_bullet(bullet)
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 0

    def test_special_characters_in_verb(self, engine):
        result = engine.validate_bullet("C++ development")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_starts_with_we(self, engine):
        result = engine.validate_bullet("We built the system")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1


# ============================================================================
# Rule: no_weak_verbs Tests
# ============================================================================

class TestNoWeakVerbs:
    def test_no_weak_verbs(self, engine):
        result = engine.validate_bullet("Developed new system")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 0

    def test_contains_helped(self, engine):
        result = engine.validate_bullet("Developed system that helped users")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_contains_worked(self, engine):
        result = engine.validate_bullet("Developed system that worked well")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_contains_responsible_for(self, engine):
        result = engine.validate_bullet("Responsible for developing systems")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_contains_assisted_with(self, engine):
        result = engine.validate_bullet("Developed system, assisted with deployment")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_contains_involved_in(self, engine):
        result = engine.validate_bullet("Developed system, involved in testing")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_case_insensitive(self, engine):
        result = engine.validate_bullet("DEVELOPED system that HELPED users")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_multiple_weak_verbs_returns_first(self, engine):
        # The engine's _check_no_weak_verbs returns on the first weak verb found.
        result = engine.validate_bullet("Helped and worked on the project")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "no_weak_verbs"]
        assert len(violations) == 0


# ============================================================================
# Rule: mentions_technology Tests
# ============================================================================

class TestMentionsTechnology:
    def test_mentions_python(self, engine):
        result = engine.validate_bullet("Built Python application")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 0

    def test_mentions_javascript(self, engine):
        result = engine.validate_bullet("Developed JavaScript frontend")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 0

    def test_mentions_aws(self, engine):
        result = engine.validate_bullet("Deployed to AWS cloud")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 0

    def test_mentions_docker(self, engine):
        result = engine.validate_bullet("Containerized with Docker")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 0

    def test_mentions_react(self, engine):
        result = engine.validate_bullet("Built React component")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 0

    def test_no_technology_mentioned(self, engine):
        result = engine.validate_bullet("Improved team productivity")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 1

    def test_case_insensitive(self, engine):
        result = engine.validate_bullet("Built PYTHON application")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 0

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "mentions_technology"]
        assert len(violations) == 1


# ============================================================================
# Rule: has_quantifiable_impact Tests
# ============================================================================

class TestHasQuantifiableImpact:
    def test_has_percentage(self, engine):
        result = engine.validate_bullet("Improved performance by 25%")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_dollar_amount(self, engine):
        result = engine.validate_bullet("Saved $50,000 in costs")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_multiplier(self, engine):
        result = engine.validate_bullet("Increased speed 3x")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_users(self, engine):
        result = engine.validate_bullet("Served 10000 users")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_reduced_by(self, engine):
        result = engine.validate_bullet("Reduced errors by 40%")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_increased_by(self, engine):
        result = engine.validate_bullet("Increased revenue by 20%")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_improved_by(self, engine):
        result = engine.validate_bullet("Improved efficiency by 35%")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_saved(self, engine):
        result = engine.validate_bullet("Saved 100 hours of manual work")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_has_requests(self, engine):
        result = engine.validate_bullet("Handled 5000 requests per second")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 0

    def test_no_quantifiable_impact(self, engine):
        result = engine.validate_bullet("Improved the system")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "has_quantifiable_impact"]
        assert len(violations) == 1


# ============================================================================
# Rule: no_vague_phrases Tests
# ============================================================================

class TestNoVaguePhrases:
    def test_no_vague_phrases(self, engine):
        result = engine.validate_bullet("Developed system serving 10000 users")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 0

    def test_contains_team_player(self, engine):
        result = engine.validate_bullet("Team player who developed systems")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_contains_self_starter(self, engine):
        result = engine.validate_bullet("Self-starter who built projects")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_contains_results_driven(self, engine):
        result = engine.validate_bullet("Results-driven developer")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_contains_detail_oriented(self, engine):
        result = engine.validate_bullet("Detail-oriented engineer")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_contains_synergy(self, engine):
        result = engine.validate_bullet("Created synergy between teams")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_case_insensitive(self, engine):
        result = engine.validate_bullet("TEAM PLAYER who developed systems")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_multiple_vague_phrases_returns_first(self, engine):
        # The engine's _check_no_vague_phrases returns on the first match found.
        result = engine.validate_bullet("Team player, self-starter, results-driven")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "no_vague_phrases"]
        assert len(violations) == 0


# ============================================================================
# Rule: no_generic_phrases Tests
# ============================================================================

class TestNoGenericPhrases:
    def test_no_generic_phrases(self, engine):
        result = engine.validate_bullet("Developed microservices architecture")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 0

    def test_contains_various_tasks(self, engine):
        result = engine.validate_bullet("Completed various tasks")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 1

    def test_contains_multiple_projects(self, engine):
        result = engine.validate_bullet("Worked on multiple projects")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 1

    def test_contains_many_responsibilities(self, engine):
        result = engine.validate_bullet("Managed many responsibilities")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 1

    def test_contains_wide_range(self, engine):
        result = engine.validate_bullet("Handled wide range of tasks")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 1

    def test_case_insensitive(self, engine):
        result = engine.validate_bullet("VARIOUS TASKS completed")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "no_generic_phrases"]
        assert len(violations) == 0


# ============================================================================
# Rule: bullet_concise Tests
# ============================================================================

class TestBulletConcise:
    def test_concise_bullet(self, engine):
        result = engine.validate_bullet("Developed system")
        violations = [v for v in result.violations if v.rule_name == "bullet_concise"]
        assert len(violations) == 0

    def test_long_bullet(self, engine):
        bullet = "A" * 201
        result = engine.validate_bullet(bullet)
        violations = [v for v in result.violations if v.rule_name == "bullet_concise"]
        assert len(violations) == 1

    def test_exactly_200_chars(self, engine):
        bullet = "A" * 200
        result = engine.validate_bullet(bullet)
        violations = [v for v in result.violations if v.rule_name == "bullet_concise"]
        assert len(violations) == 0

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "bullet_concise"]
        assert len(violations) == 0


# ============================================================================
# Rule: no_special_characters Tests
# ============================================================================

class TestNoSpecialCharacters:
    def test_no_special_characters(self, engine):
        result = engine.validate_bullet("Developed system")
        violations = [v for v in result.violations if v.rule_name == "no_special_characters"]
        assert len(violations) == 0

    def test_contains_pipe(self, engine):
        result = engine.validate_bullet("Developed | system")
        violations = [v for v in result.violations if v.rule_name == "no_special_characters"]
        assert len(violations) == 1

    def test_contains_backslash(self, engine):
        result = engine.validate_bullet("Developed \\ system")
        violations = [v for v in result.violations if v.rule_name == "no_special_characters"]
        assert len(violations) == 1

    def test_contains_curly_brace(self, engine):
        result = engine.validate_bullet("Developed {system}")
        violations = [v for v in result.violations if v.rule_name == "no_special_characters"]
        assert len(violations) == 1

    def test_contains_angle_bracket(self, engine):
        result = engine.validate_bullet("Developed <system>")
        violations = [v for v in result.violations if v.rule_name == "no_special_characters"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "no_special_characters"]
        assert len(violations) == 0


# ============================================================================
# Rule: no_first_person Tests
# ============================================================================

class TestNoFirstPerson:
    def test_no_first_person(self, engine):
        result = engine.validate_bullet("Developed system")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 0

    def test_starts_with_i(self, engine):
        result = engine.validate_bullet("I developed the system")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 1

    def test_starts_with_my(self, engine):
        result = engine.validate_bullet("My development work")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 1

    def test_contains_we(self, engine):
        result = engine.validate_bullet("Developed system, we tested it")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 1

    def test_contains_our(self, engine):
        result = engine.validate_bullet("Improved our system")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 1

    def test_case_insensitive(self, engine):
        result = engine.validate_bullet("I DEVELOPED the system")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 1

    def test_empty_bullet(self, engine):
        result = engine.validate_bullet("")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 0


# ============================================================================
# validate_bullet Integration Tests
# ============================================================================

class TestValidateBulletIntegration:
    def test_perfect_bullet(self, engine):
        result = engine.validate_bullet("Developed Python microservice serving 10000 users")
        assert result.is_valid is True
        assert result.score >= 80

    def test_multiple_violations(self, engine):
        # "Helped" is not in STRONG_ACTION_VERBS, so bullet_starts_with_verb
        # returns an ERROR, which sets is_valid=False.
        result = engine.validate_bullet("Helped with various tasks")
        assert result.is_valid is False
        assert result.score < 100
        assert len(result.violations) > 0

    def test_empty_bullet(self, engine):
        # Empty bullet causes bullet_starts_with_verb ERROR (first_word is "")
        result = engine.validate_bullet("")
        assert result.is_valid is False
        assert len(result.violations) > 0

    def test_single_word(self, engine):
        result = engine.validate_bullet("Developed")
        assert result.is_valid is True


# ============================================================================
# validate_bullets Tests
# ============================================================================

class TestValidateBullets:
    def test_validate_bullets(self, engine):
        bullets = [
            "Developed Python application",
            "Implemented REST API",
            "Deployed to AWS",
        ]
        result = engine.validate_bullets(bullets)
        assert result.is_valid is True

    def test_validate_bullets_with_violations(self, engine):
        bullets = [
            "Developed Python application",
            "Helped with various tasks",
        ]
        result = engine.validate_bullets(bullets)
        assert len(result.violations) > 0
        # The second bullet has more severe violations (starts with weak verb)
        field_paths = [v.field_path for v in result.violations]
        assert "bullets[1]" in field_paths

    def test_validate_empty_bullets(self, engine):
        result = engine.validate_bullets([])
        assert result.is_valid is True
        assert result.passed_rules == 0

    def test_validate_single_bullet(self, engine):
        result = engine.validate_bullets(["Developed system"])
        assert result.is_valid is True


# ============================================================================
# validate_resume Tests
# ============================================================================

class TestValidateResume:
    def test_valid_resume(self, engine):
        resume = {
            "summary": "Senior developer with 5+ years experience",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "bullets": ["Developed Python application serving 10000 users"],
                }
            ],
            "education": [{"institution": "MIT", "degree": "BS"}],
            "skills": ["Python", "AWS"],
        }
        result = engine.validate_resume(resume)
        assert result.is_valid is True

    def test_missing_summary(self, engine):
        resume = {
            "experience": [{"title": "Engineer", "company": "Tech", "bullets": ["Built things"]}],
            "education": [],
            "skills": [],
        }
        result = engine.validate_resume(resume)
        violations = [v for v in result.violations if v.rule_name == "has_summary"]
        assert len(violations) == 1

    def test_missing_experience(self, engine):
        resume = {
            "summary": "Developer",
            "education": [],
            "skills": [],
        }
        result = engine.validate_resume(resume)
        violations = [v for v in result.violations if v.rule_name == "has_experience"]
        assert len(violations) == 1

    def test_missing_education(self, engine):
        resume = {
            "summary": "Developer",
            "experience": [],
            "skills": [],
        }
        result = engine.validate_resume(resume)
        violations = [v for v in result.violations if v.rule_name == "has_education"]
        assert len(violations) == 1

    def test_missing_skills(self, engine):
        resume = {
            "summary": "Developer",
            "experience": [],
            "education": [],
        }
        result = engine.validate_resume(resume)
        violations = [v for v in result.violations if v.rule_name == "has_skills"]
        assert len(violations) == 1

    def test_experience_bullets_validated(self, engine):
        resume = {
            "summary": "Developer",
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Tech",
                    "bullets": ["Helped with various tasks"],
                }
            ],
            "education": [],
            "skills": [],
        }
        result = engine.validate_resume(resume)
        assert len(result.violations) > 0

    def test_summary_validated(self, engine):
        resume = {
            "summary": "I am a developer with many responsibilities",
            "experience": [],
            "education": [],
            "skills": [],
        }
        result = engine.validate_resume(resume)
        assert len(result.violations) > 0


# ============================================================================
# _validate_summary Tests
# ============================================================================

class TestValidateSummary:
    def test_concise_summary(self, engine):
        result = engine._validate_summary("Senior developer with 5+ years")
        assert result.is_valid is True

    def test_long_summary(self, engine):
        summary = "A" * 501
        result = engine._validate_summary(summary)
        violations = [v for v in result.violations if v.rule_name == "summary_concise"]
        assert len(violations) == 1

    def test_summary_with_first_person(self, engine):
        result = engine._validate_summary("I am a developer")
        violations = [v for v in result.violations if v.rule_name == "no_first_person"]
        assert len(violations) == 1


# ============================================================================
# Rule Addition and Removal Tests
# ============================================================================

class TestRuleManagement:
    def test_add_custom_rule(self, engine):
        initial_count = len(engine.rules)

        def custom_check(bullet=None):
            return None

        engine.add_rule(RuleViolation.__class__.__name__)
        assert len(engine.rules) == initial_count + 1

    def test_remove_rule(self, engine):
        initial_count = len(engine.rules)
        engine.remove_rule("bullet_starts_with_verb")
        assert len(engine.rules) == initial_count - 1

    def test_remove_nonexistent_rule(self, engine):
        initial_count = len(engine.rules)
        engine.remove_rule("nonexistent_rule")
        assert len(engine.rules) == initial_count


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    def test_whitespace_only_bullet(self, engine):
        # Whitespace-only bullet: strip() gives "", which is not a verb
        result = engine.validate_bullet("   ")
        assert result.is_valid is False
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_newline_in_bullet(self, engine):
        result = engine.validate_bullet("Developed\nsystem")
        assert result.is_valid is True

    def test_tab_in_bullet(self, engine):
        result = engine.validate_bullet("Developed\tsystem")
        assert result.is_valid is True

    def test_unicode_in_bullet(self, engine):
        result = engine.validate_bullet("Developed système")
        assert result.is_valid is True

    def test_emoji_in_bullet(self, engine):
        result = engine.validate_bullet("Developed system 🚀")
        assert result.is_valid is True

    def test_very_long_bullet(self, engine):
        bullet = "Developed " * 1000
        result = engine.validate_bullet(bullet)
        assert result.is_valid is True

    def test_number_only_bullet(self, engine):
        result = engine.validate_bullet("12345")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1

    def test_punctuation_only_bullet(self, engine):
        result = engine.validate_bullet("...")
        violations = [v for v in result.violations if v.rule_name == "bullet_starts_with_verb"]
        assert len(violations) == 1


# ============================================================================
# Score Calculation Tests
# ============================================================================

class TestScoreCalculation:
    def test_perfect_score(self, engine):
        result = engine.validate_bullet("Developed Python system serving 10000 users")
        assert result.score == 100.0

    def test_score_with_warnings(self, engine):
        result = engine.validate_bullet("Helped with Python system")
        assert result.score < 100.0
        assert result.score > 0

    def test_score_with_errors(self, engine):
        result = engine.validate_bullet("Helped with various tasks")
        assert result.score < 100.0

    def test_score_decreases_with_single_violation(self, engine):
        result = ValidationResult(is_valid=True, score=0.0)
        violation = RuleViolation(
            rule_name="test",
            category=RuleCategory.ACTION_VERB,
            severity=Severity.WARNING,
            message="test",
        )
        result.add_violation(violation)
        assert result.score < 0.0
        # Note: ValidationResult does NOT clamp score to 0.
        # Score can go negative when many violations accumulate.
