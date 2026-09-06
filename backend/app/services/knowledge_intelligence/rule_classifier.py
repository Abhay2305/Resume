"""Rule Classifier.

Classifies extracted rules by domain, priority, section, and category
using the classification taxonomy from the AI PDF Knowledge Grounding Specification.
Refines classifications from the PDF rule extractor for higher accuracy.
"""
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DOMAIN_TAXONOMY = {
    "resume": {
        "keywords": ["resume", "cv", "curriculum vitae", "resume writing", "resume format", "resume content"],
        "weight": 1.0,
    },
    "cover_letter": {
        "keywords": ["cover letter", "coverletter", "letter of application", "application letter", "opening paragraph", "closing paragraph"],
        "weight": 1.0,
    },
    "ats": {
        "keywords": ["ats", "applicant tracking system", "keyword optimization", "keyword match", "parse", "parsing", "ats-friendly"],
        "weight": 1.2,
    },
    "skills": {
        "keywords": ["skill", "technical skill", "technology", "tool", "framework", "proficiency", "competenc"],
        "weight": 1.0,
    },
    "experience": {
        "keywords": ["experience", "work experience", "employment", "role", "position", "job", "career"],
        "weight": 1.0,
    },
    "education": {
        "keywords": ["education", "degree", "university", "college", "coursework", "gpa", "academic"],
        "weight": 1.0,
    },
    "formatting": {
        "keywords": ["format", "font", "layout", "spacing", "margin", "style", "design", "visual", "appearance"],
        "weight": 0.9,
    },
    "quantification": {
        "keywords": ["quantif", "number", "percent", "%", "metric", "measur", "achiev", "result", "data"],
        "weight": 1.1,
    },
}

SECTION_TAXONOMY = {
    "summary": {
        "keywords": ["summary", "professional summary", "objective", "profile", "career summary"],
        "weight": 1.0,
    },
    "experience": {
        "keywords": ["experience", "work experience", "employment", "work history", "professional experience", "role"],
        "weight": 1.0,
    },
    "skills": {
        "keywords": ["skill", "technical skill", "competenc", "technolog", "proficienc", "tool"],
        "weight": 1.0,
    },
    "education": {
        "keywords": ["education", "degree", "university", "college", "coursework", "gpa", "academic"],
        "weight": 1.0,
    },
    "projects": {
        "keywords": ["project", "portfolio", "personal project", "side project", "github"],
        "weight": 0.9,
    },
    "certifications": {
        "keywords": ["certification", "license", "credential", "certified", "aws certif"],
        "weight": 0.9,
    },
    "formatting": {
        "keywords": ["format", "font", "layout", "spacing", "margin", "style", "page"],
        "weight": 0.9,
    },
    "ats": {
        "keywords": ["ats", "applicant tracking", "keyword", "parse", "parsing"],
        "weight": 1.0,
    },
    "cover_letter": {
        "keywords": ["cover letter", "letter", "correspondence", "opening", "closing"],
        "weight": 1.0,
    },
}

CATEGORY_TAXONOMY = {
    "Quantification": {
        "keywords": ["quantif", "number", "percent", "%", "metric", "measur", "achiev", "result", "count", "amount"],
        "weight": 1.0,
    },
    "Action Verbs": {
        "keywords": ["verb", "action", "strong", "start with", "begin with", "bullet", "led", "managed", "developed"],
        "weight": 1.0,
    },
    "Impact": {
        "keywords": ["impact", "result", "outcome", "accomplish", "achieve", "deliver", "value", "contribution"],
        "weight": 1.0,
    },
    "Keywords": {
        "keywords": ["keyword", "ats", "match", "terminolog", "phrase", "buzzword", "requisite"],
        "weight": 1.0,
    },
    "Tailoring": {
        "keywords": ["tailor", "customiz", "specific", "target", "relevant", "personaliz", "adapt"],
        "weight": 1.0,
    },
    "Relevance": {
        "keywords": ["relevan", "relat", "applicable", "pertinent", "appropriate", "pertinence"],
        "weight": 0.9,
    },
    "Clarity": {
        "keywords": ["clear", "concis", "specific", "vague", "ambiguous", "precise"],
        "weight": 0.9,
    },
    "Specificity": {
        "keywords": ["specif", "detail", "concrete", "example", "instance", "particular"],
        "weight": 0.9,
    },
    "Length": {
        "keywords": ["length", "word count", "page", "concis", "brief", "short", "long", "lines"],
        "weight": 0.8,
    },
    "Formatting": {
        "keywords": ["format", "font", "style", "layout", "design", "visual", "bullet", "indent"],
        "weight": 0.9,
    },
}

PRIORITY_KEYWORDS = {
    "Critical": ["must", "never", "always", "critical", "essential", "required", "mandatory", "do not", "don't"],
    "High": ["should", "important", "strongly", "recommended", "key", "crucial", "vital"],
    "Medium": ["consider", "recommended", "best practice", "typically", "generally", "usually"],
    "Low": ["optional", "may", "might", "nice to have", "if possible", "can also"],
}

CONFIDENCEBoostRule = re.compile(r"\b(?:always|must|never|should)\b", re.IGNORECASE)


class RuleClassifier:
    """Classifies extracted rules by domain, priority, section, and category."""

    def __init__(self):
        self.domain_taxonomy = DOMAIN_TAXONOMY
        self.section_taxonomy = SECTION_TAXONOMY
        self.category_taxonomy = CATEGORY_TAXONOMY
        self.priority_keywords = PRIORITY_KEYWORDS

    def _score_match(self, text: str, keywords: List[str], weight: float = 1.0) -> float:
        text_lower = text.lower()
        score = 0.0
        for kw in keywords:
            if kw in text_lower:
                score += weight
        return score

    def classify_domain(self, rule: Dict[str, Any]) -> str:
        text = " ".join([
            rule.get("instruction", ""),
            rule.get("source_evidence", ""),
            rule.get("source_section", ""),
        ])
        scores = {}
        for domain, config in self.domain_taxonomy.items():
            score = self._score_match(text, config["keywords"], config["weight"])
            if score > 0:
                scores[domain] = score
        if scores:
            return max(scores, key=scores.get)
        return rule.get("domain", "resume")

    def classify_section(self, rule: Dict[str, Any]) -> str:
        text = " ".join([
            rule.get("instruction", ""),
            rule.get("source_evidence", ""),
            rule.get("source_section", ""),
        ])
        scores = {}
        for section, config in self.section_taxonomy.items():
            score = self._score_match(text, config["keywords"], config["weight"])
            if score > 0:
                scores[section] = score
        if scores:
            return max(scores, key=scores.get)
        return rule.get("section_name", "general")

    def classify_category(self, rule: Dict[str, Any]) -> str:
        text = " ".join([
            rule.get("instruction", ""),
            rule.get("source_evidence", ""),
        ])
        scores = {}
        for category, config in self.category_taxonomy.items():
            score = self._score_match(text, config["keywords"], config["weight"])
            if score > 0:
                scores[category] = score
        if scores:
            return max(scores, key=scores.get)
        return rule.get("category", "General")

    def classify_priority(self, rule: Dict[str, Any]) -> str:
        text = " ".join([
            rule.get("instruction", ""),
            rule.get("source_evidence", ""),
        ])
        text_lower = text.lower()
        for priority, keywords in self.priority_keywords.items():
            if any(kw in text_lower for kw in keywords):
                return priority
        return rule.get("priority", "Medium")

    def classify_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        classified = dict(rule)
        classified["domain"] = self.classify_domain(rule)
        classified["section_name"] = self.classify_section(rule)
        classified["category"] = self.classify_category(rule)
        classified["priority"] = self.classify_priority(rule)
        classified["rule_type"] = "classified"
        return classified

    def classify_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.classify_rule(rule) for rule in rules]

    def get_classification_stats(self, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        domains = {}
        sections = {}
        categories = {}
        priorities = {}
        for rule in rules:
            d = rule.get("domain", "unknown")
            s = rule.get("section_name", "unknown")
            c = rule.get("category", "unknown")
            p = rule.get("priority", "unknown")
            domains[d] = domains.get(d, 0) + 1
            sections[s] = sections.get(s, 0) + 1
            categories[c] = categories.get(c, 0) + 1
            priorities[p] = priorities.get(p, 0) + 1
        return {
            "total_rules": len(rules),
            "domains": domains,
            "sections": sections,
            "categories": categories,
            "priorities": priorities,
        }
