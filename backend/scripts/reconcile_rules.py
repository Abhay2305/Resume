"""Rule Reconciliation Script.

Compares extracted PDF rules against existing hand-authored rules.
Identifies duplicates, conflicts, equivalents, and ambiguous rules.
Produces a reconciliation report without silently resolving conflicts.
"""
import json
import os
import sys
from collections import defaultdict
from difflib import SequenceMatcher

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def load_hand_authored_rules():
    """Load existing hand-authored rules from knowledge_rules.json."""
    rules_path = os.path.join(backend_dir, "app", "data", "knowledge_rules.json")
    with open(rules_path, encoding="utf-8") as f:
        data = json.load(f)

    all_rules = []
    for doc_key, doc_rules in data.items():
        if isinstance(doc_rules, list):
            for rule in doc_rules:
                rule["source_type"] = "hand-authored"
                rule["source_document_key"] = doc_key
                all_rules.append(rule)
    return all_rules


def load_extracted_rules():
    """Load all extracted PDF rules."""
    pdf_dir = os.path.join(backend_dir, "app", "data", "pdf_rules")
    all_rules = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith("_rules.json") and filename != "extraction_report.json":
            with open(os.path.join(pdf_dir, filename), encoding="utf-8") as f:
                data = json.load(f)
                for rule in data.get("rules", []):
                    rule["source_type"] = "pdf-extracted"
                    all_rules.append(rule)
    return all_rules


def similarity(a, b):
    """Calculate text similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def reconcile_rules(hand_authored, extracted):
    """Compare hand-authored and extracted rules.

    Returns:
        Dictionary with reconciliation results.
    """
    report = {
        "hand_authored_count": len(hand_authored),
        "extracted_count": len(extracted),
        "duplicates": [],
        "conflicts": [],
        "equivalents": [],
        "ambiguous": [],
        "unique_hand_authored": [],
        "unique_extracted": [],
    }

    # Check each hand-authored rule against extracted rules
    for ha_rule in hand_authored:
        ha_instruction = ha_rule.get("instruction", "").strip()
        ha_source = ha_rule.get("source", "")

        best_match = None
        best_score = 0.0

        for ex_rule in extracted:
            ex_instruction = ex_rule.get("instruction", "").strip()
            score = similarity(ha_instruction, ex_instruction)

            if score > best_score:
                best_score = score
                best_match = ex_rule

        if best_score >= 0.85:
            # High similarity - likely duplicate
            report["duplicates"].append({
                "hand_authored": {
                    "instruction": ha_instruction[:100],
                    "source": ha_source,
                    "section": ha_rule.get("section_name", ""),
                },
                "extracted": {
                    "instruction": best_match.get("instruction", "")[:100],
                    "source_document": best_match.get("source_document", ""),
                    "page": best_match.get("source_page", ""),
                    "section": best_match.get("section_name", ""),
                },
                "similarity": round(best_score, 3),
                "resolution": "PENDING - manual review required",
            })
        elif best_score >= 0.6:
            # Moderate similarity - equivalent rule
            report["equivalents"].append({
                "hand_authored": {
                    "instruction": ha_instruction[:100],
                    "source": ha_source,
                },
                "extracted": {
                    "instruction": best_match.get("instruction", "")[:100],
                    "source_document": best_match.get("source_document", ""),
                    "page": best_match.get("source_page", ""),
                },
                "similarity": round(best_score, 3),
                "resolution": "PENDING - manual review required",
            })
        elif best_score >= 0.4:
            # Low similarity - potentially conflicting
            # Check if they address the same section
            ha_section = ha_rule.get("section_name", "")
            ex_section = best_match.get("section_name", "")
            if ha_section == ex_section:
                report["conflicts"].append({
                    "hand_authored": {
                        "instruction": ha_instruction[:100],
                        "source": ha_source,
                        "section": ha_section,
                    },
                    "extracted": {
                        "instruction": best_match.get("instruction", "")[:100],
                        "source_document": best_match.get("source_document", ""),
                        "page": best_match.get("source_page", ""),
                        "section": ex_section,
                    },
                    "similarity": round(best_score, 3),
                    "resolution": "PENDING - manual review required",
                })
            else:
                report["unique_hand_authored"].append({
                    "instruction": ha_instruction[:100],
                    "source": ha_source,
                    "section": ha_section,
                })
        else:
            report["unique_hand_authored"].append({
                "instruction": ha_instruction[:100],
                "source": ha_source,
                "section": ha_rule.get("section_name", ""),
            })

    # Find extracted rules not matching any hand-authored rule
    matched_extracted = set()
    for dup in report["duplicates"]:
        matched_extracted.add(dup["extracted"]["instruction"])
    for eq in report["equivalents"]:
        matched_extracted.add(eq["extracted"]["instruction"])
    for conf in report["conflicts"]:
        matched_extracted.add(conf["extracted"]["instruction"])

    for ex_rule in extracted:
        ex_inst = ex_rule.get("instruction", "")[:100]
        if ex_inst not in matched_extracted:
            report["unique_extracted"].append({
                "instruction": ex_inst,
                "source_document": ex_rule.get("source_document", ""),
                "page": ex_rule.get("source_page", ""),
                "section": ex_rule.get("section_name", ""),
            })

    return report


def main():
    """Run reconciliation."""
    print("Loading hand-authored rules...")
    hand_authored = load_hand_authored_rules()
    print(f"  Loaded {len(hand_authored)} hand-authored rules")

    print("Loading extracted PDF rules...")
    extracted = load_extracted_rules()
    print(f"  Loaded {len(extracted)} extracted rules")

    print("\nRunning reconciliation...")
    report = reconcile_rules(hand_authored, extracted)

    # Save report
    report_path = os.path.join(backend_dir, "app", "data", "pdf_rules", "reconciliation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print("RECONCILIATION REPORT")
    print(f"{'='*60}")
    print(f"Hand-authored rules: {report['hand_authored_count']}")
    print(f"Extracted rules: {report['extracted_count']}")
    print(f"Duplicates: {len(report['duplicates'])}")
    print(f"Conflicts: {len(report['conflicts'])}")
    print(f"Equivalents: {len(report['equivalents'])}")
    print(f"Unique hand-authored: {len(report['unique_hand_authored'])}")
    print(f"Unique extracted: {len(report['unique_extracted'])}")
    print(f"\nReport saved to: {report_path}")

    # Show some examples
    if report["duplicates"]:
        print(f"\n--- DUPLICATES (first 3) ---")
        for d in report["duplicates"][:3]:
            print(f"  HA: {d['hand_authored']['instruction'][:80]}")
            print(f"  EX: {d['extracted']['instruction'][:80]}")
            print(f"  Similarity: {d['similarity']}")
            print()

    if report["conflicts"]:
        print(f"--- CONFLICTS (first 3) ---")
        for c in report["conflicts"][:3]:
            print(f"  HA: {c['hand_authored']['instruction'][:80]}")
            print(f"  EX: {c['extracted']['instruction'][:80]}")
            print(f"  Similarity: {c['similarity']}")
            print()


if __name__ == "__main__":
    main()
