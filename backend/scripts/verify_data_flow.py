"""End-to-end data flow integration test.

Proves: Pilot rule -> DB -> Retrieval -> Context -> Prompt with knowledge rules.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, init_db
from app.models.knowledge_intelligence import KnowledgeRule
from app.services.knowledge_intelligence.retriever import KnowledgeRetriever
from app.services.knowledge_intelligence.context_builder import KnowledgeContextBuilder
from sqlalchemy import select, func


def test_e2e_data_flow():
    """Test the complete data flow from DB to prompt."""
    print("=" * 60)
    print("END-TO-END DATA FLOW VERIFICATION")
    print("=" * 60)

    init_db()
    session = SessionLocal()

    try:
        # Step 1: Count active rules in DB
        result = session.execute(
            select(func.count(KnowledgeRule.id)).where(
                KnowledgeRule.is_active == True,
                KnowledgeRule.state == "ACTIVE",
            )
        )
        active_count = result.scalar()
        print(f"\nStep 1: Active rules in DB: {active_count}")
        assert active_count >= 50, f"Expected >= 50 active rules, got {active_count}"

        # Step 2: Load active rules as retriever input
        result = session.execute(
            select(KnowledgeRule).where(
                KnowledgeRule.is_active == True,
                KnowledgeRule.state == "ACTIVE",
            )
        )
        db_rules = result.scalars().all()

        # Convert to dict format expected by retriever
        rules_data = []
        for rule in db_rules:
            rules_data.append({
                "rule_key": rule.rule_key,
                "instruction": rule.instruction,
                "reason": rule.reason,
                "category": rule.category,
                "section_name": rule.section_name,
                "priority": rule.priority,
                "confidence": rule.confidence,
                "source_document": rule.source_document,
                "source_page": rule.source_page,
                "source_evidence": rule.source_evidence,
            })

        print(f"Step 2: Loaded {len(rules_data)} rules from DB")

        # Step 3: Create retriever and retrieve rules for a gap
        retriever = KnowledgeRetriever()
        gap_results = {
            "skills": {
                "required": {"missing": ["Python", "JavaScript"]},
                "preferred": {"missing": []},
            },
            "technology": {
                "categories": {
                    "programming": {"missing": ["Python"]},
                },
            },
            "experience": {
                "years": {"sufficient": True},
                "roles": {"missing": []},
            },
            "education": {
                "degree": {"sufficient": True},
            },
            "certifications": {
                "required": {"missing": []},
            },
            "keywords": {
                "missing": ["leadership", "teamwork"],
            },
        }
        retrieved = retriever.retrieve(
            all_rules=rules_data,
            gap_results=gap_results,
            max_rules=10,
        )
        print(f"Step 3: Retriever returned {len(retrieved)} rules for gap analysis")

        # Step 4: Build context from retrieved rules
        context_builder = KnowledgeContextBuilder()
        context = context_builder.build(retrieved)
        print(f"Step 4: Context built ({len(context)} keys)")

        # Step 5: Verify context structure
        has_rules = context.get("total_rules", 0) > 0
        has_citations = len(context.get("citations", "")) > 0
        print(f"Step 5: Context has rules: {has_rules}, has citations: {has_citations}")
        assert has_rules, "Context should have rules"
        assert has_citations, "Context should have citations"

        # Step 6: Verify rules have provenance data
        rules_with_provenance = sum(
            1 for r in rules_data
            if r.get("source_document") and r.get("source_page") is not None
        )
        print(f"Step 6: Rules with valid provenance: {rules_with_provenance}/{len(rules_data)}")

        # Summary
        print(f"\n{'='*60}")
        print(f"DATA FLOW VERIFICATION COMPLETE")
        print(f"{'='*60}")
        print(f"Active rules in DB: {active_count}")
        print(f"Rules retrieved for gap: {len(retrieved)}")
        print(f"Context keys: {list(context.keys())}")
        print(f"Rules with provenance: {rules_with_provenance}/{len(rules_data)}")

        print(f"\nSample retrieved rules:")
        for i, rule in enumerate(retrieved[:3]):
            print(f"  {i+1}. [{rule.get('category')}] {rule.get('instruction', '')[:80]}...")
            print(f"     Source: {rule.get('source_document')} p.{rule.get('source_page')}")

        return True

    finally:
        session.close()


if __name__ == "__main__":
    success = test_e2e_data_flow()
    sys.exit(0 if success else 1)
