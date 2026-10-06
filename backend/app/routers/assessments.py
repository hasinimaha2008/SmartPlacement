from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Skill, AssessmentAttempt, StudentSkill
from app.schemas.schemas import (
    AssessmentQuizResponse,
    AssessmentQuizQuestion,
    AssessmentSubmitRequest,
    AssessmentResultResponse
)
from app.services.roadmap_service import RoadmapService

router = APIRouter(prefix="/assessments", tags=["Assessments"])

SKILL_QUIZ_TEMPLATES = {
    "python": [
        {
            "id": "q_py_1",
            "question_text": "What is the key advantage of a Python generator function using 'yield' over returning a full list?",
            "options": [
                "Generators evaluate lazily, consuming O(1) memory for streaming iterations",
                "Generators automatically compile Python bytecode into C",
                "Generators run on multiple CPU cores by default",
                "Generators only support integer values"
            ],
            "correct": "Generators evaluate lazily, consuming O(1) memory for streaming iterations",
            "difficulty": "Intermediate"
        },
        {
            "id": "q_py_2",
            "question_text": "How does Python manage memory reclamation for objects with cyclic references?",
            "options": [
                "Through a generational garbage collector detecting cyclic reference graphs",
                "Pure reference counting handles cycles automatically",
                "Operating system virtual memory paging",
                "Cycles are never collected and leak memory until process termination"
            ],
            "correct": "Through a generational garbage collector detecting cyclic reference graphs",
            "difficulty": "Advanced"
        },
        {
            "id": "q_py_3",
            "question_text": "What does the GIL (Global Interpreter Lock) in CPython prevent?",
            "options": [
                "Multiple native threads from executing Python bytecodes simultaneously within a single process",
                "Asynchronous I/O operations from running in asyncio",
                "Subprocesses from utilizing more than 2GB of RAM",
                "C extensions from running multithreaded code"
            ],
            "correct": "Multiple native threads from executing Python bytecodes simultaneously within a single process",
            "difficulty": "Intermediate"
        }
    ],
    "sql": [
        {
            "id": "q_sql_1",
            "question_text": "What is the primary difference between WHERE and HAVING clauses in SQL?",
            "options": [
                "WHERE filters rows prior to aggregation, while HAVING filters post-GROUP BY aggregate metrics",
                "HAVING works only on numeric columns",
                "WHERE can only be used with primary key lookups",
                "HAVING is an outdated syntax superseded by WHERE"
            ],
            "correct": "WHERE filters rows prior to aggregation, while HAVING filters post-GROUP BY aggregate metrics",
            "difficulty": "Intermediate"
        },
        {
            "id": "q_sql_2",
            "question_text": "Which index structure is standard for range-based queries (e.g. BETWEEN, <, >) in PostgreSQL and MySQL?",
            "options": [
                "B-Tree index",
                "Hash index",
                "Full-text GIN index",
                "Bloom filter"
            ],
            "correct": "B-Tree index",
            "difficulty": "Intermediate"
        }
    ],
    "general": [
        {
            "id": "q_gen_1",
            "question_text": "What is the primary purpose of Continuous Integration (CI) in software development?",
            "options": [
                "To automatically test and validate small code commits frequently to catch regressions early",
                "To deploy software once per calendar quarter",
                "To eliminate the need for version control",
                "To replace code review completely"
            ],
            "correct": "To automatically test and validate small code commits frequently to catch regressions early",
            "difficulty": "Beginner"
        },
        {
            "id": "q_gen_2",
            "question_text": "In distributed REST architectures, why is idempotency important for HTTP PUT and DELETE operations?",
            "options": [
                "It guarantees repeated requests produce the same side-effect on the server as a single request",
                "It encrypts payloads during transit",
                "It compresses response bodies automatically",
                "It eliminates database transactions"
            ],
            "correct": "It guarantees repeated requests produce the same side-effect on the server as a single request",
            "difficulty": "Intermediate"
        }
    ]
}

@router.get("/quiz/{skill_id}", response_model=AssessmentQuizResponse)
def get_skill_quiz(skill_id: str, db: Session = Depends(get_db)):
    """
    Generates a timed diagnostic quiz for the specified skill.
    """
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    sk_key = skill.name.lower()
    raw_questions = SKILL_QUIZ_TEMPLATES.get(sk_key, SKILL_QUIZ_TEMPLATES["general"])

    questions = [
        AssessmentQuizQuestion(
            id=q["id"],
            question_text=q["question_text"],
            options=q["options"],
            difficulty=q["difficulty"]
        ) for q in raw_questions
    ]

    return AssessmentQuizResponse(
        skill_id=skill.id,
        skill_name=skill.name,
        category=skill.category,
        questions=questions
    )

@router.post("/submit", response_model=AssessmentResultResponse)
def submit_skill_quiz(payload: AssessmentSubmitRequest, db: Session = Depends(get_db)):
    """
    Evaluates quiz submissions, records the attempt, verifies skill, and adapts roadmap.
    """
    skill = db.query(Skill).filter(Skill.id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    sk_key = skill.name.lower()
    quiz_ref = {q["id"]: q["correct"] for q in SKILL_QUIZ_TEMPLATES.get(sk_key, SKILL_QUIZ_TEMPLATES["general"])}

    total = len(quiz_ref)
    correct_count = 0
    for q_id, correct_answer in quiz_ref.items():
        if payload.answers.get(q_id) == correct_answer:
            correct_count += 1

    percentage = round((correct_count / float(total)) * 100.0, 1) if total > 0 else 0.0
    passed = percentage >= 70.0

    # Save attempt
    attempt = AssessmentAttempt(
        student_profile_id=payload.student_id,
        category="Technical Quiz",
        skill_id=skill.id,
        total_questions=total,
        score=correct_count,
        percentage=percentage,
        passed=passed,
        feedback="Proficiency criteria satisfied." if passed else "Score below 70% threshold. Remedial study recommended."
    )
    db.add(attempt)

    # If passed, verify skill on profile
    if passed:
        st_skill = (
            db.query(StudentSkill)
            .filter(StudentSkill.student_profile_id == payload.student_id, StudentSkill.skill_id == skill.id)
            .first()
        )
        if st_skill:
            st_skill.verified = True

    db.commit()

    # Adaptive Roadmap Update
    roadmap_service = RoadmapService(db)
    adapt_info = roadmap_service.adapt_roadmap_on_assessment_result(
        payload.student_id, payload.skill_id, percentage
    )

    return AssessmentResultResponse(
        student_id=payload.student_id,
        skill_id=skill.id,
        skill_name=skill.name,
        score=correct_count,
        total_questions=total,
        percentage=percentage,
        passed=passed,
        feedback="Verified passing grade achieved!" if passed else "Review core tutorials and re-take when ready.",
        roadmap_adapted=adapt_info["adapted"],
        adaptation_note=adapt_info["message"]
    )
