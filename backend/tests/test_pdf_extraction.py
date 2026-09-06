"""Tests for PDF Text Extractor."""
import os
from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.services.knowledge_intelligence.pdf_extractor import (
    APPROVED_PDF_KEYS,
    APPROVED_PDFS,
    PageExtraction,
    PDFExtractionResult,
    PDFExtractor,
)


@pytest.fixture
def extractor():
    return PDFExtractor(pdf_root="pdf")


@pytest.fixture
def tmp_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake pdf content")
    return str(pdf_path)


class TestApprovedPDFs:
    def test_approved_pdfs_list_has_four(self):
        assert len(APPROVED_PDFS) == 4

    def test_approved_pdf_keys_has_four(self):
        assert len(APPROVED_PDF_KEYS) == 4

    def test_all_approved_paths_are_strings(self):
        for path in APPROVED_PDFS:
            assert isinstance(path, str)

    def test_all_keys_are_strings(self):
        for key in APPROVED_PDF_KEYS.values():
            assert isinstance(key, str)


class TestIsApproved:
    def test_harvard_approved(self, extractor):
        assert extractor.is_approved("pdf/Harvard-resume-cover-letter-guide.pdf")

    def test_yale_approved(self, extractor):
        assert extractor.is_approved("pdf/Yale resume guidance letter.pdf")

    def test_stanford_approved(self, extractor):
        assert extractor.is_approved("pdf/standord-resume-and-cover-letter-examples.pdf")

    def test_cover_letter_approved(self, extractor):
        assert extractor.is_approved("pdf/cover-letter-guidelines.pdf")

    def test_unapproved_rejected(self, extractor):
        assert not extractor.is_approved("pdf/unapproved.pdf")

    def test_random_file_rejected(self, extractor):
        assert not extractor.is_approved("some_other_path.pdf")

    def test_empty_string_rejected(self, extractor):
        assert not extractor.is_approved("")

    def test_partial_name_rejected(self, extractor):
        assert not extractor.is_approved("harvard.pdf")

    def test_path_with_spaces_approved(self, extractor):
        assert extractor.is_approved("C:/Users/admin/pdf/Yale resume guidance letter.pdf")


class TestGetDocumentKey:
    def test_harvard_key(self, extractor):
        assert extractor.get_document_key("pdf/Harvard-resume-cover-letter-guide.pdf") == "harvard"

    def test_yale_key(self, extractor):
        assert extractor.get_document_key("pdf/Yale resume guidance letter.pdf") == "yale"

    def test_stanford_key(self, extractor):
        assert extractor.get_document_key("pdf/standord-resume-and-cover-letter-examples.pdf") == "stanford"

    def test_cover_letter_key(self, extractor):
        assert extractor.get_document_key("pdf/cover-letter-guidelines.pdf") == "cover_letter"

    def test_unknown_falls_back_to_filename(self, extractor):
        key = extractor.get_document_key("pdf/My Custom Guide.pdf")
        assert key == "my_custom_guide"

    def test_backslash_path(self, extractor):
        assert extractor.get_document_key("pdf\\Harvard-resume-cover-letter-guide.pdf") == "harvard"


class TestCountWords:
    def test_empty(self, extractor):
        assert extractor._count_words("") == 0

    def test_single_word(self, extractor):
        assert extractor._count_words("hello") == 1

    def test_multiple_words(self, extractor):
        assert extractor._count_words("hello world test") == 3

    def test_whitespace_only(self, extractor):
        assert extractor._count_words("   ") == 0

    def test_extra_spaces(self, extractor):
        assert extractor._count_words("  hello   world  ") == 2


class TestExtract:
    def test_unapproved_pdf_rejected(self, extractor):
        result = extractor.extract("pdf/unapproved.pdf")
        assert result.success is False
        assert len(result.errors) == 1
        assert "Unapproved" in result.errors[0]

    def test_nonexistent_file_returns_error(self, extractor):
        result = extractor.extract("pdf/Harvard-resume-cover-letter-guide.pdf")
        assert result.success is False
        assert any("not found" in e.lower() or "failed" in e.lower() for e in result.errors)

    def test_unapproved_sets_document_key_empty(self, extractor):
        result = extractor.extract("pdf/random.pdf")
        assert result.document_key == ""

    def test_unapproved_sets_file_name(self, extractor):
        result = extractor.extract("pdf/random.pdf")
        assert result.file_name == "random.pdf"


class TestExtractAllApproved:
    def test_returns_four_results(self, extractor):
        results = extractor.extract_all_approved()
        assert len(results) == 4

    def test_all_have_document_keys(self, extractor):
        results = extractor.extract_all_approved()
        for r in results:
            assert r.document_key in ("harvard", "yale", "stanford", "cover_letter")


class TestPageExtraction:
    def test_page_extraction_dataclass(self):
        p = PageExtraction(page_number=1, text="hello", char_count=5, word_count=1)
        assert p.page_number == 1
        assert p.text == "hello"
        assert p.char_count == 5
        assert p.word_count == 1


class TestPDFExtractionResult:
    def test_initial_state(self):
        r = PDFExtractionResult(file_path="test.pdf", file_name="test.pdf", document_key="test")
        assert r.success is True
        assert r.total_pages == 0
        assert r.pages == []
        assert r.errors == []

    def test_to_dict(self):
        r = PDFExtractionResult(
            file_path="test.pdf",
            file_name="test.pdf",
            document_key="test",
            total_pages=1,
            total_chars=100,
            total_words=10,
        )
        d = r.to_dict()
        assert d["file_path"] == "test.pdf"
        assert d["total_pages"] == 1
        assert d["total_chars"] == 100
        assert d["total_words"] == 10
        assert isinstance(d["pages"], list)

    def test_to_dict_with_pages(self):
        r = PDFExtractionResult(
            file_path="test.pdf",
            file_name="test.pdf",
            document_key="test",
        )
        r.pages.append(PageExtraction(page_number=1, text="hello", char_count=5, word_count=1))
        d = r.to_dict()
        assert len(d["pages"]) == 1
        assert d["pages"][0]["page_number"] == 1
