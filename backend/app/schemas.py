from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime

# User Schemas
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

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Profile Schemas
class ProfileBase(BaseModel):
    job_title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None

class ProfileUpdate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Template Schemas
class TemplateOut(BaseModel):
    id: str
    name: str
    category: str
    preview_image: Optional[str] = None
    color_scheme: Dict[str, Any]
    layout_schema: Dict[str, Any]

    class Config:
        from_attributes = True

# Resume Section Schemas
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

    class Config:
        from_attributes = True

# Resume Schemas
class ResumeBase(BaseModel):
    title: str
    template_id: Optional[str] = None

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    pass

class ResumeOut(ResumeBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    sections: List[ResumeSectionOut] = []

    class Config:
        from_attributes = True

# Resume AI Generate Schema
class ResumeGenerateRequest(BaseModel):
    prompt: str
    archetype: Optional[str] = "experienced"  # experienced, career_switcher, fresher

# AI Actions
class ResumeImproveRequest(BaseModel):
    section_type: str
    text_content: str
    action_type: str  # improve, shorten, expand, professional, autofix

class ResumeImproveResponse(BaseModel):
    original_text: str
    improved_text: str
    applied_rules: List[str]

# Cover Letter Schemas
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

    class Config:
        from_attributes = True

# ATS Scoring Schemas
class ATSResultOut(BaseModel):
    id: str
    resume_id: str
    score: int
    details: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Subscription / Payment Schemas
class SubscriptionOut(BaseModel):
    id: str
    user_id: str
    plan_type: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentOut(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    payment_date: datetime

    class Config:
        from_attributes = True

# Activity Log Schema
class ActivityLogOut(BaseModel):
    id: str
    activity_type: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
