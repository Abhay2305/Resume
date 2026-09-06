"""Tests for Rule Approval and Repository Seeding."""
import pytest

from app.services.knowledge_intelligence.rule_approval import (
    HAND_AUTHORED_SOURCE,
    STATE_TRANSITIONS,
    VALID_STATES,
    RuleApproval,
)


@pytest.fixture
def approval():
    return RuleApproval()


@pytest.fixture
def discovered_rule():
    return {
        "rule_id": "NEW_001",
        "instruction": "Always quantify achievements",
        "state": "DISCOVERED",
        "rule_hash": "abc123",
    }


@pytest.fixture
def verified_rule():
    return {
        "rule_id": "NEW_002",
        "instruction": "Use strong action verbs",
        "state": "VERIFIED",
        "rule_hash": "def456",
    }


class TestValidStates:
    def test_has_nine_states(self):
        assert len(VALID_STATES) == 9

    def test_contains_required_states(self):
        required = ["DISCOVERED", "EXTRACTED", "CLASSIFIED", "VERIFIED",
                     "APPROVED", "ACTIVE", "VERSIONED", "AUDITED", "REJECTED"]
        for state in required:
            assert state in VALID_STATES


class TestStateTransitions:
    def test_discovered_can_go_to_extracted(self, approval):
        assert approval.can_transition("DISCOVERED", "EXTRACTED")

    def test_discovered_can_go_to_rejected(self, approval):
        assert approval.can_transition("DISCOVERED", "REJECTED")

    def test_discovered_cannot_go_to_active(self, approval):
        assert not approval.can_transition("DISCOVERED", "ACTIVE")

    def test_extracted_can_go_to_classified(self, approval):
        assert approval.can_transition("EXTRACTED", "CLASSIFIED")

    def test_verified_can_go_to_approved(self, approval):
        assert approval.can_transition("VERIFIED", "APPROVED")

    def test_approved_can_go_to_active(self, approval):
        assert approval.can_transition("APPROVED", "ACTIVE")

    def test_active_can_go_to_versioned(self, approval):
        assert approval.can_transition("ACTIVE", "VERSIONED")

    def test_active_can_go_to_rejected(self, approval):
        assert approval.can_transition("ACTIVE", "REJECTED")

    def test_versioned_can_go_to_audited(self, approval):
        assert approval.can_transition("VERSIONED", "AUDITED")

    def test_invalid_state_returns_false(self, approval):
        assert not approval.can_transition("INVALID", "ACTIVE")

    def test_rejected_has_no_transitions(self, approval):
        assert approval.can_transition("REJECTED", "ACTIVE") is False


class TestTransitionState:
    def test_valid_transition(self, approval, discovered_rule):
        result = approval.transition_state(discovered_rule, "EXTRACTED")
        assert result["state"] == "EXTRACTED"

    def test_invalid_transition_raises(self, approval, discovered_rule):
        with pytest.raises(ValueError, match="Invalid transition"):
            approval.transition_state(discovered_rule, "ACTIVE")

    def test_does_not_mutate_original(self, approval, discovered_rule):
        approval.transition_state(discovered_rule, "EXTRACTED")
        assert discovered_rule["state"] == "DISCOVERED"

    def test_logs_transition(self, approval, discovered_rule):
        approval.transition_state(discovered_rule, "EXTRACTED", actor="test", reason="testing")
        log = approval.get_transition_log()
        assert len(log) == 1
        assert log[0]["from_state"] == "DISCOVERED"
        assert log[0]["to_state"] == "EXTRACTED"


class TestApproveRule:
    def test_approves_verified_rule(self, approval, verified_rule):
        result = approval.approve_rule(verified_rule, reviewer="alice")
        assert result["state"] == "APPROVED"

    def test_cannot_approve_discovered_rule(self, approval, discovered_rule):
        with pytest.raises(ValueError):
            approval.approve_rule(discovered_rule)

    def test_logs_reviewer(self, approval, verified_rule):
        approval.approve_rule(verified_rule, reviewer="alice")
        log = approval.get_transition_log()
        assert log[0]["actor"] == "alice"


class TestActivateRule:
    def test_activates_approved_rule(self, approval):
        rule = {"rule_id": "R1", "instruction": "Test", "state": "APPROVED"}
        result = approval.activate_rule(rule)
        assert result["state"] == "ACTIVE"

    def test_cannot_activate_non_approved(self, approval, verified_rule):
        with pytest.raises(ValueError):
            approval.activate_rule(verified_rule)


class TestRejectRule:
    def test_rejects_from_any_rejectable_state(self, approval, discovered_rule):
        result = approval.reject_rule(discovered_rule, reason="Bad rule")
        assert result["state"] == "REJECTED"

    def test_logs_rejection_reason(self, approval, discovered_rule):
        approval.reject_rule(discovered_rule, reason="Poor quality")
        log = approval.get_transition_log()
        assert log[0]["reason"] == "Poor quality"


class TestSeedHandAuthoredRules:
    def test_seeds_rules(self, approval):
        rules = [
            {"rule_id": "R1", "instruction": "Test instruction 1"},
            {"rule_id": "R2", "instruction": "Test instruction 2"},
        ]
        seeded = approval.seed_hand_authored_rules(rules)
        assert len(seeded) == 2

    def test_sets_hand_authored_source(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["source_document"] == HAND_AUTHORED_SOURCE

    def test_sets_state_to_active(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["state"] == "ACTIVE"

    def test_sets_confidence_to_one(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["extraction_confidence"] == 1.0

    def test_sets_page_to_none(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["source_page"] is None

    def test_generates_hash(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test instruction"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["rule_hash"] != ""

    def test_preserves_existing_hash(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test", "rule_hash": "existing"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["rule_hash"] == "existing"

    def test_sets_version_to_one(self, approval):
        rules = [{"rule_id": "R1", "instruction": "Test"}]
        seeded = approval.seed_hand_authored_rules(rules)
        assert seeded[0]["version"] == 1

    def test_empty_list(self, approval):
        assert approval.seed_hand_authored_rules([]) == []


class TestLoadSeedRulesFromJson:
    def test_loads_rules(self, approval):
        rules = approval.load_seed_rules_from_json()
        assert len(rules) > 0

    def test_rules_have_required_fields(self, approval):
        rules = approval.load_seed_rules_from_json()
        for rule in rules:
            assert "rule_id" in rule
            assert "instruction" in rule
            assert "section_name" in rule
            assert "priority" in rule

    def test_count_matches_28(self, approval):
        rules = approval.load_seed_rules_from_json()
        assert len(rules) == 28


class TestGetSeededRulesCount:
    def test_returns_count(self, approval):
        count = approval.get_seeded_rules_count()
        assert count == 28


class TestPipelineMethods:
    def test_prepare_for_extraction(self, approval, discovered_rule):
        result = approval.prepare_for_extraction(discovered_rule)
        assert result["state"] == "EXTRACTED"

    def test_prepare_for_classification(self, approval):
        rule = {"rule_id": "R1", "instruction": "Test", "state": "EXTRACTED"}
        result = approval.prepare_for_classification(rule)
        assert result["state"] == "CLASSIFIED"

    def test_prepare_for_verification(self, approval):
        rule = {"rule_id": "R1", "instruction": "Test", "state": "CLASSIFIED"}
        result = approval.prepare_for_verification(rule)
        assert result["state"] == "VERIFIED"


class TestTransitionLog:
    def test_get_transitions_for_rule(self, approval, discovered_rule):
        approval.transition_state(discovered_rule, "EXTRACTED")
        approval.transition_state(
            {"rule_id": "NEW_001", "instruction": "Test", "state": "EXTRACTED", "rule_hash": "abc123"},
            "CLASSIFIED",
        )
        log = approval.get_transitions_for_rule("NEW_001")
        assert len(log) == 2

    def test_empty_log(self, approval):
        assert approval.get_transition_log() == []

    def test_log_has_timestamp(self, approval, discovered_rule):
        approval.transition_state(discovered_rule, "EXTRACTED")
        log = approval.get_transition_log()
        assert "timestamp" in log[0]
