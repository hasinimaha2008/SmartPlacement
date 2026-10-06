from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import StudentProfile, Role
from app.schemas.schemas import SkillGapAnalysisResponse
from app.services.skill_gap_service import SkillGapService

router = APIRouter(prefix="/skill-gap", tags=["Skill Gap"])

@router.get("/{role_id_or_slug}", response_model=SkillGapAnalysisResponse)
def get_skill_gap_analysis(
    role_id_or_slug: str,
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Computes exact skill gap analysis for a student against a specified role.
    """
    if not student_id:
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="No student profile found")
        student_id = profile.id

    role = (
        db.query(Role)
        .filter((Role.id == role_id_or_slug) | (Role.slug == role_id_or_slug))
        .first()
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    gap_service = SkillGapService(db)
    return gap_service.analyze_skill_gap(student_id, role.id)
