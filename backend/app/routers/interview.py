from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import StudentProfile, Role
from app.schemas.schemas import (
    QuestionResponse,
    MockInterviewStartRequest,
    MockInterviewAnswerSubmit,
    MockInterviewFeedbackResponse
)
from app.services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview Preparation"])

@router.get("/questions", response_model=List[QuestionResponse])
def get_practice_questions(
    category: Optional[str] = Query(None, description="Technical, Aptitude, or HR"),
    role_id: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Returns curated practice questions filtered by category and role.
    """
    service = InterviewService(db)
    return service.get_questions(category=category, role_id=role_id, limit=limit)

@router.post("/mock/start")
def start_mock_interview(payload: MockInterviewStartRequest, db: Session = Depends(get_db)):
    """
    Initializes a new text-based AI mock interview session.
    """
    student = db.query(StudentProfile).filter(StudentProfile.id == payload.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    service = InterviewService(db)
    return service.start_mock_interview(payload.student_id, payload.role_id)

@router.post("/mock/answer", response_model=MockInterviewFeedbackResponse)
def submit_mock_answer(payload: MockInterviewAnswerSubmit, db: Session = Depends(get_db)):
    """
    Evaluates student mock answer and returns structured feedback rubric and next question.
    """
    service = InterviewService(db)
    try:
        return service.evaluate_mock_answer(
            interview_id=payload.interview_id,
            question_number=payload.question_number,
            question_text=payload.question_text,
            student_answer=payload.student_answer
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
