"""PDF Text Extractor.

Extracts text from approved PDF files using pdfplumber with page-level granularity.
Only the 4 approved PDFs are accepted. Unapproved PDFs are rejected at ingestion time.

Approved PDFs:
  1. pdf/Harvard-resume-cover-letter-guide.pdf
  2. pdf/Yale resume guidance letter.pdf
  3. pdf/standord-resume-and-cover-letter-examples.pdf
  4. pdf/cover-letter-guidelines.pdf
"""
import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pdfplumber

logger = logging.getLogger(__name__)

APPROVED_PDFS = [
    "pdf/Harvard-resume-cover-letter-guide.pdf",
    "pdf/Yale resume guidance letter.pdf",
    "pdf/standord-resume-and-cover-letter-examples.pdf",
    "pdf/cover-letter-guidelines.pdf",
]

APPROVED_PDF_KEYS = {
    "harvard": "pdf/Harvard-resume-cover-letter-guide.pdf",
    "yale": "pdf/Yale resume guidance letter.pdf",
    "stanford": "pdf/standord-resume-and-cover-letter-examples.pdf",
    "cover_letter": "pdf/cover-letter-guidelines.pdf",
}


@dataclass
class PageExtraction:
    """Text extracted from a single PDF page."""
    page_number: int
    text: str
    char_count: int
    word_count: int


@dataclass
class PDFExtractionResult:
    """Result of extracting text from a PDF file."""
    file_path: str
    file_name: str
    document_key: str
    pages: List[PageExtraction] = field(default_factory=list)
    total_pages: int = 0
    total_chars: int = 0
    total_words: int = 0
    file_hash: str = ""
    extraction_timestamp: str = ""
    success: bool = True
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "document_key": self.document_key,
            "total_pages": self.total_pages,
            "total_chars": self.total_chars,
            "total_words": self.total_words,
            "file_hash": self.file_hash,
            "extraction_timestamp": self.extraction_timestamp,
            "success": self.success,
            "errors": self.errors,
            "pages": [
                {
                    "page_number": p.page_number,
                    "text": p.text,
                    "char_count": p.char_count,
                    "word_count": p.word_count,
                }
                for p in self.pages
            ],
        }


class PDFExtractor:
    """Extracts text from approved PDF files using pdfplumber."""

    def __init__(self, pdf_root: Optional[str] = None):
        if pdf_root is None:
            pdf_root = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                "pdf",
            )
        self.pdf_root = pdf_root

    def is_approved(self, file_path: str) -> bool:
        normalized = file_path.replace("\\", "/")
        for approved in APPROVED_PDFS:
            if normalized.endswith(approved) or normalized.endswith(os.path.basename(approved)):
                return True
        return False

    def get_document_key(self, file_path: str) -> str:
        normalized = file_path.replace("\\", "/")
        for key, approved_path in APPROVED_PDF_KEYS.items():
            if normalized.endswith(os.path.basename(approved_path)):
                return key
        return os.path.splitext(os.path.basename(file_path))[0].lower().replace(" ", "_")

    def _compute_file_hash(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def extract(self, file_path: str) -> PDFExtractionResult:
        if not self.is_approved(file_path):
            return PDFExtractionResult(
                file_path=file_path,
                file_name=os.path.basename(file_path),
                document_key="",
                success=False,
                errors=[f"Unapproved PDF: {os.path.basename(file_path)}"],
            )

        document_key = self.get_document_key(file_path)
        result = PDFExtractionResult(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            document_key=document_key,
            extraction_timestamp=datetime.utcnow().isoformat(),
        )

        try:
            result.file_hash = self._compute_file_hash(file_path)
        except OSError as e:
            result.errors.append(f"Failed to compute file hash: {e}")

        try:
            with pdfplumber.open(file_path) as pdf:
                result.total_pages = len(pdf.pages)
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text() or ""
                        page_extraction = PageExtraction(
                            page_number=i + 1,
                            text=text,
                            char_count=len(text),
                            word_count=self._count_words(text),
                        )
                        result.pages.append(page_extraction)
                        result.total_chars += page_extraction.char_count
                        result.total_words += page_extraction.word_count
                    except Exception as e:
                        result.errors.append(f"Failed to extract page {i + 1}: {e}")
                        logger.warning("Failed to extract page %d from %s: %s", i + 1, file_path, e)
        except Exception as e:
            result.success = False
            result.errors.append(f"Failed to open PDF: {e}")
            logger.error("Failed to open PDF %s: %s", file_path, e)

        if result.errors and result.pages:
            result.success = True

        return result

    def extract_all_approved(self) -> List[PDFExtractionResult]:
        results = []
        for approved_path in APPROVED_PDFS:
            full_path = os.path.join(self.pdf_root, os.path.basename(approved_path))
            if os.path.exists(full_path):
                results.append(self.extract(full_path))
            else:
                results.append(PDFExtractionResult(
                    file_path=full_path,
                    file_name=os.path.basename(approved_path),
                    document_key=self.get_document_key(approved_path),
                    success=False,
                    errors=[f"PDF file not found: {full_path}"],
                ))
        return results
