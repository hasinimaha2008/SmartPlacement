import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.seed_data import seed_database_if_empty
from app.routers import (
    health_router,
    roles_router,
    skills_router,
    profile_router,
    recommendations_router,
    skill_gap_router,
    roadmap_router,
    resources_router,
    interview_router,
    assessments_router,
    readiness_router,
    dashboard_router
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartplacement")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed canonical taxonomy
    logger.info("Initializing SmartPlacement database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        logger.info("Seeding canonical roles, skills, and knowledge graph mappings...")
        seed_database_if_empty(db)
        logger.info("SmartPlacement initialization complete.")
    finally:
        db.close()

    yield
    logger.info("SmartPlacement API shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="AI/ML-Powered Student Career Guidance & Placement Preparation Platform API",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Include Routers
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(roles_router, prefix=settings.API_V1_STR)
app.include_router(skills_router, prefix=settings.API_V1_STR)
app.include_router(profile_router, prefix=settings.API_V1_STR)
app.include_router(recommendations_router, prefix=settings.API_V1_STR)
app.include_router(skill_gap_router, prefix=settings.API_V1_STR)
app.include_router(roadmap_router, prefix=settings.API_V1_STR)
app.include_router(resources_router, prefix=settings.API_V1_STR)
app.include_router(interview_router, prefix=settings.API_V1_STR)
app.include_router(assessments_router, prefix=settings.API_V1_STR)
app.include_router(readiness_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": "SmartPlacement",
        "description": "AI/ML Placement Guidance & Preparation Platform",
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_STR,
        "status": "healthy"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
