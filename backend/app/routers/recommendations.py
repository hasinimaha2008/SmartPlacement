from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import StudentProfile
from app.schemas.schemas import (
    RecommendationListResponse,
    EvaluationReportResponse
)
from app.services.recommendation_service import RecommendationService
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("", response_model=RecommendationListResponse)
def get_recommendations(
    student_id: Optional[str] = Query(None),
    top_k: int = Query(5, ge=1, le=15),
    db: Session = Depends(get_db)
):
    """
    Computes hybrid job-role recommendations with multi-factor score breakdown and explainability.
    """
    if not student_id:
        profile = db.query(StudentProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="No student profile found")
        student_id = profile.id

    rec_service = RecommendationService(db)
    try:
        return rec_service.generate_recommendations(student_id, top_k=top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evaluate", response_model=EvaluationReportResponse)
def run_evaluation_benchmark(db: Session = Depends(get_db)):
    """
    Executes empirical baseline evaluation (TF-IDF vs Semantic vs Structured vs Hybrid)
    and Ablation Study analysis for academic research defense.
    """
    eval_service = EvaluationService(db)
    return eval_service.run_benchmark_and_ablation()
