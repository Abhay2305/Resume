from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..database import get_db
from ..models import Resume, ResumeSection, ResumeVersion, User, Template, Subscription, ActivityLog
from ..schemas import ResumeOut, ResumeCreate, ResumeUpdate, ResumeGenerateRequest, ResumeSectionUpdate
from ..auth import get_current_user
from ..services.ai_service import ResumeGeneratorService

router = APIRouter(prefix="/resume", tags=["Resumes"])
generator_service = ResumeGeneratorService()

# Plan-based resume limits. Free tier is capped; paid tiers are unlimited.
FREE_RESUME_LIMIT = 1


def enforce_resume_quota(db: Session, user_id: str):
    """Block resume creation beyond the free-tier limit. Paid plans are unlimited."""
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    plan = sub.plan_type if sub else "free"
    if plan == "free":
        count = db.query(Resume).filter(Resume.user_id == user_id).count()
        if count >= FREE_RESUME_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Free plan is limited to 1 resume. Upgrade to Pro for unlimited "
                    "resumes and cover letters."
                ),
            )

@router.post("/create", response_model=ResumeOut)
def create_resume(resume_in: ResumeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    enforce_resume_quota(db, current_user.id)
    # Create resume
    new_resume = Resume(
        user_id=current_user.id,
        title=resume_in.title,
        template_id=resume_in.template_id or "harvard"
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)
    
    # Initialize basic empty sections to avoid front-end issues
    default_sections = ["personalInfo", "summary", "experience", "education", "skills", "projects", "certifications", "achievements"]
    for idx, sec_type in enumerate(default_sections):
        content = {}
        if sec_type in ["experience", "education", "projects", "certifications", "achievements", "skills"]:
            content = []
            
        sec = ResumeSection(
            resume_id=new_resume.id,
            section_type=sec_type,
            content=content,
            position=idx
        )
        db.add(sec)

    db.add(ActivityLog(
        user_id=current_user.id,
        activity_type="resume_created",
        description=f"Created resume '{new_resume.title}'"
    ))

    db.commit()
    db.refresh(new_resume)
    return new_resume

@router.get("/list", response_model=List[ResumeOut])
def list_resumes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.updated_at.desc()).all()

@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.put("/{resume_id}", response_model=ResumeOut)
def update_resume(resume_id: str, resume_in: ResumeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    resume.title = resume_in.title
    if resume_in.template_id:
        resume.template_id = resume_in.template_id
        
    db.commit()
    db.refresh(resume)
    return resume

@router.delete("/{resume_id}")
def delete_resume(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted successfully"}

@router.post("/generate", response_model=ResumeOut)
def generate_resume(req: ResumeGenerateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Parses unstructured input using AI, converts to structured JSON, 
    and inserts it into database sections for the user.
    """
    enforce_resume_quota(db, current_user.id)
    # 1. Run LLM Extraction
    structured_data = generator_service.generate_structured_resume(
        db=db, 
        user_id=current_user.id, 
        prompt=req.prompt, 
        archetype=req.archetype
    )
    
    # 2. Create the Resume record
    resume_title = f"AI Generated - {structured_data.get('personalInfo', {}).get('jobTitle', 'Resume')}"
    new_resume = Resume(
        user_id=current_user.id,
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

    db.add(ActivityLog(
        user_id=current_user.id,
        activity_type="resume_generated",
        description=f"AI generated resume '{new_resume.title}'"
    ))

    db.commit()
    db.refresh(new_resume)
    return new_resume

@router.put("/{resume_id}/sections", response_model=ResumeOut)
def update_sections(resume_id: str, sections_in: List[ResumeSectionUpdate], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Bulk updates or overwrites sections, supporting instant updates,
    fields editing, and drag-and-drop position changes.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
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
