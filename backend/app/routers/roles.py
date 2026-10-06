from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.models import Role
from app.schemas.schemas import RoleDetailResponse, RoleSkillInfo

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("", response_model=List[RoleDetailResponse])
def list_roles(db: Session = Depends(get_db)):
    """
    Lists all controlled target roles with descriptions, required skills, and weights.
    """
    roles = db.query(Role).all()
    results = []
    for r in roles:
        skills_info = []
        for rs in r.role_skills:
            if rs.skill:
                skills_info.append(
                    RoleSkillInfo(
                        skill_id=rs.skill_id,
                        name=rs.skill.name,
                        category=rs.skill.category,
                        importance=rs.importance,
                        minimum_proficiency=rs.minimum_proficiency,
                        weight=rs.weight
                    )
                )
        results.append(
            RoleDetailResponse(
                id=r.id,
                slug=r.slug,
                title=r.title,
                category=r.category,
                description=r.description,
                academic_requirements=r.academic_requirements,
                career_outlook=r.career_outlook,
                skills=skills_info
            )
        )
    return results

@router.get("/{id_or_slug}", response_model=RoleDetailResponse)
def get_role_detail(id_or_slug: str, db: Session = Depends(get_db)):
    """
    Retrieves full details for a single role by UUID id or URL slug.
    """
    role = (
        db.query(Role)
        .filter((Role.id == id_or_slug) | (Role.slug == id_or_slug))
        .first()
    )
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    skills_info = []
    for rs in role.role_skills:
        if rs.skill:
            skills_info.append(
                RoleSkillInfo(
                    skill_id=rs.skill_id,
                    name=rs.skill.name,
                    category=rs.skill.category,
                    importance=rs.importance,
                    minimum_proficiency=rs.minimum_proficiency,
                    weight=rs.weight
                )
            )

    return RoleDetailResponse(
        id=role.id,
        slug=role.slug,
        title=role.title,
        category=role.category,
        description=role.description,
        academic_requirements=role.academic_requirements,
        career_outlook=role.career_outlook,
        skills=skills_info
    )
