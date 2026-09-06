"""Ingest PDF rules into the database.

This script ingests all 500 extracted PDF rules into the knowledge_rules table.
Rules start at state=VERIFIED, is_active=False.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, init_db
from app.models.knowledge_intelligence import KnowledgeRule, KnowledgeDocument
from sqlalchemy import select, func


def load_all_pdf_rules():
    """Load all rules from the 4 PDF extraction files."""
    data_dir = Path(__file__).parent.parent / "app" / "data" / "pdf_rules"
    all_rules = []

    for filename in ["harvard_rules.json", "yale_rules.json",
                      "stanford_rules.json", "cover_letter_rules.json"]:
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"WARNING: {filepath} not found")
            continue

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        rules = data.get("rules", [])
        all_rules.extend(rules)

    return all_rules


def ingest_rules():
    """Ingest all PDF rules into the database."""
    print("=" * 60)
    print("PDF RULE INGESTION")
    print("=" * 60)

    # Load rules
    all_rules = load_all_pdf_rules()
    print(f"Loaded {len(all_rules)} rules from PDF files")

    # Init DB
    init_db()
    session = SessionLocal()

    try:
        # Check existing rules
        result = session.execute(select(func.count(KnowledgeRule.id)))
        existing_count = result.scalar()
        print(f"Existing rules in database: {existing_count}")

        if existing_count > 0:
            print("Rules already exist. Skipping ingestion.")
            return

        # Create a document record for the PDF rules
        doc = KnowledgeDocument(
            document_key="pdf_knowledge_base",
            name="PDF Knowledge Base (Harvard, Yale, Stanford, Cover Letter)",
            source="pdf_extraction",
            document_type="knowledge_base",
            version="1.0",
            description="Knowledge rules extracted from 4 approved PDF documents",
            confidence=0.8,
            is_active=True,
            total_rules=len(all_rules),
        )
        session.add(doc)
        session.flush()  # Get the document ID
        document_id = doc.id
        print(f"Created document record: {document_id}")

        # Ingest rules
        ingested = 0
        for rule in all_rules:
            rule_data = {
                "document_id": document_id,
                "rule_key": rule.get("rule_id", ""),
                "source": rule.get("source_document", "unknown"),
                "section_name": rule.get("section_name", "general"),
                "priority": rule.get("priority", "medium"),
                "category": rule.get("category", "General"),
                "instruction": rule.get("instruction", ""),
                "reason": rule.get("reason", ""),
                "examples": rule.get("examples", []),
                "confidence": rule.get("confidence", 0.8),
                "is_active": False,
                "source_document": rule.get("source_document"),
                "source_page": rule.get("source_page"),
                "source_evidence": rule.get("source_evidence"),
                "extraction_confidence": rule.get("extraction_confidence"),
                "extraction_timestamp": rule.get("extraction_timestamp"),
                "rule_hash": rule.get("rule_hash"),
                "state": "VERIFIED",
                "version": 1,
            }
            new_rule = KnowledgeRule(**rule_data)
            session.add(new_rule)
            ingested += 1

        session.commit()
        print(f"\nIngested {ingested} rules into database")

        # Verify
        result = session.execute(select(func.count(KnowledgeRule.id)))
        total = result.scalar()
        print(f"Total rules in database: {total}")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    ingest_rules()
