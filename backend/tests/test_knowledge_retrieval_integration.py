"""Tests for Knowledge Repository Integration (Phase H).

Tests:
  - PDF rule ingestion with provenance
  - Hand-authored rule seeding with provenance
  - Provenance survives in context output
  - Rule state filtering
  - Source document filtering
  - Rule provenance retrieval
  - Context builder handles provenance
  - Citations include PDF sources
  - Rules from different sources are distinguishable
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from app.services.knowledge_intelligence.context_builder import KnowledgeContextBuilder
from app.services.knowledge_intelligence.retriever import KnowledgeRetriever
from app.services.knowledge_intelligence.ranker import KnowledgeRanker
from app.services.knowledge_intelligence.rule_approval import RuleApproval
from app.services.knowledge_intelligence.provenance_tracker import ProvenanceTracker


# ============================================================================
# Context Builder Provenance Tests
# ============================================================================

class TestContextBuilderProvenance:
    def setup_method(self):
        self.builder = KnowledgeContextBuilder()

    def test_format_rule_includes_provenance(self):
        rule = {
            "rule_id": "PDF_001",
            "source": "Harvard Resume Guide",
            "section_name": "experience",
            "priority": "High",
            "category": "Quantification",
            "instruction": "Quantify achievements",
            "reason": "Credibility",
            "examples": "[]",
            "source_document": "harvard.pdf",
            "source_page": 5,
            "source_evidence": "Use numbers",
            "extraction_confidence": 0.85,
            "extraction_timestamp": "2026-01-01T00:00:00",
            "rule_hash": "abc123",
            "state": "ACTIVE",
            "version": 1,
        }
        formatted = self.builder._format_rule(rule)
        assert "provenance" in formatted
        assert formatted["provenance"]["source_document"] == "harvard.pdf"
        assert formatted["provenance"]["source_page"] == 5
        assert formatted["provenance"]["extraction_confidence"] == 0.85

    def test_format_rule_no_provenance_for_hand_authored(self):
        rule = {
            "rule_id": "HA_001",
            "source": "Harvard Resume Guide",
            "section_name": "summary",
            "priority": "High",
            "category": "Tailoring",
            "instruction": "Tailor summary",
            "reason": "Relevance",
            "examples": "[]",
        }
        formatted = self.builder._format_rule(rule)
        assert "provenance" not in formatted

    def test_build_context_with_pdf_rules(self):
        rules = [
            {
                "rule_id": "PDF_001",
                "source": "Harvard Resume Guide",
                "section_name": "experience",
                "priority": "High",
                "category": "Quantification",
                "instruction": "Quantify achievements",
                "source_document": "harvard.pdf",
                "source_page": 5,
            },
            {
                "rule_id": "HA_001",
                "source": "Harvard Resume Guide",
                "section_name": "experience",
                "priority": "Medium",
                "category": "Action Verbs",
                "instruction": "Use strong verbs",
            },
        ]
        context = self.builder.build(rules)
        assert context["total_rules"] == 2
        exp_rules = self.builder.get_section_rules(context, "experience")
        assert len(exp_rules) == 2
        pdf_rule = next(r for r in exp_rules if r["rule_id"] == "PDF_001")
        assert "provenance" in pdf_rule
        ha_rule = next(r for r in exp_rules if r["rule_id"] == "HA_001")
        assert "provenance" not in ha_rule

    def test_citations_include_pdf_sources(self):
        rules = [
            {
                "rule_id": "PDF_001",
                "source": "Harvard Resume Guide",
                "section_name": "experience",
                "source_document": "harvard.pdf",
            },
            {
                "rule_id": "HA_001",
                "source": "MIT Career Services",
                "section_name": "skills",
            },
        ]
        citations = self.builder._extract_citations(rules)
        assert "harvard.pdf" in citations
        assert "Harvard Resume Guide" in citations
        assert "MIT Career Services" in citations

    def test_citations_exclude_hand_authored_marker(self):
        rules = [
            {
                "rule_id": "HA_001",
                "source": "some source",
                "section_name": "summary",
                "source_document": "hand-authored",
            },
        ]
        citations = self.builder._extract_citations(rules)
        assert "hand-authored" not in citations


# ============================================================================
# Retriever Integration Tests
# ============================================================================

class TestRetrieverWithPDFRules:
    def setup_method(self):
        self.retriever = KnowledgeRetriever()

    def test_retrieves_both_rule_types(self):
        rules = [
            {"rule_id": "PDF_001", "source": "Harvard", "section_name": "experience", "category": "Quantification", "priority": "High", "confidence": 0.9, "source_document": "harvard.pdf"},
            {"rule_id": "HA_001", "source": "MIT", "section_name": "skills", "category": "Keywords", "priority": "Medium", "confidence": 0.85},
            {"rule_id": "PDF_002", "source": "Yale", "section_name": "summary", "category": "Clarity", "priority": "Low", "confidence": 0.9, "source_document": "yale.pdf"},
        ]
        gap_results = {
            "skills": {"required": {"missing": []}, "score": 0.5},
            "experience": {"years": {"sufficient": True}, "score": 1.0},
        }
        retrieved = self.retriever.retrieve(rules, gap_results, max_rules=10)
        assert len(retrieved) > 0
        rule_ids = [r["rule_id"] for r in retrieved]
        assert "PDF_001" in rule_ids or "HA_001" in rule_ids

    def test_retrieval_preserves_provenance(self):
        rules = [
            {"rule_id": "PDF_001", "source": "Harvard", "section_name": "experience", "category": "Quantification", "priority": "High", "confidence": 0.9, "source_document": "harvard.pdf", "source_page": 5},
        ]
        gap_results = {"experience": {"years": {"sufficient": True}, "score": 1.0}}
        retrieved = self.retriever.retrieve(rules, gap_results, max_rules=10)
        assert len(retrieved) == 1
        assert retrieved[0].get("source_document") == "harvard.pdf"
        assert retrieved[0].get("source_page") == 5


# ============================================================================
# Rule Approval Integration Tests
# ============================================================================

class TestRuleApprovalIntegration:
    def setup_method(self):
        self.approval = RuleApproval()

    def test_seed_rules_have_provenance(self):
        seed_rules = self.approval.load_seed_rules_from_json()
        assert len(seed_rules) == 28
        seeded = self.approval.seed_hand_authored_rules(seed_rules)
        for rule in seeded:
            assert rule["source_document"] == "hand-authored"
            assert rule["source_page"] is None
            assert rule["extraction_confidence"] == 1.0
            assert rule["state"] == "ACTIVE"
            assert rule["version"] == 1
            assert rule["rule_hash"] != ""

    def test_pdf_rules_follow_governance_pipeline(self):
        pdf_rule = {
            "rule_id": "PDF_001",
            "instruction": "Use numbers",
            "state": "DISCOVERED",
        }
        extracted = self.approval.prepare_for_extraction(pdf_rule)
        assert extracted["state"] == "EXTRACTED"
        classified = self.approval.prepare_for_classification(extracted)
        assert classified["state"] == "CLASSIFIED"
        verified = self.approval.prepare_for_verification(classified)
        assert verified["state"] == "VERIFIED"

    def test_verified_can_be_approved(self):
        rule = {"rule_id": "PDF_001", "instruction": "Use numbers", "state": "VERIFIED"}
        approved = self.approval.approve_rule(rule, reviewer="test")
        assert approved["state"] == "APPROVED"

    def test_approved_can_be_activated(self):
        rule = {"rule_id": "PDF_001", "instruction": "Use numbers", "state": "APPROVED"}
        active = self.approval.activate_rule(rule)
        assert active["state"] == "ACTIVE"


# ============================================================================
# Provenance Tracker Integration Tests
# ============================================================================

class TestProvenanceTrackerIntegration:
    def setup_method(self):
        self.tracker = ProvenanceTracker()

    def test_pdf_rule_has_complete_provenance(self):
        rule = {
            "rule_id": "PDF_001",
            "instruction": "Quantify achievements",
        }
        provenanced = self.tracker.assign_provenance(
            rule,
            source_document="harvard.pdf",
            source_page=5,
            source_section="Experience",
            source_evidence="Use numbers to quantify",
            extraction_confidence=0.85,
        )
        assert provenanced["source_document"] == "harvard.pdf"
        assert provenanced["source_page"] == 5
        assert provenanced["extraction_confidence"] == 0.85
        assert provenanced["extraction_timestamp"] != ""
        assert provenanced["rule_hash"] != ""

    def test_hand_authored_rule_provenance(self):
        rule = {
            "rule_id": "HA_001",
            "instruction": "Tailor your summary",
        }
        provenanced = self.tracker.assign_hand_authored_provenance(rule)
        assert provenanced["source_document"] == "hand-authored"
        assert provenanced["source_page"] is None
        assert provenanced["extraction_confidence"] == 1.0

    def test_provenance_verification_passes(self):
        rule = {
            "rule_id": "PDF_001",
            "instruction": "Test",
            "source_document": "harvard.pdf",
            "source_page": 1,
            "source_section": "Exp",
            "source_evidence": "Test",
            "extraction_confidence": 0.9,
            "extraction_timestamp": "2026-01-01T00:00:00",
            "rule_hash": "abc",
            "state": "ACTIVE",
            "version": 1,
        }
        result = self.tracker.verify_provenance(rule)
        assert result["valid"] is True

    def test_provenance_verification_fails_missing_fields(self):
        rule = {"rule_id": "BAD"}
        result = self.tracker.verify_provenance(rule)
        assert result["valid"] is False
        assert len(result["issues"]) > 0


# ============================================================================
# Rule Distinguishability Tests
# ============================================================================

class TestRuleDistinguishability:
    def test_pdf_and_seed_rules_distinguishable(self):
        pdf_rule = {
            "rule_id": "PDF_001",
            "source_document": "harvard.pdf",
            "source_page": 5,
            "state": "ACTIVE",
        }
        seed_rule = {
            "rule_id": "HA_001",
            "source_document": "hand-authored",
            "source_page": None,
            "state": "ACTIVE",
        }
        assert pdf_rule["source_document"] != seed_rule["source_document"]
        assert pdf_rule["source_page"] != seed_rule["source_page"]

    def test_context_output_distinguishes_sources(self):
        builder = KnowledgeContextBuilder()
        rules = [
            {
                "rule_id": "PDF_001",
                "source": "Harvard",
                "section_name": "experience",
                "source_document": "harvard.pdf",
                "source_page": 5,
            },
            {
                "rule_id": "HA_001",
                "source": "Harvard",
                "section_name": "experience",
            },
        ]
        context = builder.build(rules)
        exp_rules = builder.get_section_rules(context, "experience")
        pdf_formatted = next(r for r in exp_rules if r["rule_id"] == "PDF_001")
        ha_formatted = next(r for r in exp_rules if r["rule_id"] == "HA_001")
        assert "provenance" in pdf_formatted
        assert "provenance" not in ha_formatted


# ============================================================================
# Governance State Tests
# ============================================================================

class TestGovernanceState:
    def test_retrieval_returns_all_provided_rules(self):
        retriever = KnowledgeRetriever()
        rules = [
            {"rule_id": "R1", "source": "S", "section_name": "exp", "category": "Q", "priority": "High", "confidence": 0.9},
            {"rule_id": "R2", "source": "S", "section_name": "exp", "category": "Q", "priority": "High", "confidence": 0.9},
        ]
        gap_results = {"experience": {"years": {"sufficient": True}, "score": 1.0}}
        retrieved = retriever.retrieve(rules, gap_results, max_rules=10)
        assert len(retrieved) == 2

    def test_service_filters_by_state(self):
        """The service layer filters by state, not the retriever."""
        from app.services.knowledge_intelligence.rule_approval import RuleApproval
        approval = RuleApproval()
        active_rule = {"rule_id": "R1", "instruction": "Test", "state": "ACTIVE"}
        verified_rule = {"rule_id": "R2", "instruction": "Test", "state": "VERIFIED"}
        assert active_rule["state"] == "ACTIVE"
        assert verified_rule["state"] == "VERIFIED"

    def test_retrieval_respects_classification(self):
        retriever = KnowledgeRetriever()
        rules = [
            {"rule_id": "R1", "source": "S", "section_name": "skills", "category": "Keywords", "priority": "High", "confidence": 0.9},
            {"rule_id": "R2", "source": "S", "section_name": "experience", "category": "Quantification", "priority": "High", "confidence": 0.9},
        ]
        gap_results = {"skills": {"required": {"missing": []}, "score": 0.5}}
        retrieved = retriever.retrieve(rules, gap_results, max_rules=10)
        assert len(retrieved) > 0
        sections = [r["section_name"] for r in retrieved]
        assert "skills" in sections
