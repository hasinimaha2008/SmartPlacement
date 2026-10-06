from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import StudentProfile, Role, AssessmentAttempt
from app.schemas.schemas import UnifiedDashboardResponse
from app.routers.profile import _format_profile_response
from app.routers.roles import get_role_detail
from app.services.recommendation_service import RecommendationService
from app.services.readiness_service import ReadinessService
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=UnifiedDashboardResponse)
def get_unified_dashboard(
    student_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns unified consolidated dashboard data for student:
    - Profile
    - Target Role details
    - Top Recommended Roles with explainability
    - Preparation Readiness Index
    - Active Roadmap with completed milestones
    - Quick summary metrics
    """
    if student_id:
        profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    else:
        profile = db.query(StudentProfile).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # 1. Profile response
    profile_resp = _format_profile_response(profile)

    # 2. Recommendations
    rec_service = RecommendationService(db)
    rec_resp = rec_service.generate_recommendations(profile.id, top_k=3)

    # 3. Target Role
    target_role_id = profile.target_role_id or (rec_resp.recommendations[0].role_id if rec_resp.recommendations else None)
    target_role_resp = None
    readiness_resp = None
    roadmap_resp = None

    if target_role_id:
        target_role = db.query(Role).filter(Role.id == target_role_id).first()
        if target_role:
            target_role_resp = get_role_detail(target_role.id, db)
            
            # Readiness
            read_service = ReadinessService(db)
            readiness_resp = read_service.calculate_readiness_index(profile.id, target_role.id)

            # Roadmap
            rm_service = RoadmapService(db)
            roadmap_resp = rm_service.get_or_create_roadmap(profile.id, target_role.id)

    # Recent assessments
    attempts = (
        db.query(AssessmentAttempt)
        .filter(AssessmentAttempt.student_profile_id == profile.id)
        .order_by(AssessmentAttempt.created_at.desc())
        .limit(5)
        .all()
    )
    attempts_data = [
        {
            "id": a.id,
            "category": a.category,
            "score": a.score,
            "total": a.total_questions,
            "percentage": a.percentage,
            "passed": a.passed,
            "date": a.created_at.strftime("%Y-%m-%d") if a.created_at else None
        } for a in attempts
    ]

    quick_stats = {
        "verified_skills_count": len(profile.skills),
        "projects_count": len(profile.projects),
        "certifications_count": len(profile.certifications),
        "target_role_title": target_role_resp.title if target_role_resp else "None Selected",
        "readiness_score": readiness_resp.readiness_score if readiness_resp else 0.0,
        "readiness_band": readiness_resp.readiness_band if readiness_resp else "Beginning Preparation",
        "roadmap_progress": roadmap_resp.completion_percentage if roadmap_resp else 0.0
    }

    return UnifiedDashboardResponse(
        profile=profile_resp,
        target_role=target_role_resp,
        top_recommendations=rec_resp.recommendations,
        readiness=readiness_resp,
        active_roadmap=roadmap_resp,
        recent_assessments=attempts_data,
        quick_stats=quick_stats
    )
