from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import CoverLetter, User, ActivityLog
from ..schemas import CoverLetterOut, CoverLetterCreate, CoverLetterUpdate
from ..auth import get_current_user
from ..services.ai_service import CoverLetterGeneratorService

router = APIRouter(prefix="/cover-letter", tags=["Cover Letters"])
cl_service = CoverLetterGeneratorService()

@router.post("/generate", response_model=CoverLetterOut)
def generate_cover_letter(req: CoverLetterCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Generates a professional cover letter, saves it to the database, and returns the result.
    """
    letter_content = cl_service.generate_cover_letter(
        db=db,
        user_id=current_user.id,
        job_role=req.job_role,
        company_name=req.company_name,
        experience_summary=req.experience_summary
    )
    
    new_cl = CoverLetter(
        user_id=current_user.id,
        title=req.title or f"Cover Letter - {req.company_name}",
        job_role=req.job_role,
        company_name=req.company_name,
        experience_summary=req.experience_summary,
        content=letter_content
    )
    db.add(new_cl)
    db.commit()
    db.refresh(new_cl)
    
    db.add(ActivityLog(
        user_id=current_user.id,
        activity_type="cover_letter_generated",
        description=f"Generated cover letter for {req.job_role} at {req.company_name}"
    ))
    db.commit()
    
    return new_cl

@router.get("/list", response_model=List[CoverLetterOut])
def list_cover_letters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(CoverLetter).filter(CoverLetter.user_id == current_user.id).order_by(CoverLetter.created_at.desc()).all()

@router.get("/{cl_id}", response_model=CoverLetterOut)
def get_cover_letter(cl_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cl = db.query(CoverLetter).filter(CoverLetter.id == cl_id, CoverLetter.user_id == current_user.id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    return cl

@router.put("/{cl_id}", response_model=CoverLetterOut)
def update_cover_letter(cl_id: str, cl_in: CoverLetterUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cl = db.query(CoverLetter).filter(CoverLetter.id == cl_id, CoverLetter.user_id == current_user.id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
        
    if cl_in.title is not None:
        cl.title = cl_in.title
    if cl_in.content is not None:
        cl.content = cl_in.content
        
    db.commit()
    db.refresh(cl)
    return cl

@router.delete("/{cl_id}")
def delete_cover_letter(cl_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cl = db.query(CoverLetter).filter(CoverLetter.id == cl_id, CoverLetter.user_id == current_user.id).first()
    if not cl:
        raise HTTPException(status_code=404, detail="Cover letter not found")
        
    db.delete(cl)
    db.commit()
    return {"message": "Cover letter deleted successfully"}
