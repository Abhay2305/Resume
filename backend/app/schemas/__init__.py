"""Schemas package — consolidated from original schemas.py + PROCS schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Configuration domain schemas
from .config import (
    ConfigCreate,
    ConfigUpdate,
    ConfigOut,
    ConfigListResponse,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagOut,
    FeatureFlagListResponse,
    FeatureFlagEvaluateResponse,
)

# RBAC domain schemas
from .rbac import (
    RoleCreate,
    RoleUpdate,
    RoleOut,
    RoleListResponse,
    PermissionOut,
    RolePermissionOut,
    AssignPermissionRequest,
    AssignPermissionResponse,
    AssignRoleRequest,
    UserRoleAssignmentOut,
    UserRoleListResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminOut,
    AdminChangePasswordRequest,
)


# ============================================================================
# Core Auth / User Schemas (from original schemas.py)
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class MessageResponse(BaseModel):
    message: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class DeleteAccountRequest(BaseModel):
    password: str
    confirmation: str  # Must match "DELETE" to confirm

class UserLoginWithRememberMe(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserOutWithVerification(UserOut):
    is_verified: bool
    email_verified_at: Optional[datetime] = None
    login_provider: Optional[str] = None  # "email" or "google"


# ============================================================================
# Profile Schemas
# ============================================================================

class ProfileBase(BaseModel):
    # Personal information
    job_title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    date_of_birth: Optional[str] = None
    professional_headline: Optional[str] = None

    # Links
    website: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other_links: Optional[str] = None  # JSON array of {label, url}

    # Professional information
    summary: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    years_of_experience: Optional[int] = None
    education_level: Optional[str] = None

    # Resume sections (JSON arrays)
    education_json: Optional[str] = None
    experience_json: Optional[str] = None
    projects_json: Optional[str] = None
    skills_json: Optional[str] = None
    certifications_json: Optional[str] = None
    achievements_json: Optional[str] = None
    languages_json: Optional[str] = None
    interests_json: Optional[str] = None
    awards_json: Optional[str] = None
    publications_json: Optional[str] = None
    volunteer_json: Optional[str] = None
    extracurricular_json: Optional[str] = None

    # Completion tracking
    profile_completed: Optional[bool] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Template Schemas
# ============================================================================

class TemplateOut(BaseModel):
    id: str
    name: str
    category: str
    preview_image: Optional[str] = None
    color_scheme: Dict[str, Any]
    layout_schema: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Resume Section Schemas
# ============================================================================

class ResumeSectionBase(BaseModel):
    section_type: str
    content: Any  # JSON list or dict
    position: int

class ResumeSectionUpdate(BaseModel):
    section_type: str
    content: Any
    position: int

class ResumeSectionOut(ResumeSectionBase):
    id: str
    resume_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Resume Schemas
# ============================================================================

class ResumeBase(BaseModel):
    title: str
    template_id: Optional[str] = None

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    section_order: Optional[List[str]] = None

class ResumeOut(ResumeBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    sections: List[ResumeSectionOut] = []
    section_order: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class ResumeGenerateRequest(BaseModel):
    prompt: str
    archetype: Optional[str] = "experienced"  # experienced, career_switcher, fresher

class ResumeImproveRequest(BaseModel):
    section_type: str
    text_content: str
    action_type: str  # improve, shorten, expand, professional, autofix

class ResumeImproveResponse(BaseModel):
    original_text: str
    improved_text: str
    applied_rules: List[str]


# ============================================================================
# Cover Letter Schemas
# ============================================================================

class CoverLetterBase(BaseModel):
    title: str
    job_role: str
    company_name: str
    experience_summary: Optional[str] = None
    content: str

class CoverLetterCreate(BaseModel):
    title: str
    job_role: str
    company_name: str
    experience_summary: Optional[str] = None

class CoverLetterUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class CoverLetterOut(CoverLetterBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ATS Scoring Schemas
# ============================================================================

class ATSResultOut(BaseModel):
    id: str
    resume_id: str
    score: int
    details: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Subscription / Payment Schemas
# ============================================================================

class SubscriptionOut(BaseModel):
    id: str
    user_id: str
    plan_type: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PaymentOut(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    payment_date: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Activity Log Schema
# ============================================================================

class ActivityLogOut(BaseModel):
    id: str
    activity_type: str
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Opportunity Intelligence Engine Schemas
# ============================================================================

class OpportunityCreate(BaseModel):
    raw_text: str = Field(..., min_length=1, max_length=50000, description="Raw opportunity description text")
    title: Optional[str] = Field(None, max_length=255, description="Opportunity title")
    company: Optional[str] = Field(None, max_length=255, description="Company name")
    url: Optional[str] = Field(None, max_length=1024, description="Source URL")

    @field_validator("raw_text")
    @classmethod
    def validate_raw_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class OpportunityUpdate(BaseModel):
    raw_text: Optional[str] = Field(None, min_length=1, max_length=50000)
    title: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=1024)
    is_archived: Optional[bool] = None


class OpportunityEntityOut(BaseModel):
    id: str
    entity_type: str
    entity_value: str
    is_required: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParsedOpportunityDataOut(BaseModel):
    id: str
    opportunity_id: str
    responsibilities: Optional[list[str]] = None
    benefits: Optional[list[str]] = None
    ats_keywords: Optional[list[str]] = None
    raw_sections: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    raw_text: str
    title: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_archived: bool
    parser_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityDetailOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    raw_text: str
    title: Optional[str] = None
    company: Optional[str] = None
    url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_archived: bool
    parser_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    parsed_data: Optional[ParsedOpportunityDataOut] = None
    entities: list[OpportunityEntityOut] = []

    model_config = ConfigDict(from_attributes=True)


class OpportunityListOut(BaseModel):
    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityListResponse(BaseModel):
    items: list[OpportunityListOut]
    total: int
    page: int
    size: int


class ParseTriggerResponse(BaseModel):
    message: str
    status: str


class OpportunityErrorResponse(BaseModel):
    detail: str


# ============================================================================
# Resume Intelligence Engine Schemas
# ============================================================================

class ResumeIntelligenceCreate(BaseModel):
    raw_text: str = Field(..., min_length=1, max_length=100000, description="Raw resume text")
    title: Optional[str] = Field(None, max_length=255, description="Resume title")

    @field_validator("raw_text")
    @classmethod
    def validate_raw_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Resume text cannot be empty")
        return v.strip()


class ResumeIntelligenceUpdate(BaseModel):
    raw_text: Optional[str] = Field(None, min_length=1, max_length=100000)
    title: Optional[str] = Field(None, max_length=255)
    is_archived: Optional[bool] = None


class ResumeEntityOut(BaseModel):
    id: str
    entity_type: str
    entity_value: str
    entity_metadata: Optional[dict] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParsedResumeDataOut(BaseModel):
    id: str
    resume_profile_id: str
    summary: Optional[str] = None
    experience_entries: Optional[list] = None
    education_entries: Optional[list] = None
    projects: Optional[list] = None
    raw_sections: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeKnowledgeOut(BaseModel):
    id: str
    resume_profile_id: str
    personal_info: Optional[dict] = None
    contact_info: Optional[dict] = None
    summary: Optional[str] = None
    skills: Optional[list] = None
    technologies: Optional[dict] = None
    experience_summary: Optional[list] = None
    education_summary: Optional[list] = None
    certifications: Optional[list] = None
    projects: Optional[list] = None
    achievements: Optional[list] = None
    total_experience_years: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeIntelligenceOut(BaseModel):
    id: str
    user_id: str
    raw_text: str
    title: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_archived: bool
    parser_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeIntelligenceDetailOut(BaseModel):
    id: str
    user_id: str
    raw_text: str
    title: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_archived: bool
    parser_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    parsed_data: Optional[ParsedResumeDataOut] = None
    entities: list[ResumeEntityOut] = []
    knowledge: Optional[ResumeKnowledgeOut] = None

    model_config = ConfigDict(from_attributes=True)


class ResumeIntelligenceListOut(BaseModel):
    id: str
    title: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeIntelligenceListResponse(BaseModel):
    items: list[ResumeIntelligenceListOut]
    total: int
    page: int
    size: int


class ResumeIntelligenceParseResponse(BaseModel):
    message: str
    status: str


# ============================================================================
# Gap Analysis Schemas
# ============================================================================

class GapAnalysisCreate(BaseModel):
    resume_profile_id: str
    opportunity_id: str


class GapAnalysisUpdate(BaseModel):
    status: Optional[str] = None
    overall_match_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    technology_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    certification_match_score: Optional[float] = None
    keyword_match_score: Optional[float] = None
    total_gaps: Optional[int] = None
    total_matches: Optional[int] = None
    total_recommendations: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None


class GapResultOut(BaseModel):
    id: str
    category: str
    match_score: Optional[float] = None
    matched_items: Optional[str] = None
    missing_items: Optional[str] = None
    partial_items: Optional[str] = None
    extra_items: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationOut(BaseModel):
    id: str
    category: str
    priority: str
    action: str
    description: str
    target_item: Optional[str] = None
    is_applied: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GapAnalysisOut(BaseModel):
    id: str
    user_id: str
    resume_profile_id: str
    opportunity_id: str
    status: str
    overall_match_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    technology_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    certification_match_score: Optional[float] = None
    keyword_match_score: Optional[float] = None
    total_gaps: Optional[int] = None
    total_matches: Optional[int] = None
    total_recommendations: Optional[int] = None
    parser_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GapAnalysisDetailOut(BaseModel):
    id: str
    user_id: str
    resume_profile_id: str
    opportunity_id: str
    status: str
    overall_match_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    technology_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    certification_match_score: Optional[float] = None
    keyword_match_score: Optional[float] = None
    total_gaps: Optional[int] = None
    total_matches: Optional[int] = None
    total_recommendations: Optional[int] = None
    parser_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    gap_results: list[GapResultOut] = []
    recommendations: list[RecommendationOut] = []

    model_config = ConfigDict(from_attributes=True)


class GapAnalysisListOut(BaseModel):
    id: str
    resume_profile_id: str
    opportunity_id: str
    status: str
    overall_match_score: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GapAnalysisListResponse(BaseModel):
    items: list[GapAnalysisListOut]
    total: int
    page: int
    size: int


class GapAnalysisAnalyzeResponse(BaseModel):
    message: str
    status: str


class MatchScoresOut(BaseModel):
    overall_match_score: Optional[float] = None
    skill_match_score: Optional[float] = None
    technology_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    education_match_score: Optional[float] = None
    certification_match_score: Optional[float] = None
    keyword_match_score: Optional[float] = None


class MissingItemsOut(BaseModel):
    missing_skills: list[str] = []
    missing_technologies: list[str] = []
    missing_certifications: list[str] = []
    missing_education: list[str] = []
    missing_keywords: list[str] = []


class GapAnalysisRecommendationsResponse(BaseModel):
    recommendations: list[RecommendationOut]
    total: int


class GapAnalysisMatchesResponse(BaseModel):
    gap_results: list[GapResultOut]
    total: int


class GapAnalysisMissingResponse(BaseModel):
    missing_items: MissingItemsOut


# ============================================================================
# Knowledge Intelligence Schemas
# ============================================================================

class KnowledgeDocumentCreate(BaseModel):
    document_key: str
    name: str
    source: str
    document_type: str
    version: str = "1.0"
    description: Optional[str] = None
    confidence: float = 0.8


class KnowledgeDocumentUpdate(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    confidence: Optional[float] = None
    is_active: Optional[bool] = None


class KnowledgeDocumentOut(BaseModel):
    id: str
    document_key: str
    name: str
    source: str
    document_type: str
    version: str
    description: Optional[str] = None
    confidence: float
    is_active: bool
    total_rules: Optional[int] = None
    total_sections: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeDocumentListResponse(BaseModel):
    items: list[KnowledgeDocumentOut]
    total: int
    page: int
    size: int


class KnowledgeSectionOut(BaseModel):
    id: str
    document_id: str
    section_key: str
    name: str
    category: str
    description: Optional[str] = None
    content_summary: Optional[str] = None
    rule_count: Optional[int] = None
    sort_order: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeRuleOut(BaseModel):
    id: str
    document_id: str
    section_id: Optional[str] = None
    rule_key: str
    source: str
    section_name: str
    priority: str
    category: str
    instruction: str
    reason: Optional[str] = None
    examples: Optional[str] = None
    is_active: bool
    confidence: float
    created_at: datetime
    # Provenance fields
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    source_evidence: Optional[str] = None
    extraction_confidence: Optional[float] = None
    extraction_timestamp: Optional[str] = None
    rule_hash: Optional[str] = None
    state: Optional[str] = None
    version: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeRuleCreate(BaseModel):
    document_id: str
    section_id: Optional[str] = None
    rule_key: str
    source: str
    section_name: str
    priority: str = "medium"
    category: str
    instruction: str
    reason: Optional[str] = None
    examples: Optional[str] = None
    confidence: float = 0.8


class KnowledgeRuleListResponse(BaseModel):
    items: list[KnowledgeRuleOut]
    total: int
    page: int
    size: int


class KnowledgeRetrievalCreate(BaseModel):
    gap_analysis_id: str


class KnowledgeRetrievalOut(BaseModel):
    id: str
    gap_analysis_id: str
    user_id: str
    total_rules_retrieved: int
    retrieval_strategy: str
    processing_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeContextOut(BaseModel):
    id: str
    retrieval_id: str
    gap_analysis_id: str
    summary_rules: Optional[str] = None
    experience_rules: Optional[str] = None
    skills_rules: Optional[str] = None
    education_rules: Optional[str] = None
    projects_rules: Optional[str] = None
    certifications_rules: Optional[str] = None
    ats_rules: Optional[str] = None
    formatting_rules: Optional[str] = None
    cover_letter_rules: Optional[str] = None
    total_rules: int
    citations: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeContextDetailOut(BaseModel):
    id: str
    retrieval_id: str
    gap_analysis_id: str
    summary_rules: Optional[str] = None
    experience_rules: Optional[str] = None
    skills_rules: Optional[str] = None
    education_rules: Optional[str] = None
    projects_rules: Optional[str] = None
    certifications_rules: Optional[str] = None
    ats_rules: Optional[str] = None
    formatting_rules: Optional[str] = None
    cover_letter_rules: Optional[str] = None
    total_rules: int
    citations: Optional[str] = None
    created_at: datetime
    retrieval: Optional[KnowledgeRetrievalOut] = None

    model_config = ConfigDict(from_attributes=True)


class KnowledgeRetrieveRequest(BaseModel):
    gap_analysis_id: str


class KnowledgeRetrieveResponse(BaseModel):
    message: str
    retrieval_id: str
    total_rules: int


class KnowledgeContextResponse(BaseModel):
    context: KnowledgeContextDetailOut
    total_rules: int
    citations: list[str]


# ============================================================================
# Knowledge Governance Schemas
# ============================================================================

class KnowledgeRuleGovernanceResponse(BaseModel):
    """Response for rule governance action (approve/activate/deactivate/reject)."""
    rule_id: str
    rule_key: str
    previous_state: str
    new_state: str
    previous_is_active: bool
    new_is_active: bool
    message: str


class KnowledgeGovernanceStatsResponse(BaseModel):
    """Governance statistics showing rules by state."""
    total_rules: int
    by_state: dict[str, int]
    by_source: dict[str, int]


class KnowledgeRuleListByStateResponse(BaseModel):
    """Paginated list of rules filtered by governance state."""
    items: list[KnowledgeRuleOut]
    total: int
    page: int
    size: int
    state: str


# ============================================================================
# Prompt Intelligence Schemas
# ============================================================================

class PromptTemplateCreate(BaseModel):
    template_key: str
    name: str
    prompt_type: str
    category: str
    content: str
    version: str = "1.0"
    variables: Optional[dict] = None


class PromptTemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None
    variables: Optional[dict] = None


class PromptTemplateOut(BaseModel):
    id: str
    template_key: str
    name: str
    prompt_type: str
    category: str
    content: str
    version: str
    is_active: bool
    variables: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptTemplateListResponse(BaseModel):
    items: list[PromptTemplateOut]
    total: int
    page: int
    size: int


class PromptPackageCreate(BaseModel):
    gap_analysis_id: str
    prompt_type: str = "resume_tailoring"
    template_id: Optional[str] = None


class PromptPackageOut(BaseModel):
    id: str
    template_id: Optional[str] = None
    user_id: str
    gap_analysis_id: Optional[str] = None
    prompt_type: str
    system_prompt: str
    resume_context: Optional[dict] = None
    opportunity_context: Optional[dict] = None
    gap_context: Optional[dict] = None
    knowledge_context: Optional[dict] = None
    instructions: Optional[list] = None
    constraints: Optional[list] = None
    output_schema: Optional[dict] = None
    total_tokens_estimate: Optional[int] = None
    is_validated: bool
    validation_errors: Optional[list] = None
    version: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptPackageDetailOut(BaseModel):
    id: str
    template_id: Optional[str] = None
    user_id: str
    gap_analysis_id: Optional[str] = None
    prompt_type: str
    system_prompt: str
    resume_context: Optional[dict] = None
    opportunity_context: Optional[dict] = None
    gap_context: Optional[dict] = None
    knowledge_context: Optional[dict] = None
    instructions: Optional[list] = None
    constraints: Optional[list] = None
    output_schema: Optional[dict] = None
    total_tokens_estimate: Optional[int] = None
    is_validated: bool
    validation_errors: Optional[list] = None
    version: str
    created_at: datetime
    updated_at: datetime
    template: Optional[PromptTemplateOut] = None

    model_config = ConfigDict(from_attributes=True)


class PromptPackageListResponse(BaseModel):
    items: list[PromptPackageOut]
    total: int
    page: int
    size: int


class PromptBuildRequest(BaseModel):
    gap_analysis_id: str
    prompt_type: str = "resume_tailoring"
    template_id: Optional[str] = None


class PromptBuildResponse(BaseModel):
    message: str
    package_id: str
    is_validated: bool
    total_tokens_estimate: Optional[int] = None


class PromptVariableOut(BaseModel):
    id: str
    variable_key: str
    name: str
    description: Optional[str] = None
    variable_type: str
    default_value: Optional[str] = None
    is_required: bool
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptExecutionOut(BaseModel):
    id: str
    package_id: str
    user_id: str
    status: str
    provider: Optional[str] = None
    model: Optional[str] = None
    total_tokens: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptVersionOut(BaseModel):
    id: str
    template_id: str
    version: str
    system_prompt_hash: Optional[str] = None
    template_version: Optional[str] = None
    rules_version: Optional[str] = None
    knowledge_version: Optional[str] = None
    changes: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptVersionListResponse(BaseModel):
    items: list[PromptVersionOut]
    total: int


# ============================================================================
# AI Execution Engine Schemas
# ============================================================================

class AIExecutionCreate(BaseModel):
    prompt_package_id: str
    provider: Optional[str] = Field(None, description="Provider override (gemini, openai, anthropic, mock)")


class AIExecutionOut(BaseModel):
    id: str
    prompt_package_id: str
    user_id: str
    provider: str
    model: str
    status: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIExecutionDetailOut(BaseModel):
    id: str
    prompt_package_id: str
    user_id: str
    provider: str
    model: str
    status: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    execution_time_ms: Optional[int] = None
    raw_response: Optional[str] = None
    parsed_response: Optional[dict] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIExecutionListOut(BaseModel):
    id: str
    prompt_package_id: str
    provider: str
    model: str
    status: str
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIExecutionListResponse(BaseModel):
    items: list[AIExecutionListOut]
    total: int
    page: int
    size: int


class AIExecutionResponseOut(BaseModel):
    execution_id: str
    status: str
    parsed_response: Optional[dict] = None
    raw_response: Optional[str] = None
    provider: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    execution_time_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class AIExecutionExecuteResponse(BaseModel):
    execution_id: str
    status: str
    provider: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    execution_time_ms: Optional[int] = None
    parsed_response: Optional[dict] = None


# ============================================================================
# AI Response Intelligence Engine Schemas
# ============================================================================

class AIResponseValidateRequest(BaseModel):
    ai_execution_id: str


class AIResponseValidationOut(BaseModel):
    id: str
    ai_execution_id: str
    prompt_package_id: str
    user_id: str
    resume_profile_id: Optional[str] = None
    gap_analysis_id: Optional[str] = None
    status: str
    is_approved: Optional[bool] = None
    schema_valid: Optional[bool] = None
    truth_valid: Optional[bool] = None
    knowledge_valid: Optional[bool] = None
    gap_valid: Optional[bool] = None
    overall_confidence: Optional[float] = None
    total_changes: Optional[int] = None
    approved_changes: Optional[int] = None
    rejected_changes: Optional[int] = None
    warning_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDiffOut(BaseModel):
    id: str
    validation_id: str
    section: str
    change_type: str
    original_value: Optional[str] = None
    new_value: Optional[str] = None
    field_path: Optional[str] = None
    item_index: Optional[int] = None
    confidence: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChangeSetOut(BaseModel):
    id: str
    validation_id: str
    category: str
    change_type: str
    description: str
    original_value: Optional[str] = None
    new_value: Optional[str] = None
    is_approved: Optional[bool] = None
    risk_level: Optional[str] = None
    supporting_rule_id: Optional[str] = None
    supporting_gap_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ValidationReportOut(BaseModel):
    id: str
    validation_id: str
    validator_name: str
    is_valid: bool
    score: Optional[float] = None
    issues: Optional[list] = None
    details: Optional[dict] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConfidenceScoreOut(BaseModel):
    id: str
    validation_id: str
    change_set_id: str
    score: float
    risk_level: str
    supporting_gap_id: Optional[str] = None
    supporting_rule_id: Optional[str] = None
    validation_result: Optional[dict] = None
    reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIResponseValidationDetailOut(BaseModel):
    id: str
    ai_execution_id: str
    prompt_package_id: str
    user_id: str
    resume_profile_id: Optional[str] = None
    gap_analysis_id: Optional[str] = None
    status: str
    is_approved: Optional[bool] = None
    schema_valid: Optional[bool] = None
    truth_valid: Optional[bool] = None
    knowledge_valid: Optional[bool] = None
    gap_valid: Optional[bool] = None
    overall_confidence: Optional[float] = None
    total_changes: Optional[int] = None
    approved_changes: Optional[int] = None
    rejected_changes: Optional[int] = None
    warning_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    diffs: list[ResumeDiffOut] = []
    change_sets: list[ChangeSetOut] = []
    validation_reports: list[ValidationReportOut] = []
    confidence_scores: list[ConfidenceScoreOut] = []

    model_config = ConfigDict(from_attributes=True)


class AIResponseValidationListOut(BaseModel):
    id: str
    ai_execution_id: str
    status: str
    is_approved: Optional[bool] = None
    overall_confidence: Optional[float] = None
    total_changes: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIResponseValidationListResponse(BaseModel):
    items: list[AIResponseValidationListOut]
    total: int
    page: int
    size: int


class AIResponseDiffResponse(BaseModel):
    diffs: list[ResumeDiffOut]
    summary: dict


class AIResponseReportResponse(BaseModel):
    reports: list[ValidationReportOut]
    overall_valid: bool


class AIResponseConfidenceResponse(BaseModel):
    scores: list[ConfidenceScoreOut]
    overall_confidence: float


class AIResponseChangesResponse(BaseModel):
    changes: list[ChangeSetOut]
    total: int


class AIResponseValidateResponse(BaseModel):
    validation_id: str
    status: str
    is_approved: bool
    overall_confidence: float
    approval_package: dict
    processing_time_ms: int


# ============================================================================
# Intelligence Pipeline Schemas
# ============================================================================

from .pipeline import (
    PipelineExecuteRequest,
    PipelineRunResponse,
    PipelineStageResponse,
    PipelineRunListOut,
    PipelineRunListResponse,
)


# ============================================================================
# PROCS User Management Schemas
# ============================================================================

class UserListOut(BaseModel):
    """User list item schema for PROCS user management."""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated user list response."""
    success: bool = True
    items: List[UserListOut] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    totalPages: int = 1


class UserRoleOut(BaseModel):
    """User role assignment schema."""
    id: str
    role_id: str
    role_name: str
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSessionOut(BaseModel):
    """User session schema."""
    id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserTimelineOut(BaseModel):
    """User timeline event schema."""
    id: str
    event_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    description: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserDetailOut(BaseModel):
    """Full user detail schema for PROCS user inspector."""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: Optional[str] = None
    timezone: Optional[str] = None
    language: str = "en"
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Profile
    profile: Optional[Dict[str, Any]] = None

    # Roles
    roles: List[UserRoleOut] = []

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(BaseModel):
    """User detail response."""
    success: bool = True
    data: UserDetailOut


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    timezone: Optional[str] = None
    language: Optional[str] = None


class UserUpdateResponse(BaseModel):
    """User update response schema."""
    success: bool = True
    data: UserDetailOut


class UserActionResponse(BaseModel):
    """Generic user action response."""
    success: bool = True
    message: str


class UserStatsOut(BaseModel):
    """User statistics schema."""
    total_users: int = 0
    active_users: int = 0
    verified_users: int = 0
    superuser_count: int = 0
    new_users_today: int = 0
    new_users_this_week: int = 0
    new_users_this_month: int = 0


class UserStatsResponse(BaseModel):
    """User stats response."""
    success: bool = True
    data: UserStatsOut


# ============================================================================
# PROCS Resume Management Schemas
# ============================================================================

class ResumeListOut(BaseModel):
    """Resume list item schema for PROCS resume management."""
    id: str
    user_id: str
    title: str
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeListResponse(BaseModel):
    """Paginated resume list response."""
    success: bool = True
    items: List[ResumeListOut] = []
    total: int = 0
    page: int = 1
    limit: int = 20
    totalPages: int = 1


class ResumeDetailOut(BaseModel):
    """Full resume detail schema for PROCS resume inspector."""
    id: str
    user_id: str
    title: str
    template_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Sections
    sections: List[ResumeSectionOut] = []

    # Version history
    versions: List["ResumeVersionOut"] = []

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(BaseModel):
    """Resume detail response."""
    success: bool = True
    data: ResumeDetailOut


class ResumeUpdateRequest(BaseModel):
    """Resume update request schema."""
    title: Optional[str] = None
    template_id: Optional[str] = None


class ResumeUpdateResponse(BaseModel):
    """Resume update response schema."""
    success: bool = True
    data: ResumeDetailOut


class ResumeActionResponse(BaseModel):
    """Generic resume action response."""
    success: bool = True
    message: str


class ResumeStatsOut(BaseModel):
    """Resume statistics schema."""
    total_resumes: int = 0
    new_resumes_today: int = 0
    new_resumes_this_week: int = 0
    new_resumes_this_month: int = 0
    total_templates: int = 0


class ResumeStatsResponse(BaseModel):
    """Resume stats response."""
    success: bool = True
    data: ResumeStatsOut


class TemplateOut(BaseModel):
    """Template schema."""
    id: str
    name: str
    category: str
    preview_image: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TemplateListResponse(BaseModel):
    """Template list response."""
    success: bool = True
    items: List[TemplateOut] = []
    total: int = 0


class TemplateStatsOut(BaseModel):
    """Template usage statistics schema."""
    id: str
    name: str
    category: str
    usage_count: int = 0


class TemplateStatsResponse(BaseModel):
    """Template stats response."""
    success: bool = True
    items: List[TemplateStatsOut] = []


class ResumeVersionOut(BaseModel):
    """Resume version schema."""
    id: str
    version_number: int
    content: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
