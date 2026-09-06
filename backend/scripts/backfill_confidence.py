"""Backfill extraction_confidence for all PDF rules in the database.

The extractor stores confidence as 'confidence' but the DB column is
extraction_confidence. This script recalculates confidence from instruction
text using the same deterministic logic as _calculate_confidence().
"""
import re
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, init_db
from app.models.knowledge_intelligence import KnowledgeRule
from sqlalchemy import select, func


def calculate_confidence(instruction: str) -> float:
    """Replicate _calculate_confidence() from rule_extractor_pdf.py."""
    if not instruction:
        return 0.5
    confidence = 0.5
    if len(instruction) > 20:
        confidence += 0.1
    if len(instruction) > 50:
        confidence += 0.1
    # has_reason and has_examples not available from DB, use 0
    # These are extraction-time fields, not stored in instruction
    if any(kw in instruction.lower() for kw in ["should", "must", "always", "never"]):
        confidence += 0.05
    if "%" in instruction or re.search(r"\d+", instruction):
        confidence += 0.05
    return min(confidence, 1.0)


def backfill():
    init_db()
    session = SessionLocal()

    try:
        # Count rules needing backfill
        result = session.execute(
            select(func.count(KnowledgeRule.id)).where(
                KnowledgeRule.source != 'hand-authored',
                KnowledgeRule.extraction_confidence.is_(None)
            )
        )
        needs_backfill = result.scalar()
        print(f"Rules needing extraction_confidence backfill: {needs_backfill}")

        if needs_backfill == 0:
            print("No backfill needed.")
            return

        # Get all rules without extraction_confidence
        result = session.execute(
            select(KnowledgeRule).where(
                KnowledgeRule.source != 'hand-authored',
                KnowledgeRule.extraction_confidence.is_(None)
            )
        )
        rules = result.scalars().all()

        updated = 0
        for rule in rules:
            confidence = calculate_confidence(rule.instruction or "")
            rule.extraction_confidence = confidence
            updated += 1

        session.commit()
        print(f"Updated {updated} rules with extraction_confidence")

        # Verify
        result = session.execute(
            select(func.count(KnowledgeRule.id)).where(
                KnowledgeRule.source != 'hand-authored',
                KnowledgeRule.extraction_confidence.isnot(None)
            )
        )
        with_conf = result.scalar()
        print(f"Rules with extraction_confidence now: {with_conf}")

        # Show distribution
        result = session.execute(
            select(KnowledgeRule.extraction_confidence, func.count(KnowledgeRule.id))
            .where(KnowledgeRule.source != 'hand-authored')
            .group_by(KnowledgeRule.extraction_confidence)
        )
        print("\nConfidence distribution:")
        for conf, count in result.all():
            print(f"  {conf}: {count} rules")

    finally:
        session.close()


if __name__ == "__main__":
    backfill()
