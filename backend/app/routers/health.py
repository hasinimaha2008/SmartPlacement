from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Role, Skill

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint verifying API service, database connectivity, and seed status.
    """
    try:
        roles_count = db.query(Role).count()
        skills_count = db.query(Skill).count()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
        roles_count = 0
        skills_count = 0

    return {
        "status": "online",
        "service": "SmartPlacement API",
        "version": "1.0.0",
        "database": db_status,
        "taxonomy": {
            "roles_loaded": roles_count,
            "skills_loaded": skills_count
        }
    }
