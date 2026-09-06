"""PDF Rule Extractor.

Extracts structured knowledge rules from PDF text chunks using heuristic patterns.
Each extracted rule conforms to the AI PDF Knowledge Grounding Specification schema.
"""
import hashlib
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.knowledge_intelligence.pdf_extractor import PDFExtractionResult

logger = logging.getLogger(__name__)

SECTION_KEYWORDS = {
    "summary": ["summary", "professional summary", "objective", "profile"],
    "experience": ["experience", "work experience", "employment", "work history", "professional experience"],
    "skills": ["skills", "technical skills", "competencies", "technologies", "proficiencies"],
    "education": ["education", "academic", "degree", "university", "college", "coursework"],
    "projects": ["projects", "project experience", "portfolio", "personal projects"],
    "certifications": ["certifications", "licenses", "credentials", "certified"],
    "formatting": ["formatting", "format", "layout", "design", "appearance", "font", "style"],
    "ats": ["ats", "applicant tracking", "keyword", "parse", "parsing"],
    "cover_letter": ["cover letter", "coverletter", "letter of application", "application letter"],
}

DOMAIN_KEYWORDS = {
    "resume": ["resume", "cv", "curriculum vitae"],
    "cover_letter": ["cover letter", "letter", "correspondence"],
    "ats": ["ats", "applicant tracking system", "keyword optimization"],
    "skills": ["skill", "technology", "tool", "framework", "proficiency"],
    "experience": ["experience", "role", "position", "job", "work"],
    "education": ["education", "degree", "university", "course", "academic"],
    "formatting": ["format", "font", "layout", "spacing", "margin", "style"],
    "quantification": ["number", "percent", "quantif", "metric", "measur", "achievement"],
}

CATEGORY_KEYWORDS = {
    "Quantification": ["quantif", "number", "percent", "%", "metric", "measur", "achiev", "result"],
    "Action Verbs": ["verb", "action", "strong", "start with", "begin with", "bullet"],
    "Impact": ["impact", "result", "outcome", "accomplish", "achieve", "deliver"],
    "Keywords": ["keyword", "ats", "match", "terminolog", "phrase", "buzzword"],
    "Tailoring": ["tailor", "customiz", "specific", "target", "relevant", "personaliz"],
    "Relevance": ["relevan", "relat", "applicable", "pertinent", "appropriate"],
    "Clarity": ["clear", "concis", "specific", "vague", "ambiguous"],
    "Specificity": ["specif", "detail", "concrete", "example", "instance"],
    "Length": ["length", "word count", "page", "concis", "brief", "short", "long"],
    "Formatting": ["format", "font", "style", "layout", "design", "visual"],
}

RULE_PATTERNS = [
    re.compile(r"^\s*[-•*]\s+(.+)", re.MULTILINE),
    re.compile(r"^\s*\d+[.)]\s+(.+)", re.MULTILINE),
    re.compile(r"^(?:You should|Make sure to|Always|Never|Do not|Don't|Ensure that|Remember to|Be sure to)\s+(.+)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^(?:Should|Must|Need to|Important to|Critical to)\s+(.+)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^[A-Z][a-z]+\s+(?:your|the|a|an)\s+(.+)", re.MULTILINE),
]

INSTRUCTION_PATTERNS = [
    re.compile(r"^\s*[-•*]\s+(.+)", re.MULTILINE),
    re.compile(r"^\s*\d+[.)]\s+(.+)", re.MULTILINE),
]


class PDFRuleExtractor:
    """Extracts structured rules from PDF text chunks."""

    def __init__(self):
        self.extraction_timestamp = datetime.utcnow().isoformat()

    def _compute_rule_hash(self, instruction: str) -> str:
        return hashlib.sha256(instruction.strip().encode("utf-8")).hexdigest()[:16]

    def _detect_section(self, text: str, surrounding_text: str = "") -> str:
        combined = (text + " " + surrounding_text).lower()
        for section, keywords in SECTION_KEYWORDS.items():
            for kw in keywords:
                if kw in combined:
                    return section
        return "general"

    def _detect_domain(self, text: str) -> str:
        text_lower = text.lower()
        scores = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = score
        if scores:
            return max(scores, key=scores.get)
        return "resume"

    def _detect_category(self, text: str) -> str:
        text_lower = text.lower()
        scores = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        if scores:
            return max(scores, key=scores.get)
        return "General"

    def _detect_priority(self, text: str) -> str:
        text_lower = text.lower()
        critical_words = ["must", "never", "always", "critical", "essential", "required"]
        high_words = ["should", "important", "strongly", "recommended", "key"]
        low_words = ["optional", "consider", "may", "might", "nice to have"]
        if any(w in text_lower for w in critical_words):
            return "Critical"
        if any(w in text_lower for w in high_words):
            return "High"
        if any(w in text_lower for w in low_words):
            return "Low"
        return "Medium"

    def _extract_instruction(self, raw_text: str) -> str:
        cleaned = raw_text.strip()
        cleaned = re.sub(r"^[•\-\*]\s*", "", cleaned)
        cleaned = re.sub(r"^\d+[.)]\s*", "", cleaned)
        if cleaned and cleaned[0].islower():
            cleaned = cleaned[0].upper() + cleaned[1:]
        return cleaned

    def _extract_reason(self, text: str) -> Optional[str]:
        reason_patterns = [
            re.compile(r"(?:because|since|as|due to|this is because)\s+(.+?)(?:\.|$)", re.IGNORECASE),
            re.compile(r"(?:this|it)\s+(?:ensures?|helps?|shows?|demonstrates?|improves?|prevents?)\s+(.+?)(?:\.|$)", re.IGNORECASE),
        ]
        for pattern in reason_patterns:
            match = pattern.search(text)
            if match:
                return match.group(0).strip().rstrip(".")
        return None

    def _extract_examples(self, text: str) -> List[str]:
        examples = []
        example_patterns = [
            re.compile(r"(?:e\.g\.|for example|such as|like|e\.g|e\.g.,)\s+(.+?)(?:\.|$)", re.IGNORECASE),
            re.compile(r'"([^"]+)"', re.IGNORECASE),
            re.compile(r"'([^']+)'", re.IGNORECASE),
        ]
        for pattern in example_patterns:
            matches = pattern.findall(text)
            examples.extend(matches)
        return examples[:3]

    def _calculate_confidence(self, text: str, has_reason: bool, has_examples: bool) -> float:
        confidence = 0.5
        if len(text) > 20:
            confidence += 0.1
        if len(text) > 50:
            confidence += 0.1
        if has_reason:
            confidence += 0.1
        if has_examples:
            confidence += 0.1
        if any(kw in text.lower() for kw in ["should", "must", "always", "never"]):
            confidence += 0.05
        if "%" in text or re.search(r"\d+", text):
            confidence += 0.05
        return min(confidence, 1.0)

    def _create_rule(
        self,
        instruction: str,
        source_document: str,
        source_page: int,
        source_evidence: str,
        surrounding_text: str = "",
    ) -> Dict[str, Any]:
        reason = self._extract_reason(source_evidence)
        examples = self._extract_examples(source_evidence)
        domain = self._detect_domain(source_evidence + " " + surrounding_text)
        category = self._detect_category(source_evidence + " " + surrounding_text)
        priority = self._detect_priority(source_evidence + " " + surrounding_text)
        section = self._detect_section(source_evidence, surrounding_text)
        confidence = self._calculate_confidence(instruction, reason is not None, len(examples) > 0)
        rule_hash = self._compute_rule_hash(instruction)
        rule_id = f"PDF_{domain.upper()[:3]}_{rule_hash[:8].upper()}"

        return {
            "rule_id": rule_id,
            "source_document": source_document,
            "source_page": source_page,
            "source_section": section,
            "source_evidence": source_evidence[:500],
            "rule_type": "extracted",
            "domain": domain,
            "priority": priority,
            "category": category,
            "section_name": section,
            "instruction": instruction,
            "reason": reason,
            "examples": examples,
            "confidence": confidence,
            "extraction_timestamp": self.extraction_timestamp,
            "rule_hash": rule_hash,
            "state": "DISCOVERED",
            "version": 1,
        }

    def extract_rules_from_page(
        self,
        page_text: str,
        page_number: int,
        source_document: str,
        section_hint: str = "",
    ) -> List[Dict[str, Any]]:
        rules = []
        seen_hashes = set()
        lines = page_text.split("\n")
        current_section_hint = section_hint

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) < 10:
                continue
            is_section_header = False
            for section, keywords in SECTION_KEYWORDS.items():
                if any(kw in line_stripped.lower() for kw in keywords):
                    if len(line_stripped) < 60:
                        current_section_hint = section
                        is_section_header = True
                        break
            if is_section_header:
                continue
            instruction = self._extract_instruction(line_stripped)
            if not instruction or len(instruction) < 10:
                continue
            surrounding = " ".join(lines[max(0, i - 2):i + 3])
            rule = self._create_rule(
                instruction=instruction,
                source_document=source_document,
                source_page=page_number,
                source_evidence=line_stripped,
                surrounding_text=surrounding + " " + current_section_hint,
            )
            if rule["rule_hash"] not in seen_hashes:
                seen_hashes.add(rule["rule_hash"])
                rules.append(rule)

        return rules

    def extract_rules_from_pdf(self, extraction_result: PDFExtractionResult) -> List[Dict[str, Any]]:
        all_rules = []
        seen_hashes = set()

        for page in extraction_result.pages:
            page_rules = self.extract_rules_from_page(
                page_text=page.text,
                page_number=page.page_number,
                source_document=extraction_result.file_name,
            )
            for rule in page_rules:
                if rule["rule_hash"] not in seen_hashes:
                    seen_hashes.add(rule["rule_hash"])
                    all_rules.append(rule)

        # Apply quality filtering
        filtered = self._filter_rules(all_rules)
        return filtered

    def _filter_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out low-quality extracted rules.

        Quality criteria:
        - Instruction must be at least 15 characters (not a header/fragment)
        - Instruction must not be a URL or email
        - Instruction must not be all uppercase (likely a header)
        - Instruction must contain at least one verb-like word (actionable)
        - Instruction must not be a page number or reference
        """
        filtered = []
        for rule in rules:
            instruction = rule.get("instruction", "").strip()

            # Skip very short instructions
            if len(instruction) < 15:
                continue

            # Skip URLs and emails
            if any(x in instruction.lower() for x in ["http", "www.", "@", ".edu", ".com", ".org"]):
                continue

            # Skip all-uppercase headers
            if instruction.isupper() and len(instruction) > 30:
                continue

            # Skip page numbers and references
            if instruction.isdigit():
                continue
            if len(instruction) < 20 and instruction.replace(".", "").replace(",", "").replace(" ", "").isdigit():
                continue

            # Skip obvious navigation/header text
            header_indicators = ["table of contents", "click here", "page ", "copyright"]
            if any(h in instruction.lower() for h in header_indicators):
                continue

            # Must contain at least one verb-like word
            verb_indicators = [
                "should", "must", "use", "include", "avoid", "start", "begin",
                "write", "keep", "make", "ensure", "provide", "create", "show",
                "demonstrate", "highlight", "quantify", "tailor", "customize",
                "focus", "emphasize", "describe", "list", "organize", "group",
                "consider", "think", "remember", "never", "always", "do not",
            ]
            has_verb = any(v in instruction.lower() for v in verb_indicators)
            if not has_verb:
                # Still keep if it's a clear rule pattern (starts with bullet, has section context)
                if not any(instruction.startswith(x) for x in ["-", "•", "*", "1", "2", "3"]):
                    continue

            filtered.append(rule)

        return filtered

    def extract_rules_from_all(
        self, extraction_results: List[PDFExtractionResult]
    ) -> List[Dict[str, Any]]:
        all_rules = []
        seen_hashes = set()

        for result in extraction_results:
            if not result.success:
                continue
            rules = self.extract_rules_from_pdf(result)
            for rule in rules:
                if rule["rule_hash"] not in seen_hashes:
                    seen_hashes.add(rule["rule_hash"])
                    all_rules.append(rule)

        return all_rules
