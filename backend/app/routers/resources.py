from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import LearningResource, Skill
from app.schemas.schemas import LearningResourceResponse

router = APIRouter(prefix="/resources", tags=["Learning Resources"])

@router.get("", response_model=List[LearningResourceResponse])
def get_learning_resources(
    skill_name: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Retrieves curated learning resources with filtering.
    """
    query = db.query(LearningResource)

    if skill_name:
        skill = db.query(Skill).filter(Skill.name.ilike(skill_name.strip())).first()
        if skill:
            query = query.filter(LearningResource.skill_id == skill.id)

    if difficulty:
        query = query.filter(LearningResource.difficulty == difficulty)

    if resource_type:
        query = query.filter(LearningResource.resource_type == resource_type)

    resources = query.order_by(LearningResource.rating.desc()).all()
    results = []
    for r in resources:
        results.append(
            LearningResourceResponse(
                id=r.id,
                title=r.title,
                category=r.category,
                skill_name=r.skill.name if r.skill else None,
                difficulty=r.difficulty,
                resource_type=r.resource_type,
                url=r.url,
                estimated_hours=r.estimated_hours,
                rating=r.rating
            )
        )
    return results
