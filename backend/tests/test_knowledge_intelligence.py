"""Unit tests for Knowledge Intelligence Engine.

Tests:
  - KnowledgeRuleExtractor
  - KnowledgeIndexer
  - KnowledgeRanker
  - KnowledgeRetriever
  - KnowledgeContextBuilder
"""
import json
import pytest
from unittest.mock import MagicMock

from app.services.knowledge_intelligence.rule_extractor import KnowledgeRuleExtractor
from app.services.knowledge_intelligence.indexer import KnowledgeIndexer
from app.services.knowledge_intelligence.ranker import KnowledgeRanker
from app.services.knowledge_intelligence.retriever import KnowledgeRetriever
from app.services.knowledge_intelligence.context_builder import KnowledgeContextBuilder


# ============================================================================
# KnowledgeRuleExtractor Tests
# ============================================================================

class TestKnowledgeRuleExtractor:
    def setup_method(self):
        self.extractor = KnowledgeRuleExtractor()

    def test_extract_from_document(self):
        rules = self.extractor.extract_from_document("harvard_resume")
        assert len(rules) > 0
        assert all("rule_id" in r for r in rules)

    def test_extract_from_unknown_document(self):
        rules = self.extractor.extract_from_document("unknown_doc")
        assert rules == []

    def test_extract_by_section(self):
        rules = self.extractor.extract_by_section("Experience")
        assert len(rules) > 0
        assert all(r["section"] == "Experience" for r in rules)

    def test_extract_by_category(self):
        rules = self.extractor.extract_by_category("Quantification")
        assert len(rules) > 0
        assert all(r["category"] == "Quantification" for r in rules)

    def test_extract_by_priority(self):
        rules = self.extractor.extract_by_priority("High")
        assert len(rules) > 0
        assert all(r["priority"] == "High" for r in rules)

    def test_extract_all(self):
        rules = self.extractor.extract_all()
        assert len(rules) > 10

    def test_get_available_documents(self):
        docs = self.extractor.get_available_documents()
        assert "harvard_resume" in docs
        assert "ats" in docs

    def test_normalize_rule(self):
        rule = {
            "rule_id": "TEST_001",
            "source": "Test Source",
            "section": "Skills",
            "priority": "High",
            "category": "Keywords",
            "instruction": "Test instruction",
            "reason": "Test reason",
            "examples": ["Example 1", "Example 2"],
        }
        normalized = self.extractor.normalize_rule(rule)
        assert normalized["rule_id"] == "TEST_001"
        assert normalized["section_name"] == "Skills"
        assert isinstance(normalized["examples"], str)


# ============================================================================
# KnowledgeIndexer Tests
# ============================================================================

class TestKnowledgeIndexer:
    def setup_method(self):
        self.indexer = KnowledgeIndexer()
        self.sample_rules = [
            {"rule_id": "R1", "source": "Harvard", "section_name": "Experience", "category": "Quantification", "priority": "High", "instruction": "Quantify accomplishments", "reason": "Improves credibility"},
            {"rule_id": "R2", "source": "MIT", "section_name": "Skills", "category": "Keywords", "priority": "Medium", "instruction": "Include technical keywords", "reason": "ATS optimization"},
            {"rule_id": "R3", "source": "Yale", "section_name": "Summary", "category": "Clarity", "priority": "Low", "instruction": "Keep summary concise", "reason": "Recruiter attention span"},
        ]

    def test_build_indexes(self):
        indexes = self.indexer.build_indexes(self.sample_rules)
        assert "Experience" in indexes["by_section"]
        assert "Quantification" in indexes["by_category"]
        assert "High" in indexes["by_priority"]
        assert "Harvard" in indexes["by_source"]

    def test_get_by_section(self):
        self.indexer.build_indexes(self.sample_rules)
        rules = self.indexer.get_by_section("Experience")
        assert len(rules) == 1

    def test_get_by_category(self):
        self.indexer.build_indexes(self.sample_rules)
        rules = self.indexer.get_by_category("Keywords")
        assert len(rules) == 1

    def test_get_by_priority(self):
        self.indexer.build_indexes(self.sample_rules)
        rules = self.indexer.get_by_priority("High")
        assert len(rules) == 1

    def test_get_by_source(self):
        self.indexer.build_indexes(self.sample_rules)
        rules = self.indexer.get_by_source("Harvard")
        assert len(rules) == 1

    def test_get_sections_for_gap(self):
        sections = self.indexer.get_sections_for_gap(["skills", "experience"])
        assert "skills" in sections
        assert "experience" in sections

    def test_get_categories_for_action(self):
        categories = self.indexer.get_categories_for_action("add_skill")
        assert "keywords" in categories

    def test_get_index_stats(self):
        self.indexer.build_indexes(self.sample_rules)
        stats = self.indexer.get_index_stats()
        assert stats["sections"] > 0


# ============================================================================
# KnowledgeRanker Tests
# ============================================================================

class TestKnowledgeRanker:
    def setup_method(self):
        self.ranker = KnowledgeRanker()
        self.sample_rules = [
            {"rule_id": "R1", "source": "Harvard", "section_name": "Experience", "category": "Quantification", "priority": "High", "confidence": 0.9},
            {"rule_id": "R2", "source": "MIT", "section_name": "Skills", "category": "Keywords", "priority": "Medium", "confidence": 0.85},
            {"rule_id": "R3", "source": "Yale", "section_name": "Summary", "category": "Clarity", "priority": "Low", "confidence": 0.9},
        ]

    def test_rank_by_category(self):
        ranked = self.ranker.rank(
            self.sample_rules,
            gap_categories=["experience"],
            gap_actions=["highlight_experience"],
        )
        assert len(ranked) == 3
        assert ranked[0]["_relevance_score"] >= ranked[-1]["_relevance_score"]

    def test_rank_by_action(self):
        ranked = self.ranker.rank(
            self.sample_rules,
            gap_categories=["skills"],
            gap_actions=["add_skill"],
        )
        assert len(ranked) == 3

    def test_rank_with_source_confidence(self):
        ranked = self.ranker.rank(
            self.sample_rules,
            gap_categories=[],
            gap_actions=[],
            source_confidence={"Harvard": 0.95},
        )
        assert len(ranked) == 3
        harvard_rule = next(r for r in ranked if r["source"] == "Harvard")
        assert harvard_rule["_relevance_score"] > 0

    def test_get_top_rules(self):
        ranked = self.ranker.rank(
            self.sample_rules,
            gap_categories=["experience"],
            gap_actions=[],
        )
        top = self.ranker.get_top_rules(ranked, max_rules=2)
        assert len(top) == 2

    def test_filter_by_section(self):
        ranked = self.ranker.rank(
            self.sample_rules,
            gap_categories=[],
            gap_actions=[],
        )
        filtered = self.ranker.filter_by_section(ranked, "Experience")
        assert len(filtered) == 1
        assert filtered[0]["section_name"] == "Experience"


# ============================================================================
# KnowledgeRetriever Tests
# ============================================================================

class TestKnowledgeRetriever:
    def setup_method(self):
        self.retriever = KnowledgeRetriever()
        self.sample_rules = [
            {"rule_id": "R1", "source": "Harvard", "section_name": "Experience", "category": "Quantification", "priority": "High", "confidence": 0.9},
            {"rule_id": "R2", "source": "MIT", "section_name": "Skills", "category": "Keywords", "priority": "Medium", "confidence": 0.85},
            {"rule_id": "R3", "source": "Yale", "section_name": "Summary", "category": "Clarity", "priority": "Low", "confidence": 0.9},
            {"rule_id": "R4", "source": "ATS", "section_name": "Skills", "category": "Keywords", "priority": "Critical", "confidence": 0.85},
        ]

    def test_retrieve(self):
        gap_results = {
            "skills": {"required": {"missing": ["Python"], "matched": []}, "score": 0.5},
            "experience": {"years": {"sufficient": True}, "score": 1.0},
        }
        rules = self.retriever.retrieve(self.sample_rules, gap_results, max_rules=3)
        assert len(rules) <= 3

    def test_retrieve_empty_gap(self):
        gap_results = {}
        rules = self.retriever.retrieve(self.sample_rules, gap_results, max_rules=10)
        assert len(rules) <= 10

    def test_get_section_rules(self):
        rules = self.retriever.get_section_rules(self.sample_rules, "Experience")
        assert len(rules) == 1
        assert rules[0]["section_name"] == "Experience"


# ============================================================================
# KnowledgeContextBuilder Tests
# ============================================================================

class TestKnowledgeContextBuilder:
    def setup_method(self):
        self.builder = KnowledgeContextBuilder()
        self.sample_rules = [
            {"rule_id": "R1", "source": "Harvard", "section_name": "Experience", "category": "Quantification", "priority": "High", "instruction": "Quantify", "reason": "Credibility", "examples": "[\"Example 1\"]"},
            {"rule_id": "R2", "source": "MIT", "section_name": "Skills", "category": "Keywords", "priority": "Medium", "instruction": "Keywords", "reason": "ATS", "examples": "[]"},
        ]

    def test_build(self):
        context = self.builder.build(self.sample_rules)
        assert "experience_rules" in context
        assert "skills_rules" in context
        assert context["total_rules"] == 2

    def test_build_empty(self):
        context = self.builder.build([])
        assert context["total_rules"] == 0

    def test_get_section_rules(self):
        context = self.builder.build(self.sample_rules)
        exp_rules = self.builder.get_section_rules(context, "experience")
        assert len(exp_rules) == 1

    def test_get_all_rules(self):
        context = self.builder.build(self.sample_rules)
        all_rules = self.builder.get_all_rules(context)
        assert len(all_rules) == 2

    def test_get_citations(self):
        context = self.builder.build(self.sample_rules)
        citations = self.builder.get_citations(context)
        assert "Harvard" in citations
        assert "MIT" in citations

    def test_format_rule(self):
        rule = {"rule_id": "R1", "source": "Harvard", "section_name": "Exp", "priority": "High", "category": "Test", "instruction": "Do this", "reason": "Because", "examples": "[\"ex1\"]"}
        formatted = self.builder._format_rule(rule)
        assert formatted["rule_id"] == "R1"
        assert isinstance(formatted["examples"], list)
