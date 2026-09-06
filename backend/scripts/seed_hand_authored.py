"""Seed 28 hand-authored rules into the database.

Uses the existing seed_hand_authored_rules() method from the knowledge
intelligence service. Rules are seeded as ACTIVE with proper provenance.
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, init_db
from app.models.knowledge_intelligence import KnowledgeRule, KnowledgeDocument
from app.services.knowledge_intelligence.rule_approval import RuleApproval
from sqlalchemy import select, func


def seed():
    init_db()
    session = SessionLocal()

    try:
        # Check if hand-authored rules already exist
        result = session.execute(
            select(func.count(KnowledgeRule.id)).where(
                KnowledgeRule.source == 'hand-authored'
            )
        )
        existing = result.scalar()
        print(f"Existing hand-authored rules in DB: {existing}")

        if existing > 0:
            print("Hand-authored rules already seeded. Skipping.")
            return

        # Find or create a document for hand-authored rules
        result = session.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.document_key == "hand_authored_rules"
            )
        )
        doc = result.scalar_one_or_none()

        if not doc:
            doc = KnowledgeDocument(
                document_key="hand_authored_rules",
                name="Hand-Authored Knowledge Rules",
                source="knowledge_rules.json",
                document_type="knowledge_base",
                version="1.0",
                description="28 hand-authored career-writing rules from Harvard, MIT, Yale, ATS, and Internal sources",
                confidence=1.0,
                is_active=True,
                total_rules=0,
            )
            session.add(doc)
            session.flush()
            print(f"Created document: {doc.id}")

        # Use RuleApproval to seed the rules
        rule_approval = RuleApproval()
        seed_rules = rule_approval.load_seed_rules_from_json()
        print(f"Loaded {len(seed_rules)} rules from knowledge_rules.json")

        if not seed_rules:
            print("No seed rules found.")
            return

        seeded = rule_approval.seed_hand_authored_rules(seed_rules)
        print(f"Prepared {len(seeded)} rules for seeding")

        # Check for duplicates by rule_key
        existing_keys = set()
        result = session.execute(select(KnowledgeRule.rule_key))
        for row in result:
            existing_keys.add(row[0])

        inserted = 0
        skipped = 0
        for rule in seeded:
            rule_key = rule.get("rule_id", "")
            if rule_key in existing_keys:
                skipped += 1
                print(f"  Skipped duplicate: {rule_key}")
                continue

            rule_data = {
                "document_id": doc.id,
                "rule_key": rule_key,
                "source": rule.get("source", "hand-authored"),
                "section_name": rule.get("section_name", "general"),
                "priority": rule.get("priority", "medium"),
                "category": rule.get("category", "General"),
                "instruction": rule.get("instruction", ""),
                "reason": rule.get("reason", ""),
                "examples": rule.get("examples", []),
                "confidence": 1.0,
                "is_active": True,
                "source_document": "hand-authored",
                "source_page": None,
                "source_evidence": None,
                "extraction_confidence": 1.0,
                "extraction_timestamp": rule.get("extraction_timestamp"),
                "rule_hash": rule.get("rule_hash"),
                "state": "ACTIVE",
                "version": 1,
            }
            new_rule = KnowledgeRule(**rule_data)
            session.add(new_rule)
            inserted += 1
            existing_keys.add(rule_key)

        session.commit()
        print(f"\nInserted {inserted} hand-authored rules")
        print(f"Skipped {skipped} duplicates")

        # Verify
        result = session.execute(
            select(func.count(KnowledgeRule.id)).where(
                KnowledgeRule.source == 'hand-authored'
            )
        )
        total = result.scalar()
        print(f"Total hand-authored rules in DB: {total}")

        # Update document total
        doc.total_rules = total
        session.commit()

    finally:
        session.close()


if __name__ == "__main__":
    seed()
