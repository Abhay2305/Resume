"""Tests for Rule Classifier."""
import pytest

from app.services.knowledge_intelligence.rule_classifier import RuleClassifier


@pytest.fixture
def classifier():
    return RuleClassifier()


def _make_rule(instruction, source_evidence="", source_section=""):
    return {
        "rule_id": "TEST_001",
        "instruction": instruction,
        "source_evidence": source_evidence,
        "source_section": source_section,
        "domain": "resume",
        "priority": "Medium",
        "category": "General",
        "section_name": "general",
    }


class TestScoreMatch:
    def test_empty_text(self, classifier):
        assert classifier._score_match("", ["keyword"]) == 0.0

    def test_match_found(self, classifier):
        assert classifier._score_match("use keywords effectively", ["keyword"]) > 0

    def test_no_match(self, classifier):
        assert classifier._score_match("some text", ["xyz"]) == 0.0

    def test_multiple_matches(self, classifier):
        score = classifier._score_match("use keywords and phrases", ["keyword", "phrase"])
        assert score >= 2.0

    def test_weight_applied(self, classifier):
        score = classifier._score_match("keyword", ["keyword"], weight=2.0)
        assert score == 2.0


class TestClassifyDomain:
    def test_quantification_domain(self, classifier):
        rule = _make_rule("Use numbers and percentages to show impact")
        assert classifier.classify_domain(rule) == "quantification"

    def test_ats_domain(self, classifier):
        rule = _make_rule("Optimize for ATS applicant tracking systems")
        assert classifier.classify_domain(rule) == "ats"

    def test_cover_letter_domain(self, classifier):
        rule = _make_rule("Write a compelling cover letter opening paragraph")
        assert classifier.classify_domain(rule) == "cover_letter"

    def test_skills_domain(self, classifier):
        rule = _make_rule("List your technical skills and proficiencies")
        assert classifier.classify_domain(rule) == "skills"

    def test_education_domain(self, classifier):
        rule = _make_rule("Include relevant coursework and GPA from university")
        assert classifier.classify_domain(rule) == "education"

    def test_formatting_domain(self, classifier):
        rule = _make_rule("Use consistent font and layout formatting")
        assert classifier.classify_domain(rule) == "formatting"

    def test_experience_domain(self, classifier):
        rule = _make_rule("Describe your work experience with action verbs")
        assert classifier.classify_domain(rule) == "experience"

    def test_resume_domain_default(self, classifier):
        rule = _make_rule("Write a professional resume document")
        assert classifier.classify_domain(rule) == "resume"

    def test_preserves_existing_if_no_match(self, classifier):
        rule = _make_rule("Do something unrelated to any domain")
        rule["domain"] = "custom"
        assert classifier.classify_domain(rule) == "custom"


class TestClassifySection:
    def test_summary_section(self, classifier):
        rule = _make_rule("Write a concise professional summary")
        assert classifier.classify_section(rule) == "summary"

    def test_experience_section(self, classifier):
        rule = _make_rule("Describe your work experience clearly")
        assert classifier.classify_section(rule) == "experience"

    def test_skills_section(self, classifier):
        rule = _make_rule("List your technical skills")
        assert classifier.classify_section(rule) == "skills"

    def test_education_section(self, classifier):
        rule = _make_rule("Include your education and degree information")
        assert classifier.classify_section(rule) == "education"

    def test_projects_section(self, classifier):
        rule = _make_rule("Describe your personal projects and portfolio")
        assert classifier.classify_section(rule) == "projects"

    def test_certifications_section(self, classifier):
        rule = _make_rule("List your professional certifications and credentials")
        assert classifier.classify_section(rule) == "certifications"

    def test_cover_letter_section(self, classifier):
        rule = _make_rule("Write a compelling cover letter")
        assert classifier.classify_section(rule) == "cover_letter"

    def test_preserves_existing_if_no_match(self, classifier):
        rule = _make_rule("Do something unrelated to any section")
        rule["section_name"] = "custom"
        assert classifier.classify_section(rule) == "custom"


class TestClassifyCategory:
    def test_quantification_category(self, classifier):
        rule = _make_rule("Use numbers and percentages to quantify results")
        assert classifier.classify_category(rule) == "Quantification"

    def test_action_verbs_category(self, classifier):
        rule = _make_rule("Start each bullet with a strong action verb")
        assert classifier.classify_category(rule) == "Action Verbs"

    def test_impact_category(self, classifier):
        rule = _make_rule("Focus on demonstrating your impact and results")
        assert classifier.classify_category(rule) == "Impact"

    def test_keywords_category(self, classifier):
        rule = _make_rule("Include relevant ATS keywords from the job description")
        assert classifier.classify_category(rule) == "Keywords"

    def test_tailoring_category(self, classifier):
        rule = _make_rule("Tailor your resume to the specific job target")
        assert classifier.classify_category(rule) == "Tailoring"

    def test_clarity_category(self, classifier):
        rule = _make_rule("Be clear and precise in your writing")
        assert classifier.classify_category(rule) == "Clarity"

    def test_length_category(self, classifier):
        rule = _make_rule("Keep your resume brief with appropriate word count")
        assert classifier.classify_category(rule) == "Length"

    def test_formatting_category(self, classifier):
        rule = _make_rule("Use proper font style and layout formatting")
        assert classifier.classify_category(rule) == "Formatting"

    def test_preserves_existing_if_no_match(self, classifier):
        rule = _make_rule("Write good content for your application")
        rule["category"] = "Custom"
        assert classifier.classify_category(rule) == "Custom"


class TestClassifyPriority:
    def test_critical_priority(self, classifier):
        rule = _make_rule("You must never use first person pronouns")
        assert classifier.classify_priority(rule) == "Critical"

    def test_high_priority(self, classifier):
        rule = _make_rule("You should quantify achievements")
        assert classifier.classify_priority(rule) == "High"

    def test_medium_priority(self, classifier):
        rule = _make_rule("It is a best practice to group skills")
        assert classifier.classify_priority(rule) == "Medium"

    def test_low_priority(self, classifier):
        rule = _make_rule("You may optionally include your GPA")
        assert classifier.classify_priority(rule) == "Low"

    def test_always_is_critical(self, classifier):
        rule = _make_rule("Always start with a strong summary")
        assert classifier.classify_priority(rule) == "Critical"

    def test_should_is_high(self, classifier):
        rule = _make_rule("Should include relevant keywords")
        assert classifier.classify_priority(rule) == "High"

    def test_preserves_existing_if_no_match(self, classifier):
        rule = _make_rule("Write good content for your application")
        rule["priority"] = "Custom"
        assert classifier.classify_priority(rule) == "Custom"


class TestClassifyRule:
    def test_classifies_all_fields(self, classifier):
        rule = _make_rule("Always quantify your achievements with specific numbers")
        classified = classifier.classify_rule(rule)
        assert classified["domain"] in ("quantification", "resume")
        assert classified["section_name"] in ("summary", "general", "ats")
        assert classified["category"] in ("Quantification", "Keywords", "General")
        assert classified["priority"] in ("Critical", "High", "Medium", "Low")

    def test_rule_type_set_to_classified(self, classifier):
        rule = _make_rule("Test instruction")
        classified = classifier.classify_rule(rule)
        assert classified["rule_type"] == "classified"

    def test_preserves_original_rule_id(self, classifier):
        rule = _make_rule("Test instruction")
        rule["rule_id"] = "CUSTOM_ID"
        classified = classifier.classify_rule(rule)
        assert classified["rule_id"] == "CUSTOM_ID"

    def test_does_not_mutate_original(self, classifier):
        rule = _make_rule("Test instruction")
        original_domain = rule["domain"]
        classifier.classify_rule(rule)
        assert rule["domain"] == original_domain


class TestClassifyRules:
    def test_classifies_multiple_rules(self, classifier):
        rules = [
            _make_rule("Use numbers"),
            _make_rule("Start with verbs"),
            _make_rule("Be concise"),
        ]
        classified = classifier.classify_rules(rules)
        assert len(classified) == len(rules)

    def test_all_rules_classified(self, classifier):
        rules = [_make_rule("Test instruction") for _ in range(3)]
        classified = classifier.classify_rules(rules)
        for rule in classified:
            assert rule["rule_type"] == "classified"

    def test_empty_list(self, classifier):
        assert classifier.classify_rules([]) == []


class TestGetClassificationStats:
    def test_stats_structure(self, classifier):
        rules = [_make_rule("Use numbers"), _make_rule("Be concise")]
        classified = classifier.classify_rules(rules)
        stats = classifier.get_classification_stats(classified)
        assert "total_rules" in stats
        assert "domains" in stats
        assert "sections" in stats
        assert "categories" in stats
        assert "priorities" in stats

    def test_total_rules_count(self, classifier):
        rules = [_make_rule("Test") for _ in range(5)]
        classified = classifier.classify_rules(rules)
        stats = classifier.get_classification_stats(classified)
        assert stats["total_rules"] == 5

    def test_empty_rules(self, classifier):
        stats = classifier.get_classification_stats([])
        assert stats["total_rules"] == 0
        assert stats["domains"] == {}

    def test_domains_are_counts(self, classifier):
        rules = [_make_rule("Use numbers"), _make_rule("Use percentages")]
        classified = classifier.classify_rules(rules)
        stats = classifier.get_classification_stats(classified)
        for domain, count in stats["domains"].items():
            assert isinstance(count, int)
            assert count > 0
