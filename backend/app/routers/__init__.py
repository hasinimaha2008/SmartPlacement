from app.routers.health import router as health_router
from app.routers.roles import router as roles_router
from app.routers.skills import router as skills_router
from app.routers.profile import router as profile_router
from app.routers.recommendations import router as recommendations_router
from app.routers.skill_gap import router as skill_gap_router
from app.routers.roadmap import router as roadmap_router
from app.routers.resources import router as resources_router
from app.routers.interview import router as interview_router
from app.routers.assessments import router as assessments_router
from app.routers.readiness import router as readiness_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "health_router",
    "roles_router",
    "skills_router",
    "profile_router",
    "recommendations_router",
    "skill_gap_router",
    "roadmap_router",
    "resources_router",
    "interview_router",
    "assessments_router",
    "readiness_router",
    "dashboard_router"
]
