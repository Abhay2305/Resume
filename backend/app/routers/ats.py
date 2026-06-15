from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from ..database import get_db
from ..models import User, ATSResult, Resume
from ..schemas import ATSResultOut, ResumeImproveRequest, ResumeImproveResponse
from ..auth import get_current_user
from ..services.ai_service import ATSScoreService
from ..services.llm_service import LLMProviderService, PromptBuilderService

router = APIRouter(prefix="/ats", tags=["ATS Scoring & AI Assistance"])
llm = LLMProviderService()

@router.post("/analyze/{resume_id}", response_model=ATSResultOut)
def analyze_resume(resume_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Analyzes the resume sections, calculates the ATS score (0-100), 
    generates targeted improvements, saves the history in `ats_results`, and returns the results.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Reconstruct resume dictionary representation for the analyzer
    resume_dict = {
        "personalInfo": {},
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "achievements": []
    }
    
    for sec in resume.sections:
        resume_dict[sec.section_type] = sec.content
        
    analysis = ATSScoreService.calculate_score(resume_dict)
    
    # Save the ATS result
    new_result = ATSResult(
        resume_id=resume.id,
        score=analysis["score"],
        details=analysis["details"],
        recommendations=analysis["recommendations"]
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    
    return new_result

@router.post("/improve-text", response_model=ResumeImproveResponse)
def improve_text(req: ResumeImproveRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Polishes experience bullets or summaries dynamically based on Harvard resume writing rules.
    Actions supported: 'improve', 'shorten', 'expand', 'professional', 'autofix'
    """
    system_rules = PromptBuilderService.get_active_rules_instruction(db)
    
    action_prompts = {
        "improve": f"Polishing this wording to sound more professional and high impact: \"{req.text_content}\".",
        "shorten": f"Condense this experience bullet to be brief and punchy, maintaining active verbs: \"{req.text_content}\".",
        "expand": f"Expand this experience to add detail, context, and potential achievements (add placeholders for metrics if needed): \"{req.text_content}\".",
        "professional": f"Translate this casual experience bullet into professional business language: \"{req.text_content}\".",
        "autofix": f"Fix all Harvard style rule issues (like removing 'I' or starting with active verbs) for this item: \"{req.text_content}\"."
    }
    
    action_prompt = action_prompts.get(req.action_type.lower(), action_prompts["improve"])
    
    improved_text = llm.generate(action_prompt, system_instruction=system_rules)
    
    # Clean output
    cleaned_improved = improved_text.strip()
    if cleaned_improved.startswith('"') and cleaned_improved.endswith('"'):
        cleaned_improved = cleaned_improved[1:-1]
        
    # Query rules active for information response
    rules = [rule.rule_name for rule in db.query(db.models.ResumeRule if hasattr(db, "models") else ResumeRule).filter(ResumeRule.is_active == True).all()]
    
    return ResumeImproveResponse(
        original_text=req.text_content,
        improved_text=cleaned_improved,
        applied_rules=rules[:3]  # Return top rules applied
    )
