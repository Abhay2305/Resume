"""Analyze extracted PDF rules quality."""
import json
from collections import Counter

for pdf_key in ["harvard", "yale", "stanford", "cover_letter"]:
    with open(f"D:/contact/Resume-main/backend/app/data/pdf_rules/{pdf_key}_rules.json", encoding="utf-8") as f:
        data = json.load(f)
    rules = data["rules"]
    print(f"\n{'='*60}")
    print(f"{pdf_key.upper()} - {len(rules)} rules")
    print(f"{'='*60}")

    sections = Counter(r.get("section_name", "unknown") for r in rules)
    print("Sections:")
    for s, c in sections.most_common():
        print(f"  {s}: {c}")

    priorities = Counter(r.get("priority", "unknown") for r in rules)
    print("Priorities:")
    for p, c in priorities.most_common():
        print(f"  {p}: {c}")

    print("First 3 rules:")
    for i, r in enumerate(rules[:3]):
        inst = r.get("instruction", "")[:120]
        print(f"  {i+1}. [{r.get('section_name')}] [{r.get('priority')}] {inst}")
