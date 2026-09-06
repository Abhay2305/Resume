"""Verify mandatory knowledge rules exist in the database.

Checks that the 9 mandatory rule keys referenced by
KnowledgeIntelligenceService._get_all_active_rules() are present
with state=ACTIVE and is_active=True.

Usage:
    cd backend && python scripts/verify_mandatory_rules.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, init_db
from app.models.knowledge_intelligence import KnowledgeRule
from sqlalchemy import select

MANDATORY_KEYS = [
    "INT_BUL_001", "INT_BUL_002", "INT_BUL_003", "INT_BUL_004", "INT_BUL_005",
    "INT_VER_001", "INT_VER_002", "INT_PHR_001", "INT_PHR_002",
]


def verify():
    init_db()
    session = SessionLocal()

    try:
        print("=" * 60)
        print("MANDATORY RULES VERIFICATION")
        print("=" * 60)

        missing = []
        inactive = []

        for key in MANDATORY_KEYS:
            result = session.execute(
                select(KnowledgeRule).where(KnowledgeRule.rule_key == key)
            )
            rule = result.scalar_one_or_none()

            if rule is None:
                missing.append(key)
                print(f"  MISSING: {key}")
            elif rule.state != "ACTIVE" or not rule.is_active:
                inactive.append(key)
                print(f"  INACTIVE: {key} (state={rule.state}, is_active={rule.is_active})")
            else:
                print(f"  OK: {key} (state={rule.state}, is_active={rule.is_active})")

        print()
        print("=" * 60)
        if missing:
            print(f"FAIL: {len(missing)} mandatory rules missing: {missing}")
            print("Run: python scripts/migrate_shadow1_rules.py")
            sys.exit(1)
        elif inactive:
            print(f"WARN: {len(inactive)} mandatory rules not active: {inactive}")
            print("Rules exist but are not in ACTIVE state with is_active=True.")
            sys.exit(1)
        else:
            print(f"PASS: All {len(MANDATORY_KEYS)} mandatory rules present and active.")
            sys.exit(0)
    finally:
        session.close()


if __name__ == "__main__":
    verify()
