from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from ..database import get_db
from ..models import User, ATSResult, Resume
from ..schemas import ATSResultOut, ResumeImproveRequest, ResumeImproveResponse
from ..auth import get_current_user
from ..services.ai_service import ATSScoreService, get_ai_service, run_async, get_knowledge_rules_for_context
from ..services.llm_service import LLMProviderService
from ..services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from ..services.prompt_intelligence_v2.types import PromptRequest

router = APIRouter(prefix="/ats", tags=["ATS Scoring & AI Assistance"])
llm = LLMProviderService()
prompt_engine = PromptBuilderV2()

# Action type → Prompt Intelligence v2 prompt_type mapping
_ACTION_TO_PROMPT_TYPE = {
    "improve": "text_improve",
    "shorten": "text_shorten",
    "expand": "text_expand",
    "professional": "text_professional",
    "autofix": "text_autofix",
}

@router.post("/analyze/{resume_id}", response_model=ATSResultOut)
def analyze_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Analyzes the resume sections, calculates the ATS score (0-100), 
    generates targeted improvements, saves the history in `ats_results`, and returns the results.
    
    Guests can analyze resumes - no authentication required.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # For security, only allow access to own resumes or guest resumes
    if current_user and resume.user_id != current_user.id and resume.user_id != "guest":
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
def improve_text(
    req: ResumeImproveRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """
    Polishes experience bullets or summaries dynamically based on approved knowledge rules.
    Actions supported: 'improve', 'shorten', 'expand', 'professional', 'autofix'
    
    Guests can use AI text improvement - no authentication required.
    """
    # Get knowledge rules from knowledge_intelligence (approved methodology)
    knowledge_rules = get_knowledge_rules_for_context(db)
    
    # Map action type to Prompt Intelligence v2 prompt type
    prompt_type = _ACTION_TO_PROMPT_TYPE.get(req.action_type.lower(), "text_improve")
    
    # Build context with knowledge rules
    context = {"text_content": req.text_content}
    if knowledge_rules:
        context["knowledge_rules"] = knowledge_rules
    
    # Build request for Prompt Intelligence v2
    request = PromptRequest(
        prompt_type=prompt_type,
        context=context,
    )
    
    # Get messages from Prompt Intelligence v2
    messages = prompt_engine.build_messages(request)
    
    # Call UniversalAIService directly with the constructed messages
    ai_service = get_ai_service()
    response = run_async(ai_service.generate(messages))
    improved_text = response.content
    
    # Clean output
    cleaned_improved = improved_text.strip()
    if cleaned_improved.startswith('"') and cleaned_improved.endswith('"'):
        cleaned_improved = cleaned_improved[1:-1]
        
    # Report which knowledge rules were applied
    applied_rules = [r.get("source", "knowledge") for r in knowledge_rules[:3]] if knowledge_rules else []
    
    return ResumeImproveResponse(
        original_text=req.text_content,
        improved_text=cleaned_improved,
        applied_rules=applied_rules
    )
