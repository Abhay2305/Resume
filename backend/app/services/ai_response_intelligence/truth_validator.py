"""Truth Validator.

Compares AI output against Resume Knowledge to detect fabricated information.
Rejects invented companies, skills, education, certifications, and false metrics.
Only truthful enhancements are allowed.
"""
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class TruthValidator:
    """Validates AI response against known Resume Knowledge.

    Ensures AI has not fabricated companies, skills, education,
    certifications, or false metrics.
    """

    def validate(
        self,
        response_data: Dict[str, Any],
        resume_knowledge: Dict[str, Any],
    ) -> Tuple[bool, float, List[Dict[str, Any]], Dict[str, Any]]:
        """Validate AI response against resume knowledge.

        Args:
            response_data: The parsed AI response.
            resume_knowledge: The canonical Resume Knowledge.

        Returns:
            Tuple of (is_valid, score, issues, details).
        """
        issues = []
        details = {}
        score = 100.0

        if not response_data:
            return False, 0.0, [{"type": "empty_response", "message": "No response to validate"}], {}

        if not resume_knowledge:
            return True, 50.0, [{"type": "no_knowledge", "message": "No resume knowledge available for validation"}], {}

        # Validate experience entries
        exp_issues = self._validate_experience_truth(response_data, resume_knowledge)
        issues.extend(exp_issues)
        score -= len(exp_issues) * 8.0

        # Validate skills
        skill_issues = self._validate_skills_truth(response_data, resume_knowledge)
        issues.extend(skill_issues)
        score -= len(skill_issues) * 5.0

        # Validate education
        edu_issues = self._validate_education_truth(response_data, resume_knowledge)
        issues.extend(edu_issues)
        score -= len(edu_issues) * 8.0

        # Validate certifications
        cert_issues = self._validate_certifications_truth(response_data, resume_knowledge)
        issues.extend(cert_issues)
        score -= len(cert_issues) * 5.0

        # Validate metrics (check for inflated claims)
        metric_issues = self._validate_metrics(response_data, resume_knowledge)
        issues.extend(metric_issues)
        score -= len(metric_issues) * 3.0

        # Check for removed important experience
        removal_issues = self._validate_no_important_removals(response_data, resume_knowledge)
        issues.extend(removal_issues)
        score -= len(removal_issues) * 10.0

        score = max(0.0, min(100.0, score))
        is_valid = score >= 40.0

        details["total_issues"] = len(issues)
        details["fabricated_items"] = len([i for i in issues if i["type"].startswith("fabricated")])
        details["removed_items"] = len([i for i in issues if i["type"].startswith("removed")])

        return is_valid, score, issues, details

    def _validate_experience_truth(
        self, response: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check that experience entries reference real companies/roles."""
        issues = []
        known_companies = self._extract_known_companies(knowledge)
        known_roles = self._extract_known_roles(knowledge)

        response_experience = response.get("experience", [])
        if not isinstance(response_experience, list):
            return issues

        for i, entry in enumerate(response_experience):
            if not isinstance(entry, dict):
                continue

            company = entry.get("company", "")
            if company and company.lower() not in {c.lower() for c in known_companies}:
                issues.append({
                    "type": "fabricated_company",
                    "section": "experience",
                    "index": i,
                    "value": company,
                    "message": f"Company '{company}' not found in resume knowledge",
                })

            title = entry.get("title", "")
            if title and known_roles and title.lower() not in {r.lower() for r in known_roles}:
                # Only flag if it's clearly different (not just a variation)
                if not self._is_role_variation(title, known_roles):
                    issues.append({
                        "type": "fabricated_role",
                        "section": "experience",
                        "index": i,
                        "value": title,
                        "message": f"Role '{title}' not found in resume knowledge",
                    })

        return issues

    def _validate_skills_truth(
        self, response: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check that skills are from the known skill set."""
        issues = []
        known_skills = self._extract_known_skills(knowledge)

        response_skills = response.get("skills", [])
        if not isinstance(response_skills, list):
            return issues

        for skill in response_skills:
            if isinstance(skill, str) and skill.lower() not in {s.lower() for s in known_skills}:
                issues.append({
                    "type": "fabricated_skill",
                    "section": "skills",
                    "value": skill,
                    "message": f"Skill '{skill}' not found in resume knowledge",
                })

        return issues

    def _validate_education_truth(
        self, response: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check that education entries are truthful."""
        issues = []
        known_education = knowledge.get("education_summary", [])

        response_education = response.get("education", [])
        if not isinstance(response_education, list):
            return issues

        for i, entry in enumerate(response_education):
            if not isinstance(entry, dict):
                continue

            institution = entry.get("institution", "")
            if institution and known_education:
                known_institutions = [
                    e.get("institution", "") for e in known_education if isinstance(e, dict)
                ]
                if institution.lower() not in {inst.lower() for inst in known_institutions if inst}:
                    issues.append({
                        "type": "fabricated_institution",
                        "section": "education",
                        "index": i,
                        "value": institution,
                        "message": f"Institution '{institution}' not found in resume knowledge",
                    })

        return issues

    def _validate_certifications_truth(
        self, response: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check that certifications are truthful."""
        issues = []
        known_certs = knowledge.get("certifications", [])

        response_certs = response.get("certifications", [])
        if not isinstance(response_certs, list):
            return issues

        for cert in response_certs:
            if isinstance(cert, str) and known_certs:
                if cert.lower() not in {c.lower() for c in known_certs if isinstance(c, str)}:
                    issues.append({
                        "type": "fabricated_certification",
                        "section": "certifications",
                        "value": cert,
                        "message": f"Certification '{cert}' not found in resume knowledge",
                    })

        return issues

    def _validate_metrics(
        self, response: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for potentially inflated metrics."""
        issues = []
        known_metrics = self._extract_known_metrics(knowledge)

        response_experience = response.get("experience", [])
        if not isinstance(response_experience, list):
            return issues

        for i, entry in enumerate(response_experience):
            if not isinstance(entry, dict):
                continue

            description = entry.get("description", [])
            if not isinstance(description, list):
                continue

            for bullet in description:
                if not isinstance(bullet, str):
                    continue

                # Extract percentage claims
                import re
                percentages = re.findall(r'(\d+)%', bullet)
                for pct_str in percentages:
                    pct = int(pct_str)
                    if pct > 100:
                        issues.append({
                            "type": "inflated_metric",
                            "section": "experience",
                            "index": i,
                            "value": f"{pct}%",
                            "message": f"Percentage {pct}% exceeds 100% in experience entry {i}",
                        })

        return issues

    def _validate_no_important_removals(
        self, response: Dict[str, Any], knowledge: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Ensure AI hasn't removed important experience."""
        issues = []

        known_experience = knowledge.get("experience_summary", [])
        response_experience = response.get("experience", [])

        if not isinstance(known_experience, list) or not isinstance(response_experience, list):
            return issues

        known_companies = {
            e.get("company", "").lower()
            for e in known_experience
            if isinstance(e, dict) and e.get("company")
        }
        response_companies = {
            e.get("company", "").lower()
            for e in response_experience
            if isinstance(e, dict) and e.get("company")
        }

        for company in known_companies:
            if company and company not in response_companies:
                issues.append({
                    "type": "removed_experience",
                    "section": "experience",
                    "value": company,
                    "message": f"Experience at '{company}' was removed by AI",
                })

        return issues

    def _extract_known_companies(self, knowledge: Dict[str, Any]) -> Set[str]:
        """Extract known companies from resume knowledge."""
        companies = set()
        experience = knowledge.get("experience_summary", [])
        if isinstance(experience, list):
            for entry in experience:
                if isinstance(entry, dict) and entry.get("company"):
                    companies.add(entry["company"])
        return companies

    def _extract_known_roles(self, knowledge: Dict[str, Any]) -> Set[str]:
        """Extract known roles from resume knowledge."""
        roles = set()
        experience = knowledge.get("experience_summary", [])
        if isinstance(experience, list):
            for entry in experience:
                if isinstance(entry, dict) and entry.get("title"):
                    roles.add(entry["title"])
        return roles

    def _extract_known_skills(self, knowledge: Dict[str, Any]) -> Set[str]:
        """Extract known skills from resume knowledge."""
        skills = set()
        known_skills = knowledge.get("skills", [])
        if isinstance(known_skills, list):
            for skill in known_skills:
                if isinstance(skill, str):
                    skills.add(skill)
        return skills

    def _extract_known_metrics(self, knowledge: Dict[str, Any]) -> Set[str]:
        """Extract known metrics from resume knowledge."""
        metrics = set()
        achievements = knowledge.get("achievements", [])
        if isinstance(achievements, list):
            for achievement in achievements:
                if isinstance(achievement, str):
                    metrics.add(achievement)
        return metrics

    def _is_role_variation(self, role: str, known_roles: Set[str]) -> bool:
        """Check if a role is a variation of a known role."""
        role_lower = role.lower()
        for known in known_roles:
            known_lower = known.lower()
            if role_lower in known_lower or known_lower in role_lower:
                return True
        return False
