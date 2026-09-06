"""Migrate SHADOW-1 hardcoded career knowledge into governed KnowledgeRule DB.

Phase 2 of SHADOW-1 Remediation: creates new KnowledgeRule entries for all
career-writing instructions currently hardcoded in templates.py, rules_engine.py,
and other files.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, ".")

from app.database import SessionLocal, init_db
from app.models.knowledge_intelligence import KnowledgeDocument, KnowledgeRule
from sqlalchemy import func, select


def _hash_instruction(instruction: str) -> str:
    return hashlib.sha256(instruction.encode("utf-8")).hexdigest()


# ── New rules to create (from execution spec Phase 2.1–2.3) ──────────────

NEW_RULES = [
    # ── Core Writing Principles (INT_BUL_001–005) ──
    {
        "rule_key": "INT_BUL_001",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Bullet Structure",
        "priority": "High",
        "instruction": "Every bullet must explain: WHAT was built, HOW it was built, with WHAT technologies, and WHAT measurable impact it had.",
        "reason": "Ensures bullets cover all four dimensions of a strong resume bullet.",
    },
    {
        "rule_key": "INT_BUL_002",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Tone",
        "priority": "Medium",
        "instruction": "Write like an experienced software engineer, not a marketer.",
        "reason": "Technical hiring managers prefer specific, technical descriptions over marketing language.",
    },
    {
        "rule_key": "INT_BUL_003",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Evidence",
        "priority": "High",
        "instruction": "Every claim must be backed by evidence or specific details.",
        "reason": "Vague claims reduce credibility; specific details demonstrate real experience.",
    },
    {
        "rule_key": "INT_BUL_004",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Conciseness",
        "priority": "Medium",
        "instruction": "Stay under 2 lines (200 characters max) per bullet point.",
        "reason": "Recruiters scan resumes quickly; concise bullets are more impactful.",
    },
    {
        "rule_key": "INT_BUL_005",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Style",
        "priority": "High",
        "instruction": "Avoid vague or marketing-style statements. Be specific and technical.",
        "reason": "Specificity demonstrates genuine experience and technical competence.",
    },
    # ── Cover Letter Principles (INT_CL_003–008) ──
    {
        "rule_key": "INT_CL_003",
        "source": "Platform Internal",
        "section_name": "Cover Letter",
        "category": "Personalization",
        "priority": "High",
        "instruction": "Open with why you are excited about THIS company specifically.",
        "reason": "Generic openings fail to demonstrate genuine interest in the company.",
    },
    {
        "rule_key": "INT_CL_004",
        "source": "Platform Internal",
        "section_name": "Cover Letter",
        "category": "Examples",
        "priority": "High",
        "instruction": "Use 2-3 concrete examples from your resume.",
        "reason": "Concrete examples provide evidence of qualifications.",
    },
    {
        "rule_key": "INT_CL_005",
        "source": "Platform Internal",
        "section_name": "Cover Letter",
        "category": "Closing",
        "priority": "Medium",
        "instruction": "Close with a forward-looking statement.",
        "reason": "Forward-looking statements show enthusiasm and initiative.",
    },
    {
        "rule_key": "INT_CL_006",
        "source": "Platform Internal",
        "section_name": "Cover Letter",
        "category": "Personalization",
        "priority": "High",
        "instruction": "Avoid generic templates - each letter must feel personalized.",
        "reason": "Generic templates are easily detected and reduce impact.",
    },
    {
        "rule_key": "INT_CL_007",
        "source": "Platform Internal",
        "section_name": "Cover Letter",
        "category": "Formatting",
        "priority": "Medium",
        "instruction": "Keep the cover letter under 400 words (1 page).",
        "reason": "Lengthy cover letters are rarely read in full.",
    },
    {
        "rule_key": "INT_CL_008",
        "source": "Platform Internal",
        "section_name": "Cover Letter",
        "category": "Tone",
        "priority": "Medium",
        "instruction": "Use a professional but warm tone.",
        "reason": "Balance between professionalism and approachability is key for cover letters.",
    },
    # ── Summary Principles (INT_SUM_002–005) ──
    {
        "rule_key": "INT_SUM_002",
        "source": "Platform Internal",
        "section_name": "Summary",
        "category": "Structure",
        "priority": "High",
        "instruction": "Open your summary with your professional identity.",
        "reason": "Immediately communicates who you are and what you do.",
    },
    {
        "rule_key": "INT_SUM_003",
        "source": "Platform Internal",
        "section_name": "Summary",
        "category": "Impact",
        "priority": "High",
        "instruction": "Highlight your most impressive technical achievement.",
        "reason": "Leads with the strongest qualification to capture attention.",
    },
    {
        "rule_key": "INT_SUM_004",
        "source": "Platform Internal",
        "section_name": "Summary",
        "category": "Value",
        "priority": "Medium",
        "instruction": "Show what value you bring to the employer.",
        "reason": "Focuses on employer benefit rather than personal goals.",
    },
    {
        "rule_key": "INT_SUM_005",
        "source": "Platform Internal",
        "section_name": "Summary",
        "category": "Structure",
        "priority": "Medium",
        "instruction": "End your summary with what you are looking for.",
        "reason": "Provides clear direction and intent to the reader.",
    },
    # ── ATS Principles (INT_ATS_001–005) ──
    {
        "rule_key": "INT_ATS_001",
        "source": "Platform Internal",
        "section_name": "ATS",
        "category": "Optimization",
        "priority": "High",
        "instruction": "Optimize for Applicant Tracking Systems (ATS) by using standard section headings and relevant keywords.",
        "reason": "ATS systems parse standard headings to categorize content.",
    },
    {
        "rule_key": "INT_ATS_002",
        "source": "Platform Internal",
        "section_name": "ATS",
        "category": "Formatting",
        "priority": "High",
        "instruction": "Use standard section headings (Summary, Experience, Education, Skills).",
        "reason": "Non-standard headings may not be parsed correctly by ATS.",
    },
    {
        "rule_key": "INT_ATS_003",
        "source": "Platform Internal",
        "section_name": "ATS",
        "category": "Scoring",
        "priority": "Medium",
        "instruction": "A professional summary should be at least 30 words for optimal ATS scoring.",
        "reason": "ATS systems score summary length as a completeness indicator.",
    },
    {
        "rule_key": "INT_ATS_004",
        "source": "Platform Internal",
        "section_name": "ATS",
        "category": "Scoring",
        "priority": "Medium",
        "instruction": "Include at least 5 relevant technical skills for optimal ATS scoring.",
        "reason": "ATS systems score skill count as a completeness indicator.",
    },
    {
        "rule_key": "INT_ATS_005",
        "source": "Platform Internal",
        "section_name": "ATS",
        "category": "Scoring",
        "priority": "Medium",
        "instruction": "Include quantified achievements (percentages, dollar amounts, metrics) in experience bullets.",
        "reason": "Quantified achievements are scored higher by ATS and human reviewers.",
    },
    # ── Text Improvement Principles (INT_TXT_001–003) ──
    {
        "rule_key": "INT_TXT_001",
        "source": "Platform Internal",
        "section_name": "Formatting",
        "category": "Tone",
        "priority": "Medium",
        "instruction": "Use professional business language in all written content.",
        "reason": "Professional language maintains credibility and readability.",
    },
    {
        "rule_key": "INT_TXT_002",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Content",
        "priority": "Medium",
        "instruction": "Include specific achievements and skills relevant to the role.",
        "reason": "Relevance increases the impact of written content.",
    },
    {
        "rule_key": "INT_TXT_003",
        "source": "Platform Internal",
        "section_name": "Formatting",
        "category": "Conciseness",
        "priority": "Medium",
        "instruction": "Keep written content concise (3-4 paragraphs for letters).",
        "reason": "Concise content is more likely to be read in full.",
    },
    # ── Vocabulary List KnowledgeRules (INT_VER_001–002, INT_PHR_001–002) ──
    {
        "rule_key": "INT_VER_001",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Action Verbs",
        "priority": "High",
        "instruction": "Start every bullet point with a strong action verb.",
        "reason": "Action verbs demonstrate initiative and make descriptions more dynamic.",
        "examples": [
            "developed", "implemented", "designed", "architected", "built",
            "created", "optimized", "reduced", "increased", "improved",
            "enhanced", "streamlined", "automated", "engineered", "deployed",
            "migrated", "refactored", "scaled", "led", "managed",
            "directed", "coordinated", "supervised", "mentored", "analyzed",
            "evaluated", "assessed", "identified", "resolved", "diagnosed",
            "configured", "integrated", "established", "launched", "delivered",
            "shipped", "orchestrated", "spearheaded", "pioneered", "championed",
            "facilitated", "eliminated", "minimized", "maximized", "accelerated",
            "authored", "documented", "presented", "collaborated", "partnered",
            "researched", "investigated", "explored", "discovered", "validated",
        ],
    },
    {
        "rule_key": "INT_VER_002",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Weak Verbs",
        "priority": "High",
        "instruction": "Avoid weak verbs that reduce impact.",
        "reason": "Weak verbs make accomplishments sound less impressive.",
        "examples": [
            "helped", "worked", "was", "had", "did", "made", "got", "used",
            "responsible for", "tasked with", "involved in", "participated in",
            "assisted with", "contributed to", "supported", "handled",
        ],
    },
    {
        "rule_key": "INT_PHR_001",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Vague Phrases",
        "priority": "High",
        "instruction": "Avoid vague or marketing-style phrases without evidence.",
        "reason": "Vague phrases are red flags for recruiters and hiring managers.",
        "examples": [
            "team player", "self-starter", "go-getter", "results-driven",
            "detail-oriented", "problem solver", "critical thinker",
            "excellent communication", "strong work ethic", "fast learner",
            "passionate", "dedicated", "motivated", "enthusiastic",
            "synergy", "leverage", "ecosystem", "paradigm",
        ],
    },
    {
        "rule_key": "INT_PHR_002",
        "source": "Platform Internal",
        "section_name": "Experience",
        "category": "Generic Phrases",
        "priority": "High",
        "instruction": "Avoid generic phrases that lack specificity.",
        "reason": "Generic phrases fail to demonstrate specific accomplishments.",
        "examples": [
            "various tasks", "multiple projects", "different areas",
            "many responsibilities", "several initiatives", "diverse projects",
            "wide range", "broad experience", "extensive knowledge",
        ],
    },
]


def migrate():
    init_db()
    session = SessionLocal()

    try:
        # Find or create document for internal rules
        result = session.execute(
            select(KnowledgeDocument).where(
                KnowledgeDocument.document_key == "shadow1_internal_rules"
            )
        )
        doc = result.scalar_one_or_none()

        if not doc:
            doc = KnowledgeDocument(
                document_key="shadow1_internal_rules",
                name="SHADOW-1 Internal Knowledge Rules",
                source="platform-internal",
                document_type="knowledge_base",
                version="1.0",
                description="Career-writing rules migrated from hardcoded system prompts per SHADOW-1 remediation",
                confidence=1.0,
                is_active=True,
                total_rules=0,
            )
            session.add(doc)
            session.flush()
            print(f"Created document: {doc.id}")

        # Check existing keys
        existing_keys = set()
        result = session.execute(select(KnowledgeRule.rule_key))
        for row in result:
            existing_keys.add(row[0])

        # Also check existing instructions to avoid duplicates
        existing_instructions = set()
        result = session.execute(
            select(KnowledgeRule.instruction).where(
                KnowledgeRule.state == "ACTIVE"
            )
        )
        for row in result:
            existing_instructions.add(row[0].strip().lower())

        now = datetime.now(timezone.utc).isoformat()
        inserted = 0
        skipped_key = 0
        skipped_instruction = 0
        failed = 0

        for rule_def in NEW_RULES:
            rule_key = rule_def["rule_key"]
            instruction = rule_def["instruction"]

            if rule_key in existing_keys:
                skipped_key += 1
                print(f"  Skipped (key exists): {rule_key}")
                continue

            if instruction.strip().lower() in existing_instructions:
                skipped_instruction += 1
                print(f"  Skipped (instruction exists): {rule_key}")
                continue

            try:
                examples = rule_def.get("examples")
                examples_json = json.dumps(examples) if examples else None

                rule_data = {
                    "document_id": doc.id,
                    "rule_key": rule_key,
                    "source": rule_def["source"],
                    "section_name": rule_def["section_name"],
                    "priority": rule_def["priority"],
                    "category": rule_def["category"],
                    "instruction": instruction,
                    "reason": rule_def.get("reason", ""),
                    "examples": examples_json,
                    "confidence": 1.0,
                    "is_active": True,
                    "source_document": "hand-authored",
                    "source_page": None,
                    "source_evidence": None,
                    "extraction_confidence": 1.0,
                    "extraction_timestamp": now,
                    "rule_hash": _hash_instruction(instruction),
                    "state": "ACTIVE",
                    "version": 1,
                }

                new_rule = KnowledgeRule(**rule_data)
                session.add(new_rule)
                inserted += 1
                existing_keys.add(rule_key)
                existing_instructions.add(instruction.strip().lower())
                print(f"  Inserted: {rule_key}")

            except Exception as e:
                failed += 1
                print(f"  FAILED: {rule_key} — {e}")

        session.commit()

        # Update document total
        result = session.execute(
            select(func.count(KnowledgeRule.id)).where(
                KnowledgeRule.source_document == "hand-authored"
            )
        )
        total = result.scalar()
        doc.total_rules = total
        session.commit()

        print(f"\n{'='*60}")
        print(f"SHADOW-1 Migration Complete")
        print(f"  Inserted:       {inserted}")
        print(f"  Skipped (key):  {skipped_key}")
        print(f"  Skipped (text): {skipped_instruction}")
        print(f"  Failed:         {failed}")
        print(f"  Total hand-authored rules in DB: {total}")
        print(f"{'='*60}")

    except Exception as e:
        session.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
