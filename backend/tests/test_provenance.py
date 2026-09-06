"""Tests for Provenance Tracker."""
import pytest

from app.services.knowledge_intelligence.provenance_tracker import (
    HAND_AUTHORED_SOURCE,
    PROVENANCE_FIELDS,
    ProvenanceTracker,
)


@pytest.fixture
def tracker():
    return ProvenanceTracker()


@pytest.fixture
def sample_rule():
    return {
        "rule_id": "TEST_001",
        "instruction": "Always quantify achievements",
        "domain": "resume",
        "priority": "High",
        "category": "Quantification",
        "section_name": "experience",
        "rule_hash": "abc123",
    }


@pytest.fixture
def sample_pdf_rule():
    return {
        "rule_id": "PDF_001",
        "instruction": "Use strong action verbs in bullet points",
        "domain": "experience",
        "priority": "High",
        "category": "Action Verbs",
        "section_name": "experience",
        "rule_hash": "def456",
    }


class TestProvenanceFields:
    def test_has_seven_fields(self):
        assert len(PROVENANCE_FIELDS) == 7

    def test_contains_required_fields(self):
        required = ["source_document", "source_page", "extraction_confidence",
                     "extraction_timestamp", "rule_hash"]
        for field in required:
            assert field in PROVENANCE_FIELDS


class TestAssignProvenance:
    def test_assigns_all_fields(self, tracker, sample_rule):
        result = tracker.assign_provenance(
            sample_rule,
            source_document="harvard.pdf",
            source_page=5,
            source_section="Experience",
            source_evidence="Use action verbs",
            extraction_confidence=0.9,
        )
        assert result["source_document"] == "harvard.pdf"
        assert result["source_page"] == 5
        assert result["source_section"] == "Experience"
        assert result["source_evidence"] == "Use action verbs"
        assert result["extraction_confidence"] == 0.9
        assert "extraction_timestamp" in result
        assert "rule_hash" in result

    def test_preserves_existing_fields(self, tracker, sample_rule):
        result = tracker.assign_provenance(
            sample_rule,
            source_document="harvard.pdf",
            source_page=1,
        )
        assert result["rule_id"] == "TEST_001"
        assert result["instruction"] == "Always quantify achievements"

    def test_does_not_mutate_original(self, tracker, sample_rule):
        tracker.assign_provenance(sample_rule, source_document="test.pdf", source_page=1)
        assert "source_document" not in sample_rule

    def test_generates_hash_if_missing(self, tracker):
        rule = {"rule_id": "TEST", "instruction": "Test instruction"}
        result = tracker.assign_provenance(rule, source_document="test.pdf", source_page=1)
        assert result["rule_hash"] != ""

    def test_preserves_existing_hash(self, tracker, sample_rule):
        result = tracker.assign_provenance(
            sample_rule, source_document="test.pdf", source_page=1
        )
        assert result["rule_hash"] == "abc123"


class TestAssignHandAuthoredProvenance:
    def test_sets_hand_authored_source(self, tracker, sample_rule):
        result = tracker.assign_hand_authored_provenance(sample_rule)
        assert result["source_document"] == HAND_AUTHORED_SOURCE

    def test_sets_page_to_none(self, tracker, sample_rule):
        result = tracker.assign_hand_authored_provenance(sample_rule)
        assert result["source_page"] is None

    def test_sets_confidence_to_one(self, tracker, sample_rule):
        result = tracker.assign_hand_authored_provenance(sample_rule)
        assert result["extraction_confidence"] == 1.0

    def test_sets_evidence_to_none(self, tracker, sample_rule):
        result = tracker.assign_hand_authored_provenance(sample_rule)
        assert result["source_evidence"] is None

    def test_has_timestamp(self, tracker, sample_rule):
        result = tracker.assign_hand_authored_provenance(sample_rule)
        assert "extraction_timestamp" in result


class TestVerifyProvenance:
    def test_valid_pdf_rule(self, tracker, sample_pdf_rule):
        rule = tracker.assign_provenance(
            sample_pdf_rule,
            source_document="harvard.pdf",
            source_page=3,
            extraction_confidence=0.85,
        )
        result = tracker.verify_provenance(rule)
        assert result["valid"] is True
        assert result["issues"] == []

    def test_valid_hand_authored_rule(self, tracker, sample_rule):
        rule = tracker.assign_hand_authored_provenance(sample_rule)
        result = tracker.verify_provenance(rule)
        assert result["valid"] is True

    def test_missing_fields(self, tracker):
        rule = {"rule_id": "TEST"}
        result = tracker.verify_provenance(rule)
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_hand_authored_with_page_fails(self, tracker, sample_rule):
        rule = dict(sample_rule)
        rule["source_document"] = HAND_AUTHORED_SOURCE
        rule["source_page"] = 5
        rule["extraction_confidence"] = 1.0
        rule["extraction_timestamp"] = "2026-01-01T00:00:00"
        rule["rule_hash"] = "abc"
        result = tracker.verify_provenance(rule)
        assert result["valid"] is False
        assert any("source_page" in i for i in result["issues"])

    def test_hand_authored_low_confidence_fails(self, tracker, sample_rule):
        rule = dict(sample_rule)
        rule["source_document"] = HAND_AUTHORED_SOURCE
        rule["source_page"] = None
        rule["extraction_confidence"] = 0.5
        rule["extraction_timestamp"] = "2026-01-01T00:00:00"
        rule["rule_hash"] = "abc"
        result = tracker.verify_provenance(rule)
        assert result["valid"] is False
        assert any("confidence" in i for i in result["issues"])

    def test_pdf_rule_missing_page_fails(self, tracker, sample_pdf_rule):
        rule = dict(sample_pdf_rule)
        rule["source_document"] = "harvard.pdf"
        rule["source_page"] = None
        rule["extraction_confidence"] = 0.8
        rule["extraction_timestamp"] = "2026-01-01T00:00:00"
        rule["rule_hash"] = "abc"
        result = tracker.verify_provenance(rule)
        assert result["valid"] is False
        assert any("source_page" in i for i in result["issues"])

    def test_includes_rule_id_in_result(self, tracker, sample_rule):
        rule = tracker.assign_hand_authored_provenance(sample_rule)
        result = tracker.verify_provenance(rule)
        assert result["rule_id"] == "TEST_001"


class TestComputeLineage:
    def test_returns_lineage_dict(self, tracker, sample_pdf_rule):
        rule = tracker.assign_provenance(
            sample_pdf_rule,
            source_document="harvard.pdf",
            source_page=3,
        )
        lineage = tracker.compute_lineage(rule)
        assert lineage["rule_id"] == "PDF_001"
        assert lineage["source_document"] == "harvard.pdf"
        assert lineage["source_page"] == 3

    def test_includes_state(self, tracker, sample_pdf_rule):
        rule = tracker.assign_provenance(
            sample_pdf_rule,
            source_document="harvard.pdf",
            source_page=1,
        )
        rule["state"] = "ACTIVE"
        lineage = tracker.compute_lineage(rule)
        assert lineage["state"] == "ACTIVE"

    def test_includes_version(self, tracker, sample_pdf_rule):
        rule = tracker.assign_provenance(
            sample_pdf_rule,
            source_document="harvard.pdf",
            source_page=1,
        )
        rule["version"] = 2
        lineage = tracker.compute_lineage(rule)
        assert lineage["version"] == 2


class TestDetectModification:
    def test_no_modification(self, tracker, sample_rule):
        result = tracker.detect_modification(sample_rule, sample_rule)
        assert result["modified"] is False
        assert result["changes"] == []

    def test_instruction_changed(self, tracker, sample_rule):
        modified = dict(sample_rule)
        modified["instruction"] = "New instruction"
        result = tracker.detect_modification(sample_rule, modified)
        assert result["modified"] is True
        assert len(result["changes"]) == 1
        assert result["changes"][0]["field"] == "instruction"

    def test_priority_changed(self, tracker, sample_rule):
        modified = dict(sample_rule)
        modified["priority"] = "Critical"
        result = tracker.detect_modification(sample_rule, modified)
        assert result["modified"] is True

    def test_hash_changed(self, tracker, sample_rule):
        modified = dict(sample_rule)
        modified["rule_hash"] = "different_hash"
        result = tracker.detect_modification(sample_rule, modified)
        assert result["modified"] is True
        assert result["hash_changed"] is True

    def test_multiple_changes(self, tracker, sample_rule):
        modified = dict(sample_rule)
        modified["instruction"] = "New"
        modified["priority"] = "Low"
        result = tracker.detect_modification(sample_rule, modified)
        assert result["modified"] is True
        assert len(result["changes"]) == 2


class TestLineageLog:
    def test_log_event(self, tracker):
        tracker.log_lineage_event("RULE_001", "extracted", {"page": 1})
        log = tracker.get_lineage_log()
        assert len(log) == 1
        assert log[0]["rule_id"] == "RULE_001"
        assert log[0]["event_type"] == "extracted"

    def test_get_lineage_for_rule(self, tracker):
        tracker.log_lineage_event("RULE_001", "extracted")
        tracker.log_lineage_event("RULE_002", "extracted")
        tracker.log_lineage_event("RULE_001", "classified")
        lineage = tracker.get_lineage_for_rule("RULE_001")
        assert len(lineage) == 2

    def test_empty_log(self, tracker):
        assert tracker.get_lineage_log() == []

    def test_log_has_timestamp(self, tracker):
        tracker.log_lineage_event("RULE_001", "extracted")
        log = tracker.get_lineage_log()
        assert "timestamp" in log[0]


class TestValidateRulesBatch:
    def test_all_valid(self, tracker, sample_pdf_rule):
        rules = [
            tracker.assign_provenance(
                dict(sample_pdf_rule),
                source_document="harvard.pdf",
                source_page=i,
            )
            for i in range(3)
        ]
        result = tracker.validate_rules_batch(rules)
        assert result["total"] == 3
        assert result["valid"] == 3
        assert result["invalid"] == 0

    def test_some_invalid(self, tracker, sample_pdf_rule):
        valid_rule = tracker.assign_provenance(
            dict(sample_pdf_rule),
            source_document="harvard.pdf",
            source_page=1,
        )
        invalid_rule = {"rule_id": "BAD"}
        result = tracker.validate_rules_batch([valid_rule, invalid_rule])
        assert result["total"] == 2
        assert result["valid"] == 1
        assert result["invalid"] == 1

    def test_empty_batch(self, tracker):
        result = tracker.validate_rules_batch([])
        assert result["total"] == 0
        assert result["valid"] == 0
