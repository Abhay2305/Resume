from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Template
from ..schemas import TemplateOut

router = APIRouter(prefix="/templates", tags=["Templates"])

@router.get("", response_model=List[TemplateOut])
def list_templates(db: Session = Depends(get_db)):
    """
    Returns the dynamic template metadata (24 custom templates) stored in the database.
    """
    return db.query(Template).all()

@router.get("/{template_id}", response_model=TemplateOut)
def get_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
