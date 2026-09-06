"""Tests for PDF Rule Extractor."""
import pytest

from app.services.knowledge_intelligence.pdf_extractor import PageExtraction, PDFExtractionResult
from app.services.knowledge_intelligence.rule_extractor_pdf import PDFRuleExtractor


@pytest.fixture
def extractor():
    return PDFRuleExtractor()


@pytest.fixture
def sample_page_text():
    return (
        "Resume Writing Tips\n"
        "Always start your resume with a strong professional summary.\n"
        "Use quantified achievements: 'Increased sales by 25% in Q3'.\n"
        "Never use first person pronouns like 'I' or 'my'.\n"
        "Keep your summary to 3-4 lines or 50-75 words.\n"
        "Include technical keywords from the job description.\n"
    )


@pytest.fixture
def sample_extraction_result():
    return PDFExtractionResult(
        file_path="pdf/Harvard-resume-cover-letter-guide.pdf",
        file_name="Harvard-resume-cover-letter-guide.pdf",
        document_key="harvard",
        pages=[
            PageExtraction(
                page_number=1,
                text=(
                    "Resume Summary Guidelines\n"
                    "Always tailor your summary to each specific job application.\n"
                    "Keep your summary to 3-4 lines or 50-75 words.\n"
                    "Lead with your strongest qualification.\n"
                ),
                char_count=150,
                word_count=25,
            ),
            PageExtraction(
                page_number=2,
                text=(
                    "Experience Section\n"
                    "Quantify accomplishments whenever possible.\n"
                    "Start each bullet point with a strong action verb.\n"
                    "Focus on results and impact rather than responsibilities.\n"
                ),
                char_count=150,
                word_count=25,
            ),
        ],
        total_pages=2,
        total_chars=300,
        total_words=50,
        file_hash="abc123",
        extraction_timestamp="2026-01-01T00:00:00",
        success=True,
    )


class TestComputeRuleHash:
    def test_same_instruction_same_hash(self, extractor):
        h1 = extractor._compute_rule_hash("Always use strong action verbs")
        h2 = extractor._compute_rule_hash("Always use strong action verbs")
        assert h1 == h2

    def test_different_instruction_different_hash(self, extractor):
        h1 = extractor._compute_rule_hash("Always use strong action verbs")
        h2 = extractor._compute_rule_hash("Never use first person pronouns")
        assert h1 != h2

    def test_hash_is_string(self, extractor):
        h = extractor._compute_rule_hash("test instruction")
        assert isinstance(h, str)
        assert len(h) == 16


class TestDetectSection:
    def test_summary(self, extractor):
        assert extractor._detect_section("Resume Summary Guidelines") == "summary"

    def test_experience(self, extractor):
        assert extractor._detect_section("Work Experience section") == "experience"

    def test_skills(self, extractor):
        assert extractor._detect_section("Technical Skills") == "skills"

    def test_education(self, extractor):
        assert extractor._detect_section("Education and degree") == "education"

    def test_projects(self, extractor):
        assert extractor._detect_section("Personal projects and portfolio") == "projects"

    def test_certifications(self, extractor):
        assert extractor._detect_section("Professional certifications") == "certifications"

    def test_formatting(self, extractor):
        assert extractor._detect_section("Document formatting guidelines") == "formatting"

    def test_ats(self, extractor):
        assert extractor._detect_section("ATS applicant tracking system") == "ats"

    def test_cover_letter(self, extractor):
        assert extractor._detect_section("Cover letter writing tips") == "cover_letter"

    def test_unknown_defaults_to_general(self, extractor):
        assert extractor._detect_section("Some random text") == "general"

    def test_surrounding_text_affects_detection(self, extractor):
        section = extractor._detect_section("Use numbers", "The experience section should")
        assert section == "experience"


class TestDetectDomain:
    def test_resume(self, extractor):
        assert extractor._detect_domain("Resume writing tips") == "resume"

    def test_cover_letter(self, extractor):
        assert extractor._detect_domain("Cover letter opening paragraph") == "cover_letter"

    def test_ats(self, extractor):
        assert extractor._detect_domain("ATS keyword optimization") == "ats"

    def test_skills(self, extractor):
        assert extractor._detect_domain("Technical skills and technologies") == "skills"

    def test_experience(self, extractor):
        assert extractor._detect_domain("Work experience and roles") == "experience"

    def test_education(self, extractor):
        assert extractor._detect_domain("Education and degree") == "education"

    def test_formatting(self, extractor):
        assert extractor._detect_domain("Font and layout formatting") == "formatting"

    def test_quantification(self, extractor):
        assert extractor._detect_domain("Metrics and percentage achievements") == "quantification"

    def test_unknown_defaults_to_resume(self, extractor):
        assert extractor._detect_domain("Some random text") == "resume"


class TestDetectCategory:
    def test_quantification(self, extractor):
        assert extractor._detect_category("Use numbers and percentages") == "Quantification"

    def test_action_verbs(self, extractor):
        assert extractor._detect_category("Start with strong action verbs") == "Action Verbs"

    def test_impact(self, extractor):
        assert extractor._detect_category("Focus on impact and results") == "Impact"

    def test_keywords(self, extractor):
        assert extractor._detect_category("Include ATS keywords") == "Keywords"

    def test_tailoring(self, extractor):
        assert extractor._detect_category("Tailor your resume to the job") == "Tailoring"

    def test_relevance(self, extractor):
        assert extractor._detect_category("Content should be relevant to position") in ("Relevance", "Tailoring")

    def test_clarity(self, extractor):
        assert extractor._detect_category("Be clear and concise") == "Clarity"

    def test_specificity(self, extractor):
        assert extractor._detect_category("Use specific details and examples") == "Specificity"

    def test_length(self, extractor):
        assert extractor._detect_category("Keep it short and brief") == "Length"

    def test_formatting(self, extractor):
        assert extractor._detect_category("Use proper font and style") == "Formatting"

    def test_unknown_defaults_to_general(self, extractor):
        assert extractor._detect_category("Some text") == "General"


class TestDetectPriority:
    def test_critical(self, extractor):
        assert extractor._detect_priority("You must never use first person") == "Critical"

    def test_high(self, extractor):
        assert extractor._detect_priority("You should quantify achievements") == "High"

    def test_medium(self, extractor):
        assert extractor._detect_priority("Group skills by category for readability") == "Medium"

    def test_low(self, extractor):
        assert extractor._detect_priority("You may optionally include GPA") == "Low"

    def test_critical_always(self, extractor):
        assert extractor._detect_priority("Always start with action verbs") == "Critical"

    def test_critical_never(self, extractor):
        assert extractor._detect_priority("Never exceed two pages") == "Critical"


class TestExtractInstruction:
    def test_bulleted(self, extractor):
        assert extractor._extract_instruction("- Use strong verbs") == "Use strong verbs"

    def test_numbered(self, extractor):
        assert extractor._extract_instruction("1) Start with summary") == "Start with summary"

    def test_starred(self, extractor):
        assert extractor._extract_instruction("* Be specific") == "Be specific"

    def test_lowercase_start_capitalized(self, extractor):
        result = extractor._extract_instruction("always tailor your resume")
        assert result[0].isupper()

    def test_already_capitalized(self, extractor):
        assert extractor._extract_instruction("Always quantify achievements") == "Always quantify achievements"


class TestExtractReason:
    def test_because_pattern(self, extractor):
        reason = extractor._extract_reason("Use numbers because they add credibility")
        assert reason is not None
        assert "because" in reason.lower()

    def test_helps_pattern(self, extractor):
        reason = extractor._extract_reason("This helps recruiters scan quickly")
        assert reason is not None

    def test_no_reason(self, extractor):
        reason = extractor._extract_reason("Use strong verbs")
        assert reason is None


class TestExtractExamples:
    def test_quotes(self, extractor):
        examples = extractor._extract_examples('Write "Increased sales by 25%"')
        assert len(examples) >= 1
        assert "Increased sales by 25%" in examples

    def test_such_as(self, extractor):
        examples = extractor._extract_examples("Use tools such as Python and JavaScript")
        assert len(examples) >= 1

    def test_for_example(self, extractor):
        examples = extractor._extract_examples("For example, use metrics like 25% increase")
        assert len(examples) >= 1

    def test_no_examples(self, extractor):
        examples = extractor._extract_examples("Use strong verbs")
        assert len(examples) == 0

    def test_max_three(self, extractor):
        text = '"a", "b", "c", "d"'
        examples = extractor._extract_examples(text)
        assert len(examples) <= 3


class TestCalculateConfidence:
    def test_short_text_low_confidence(self, extractor):
        c = extractor._calculate_confidence("short", False, False)
        assert c < 0.8

    def test_long_text_higher_confidence(self, extractor):
        c = extractor._calculate_confidence("A" * 60, True, True)
        assert c >= 0.8

    def test_with_reason_increases(self, extractor):
        c_no = extractor._calculate_confidence("test instruction here", False, False)
        c_yes = extractor._calculate_confidence("test instruction here", True, False)
        assert c_yes > c_no

    def test_with_examples_increases(self, extractor):
        c_no = extractor._calculate_confidence("test instruction here", False, False)
        c_yes = extractor._calculate_confidence("test instruction here", False, True)
        assert c_yes > c_no

    def test_max_is_one(self, extractor):
        c = extractor._calculate_confidence("A" * 100, True, True)
        assert c <= 1.0


class TestCreateRule:
    def test_rule_has_all_fields(self, extractor):
        rule = extractor._create_rule(
            instruction="Always quantify achievements",
            source_document="test.pdf",
            source_page=1,
            source_evidence="Use numbers to quantify achievements",
        )
        required_fields = [
            "rule_id", "source_document", "source_page", "source_section",
            "source_evidence", "rule_type", "domain", "priority", "category",
            "section_name", "instruction", "reason", "examples", "confidence",
            "extraction_timestamp", "rule_hash", "state", "version",
        ]
        for field in required_fields:
            assert field in rule, f"Missing field: {field}"

    def test_rule_state_is_discovered(self, extractor):
        rule = extractor._create_rule(
            instruction="Test", source_document="test.pdf",
            source_page=1, source_evidence="Test evidence",
        )
        assert rule["state"] == "DISCOVERED"

    def test_rule_version_is_one(self, extractor):
        rule = extractor._create_rule(
            instruction="Test", source_document="test.pdf",
            source_page=1, source_evidence="Test evidence",
        )
        assert rule["version"] == 1

    def test_rule_has_rule_id(self, extractor):
        rule = extractor._create_rule(
            instruction="Test instruction here",
            source_document="test.pdf",
            source_page=1,
            source_evidence="Test evidence text",
        )
        assert rule["rule_id"].startswith("PDF_")

    def test_rule_confidence_is_float(self, extractor):
        rule = extractor._create_rule(
            instruction="Test", source_document="test.pdf",
            source_page=1, source_evidence="Test evidence",
        )
        assert isinstance(rule["confidence"], float)

    def test_rule_hash_matches_instruction(self, extractor):
        rule = extractor._create_rule(
            instruction="Always quantify achievements",
            source_document="test.pdf",
            source_page=1,
            source_evidence="Use numbers",
        )
        expected_hash = extractor._compute_rule_hash("Always quantify achievements")
        assert rule["rule_hash"] == expected_hash


class TestExtractRulesFromPage:
    def test_extracts_rules(self, extractor, sample_page_text):
        rules = extractor.extract_rules_from_page(
            sample_page_text, 1, "test.pdf"
        )
        assert len(rules) > 0

    def test_rules_have_unique_hashes(self, extractor, sample_page_text):
        rules = extractor.extract_rules_from_page(
            sample_page_text, 1, "test.pdf"
        )
        hashes = [r["rule_hash"] for r in rules]
        assert len(hashes) == len(set(hashes))

    def test_empty_page(self, extractor):
        rules = extractor.extract_rules_from_page("", 1, "test.pdf")
        assert rules == []

    def test_short_lines_skipped(self, extractor):
        rules = extractor.extract_rules_from_page("Hi\nOK\nGo", 1, "test.pdf")
        assert rules == []


class TestExtractRulesFromPdf:
    def test_extracts_from_multiple_pages(self, extractor, sample_extraction_result):
        rules = extractor.extract_rules_from_pdf(sample_extraction_result)
        assert len(rules) > 0

    def test_rules_deduplicated_across_pages(self, extractor):
        result = PDFExtractionResult(
            file_path="test.pdf",
            file_name="test.pdf",
            document_key="test",
            pages=[
                PageExtraction(1, "Always quantify achievements with numbers", 40, 6),
                PageExtraction(2, "Always quantify achievements with numbers", 40, 6),
            ],
        )
        rules = extractor.extract_rules_from_pdf(result)
        hashes = [r["rule_hash"] for r in rules]
        assert len(hashes) == len(set(hashes))


class TestExtractRulesFromAll:
    def test_extracts_from_multiple_pdfs(self, extractor):
        results = [
            PDFExtractionResult(
                file_path="pdf/Harvard-resume-cover-letter-guide.pdf",
                file_name="Harvard-resume-cover-letter-guide.pdf",
                document_key="harvard",
                pages=[PageExtraction(1, "Always quantify achievements", 30, 4)],
                success=True,
            ),
            PDFExtractionResult(
                file_path="pdf/Yale resume guidance letter.pdf",
                file_name="Yale resume guidance letter.pdf",
                document_key="yale",
                pages=[PageExtraction(1, "Never use first person pronouns", 30, 5)],
                success=True,
            ),
        ]
        rules = extractor.extract_rules_from_all(results)
        assert len(rules) >= 2

    def test_skips_failed_extractions(self, extractor):
        results = [
            PDFExtractionResult(
                file_path="test.pdf",
                file_name="test.pdf",
                document_key="test",
                success=False,
                errors=["Failed"],
            ),
        ]
        rules = extractor.extract_rules_from_all(results)
        assert rules == []

    def test_deduplicates_across_pdfs(self, extractor):
        results = [
            PDFExtractionResult(
                file_path="pdf/Harvard-resume-cover-letter-guide.pdf",
                file_name="Harvard-resume-cover-letter-guide.pdf",
                document_key="harvard",
                pages=[PageExtraction(1, "Always quantify achievements", 30, 4)],
                success=True,
            ),
            PDFExtractionResult(
                file_path="pdf/Yale resume guidance letter.pdf",
                file_name="Yale resume guidance letter.pdf",
                document_key="yale",
                pages=[PageExtraction(1, "Always quantify achievements", 30, 4)],
                success=True,
            ),
        ]
        rules = extractor.extract_rules_from_all(results)
        hashes = [r["rule_hash"] for r in rules]
        assert len(hashes) == len(set(hashes))
