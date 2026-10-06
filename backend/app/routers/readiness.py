from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import StudentProfile, Role
from app.schemas.schemas import PreparationReadinessResponse
from app.services.readiness_service import ReadinessService

router = APIRouter(prefix="/readiness", tags=["Preparation Readiness"])

@router.get("/{role_id_or_slug}", response_model=PreparationReadinessResponse)
def get_preparation_readiness(
    role_id_or_slug: str,
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Computes transparent multi-factor Preparation Readiness Index (0-100)
    combining Skill Coverage, Roadmap Completion, Quiz Scores, and Mock Interviews.
    """
    if not student_id:
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Student profile not found")
        student_id = profile.id

    role = (
        db.query(Role)
        .filter((Role.id == role_id_or_slug) | (Role.slug == role_id_or_slug))
        .first()
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    service = ReadinessService(db)
    return service.calculate_readiness_index(student_id, role.id)
