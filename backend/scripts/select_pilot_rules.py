"""Pilot Activation Script.

Selects ~50 high-confidence rules from extracted PDF rules for pilot activation.
Uses deterministic criteria based on actual stored metadata.

Criteria:
1. State = VERIFIED
2. extraction_confidence >= 0.7
3. Has valid source_document
4. Has valid source_page (not None)
5. Has valid extraction_timestamp
6. Has valid rule_hash
7. No duplicate instruction text
8. Balanced across source PDFs
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


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

        pdf_key = data.get("pdf_key", filename.replace("_rules.json", ""))
        rules = data.get("rules", [])
        for rule in rules:
            rule["pdf_key"] = pdf_key
        all_rules.extend(rules)

    return all_rules


def select_pilot_rules(all_rules, target_count=50):
    """Select pilot rules using deterministic criteria.

    Rules in the JSON files are in DISCOVERED state (raw extraction).
    After ingestion via ingest_pdf_rules(), they become VERIFIED.
    This script selects rules that WILL be eligible after ingestion.

    Args:
        all_rules: All extracted PDF rules.
        target_count: Target number of rules to select.

    Returns:
        List of selected rules and a selection report.
    """
    # Step 1: Filter by basic eligibility
    # Rules in JSON are DISCOVERED; after ingestion they become VERIFIED
    # We select rules that will be eligible for VERIFIED → APPROVED → ACTIVE
    eligible = []
    for rule in all_rules:
        # State check: rules in JSON are DISCOVERED (pre-ingestion)
        state = rule.get("state", "DISCOVERED")
        if state not in ("DISCOVERED", "VERIFIED"):
            continue
        # Confidence: some rules have None, others have float
        confidence = rule.get("extraction_confidence")
        if confidence is not None and confidence < 0.7:
            continue
        # If confidence is None, we still include (will be assigned default during ingestion)
        if not rule.get("source_document"):
            continue
        if rule.get("source_page") is None:
            continue
        if not rule.get("extraction_timestamp"):
            continue
        if not rule.get("rule_hash"):
            continue
        eligible.append(rule)

    print(f"Step 1: {len(eligible)} rules pass basic eligibility (from {len(all_rules)} total)")

    # Step 2: Remove duplicates by instruction text
    seen_instructions = set()
    unique = []
    for rule in eligible:
        instruction = rule.get("instruction", "").strip().lower()
        if instruction and instruction not in seen_instructions:
            seen_instructions.add(instruction)
            unique.append(rule)

    print(f"Step 2: {len(unique)} rules after deduplication")

    # Step 3: Sort by confidence (descending), then by source_page (ascending)
    unique.sort(key=lambda r: (
        -r.get("extraction_confidence", 0),
        r.get("source_page", 999),
    ))

    # Step 4: Balance across source PDFs (max 15 per source)
    by_pdf = defaultdict(list)
    for rule in unique:
        by_pdf[rule["pdf_key"]].append(rule)

    selected = []
    per_pdf_limit = max(5, target_count // 4 + 5)  # ~15 per PDF

    for pdf_key in ["harvard", "yale", "stanford", "cover_letter"]:
        pdf_rules = by_pdf.get(pdf_key, [])
        selected.extend(pdf_rules[:per_pdf_limit])
        print(f"  {pdf_key}: selected {min(len(pdf_rules), per_pdf_limit)} from {len(pdf_rules)} eligible")

    # Step 5: Trim to target count
    selected = selected[:target_count]

    # Step 6: Generate selection report
    report = {
        "total_extracted": len(all_rules),
        "eligible": len(eligible),
        "after_dedup": len(unique),
        "selected_count": len(selected),
        "target_count": target_count,
        "selection_criteria": {
            "state": "DISCOVERED or VERIFIED (pre-ingestion)",
            "min_confidence": ">= 0.7 or None (default during ingestion)",
            "requires_source_document": True,
            "requires_source_page": True,
            "requires_extraction_timestamp": True,
            "requires_rule_hash": True,
        },
        "by_source": defaultdict(int),
        "selected_rules": [],
    }

    for rule in selected:
        report["by_source"][rule["pdf_key"]] += 1
        report["selected_rules"].append({
            "rule_id": rule.get("rule_id"),
            "source_document": rule.get("source_document"),
            "source_page": rule.get("source_page"),
            "instruction": rule.get("instruction", "")[:100],
            "confidence": rule.get("extraction_confidence"),
            "section": rule.get("section_name"),
            "category": rule.get("category"),
        })

    report["by_source"] = dict(report["by_source"])

    return selected, report


def main():
    """Run pilot selection and output report."""
    print("=" * 60)
    print("PILOT RULE SELECTION")
    print("=" * 60)

    all_rules = load_all_pdf_rules()
    print(f"\nTotal rules loaded: {len(all_rules)}")

    selected, report = select_pilot_rules(all_rules, target_count=50)

    print(f"\n{'=' * 60}")
    print(f"SELECTION RESULT: {report['selected_count']} rules selected")
    print(f"{'=' * 60}")

    print(f"\nBy source:")
    for source, count in report["by_source"].items():
        print(f"  {source}: {count}")

    print("\nSelected rule IDs:")
    for rule in report["selected_rules"]:
        try:
            inst = rule['instruction'][:60].encode('ascii', 'replace').decode('ascii')
            print(f"  {rule['rule_id']} (p.{rule['source_page']}, conf={rule['confidence']}) - {inst}...")
        except Exception:
            print(f"  {rule['rule_id']} (p.{rule['source_page']}, conf={rule['confidence']})")

    # Save report
    report_path = Path(__file__).parent.parent / "app" / "data" / "pdf_rules" / "pilot_selection_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to: {report_path}")

    return report


if __name__ == "__main__":
    main()
