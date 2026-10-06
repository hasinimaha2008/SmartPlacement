from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import StudentProfile, Role
from app.schemas.schemas import RoadmapResponse, RoadmapItemToggleResponse
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/roadmap", tags=["Roadmap"])

@router.get("/{role_id_or_slug}", response_model=RoadmapResponse)
def get_or_generate_roadmap(
    role_id_or_slug: str,
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieves or generates a personalized preparation roadmap for the student and role.
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

    service = RoadmapService(db)
    return service.get_or_create_roadmap(student_id, role.id)

@router.post("/item/{item_id}/toggle", response_model=RoadmapItemToggleResponse)
def toggle_roadmap_milestone(item_id: str, db: Session = Depends(get_db)):
    """
    Toggles completion state of a specific roadmap milestone.
    """
    service = RoadmapService(db)
    try:
        return service.toggle_item_completion(item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
