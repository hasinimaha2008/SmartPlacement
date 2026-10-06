from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import (
    StudentProfile, User, Skill, StudentSkill,
    StudentProject, StudentCertification, StudentExperience
)
from app.schemas.schemas import (
    StudentProfileCreate,
    StudentProfileResponse,
    StudentSkillResponse,
    ProjectResponse,
    CertificationResponse,
    ExperienceResponse
)

router = APIRouter(prefix="/profile", tags=["Profile"])

def _format_profile_response(profile: StudentProfile) -> StudentProfileResponse:
    skills_list = []
    for ss in profile.skills:
        if ss.skill:
            skills_list.append(
                StudentSkillResponse(
                    id=ss.id,
                    skill_id=ss.skill_id,
                    name=ss.skill.name,
                    category=ss.skill.category,
                    proficiency=ss.proficiency,
                    verified=ss.verified
                )
            )

    projects_list = [
        ProjectResponse(
            id=p.id,
            title=p.title,
            description=p.description,
            technologies=p.technologies or [],
            github_url=p.github_url,
            live_url=p.live_url
        ) for p in (profile.projects or [])
    ]

    certs_list = [
        CertificationResponse(
            id=c.id,
            title=c.title,
            issuing_organization=c.issuing_organization,
            issue_year=c.issue_year,
            credential_url=c.credential_url
        ) for c in (profile.certifications or [])
    ]

    exp_list = [
        ExperienceResponse(
            id=e.id,
            title=e.title,
            company=e.company,
            experience_type=e.experience_type,
            start_date=e.start_date,
            end_date=e.end_date,
            description=e.description,
            skills_used=e.skills_used or []
        ) for e in (profile.experiences or [])
    ]

    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        full_name=profile.user.full_name if profile.user else "Student",
        email=profile.user.email if profile.user else "",
        headline=profile.headline,
        degree=profile.degree,
        branch=profile.branch,
        graduation_year=profile.graduation_year,
        cgpa=profile.cgpa,
        bio=profile.bio,
        interests=profile.interests or [],
        target_role_id=profile.target_role_id,
        skills=skills_list,
        projects=projects_list,
        certifications=certs_list,
        experiences=exp_list
    )

@router.get("", response_model=StudentProfileResponse)
def get_student_profile(student_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Returns the student profile. If student_id is not specified, returns the first/demo profile.
    """
    if student_id:
        profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    else:
        profile = db.query(StudentProfile).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    return _format_profile_response(profile)

@router.post("", response_model=StudentProfileResponse)
def create_or_update_profile(payload: StudentProfileCreate, db: Session = Depends(get_db)):
    """
    Creates or updates the student profile, updating skills, projects, certifications, experiences.
    """
    # Find existing user or create
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        user = User(
            email=payload.email,
            full_name=payload.full_name,
            role="student"
        )
        db.add(user)
        db.flush()
    else:
        user.full_name = payload.full_name

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(user_id=user.id)
        db.add(profile)
        db.flush()

    profile.headline = payload.headline
    profile.degree = payload.degree
    profile.branch = payload.branch
    profile.graduation_year = payload.graduation_year
    profile.cgpa = payload.cgpa
    profile.bio = payload.bio
    profile.interests = payload.interests
    if payload.target_role_id:
        profile.target_role_id = payload.target_role_id

    # Update skills
    db.query(StudentSkill).filter(StudentSkill.student_profile_id == profile.id).delete()
    for s_in in payload.skills:
        # Match canonical skill
        sk = db.query(Skill).filter(Skill.name.ilike(s_in.skill_name.strip())).first()
        if not sk:
            # Check aliases
            all_skills = db.query(Skill).all()
            for cand in all_skills:
                if s_in.skill_name.strip().lower() in [a.lower() for a in (cand.aliases or [])]:
                    sk = cand
                    break

        if sk:
            st_skill = StudentSkill(
                student_profile_id=profile.id,
                skill_id=sk.id,
                proficiency=s_in.proficiency,
                verified=True
            )
            db.add(st_skill)

    # Update projects
    db.query(StudentProject).filter(StudentProject.student_profile_id == profile.id).delete()
    for p_in in payload.projects:
        proj = StudentProject(
            student_profile_id=profile.id,
            title=p_in.title,
            description=p_in.description,
            technologies=p_in.technologies,
            github_url=p_in.github_url,
            live_url=p_in.live_url
        )
        db.add(proj)

    # Update certifications
    db.query(StudentCertification).filter(StudentCertification.student_profile_id == profile.id).delete()
    for c_in in payload.certifications:
        cert = StudentCertification(
            student_profile_id=profile.id,
            title=c_in.title,
            issuing_organization=c_in.issuing_organization,
            issue_year=c_in.issue_year,
            credential_url=c_in.credential_url
        )
        db.add(cert)

    # Update experiences
    db.query(StudentExperience).filter(StudentExperience.student_profile_id == profile.id).delete()
    for e_in in payload.experiences:
        exp = StudentExperience(
            student_profile_id=profile.id,
            title=e_in.title,
            company=e_in.company,
            experience_type=e_in.experience_type,
            start_date=e_in.start_date,
            end_date=e_in.end_date,
            description=e_in.description,
            skills_used=e_in.skills_used
        )
        db.add(exp)

    db.commit()
    db.refresh(profile)
    return _format_profile_response(profile)
