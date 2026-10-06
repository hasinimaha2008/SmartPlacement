from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import (
    StudentProfile, Role, Roadmap, AssessmentAttempt, MockInterview, ReadinessSnapshot
)
from app.schemas.schemas import (
    PreparationReadinessResponse,
    ReadinessFactorDetail
)
from app.services.skill_gap_service import SkillGapService

class ReadinessService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_readiness_index(
        self, student_id: str, role_id: str
    ) -> PreparationReadinessResponse:
        """
        Calculates the transparent Preparation Readiness Index (0-100) based on
        four empirical pillars of preparation evidence:
        1. Skill Coverage & Proficiency Alignment (35%)
        2. Roadmap Milestone Completion (25%)
        3. Assessment & Technical Quiz Performance (20%)
        4. Mock Interview & Practice Drills (20%)
        """
        profile = self.db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not profile:
            raise ValueError(f"Student profile {student_id} not found")

        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role {role_id} not found")

        # 1. Skill Coverage Factor (Weight 0.35)
        gap_service = SkillGapService(self.db)
        gap_report = gap_service.analyze_skill_gap(student_id, role_id)
        skill_score = gap_report.overall_coverage_pct

        # 2. Roadmap Milestone Completion (Weight 0.25)
        roadmap = (
            self.db.query(Roadmap)
            .filter(Roadmap.student_profile_id == student_id, Roadmap.role_id == role_id)
            .first()
        )
        if roadmap and roadmap.items:
            total_items = len(roadmap.items)
            completed_items = sum(1 for i in roadmap.items if i.is_completed)
            roadmap_score = round((completed_items / float(total_items)) * 100.0, 1)
        else:
            roadmap_score = 15.0 # baseline credit

        # 3. Assessment & Quiz Performance (Weight 0.20)
        attempts = (
            self.db.query(AssessmentAttempt)
            .filter(AssessmentAttempt.student_profile_id == student_id)
            .all()
        )
        if attempts:
            avg_assessment = sum(a.percentage for a in attempts) / len(attempts)
            assessment_score = round(min(100.0, avg_assessment), 1)
        else:
            assessment_score = 30.0 # baseline before taking quizzes

        # 4. Mock Interview & Practice (Weight 0.20)
        interviews = (
            self.db.query(MockInterview)
            .filter(MockInterview.student_profile_id == student_id, MockInterview.role_id == role_id)
            .all()
        )
        completed_interviews = [i for i in interviews if i.status == "completed"]
        if completed_interviews:
            avg_interview = sum(i.overall_score or 70.0 for i in completed_interviews) / len(completed_interviews)
            interview_score = round(min(100.0, avg_interview), 1)
        elif interviews:
            interview_score = 45.0 # started but in progress
        else:
            interview_score = 25.0

        # Weighted calculation
        overall_score = round(
            0.35 * skill_score +
            0.25 * roadmap_score +
            0.20 * assessment_score +
            0.20 * interview_score,
            1
        )

        # Interpretable Readiness Bands
        if overall_score >= 85.0:
            band = "Highly Competitive"
            badge = "success"
            interpretation = (
                "Exceptional readiness! Your technical skill coverage, project implementations, "
                "and assessment results place you in the top tier of candidates for campus placement drives."
            )
        elif overall_score >= 65.0:
            band = "Placement Ready"
            badge = "accent"
            interpretation = (
                "Solid preparation foundation! You meet the core requirements for entry-level positions. "
                "Targeting remaining roadmap milestones will further boost your confidence during technical interviews."
            )
        elif overall_score >= 40.0:
            band = "Developing Readiness"
            badge = "warning"
            interpretation = (
                "Steady progress underway. You have foundational skills in place, but need more practical project "
                "implementations and quiz validation before placement drives commence."
            )
        else:
            band = "Beginning Preparation"
            badge = "default"
            interpretation = (
                "Early preparation stage. Follow your personalized roadmap milestones to build core prerequisites "
                "and complete your first skill assessments."
            )

        factors = [
            ReadinessFactorDetail(
                factor_name="Role Skill Coverage & Proficiency",
                weight=0.35,
                score=skill_score,
                weighted_score=round(skill_score * 0.35, 1),
                benchmark="Target ≥ 75%",
                description=f"Evaluates verified skills and minimum proficiency levels against {role.title} requirements."
            ),
            ReadinessFactorDetail(
                factor_name="Roadmap Milestone Completion",
                weight=0.25,
                score=roadmap_score,
                weighted_score=round(roadmap_score * 0.25, 1),
                benchmark="Target ≥ 60%",
                description="Tracks progress across scheduled prerequisite, framework, and project learning modules."
            ),
            ReadinessFactorDetail(
                factor_name="Assessment & Technical Quiz Scores",
                weight=0.20,
                score=assessment_score,
                weighted_score=round(assessment_score * 0.20, 1),
                benchmark="Target ≥ 70%",
                description="Objective validation of theoretical concepts and coding fundamentals through timed quizzes."
            ),
            ReadinessFactorDetail(
                factor_name="Mock Interview & Practice Drills",
                weight=0.20,
                score=interview_score,
                weighted_score=round(interview_score * 0.20, 1),
                benchmark="Target ≥ 65%",
                description="Text-based AI interview simulation scores measuring clarity, technical depth, and structure."
            )
        ]

        strengths = []
        if skill_score >= 65.0:
            strengths.append(f"Strong fundamental skill coverage ({skill_score}%) for {role.title}.")
        if roadmap_score >= 50.0:
            strengths.append(f"Consistent progress on structured learning roadmap ({roadmap_score}% completed).")
        if assessment_score >= 70.0:
            strengths.append(f"Reliable domain knowledge demonstrated in quiz assessments ({assessment_score}%).")
        if not strengths:
            strengths.append("Clear growth trajectory with high upside once initial roadmap stages are completed.")

        focus_areas = []
        if skill_score < 70.0 and gap_report.critical_missing:
            focus_areas.append(f"Acquire missing core prerequisites: {', '.join(gap_report.critical_missing[:2])}.")
        if roadmap_score < 60.0:
            focus_areas.append("Complete pending Stage 1 & Stage 2 roadmap milestones.")
        if assessment_score < 70.0:
            focus_areas.append("Take skill validation quizzes to formally verify technical competencies.")
        if interview_score < 60.0:
            focus_areas.append("Participate in interactive mock interview sessions to refine answer articulation.")

        # Save snapshot
        snapshot = ReadinessSnapshot(
            student_profile_id=student_id,
            role_id=role_id,
            readiness_score=overall_score,
            readiness_band=band,
            skill_coverage_score=skill_score,
            roadmap_completion_score=roadmap_score,
            assessment_score=assessment_score,
            interview_practice_score=interview_score,
            snapshot_data={"factors": [f.model_dump() for f in factors]}
        )
        self.db.add(snapshot)
        self.db.commit()

        return PreparationReadinessResponse(
            student_id=student_id,
            role_id=role_id,
            role_title=role.title,
            readiness_score=overall_score,
            readiness_band=band,
            badge_variant=badge,
            interpretation=interpretation,
            factors=factors,
            strengths=strengths,
            priority_focus_areas=focus_areas
        )
