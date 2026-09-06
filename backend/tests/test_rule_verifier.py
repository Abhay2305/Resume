"""Tests for Rule Verifier."""
import pytest

from app.services.knowledge_intelligence.rule_verifier import RuleVerifier


@pytest.fixture
def verifier():
    return RuleVerifier()


@pytest.fixture
def existing_rules():
    return [
        {
            "rule_id": "EXISTING_001",
            "instruction": "Always quantify your achievements with specific numbers",
            "section_name": "experience",
            "rule_hash": "hash_001",
        },
        {
            "rule_id": "EXISTING_002",
            "instruction": "Use strong action verbs to start each bullet point",
            "section_name": "experience",
            "rule_hash": "hash_002",
        },
        {
            "rule_id": "EXISTING_003",
            "instruction": "Keep your summary to 3-4 lines or 50-75 words",
            "section_name": "summary",
            "rule_hash": "hash_003",
        },
    ]


class TestNormalizeText:
    def test_lowercase(self, verifier):
        assert verifier._normalize_text("HELLO World") == "hello world"

    def test_strips_whitespace(self, verifier):
        assert verifier._normalize_text("  hello  ") == "hello"

    def test_removes_punctuation(self, verifier):
        assert verifier._normalize_text("hello, world!") == "hello world"

    def test_normalizes_spaces(self, verifier):
        assert verifier._normalize_text("hello   world") == "hello world"


class TestComputeSimilarity:
    def test_identical_texts(self, verifier):
        assert verifier._compute_similarity("hello world", "hello world") == 1.0

    def test_similar_texts(self, verifier):
        sim = verifier._compute_similarity(
            "Use strong action verbs",
            "Use powerful action verbs",
        )
        assert sim > 0.7

    def test_different_texts(self, verifier):
        sim = verifier._compute_similarity(
            "Use strong action verbs",
            "Keep your resume short",
        )
        assert sim < 0.5

    def test_case_insensitive(self, verifier):
        sim = verifier._compute_similarity("HELLO WORLD", "hello world")
        assert sim == 1.0


class TestDetectExactDuplicate:
    def test_exact_duplicate_found(self, verifier, existing_rules):
        new_rule = {
            "rule_id": "NEW_001",
            "instruction": "Always quantify your achievements with specific numbers",
            "rule_hash": "hash_001",
        }
        result = verifier._detect_exact_duplicate(new_rule, existing_rules)
        assert result is not None
        assert result["type"] == "exact_duplicate"
        assert result["existing_rule_id"] == "EXISTING_001"

    def test_no_exact_duplicate(self, verifier, existing_rules):
        new_rule = {
            "rule_id": "NEW_002",
            "instruction": "New instruction",
            "rule_hash": "hash_new",
        }
        result = verifier._detect_exact_duplicate(new_rule, existing_rules)
        assert result is None

    def test_empty_hash(self, verifier, existing_rules):
        new_rule = {"rule_id": "NEW", "instruction": "Test", "rule_hash": ""}
        result = verifier._detect_exact_duplicate(new_rule, existing_rules)
        assert result is None


class TestDetectSemanticDuplicate:
    def test_semantic_duplicate_found(self, verifier, existing_rules):
        new_rule = {
            "rule_id": "NEW_001",
            "instruction": "Always quantify your achievements with specific numbers and percentages",
            "section_name": "experience",
        }
        results = verifier._detect_semantic_duplicate(new_rule, existing_rules)
        assert len(results) > 0
        assert results[0]["type"] == "semantic_duplicate"

    def test_no_semantic_duplicate(self, verifier, existing_rules):
        new_rule = {
            "rule_id": "NEW_002",
            "instruction": "Write a compelling cover letter opening paragraph",
            "section_name": "cover_letter",
        }
        results = verifier._detect_semantic_duplicate(new_rule, existing_rules)
        assert len(results) == 0

    def test_multiple_semantic_duplicates(self, verifier):
        existing = [
            {"rule_id": "E1", "instruction": "Use Python for data analysis"},
            {"rule_id": "E2", "instruction": "Use Python for machine learning"},
        ]
        new_rule = {"rule_id": "NEW", "instruction": "Use Python for data analysis and ML"}
        results = verifier._detect_semantic_duplicate(new_rule, existing)
        assert len(results) >= 1


class TestDetectConflicts:
    def test_conflict_found(self, verifier):
        existing = [
            {"rule_id": "E1", "instruction": "Always use first person", "section_name": "summary"},
        ]
        new_rule = {"rule_id": "NEW", "instruction": "Never use first person", "section_name": "summary"}
        results = verifier._detect_conflicts(new_rule, existing)
        assert len(results) > 0
        assert results[0]["type"] == "conflict"

    def test_no_conflict_different_sections(self, verifier):
        existing = [
            {"rule_id": "E1", "instruction": "Always use first person", "section_name": "summary"},
        ]
        new_rule = {"rule_id": "NEW", "instruction": "Never use first person", "section_name": "experience"}
        results = verifier._detect_conflicts(new_rule, existing)
        assert len(results) == 0

    def test_no_conflict_similar_instructions(self, verifier):
        existing = [
            {"rule_id": "E1", "instruction": "Always quantify achievements", "section_name": "experience"},
        ]
        new_rule = {"rule_id": "NEW", "instruction": "Always quantify achievements", "section_name": "experience"}
        results = verifier._detect_conflicts(new_rule, existing)
        assert len(results) == 0


class TestVerifyRule:
    def test_verified_no_issues(self, verifier, existing_rules):
        new_rule = {
            "rule_id": "NEW_001",
            "instruction": "Write a compelling cover letter opening",
            "section_name": "cover_letter",
            "rule_hash": "unique_hash",
        }
        result = verifier.verify_rule(new_rule, existing_rules)
        assert result["verified"] is True
        assert result["issue_count"] == 0

    def test_rejected_exact_duplicate(self, verifier, existing_rules):
        new_rule = {
            "rule_id": "NEW_002",
            "instruction": "Always quantify your achievements with specific numbers",
            "section_name": "experience",
            "rule_hash": "hash_001",
        }
        result = verifier.verify_rule(new_rule, existing_rules)
        assert result["verified"] is False
        assert result["has_exact_duplicate"] is True

    def test_rejected_conflict(self, verifier):
        existing = [
            {"rule_id": "E1", "instruction": "Always use first person", "section_name": "summary", "rule_hash": "h1"},
        ]
        new_rule = {
            "rule_id": "NEW",
            "instruction": "Never use first person",
            "section_name": "summary",
            "rule_hash": "h2",
        }
        result = verifier.verify_rule(new_rule, existing)
        assert result["verified"] is False
        assert result["has_conflicts"] is True

    def test_result_structure(self, verifier, existing_rules):
        new_rule = {"rule_id": "NEW", "instruction": "Test", "rule_hash": "h"}
        result = verifier.verify_rule(new_rule, existing_rules)
        assert "rule_id" in result
        assert "verified" in result
        assert "issues" in result
        assert "issue_count" in result


class TestVerifyRulesBatch:
    def test_all_verified(self, verifier, existing_rules):
        new_rules = [
            {"rule_id": "NEW_001", "instruction": "Write a compelling cover letter", "section_name": "cover_letter", "rule_hash": "h1"},
            {"rule_id": "NEW_002", "instruction": "Use specific metrics in your resume", "section_name": "resume", "rule_hash": "h2"},
        ]
        result = verifier.verify_rules_batch(new_rules, existing_rules)
        assert result["verified"] == 2
        assert result["rejected"] == 0

    def test_some_rejected(self, verifier, existing_rules):
        new_rules = [
            {"rule_id": "NEW_001", "instruction": "Write a cover letter", "section_name": "cover_letter", "rule_hash": "h1"},
            {"rule_id": "NEW_002", "instruction": "Always quantify your achievements with specific numbers", "section_name": "experience", "rule_hash": "hash_001"},
        ]
        result = verifier.verify_rules_batch(new_rules, existing_rules)
        assert result["verified"] == 1
        assert result["rejected"] == 1

    def test_empty_batch(self, verifier, existing_rules):
        result = verifier.verify_rules_batch([], existing_rules)
        assert result["total_new_rules"] == 0
        assert result["verified"] == 0

    def test_result_structure(self, verifier, existing_rules):
        new_rules = [{"rule_id": "NEW", "instruction": "Test", "rule_hash": "h"}]
        result = verifier.verify_rules_batch(new_rules, existing_rules)
        assert "total_new_rules" in result
        assert "verified" in result
        assert "rejected" in result
        assert "total_issues" in result
        assert "results" in result


class TestGenerateReport:
    def test_report_structure(self, verifier, existing_rules):
        new_rules = [
            {"rule_id": "NEW_001", "instruction": "Write a cover letter", "section_name": "cover_letter", "rule_hash": "h1"},
        ]
        result = verifier.verify_rules_batch(new_rules, existing_rules)
        report = verifier.generate_report(result)
        assert "Rule Verification Report" in report
        assert "Total new rules" in report
        assert "NEW_001" in report

    def test_report_with_failures(self, verifier, existing_rules):
        new_rules = [
            {"rule_id": "NEW_001", "instruction": "Always quantify your achievements with specific numbers", "section_name": "experience", "rule_hash": "hash_001"},
        ]
        result = verifier.verify_rules_batch(new_rules, existing_rules)
        report = verifier.generate_report(result)
        assert "FAIL" in report


class TestVerificationLog:
    def test_log_verification(self, verifier):
        verifier.log_verification("RULE_001", {"verified": True, "issue_count": 0})
        log = verifier.get_verification_log()
        assert len(log) == 1
        assert log[0]["rule_id"] == "RULE_001"

    def test_empty_log(self, verifier):
        assert verifier.get_verification_log() == []
