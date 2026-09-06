from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from ..database import get_db
from ..models import Resume, ResumeSection, ResumeVersion, User, Template, ActivityLog
from ..models.identity import Profile
from ..schemas import ResumeOut, ResumeCreate, ResumeUpdate, ResumeGenerateRequest, ResumeSectionUpdate
from ..auth import get_current_user, require_auth
from ..services.ai_service import ResumeGeneratorService, validate_resume_output

router = APIRouter(prefix="/resume", tags=["Resumes"])
generator_service = ResumeGeneratorService()


class TransferGuestResumesRequest(BaseModel):
    """Schema for transferring guest resumes to an authenticated user."""
    guest_session_id: Optional[str] = "guest"


def get_guest_id(request=None, current_user=None):
    """Get user ID for resume operations.
    
    For authenticated users: returns their user ID.
    For guests: returns a guest identifier (header or default).
    This enables guest resume creation while maintaining data isolation.
    """
    if current_user:
        return current_user.id
    # For guests, use a header-based ID or default to "guest"
    # In production, generate unique guest IDs on the frontend
    return "guest"


@router.post("/create", response_model=ResumeOut)
def create_resume(
    resume_in: ResumeCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Create a new resume.
    
    Guests can create resumes - they are stored with user_id="guest".
    Authenticated users get resumes linked to their account.
    Auto-fills sections from the user's profile if available.
    """
    user_id = get_guest_id(current_user=current_user)
    
    # Create resume
    new_resume = Resume(
        user_id=user_id,
        title=resume_in.title,
        template_id=resume_in.template_id or "harvard"
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    # Auto-fill from profile if user is authenticated and has profile data
    profile = None
    if current_user:
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    
    def parse_json_field(value):
        """Parse a JSON string field, returning the parsed value or fallback."""
        if not value:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
    
    # Build sections from profile or defaults
    sections_data = []
    
    # personalInfo
    personal_info = {}
    if profile:
        personal_info = {
            "fullName": current_user.full_name or "",
            "jobTitle": profile.job_title or "",
            "email": current_user.email or "",
            "phone": profile.phone or "",
            "location": profile.location or "",
            "website": profile.website or "",
            "linkedin": profile.linkedin or "",
        }
    sections_data.append(("personalInfo", personal_info, 0))
    
    # summary
    summary = ""
    if profile and profile.summary:
        summary = profile.summary
    sections_data.append(("summary", summary, 1))
    
    # experience
    experience = []
    if profile and profile.experience_json:
        parsed = parse_json_field(profile.experience_json)
        if parsed and isinstance(parsed, list):
            experience = parsed
    sections_data.append(("experience", experience, 2))
    
    # education
    education = []
    if profile and profile.education_json:
        parsed = parse_json_field(profile.education_json)
        if parsed and isinstance(parsed, list):
            education = parsed
    sections_data.append(("education", education, 3))
    
    # skills
    skills = []
    if profile and profile.skills_json:
        parsed = parse_json_field(profile.skills_json)
        if parsed and isinstance(parsed, list):
            skills = parsed
    sections_data.append(("skills", skills, 4))
    
    # projects
    projects = []
    if profile and profile.projects_json:
        parsed = parse_json_field(profile.projects_json)
        if parsed and isinstance(parsed, list):
            projects = parsed
    sections_data.append(("projects", projects, 5))
    
    # certifications
    certifications = []
    if profile and profile.certifications_json:
        parsed = parse_json_field(profile.certifications_json)
        if parsed and isinstance(parsed, list):
            certifications = parsed
    sections_data.append(("certifications", certifications, 6))
    
    # achievements
    achievements = []
    if profile and profile.achievements_json:
        parsed = parse_json_field(profile.achievements_json)
        if parsed and isinstance(parsed, list):
            achievements = parsed
    sections_data.append(("achievements", achievements, 7))
    
    for sec_type, content, position in sections_data:
        sec = ResumeSection(
            resume_id=new_resume.id,
            section_type=sec_type,
            content=content,
            position=position
        )
        db.add(sec)

    if current_user:
        db.add(ActivityLog(
            user_id=current_user.id,
            activity_type="resume_created",
            description=f"Created resume '{new_resume.title}'"
        ))

    db.commit()
    db.refresh(new_resume)
    return new_resume


@router.get("/list", response_model=List[ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List resumes.
    
    For authenticated users: returns their resumes.
    For guests: returns guest resumes.
    """
    user_id = get_guest_id(current_user=current_user)
    return db.query(Resume).filter(Resume.user_id == user_id).order_by(Resume.updated_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Get a specific resume.
    
    Accessible by anyone with the resume ID (guest or authenticated).
    This enables the guest flow where users edit resumes without login.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # For security, only allow access to own resumes or guest resumes
    if current_user and resume.user_id != current_user.id and resume.user_id != "guest":
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.put("/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: str,
    resume_in: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Update resume settings (title, template).
    
    Accessible by anyone with the resume ID (guest or authenticated).
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # For security, only allow access to own resumes or guest resumes
    if current_user and resume.user_id != current_user.id and resume.user_id != "guest":
        raise HTTPException(status_code=404, detail="Resume not found")
        
    resume.title = resume_in.title
    if resume_in.template_id:
        resume.template_id = resume_in.template_id
    if resume_in.section_order is not None:
        resume.section_order = resume_in.section_order
        
    db.commit()
    db.refresh(resume)
    return resume


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Delete a resume.
    
    Accessible by anyone with the resume ID (guest or authenticated).
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # For security, only allow access to own resumes or guest resumes
    if current_user and resume.user_id != current_user.id and resume.user_id != "guest":
        raise HTTPException(status_code=404, detail="Resume not found")
        
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}


@router.post("/generate", response_model=ResumeOut)
def generate_resume(
    req: ResumeGenerateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Parses unstructured input using AI, converts to structured JSON, 
    and inserts it into database sections.
    
    Guests can generate resumes - they are stored with user_id="guest".
    """
    user_id = get_guest_id(current_user=current_user)
    
    # 1. Run LLM Extraction
    structured_data = generator_service.generate_structured_resume(
        db=db, 
        user_id=user_id, 
        prompt=req.prompt, 
        archetype=req.archetype
    )
    
    # 2. Validate output using governed validators
    validation_result = validate_resume_output(structured_data, req.prompt, db=db)
    
    # 2. Create the Resume record
    resume_title = f"AI Generated - {structured_data.get('personalInfo', {}).get('jobTitle', 'Resume')}"
    new_resume = Resume(
        user_id=user_id,
        title=resume_title,
        template_id="harvard"  # Default template
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    # 3. Create all sections
    section_keys = ["personalInfo", "summary", "experience", "education", "skills", "projects", "certifications", "achievements"]
    for idx, key in enumerate(section_keys):
        content_val = structured_data.get(key, {})
        # Safety normalization
        if key in ["experience", "education", "projects", "certifications", "achievements", "skills"] and not isinstance(content_val, list):
            content_val = [] if not content_val else [content_val]
            
        sec = ResumeSection(
            resume_id=new_resume.id,
            section_type=key,
            content=content_val,
            position=idx
        )
        db.add(sec)

    new_resume.section_order = ["summary", "experience", "education", "projects", "skills", "certifications", "achievements"]

    if current_user:
        db.add(ActivityLog(
            user_id=current_user.id,
            activity_type="resume_generated",
            description=f"AI generated resume '{new_resume.title}'"
        ))

    db.commit()
    db.refresh(new_resume)
    return new_resume


@router.put("/{resume_id}/sections", response_model=ResumeOut)
def update_sections(
    resume_id: str,
    sections_in: List[ResumeSectionUpdate],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Bulk updates or overwrites sections, supporting instant updates,
    fields editing, and drag-and-drop position changes.
    
    Accessible by anyone with the resume ID (guest or authenticated).
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # For security, only allow access to own resumes or guest resumes
    if current_user and resume.user_id != current_user.id and resume.user_id != "guest":
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Delete old sections and replace or update them
    db.query(ResumeSection).filter(ResumeSection.resume_id == resume_id).delete()
    
    for sec_data in sections_in:
        new_sec = ResumeSection(
            resume_id=resume_id,
            section_type=sec_data.section_type,
            content=sec_data.content,
            position=sec_data.position
        )
        db.add(new_sec)
        
    # Save a snapshot version in history for versioning control
    # Let's count current versions to set version_number
    v_count = db.query(ResumeVersion).filter(ResumeVersion.resume_id == resume_id).count()
    full_content = {s.section_type: s.content for s in sections_in}
    
    version_log = ResumeVersion(
        resume_id=resume_id,
        version_number=v_count + 1,
        content=full_content
    )
    db.add(version_log)
    
    db.commit()
    db.refresh(resume)
    return resume


@router.post("/transfer-guest", response_model=List[ResumeOut])
def transfer_guest_resumes(
    req: TransferGuestResumesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_auth),
):
    """Transfer guest resumes to the authenticated user's account.
    
    Called after a guest registers to claim their resumes.
    Only transfers resumes with user_id="guest".
    """
    guest_id = req.guest_session_id or "guest"
    
    # Find all guest resumes
    guest_resumes = db.query(Resume).filter(Resume.user_id == guest_id).all()
    
    if not guest_resumes:
        return []
    
    # Transfer each resume to the new user
    transferred = []
    for resume in guest_resumes:
        resume.user_id = current_user.id
        transferred.append(resume)
        
        # Log the activity
        db.add(ActivityLog(
            user_id=current_user.id,
            activity_type="resume_transferred",
            description=f"Transferred guest resume '{resume.title}' to your account"
        ))
    
    db.commit()
    
    # Refresh all transferred resumes
    for resume in transferred:
        db.refresh(resume)
    
    return transferred
