import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Question, Role, MockInterview, StudentProfile
from app.schemas.schemas import (
    QuestionResponse,
    MockInterviewTurn,
    MockInterviewFeedbackResponse
)

class InterviewService:
    def __init__(self, db: Session):
        self.db = db

    def get_questions(
        self,
        category: Optional[str] = None,
        role_id: Optional[str] = None,
        limit: int = 20
    ) -> List[QuestionResponse]:
        """
        Retrieves curated practice questions filtered by category and role.
        """
        query = self.db.query(Question)
        if category:
            query = query.filter(Question.category == category)
        if role_id:
            query = query.filter((Question.role_id == role_id) | (Question.role_id.is_(None)))

        questions = query.limit(limit).all()
        results = []
        for q in questions:
            results.append(
                QuestionResponse(
                    id=q.id,
                    category=q.category,
                    sub_category=q.sub_category,
                    difficulty=q.difficulty,
                    question_text=q.question_text,
                    options=q.options,
                    explanation=q.explanation,
                    skill_name=q.role.title if q.role else None
                )
            )
        return results

    def start_mock_interview(self, student_id: str, role_id: str) -> Dict[str, Any]:
        """
        Initializes an interactive 3-round text mock interview for the given role.
        """
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role {role_id} not found")

        # Questions tailored for role
        role_questions = [
            f"Explain how you would design and implement scalable, resilient API endpoints in {role.title} projects, including error handling and data validation.",
            f"Describe how you handle database query optimization, indexing strategies, and caching when throughput increases.",
            "Tell me about a difficult technical challenge or bug you solved in a previous project. What was the root cause and how did you verify the fix?"
        ]

        interview = MockInterview(
            student_profile_id=student_id,
            role_id=role_id,
            status="in_progress",
            transcript=[],
            strengths=[],
            areas_for_improvement=[]
        )
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)

        first_turn = MockInterviewTurn(
            question_number=1,
            question=role_questions[0],
            category="Technical Architecture"
        )

        return {
            "interview_id": interview.id,
            "role_title": role.title,
            "total_questions": len(role_questions),
            "current_turn": first_turn
        }

    def evaluate_mock_answer(
        self, interview_id: str, question_number: int, question_text: str, student_answer: str
    ) -> MockInterviewFeedbackResponse:
        """
        Evaluates student's text response using a structured rubric:
        - Relevance (alignment to prompt)
        - Technical Accuracy & Depth
        - Clarity & Structure (e.g. STAR methodology, concise terminology)
        """
        interview = self.db.query(MockInterview).filter(MockInterview.id == interview_id).first()
        if not interview:
            raise ValueError(f"Mock interview {interview_id} not found")

        answer_clean = student_answer.strip()
        word_count = len(answer_clean.split())

        # Scoring heuristics based on technical depth and structure
        relevance_score = 7.5
        technical_score = 7.0
        clarity_score = 8.0
        strengths = []
        improvements = []

        if word_count < 25:
            relevance_score = max(4.0, relevance_score - 2.5)
            technical_score = max(4.0, technical_score - 2.5)
            clarity_score = max(5.0, clarity_score - 2.0)
            improvements.append("Response is too brief. Elaborate with specific technical details, tools, and quantifiable results.")
        elif word_count >= 60:
            technical_score = min(9.5, technical_score + 1.5)
            relevance_score = min(9.5, relevance_score + 1.0)
            strengths.append("Comprehensive depth with adequate explanation of rationale and steps.")

        # Check for technical terminology
        tech_terms = [
            "database", "api", "cache", "redis", "index", "async", "latency",
            "microservice", "docker", "schema", "test", "verification", "scalability", "metric"
        ]
        matched_terms = [t for t in tech_terms if re.search(r'\b' + t + r'\b', answer_clean.lower())]

        if len(matched_terms) >= 3:
            technical_score = min(9.5, technical_score + 1.2)
            strengths.append(f"Effective use of professional domain vocabulary: {', '.join(matched_terms[:4])}.")
        else:
            improvements.append("Incorporate more precise architectural terminology (e.g., query execution plans, latency metrics, caching layers).")

        # Check for structured phrasing (e.g., first, because, result, optimized)
        if any(w in answer_clean.lower() for w in ["first", "then", "because", "result", "improved", "measured"]):
            clarity_score = min(9.5, clarity_score + 1.0)
            strengths.append("Logical progression and clear cause-and-effect reasoning.")
        else:
            improvements.append("Structure your answer using a clear sequence: Context → Action Taken → Verifiable Outcome.")

        overall_score = round((relevance_score * 0.35 + technical_score * 0.45 + clarity_score * 0.20), 1)

        model_ideal_answer = (
            "An exemplary response clearly defines the problem, articulates architectural trade-offs, "
            "specifies concrete tools (e.g. FastAPI middleware, PostgreSQL EXPLAIN ANALYZE, Redis TTL caching), "
            "and highlights measurable verification metrics (e.g., 40% reduction in p99 response latency)."
        )

        # Update transcript
        transcript_item = {
            "round": question_number,
            "question": question_text,
            "answer": student_answer,
            "scores": {
                "overall": overall_score,
                "relevance": round(relevance_score, 1),
                "technical": round(technical_score, 1),
                "clarity": round(clarity_score, 1)
            }
        }
        current_transcript = list(interview.transcript or [])
        current_transcript.append(transcript_item)
        interview.transcript = current_transcript

        # Determine next question or completion
        role_questions = [
            "Explain how you would design and implement scalable, resilient API endpoints in your projects, including error handling and data validation.",
            "Describe how you handle database query optimization, indexing strategies, and caching when throughput increases.",
            "Tell me about a difficult technical challenge or bug you solved in a previous project. What was the root cause and how did you verify the fix?"
        ]

        is_complete = question_number >= len(role_questions)
        next_turn = None

        if is_complete:
            interview.status = "completed"
            # Calculate aggregate score across all rounds
            all_scores = [t["scores"]["overall"] for t in current_transcript]
            interview.overall_score = round(sum(all_scores) / len(all_scores) * 10.0, 1) # scale to 100
        else:
            next_turn = MockInterviewTurn(
                question_number=question_number + 1,
                question=role_questions[question_number],
                category="System Architecture & Optimization" if question_number == 1 else "Behavioral Engineering"
            )

        self.db.commit()

        return MockInterviewFeedbackResponse(
            interview_id=interview.id,
            question_number=question_number,
            overall_score=overall_score,
            relevance_score=round(relevance_score, 1),
            technical_accuracy_score=round(technical_score, 1),
            clarity_score=round(clarity_score, 1),
            strengths=strengths if strengths else ["Polite and prompt communication."],
            areas_to_improve=improvements if improvements else ["Continue practicing with timed constraints."],
            model_improved_answer=model_ideal_answer,
            is_complete=is_complete,
            next_question=next_turn
        )
