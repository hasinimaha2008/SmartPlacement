from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Skill
from app.schemas.schemas import (
    SkillResponse,
    SkillExtractionRequest,
    SkillExtractionResponse
)
from app.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=List[SkillResponse])
def list_canonical_skills(db: Session = Depends(get_db)):
    """
    Returns all canonical skills with categories and aliases.
    """
    skills = db.query(Skill).order_by(Skill.category, Skill.name).all()
    return skills

@router.post("/extract", response_model=SkillExtractionResponse)
def extract_skills_from_text(payload: SkillExtractionRequest, db: Session = Depends(get_db)):
    """
    Extracts and normalizes technical skills from free text or pasted resume content.
    """
    service = SkillService(db)
    return service.extract_skills_from_text(payload.text)
