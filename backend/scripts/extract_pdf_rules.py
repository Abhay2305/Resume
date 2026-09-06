"""PDF Rule Extraction Script.

Extracts structured knowledge rules from all 4 approved PDFs.
Each rule has full provenance: source document, page, section, confidence.

Approved PDFs:
  1. pdf/Harvard-resume-cover-letter-guide.pdf
  2. pdf/Yale resume guidance letter.pdf
  3. pdf/standord-resume-and-cover-letter-examples.pdf
  4. pdf/cover-letter-guidelines.pdf
"""
import json
import os
import sys

# Ensure backend is on the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.services.knowledge_intelligence.pdf_extractor import PDFExtractor
from app.services.knowledge_intelligence.rule_extractor_pdf import PDFRuleExtractor


PDF_DIR = os.path.join(os.path.dirname(backend_dir), "pdf")
OUTPUT_DIR = os.path.join(backend_dir, "app", "data", "pdf_rules")

APPROVED_PDFS = {
    "harvard": "Harvard-resume-cover-letter-guide.pdf",
    "yale": "Yale resume guidance letter.pdf",
    "stanford": "standord-resume-and-cover-letter-examples.pdf",
    "cover_letter": "cover-letter-guidelines.pdf",
}


def extract_rules_from_pdf(pdf_key: str, pdf_filename: str) -> dict:
    """Extract rules from a single approved PDF.

    Args:
        pdf_key: Short key for the PDF (harvard, yale, stanford, cover_letter).
        pdf_filename: Filename of the PDF.

    Returns:
        Dictionary with extraction results and rules.
    """
    pdf_path = os.path.join(PDF_DIR, pdf_filename)

    if not os.path.exists(pdf_path):
        return {"error": f"PDF not found: {pdf_path}", "rules": []}

    print(f"\n{'='*60}")
    print(f"Extracting: {pdf_filename}")
    print(f"{'='*60}")

    # Step 1: Extract text from PDF
    extractor = PDFExtractor()
    extraction_result = extractor.extract(pdf_path)

    if not extraction_result.success:
        return {"error": extraction_result.errors, "rules": []}

    print(f"  Pages: {extraction_result.total_pages}")
    print(f"  Words: {extraction_result.total_words}")

    # Step 2: Extract rules from text
    rule_extractor = PDFRuleExtractor()
    rules = rule_extractor.extract_rules_from_pdf(extraction_result)

    print(f"  Rules extracted: {len(rules)}")

    # Step 3: Add provenance to each rule
    for rule in rules:
        rule["source_document"] = pdf_filename
        rule["pdf_key"] = pdf_key
        # Provenance fields are already set by the extractor

    return {
        "pdf_key": pdf_key,
        "pdf_filename": pdf_filename,
        "total_pages": extraction_result.total_pages,
        "total_words": extraction_result.total_words,
        "file_hash": extraction_result.file_hash,
        "rules_count": len(rules),
        "rules": rules,
    }


def main():
    """Extract rules from all approved PDFs."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_results = {}
    total_rules = 0

    for pdf_key, pdf_filename in APPROVED_PDFS.items():
        result = extract_rules_from_pdf(pdf_key, pdf_filename)
        all_results[pdf_key] = result
        total_rules += result.get("rules_count", 0)

        # Save individual PDF rules
        output_file = os.path.join(OUTPUT_DIR, f"{pdf_key}_rules.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Saved to: {output_file}")

    # Save combined extraction report
    report_file = os.path.join(OUTPUT_DIR, "extraction_report.json")
    report = {
        "extraction_timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "pdfs_processed": len(APPROVED_PDFS),
        "total_rules_extracted": total_rules,
        "results": all_results,
    }
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"PDFs processed: {len(APPROVED_PDFS)}")
    print(f"Total rules extracted: {total_rules}")
    print(f"Report saved to: {report_file}")

    return all_results


if __name__ == "__main__":
    main()
