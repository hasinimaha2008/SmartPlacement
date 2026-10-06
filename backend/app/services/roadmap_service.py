from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import (
    Roadmap, RoadmapItem, Role, StudentProfile, LearningResource, Skill
)
from app.schemas.schemas import (
    RoadmapResponse, RoadmapStage, RoadmapMilestoneItem,
    RoadmapResourceSummary, RoadmapItemToggleResponse
)
from app.services.skill_gap_service import SkillGapService

class RoadmapService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_roadmap(self, student_id: str, role_id: str) -> RoadmapResponse:
        """
        Retrieves existing active roadmap or generates a deterministic personalized roadmap
        grounded in the student's exact skill gaps for the role.
        """
        existing = (
            self.db.query(Roadmap)
            .filter(Roadmap.student_profile_id == student_id, Roadmap.role_id == role_id)
            .first()
        )
        if existing and existing.items:
            return self._build_roadmap_response(existing)

        # Generate new personalized roadmap based on skill gap analysis
        gap_service = SkillGapService(self.db)
        gap_report = gap_service.analyze_skill_gap(student_id, role_id)
        role = self.db.query(Role).filter(Role.id == role_id).first()

        if existing:
            roadmap = existing
            # Clear old items to regenerate fresh
            for item in existing.items:
                self.db.delete(item)
            self.db.flush()
        else:
            roadmap = Roadmap(
                student_profile_id=student_id,
                role_id=role_id,
                title=f"Preparation Roadmap: {role.title}",
                description=f"Personalized milestone roadmap engineered to bridge {gap_report.missing_skills_count + gap_report.proficiency_gap_count} priority competencies for {role.title}.",
                status="active"
            )
            self.db.add(roadmap)
            self.db.flush()

        # Categorize gaps into 4 structured stages
        critical_missing = [g for g in gap_report.gaps if g.status == "missing" and g.priority_level == "Critical"]
        high_missing = [g for g in gap_report.gaps if g.status == "missing" and g.priority_level in ("High", "Medium")]
        proficiency_gaps = [g for g in gap_report.gaps if g.status == "proficiency_gap"]
        matched_skills = [g for g in gap_report.gaps if g.status == "matched"]

        order_idx = 0

        # Stage 1: Critical Prerequisite Foundations
        stage1_items = critical_missing if critical_missing else high_missing[:2]
        if not stage1_items and high_missing:
            stage1_items = high_missing[:1]

        for gap in stage1_items:
            item = RoadmapItem(
                roadmap_id=roadmap.id,
                skill_id=gap.skill_id,
                stage_number=1,
                stage_title="Stage 1: Core Prerequisite Foundations",
                title=f"Acquire Core Foundations: {gap.skill_name}",
                learning_objective=f"Master fundamental syntax, concepts, and standard library patterns in {gap.skill_name}. Target: {gap.required_proficiency}.",
                priority="Critical",
                estimated_hours=8,
                is_completed=False,
                order_index=order_idx
            )
            self.db.add(item)
            order_idx += 1

        # Stage 2: Applied Tooling & Framework Proficiency
        for gap in proficiency_gaps:
            item = RoadmapItem(
                roadmap_id=roadmap.id,
                skill_id=gap.skill_id,
                stage_number=2,
                stage_title="Stage 2: Applied Tooling & Framework Proficiency",
                title=f"Level Up {gap.skill_name} ({gap.student_proficiency} → {gap.required_proficiency})",
                learning_objective=f"Bridge proficiency gap in {gap.skill_name} through hands-on intermediate architectures, async workflows, and production patterns.",
                priority=gap.priority_level,
                estimated_hours=6,
                is_completed=False,
                order_index=order_idx
            )
            self.db.add(item)
            order_idx += 1

        # Stage 3: Systems Architecture & Project Implementation
        remaining_high = [g for g in high_missing if g not in stage1_items]
        for gap in remaining_high:
            item = RoadmapItem(
                roadmap_id=roadmap.id,
                skill_id=gap.skill_id,
                stage_number=3,
                stage_title="Stage 3: Systems Architecture & Project Implementation",
                title=f"Implement Project Integration: {gap.skill_name}",
                learning_objective=f"Integrate {gap.skill_name} into an end-to-end portfolio project featuring production test coverage and CI/CD packaging.",
                priority=gap.priority_level,
                estimated_hours=10,
                is_completed=False,
                order_index=order_idx
            )
            self.db.add(item)
            order_idx += 1

        # Stage 4: Placement Readiness & Interview Mastery
        final_interview_item = RoadmapItem(
            roadmap_id=roadmap.id,
            skill_id=None,
            stage_number=4,
            stage_title="Stage 4: Placement Readiness & Mock Interview Drills",
            title=f"Placement Mock Interview & Domain Assessments for {role.title}",
            learning_objective=f"Complete simulated technical question banks, timed aptitude drills, and AI mock interview sessions tailored for {role.title}.",
            priority="Critical",
            estimated_hours=8,
            is_completed=False,
            order_index=order_idx
        )
        self.db.add(final_interview_item)

        self.db.commit()
        self.db.refresh(roadmap)

        return self._build_roadmap_response(roadmap)

    def toggle_item_completion(self, item_id: str) -> RoadmapItemToggleResponse:
        """
        Toggles completion state of a specific roadmap milestone.
        """
        item = self.db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
        if not item:
            raise ValueError(f"Roadmap item {item_id} not found")

        item.is_completed = not item.is_completed
        item.completed_at = datetime.utcnow() if item.is_completed else None
        self.db.commit()

        # Recalculate roadmap completion percentage
        roadmap = self.db.query(Roadmap).filter(Roadmap.id == item.roadmap_id).first()
        total = len(roadmap.items)
        completed = sum(1 for i in roadmap.items if i.is_completed)
        pct = round((completed / float(total)) * 100.0, 1) if total > 0 else 0.0

        return RoadmapItemToggleResponse(
            item_id=item.id,
            is_completed=item.is_completed,
            roadmap_progress_percentage=pct
        )

    def adapt_roadmap_on_assessment_result(
        self, student_id: str, skill_id: str, score_pct: float
    ) -> Dict[str, Any]:
        """
        Concrete Adaptive Learning Mechanism:
        - If score < 70%: Flag topic as needing remedial practice, increase priority to 'Critical', add extra hours.
        - If score >= 70%: Auto-complete matching milestone item, celebrate proficiency verification.
        """
        roadmaps = self.db.query(Roadmap).filter(Roadmap.student_profile_id == student_id).all()
        adapted = False
        message = "No matching roadmap item found to adapt."

        for rm in roadmaps:
            for item in rm.items:
                if item.skill_id == skill_id:
                    adapted = True
                    if score_pct < 70.0:
                        item.priority = "Critical"
                        item.is_completed = False
                        item.estimated_hours += 4
                        item.learning_objective += " [REMEDIAL: Assessment score below 70%. Focus on review resources and re-take quiz.]"
                        message = f"Assessment score {score_pct}% below threshold. Roadmap item '{item.title}' priority elevated to Critical with 4 extra remedial hours assigned."
                    else:
                        item.is_completed = True
                        item.completed_at = datetime.utcnow()
                        message = f"Assessment score {score_pct}% meets target threshold! Roadmap item '{item.title}' marked completed."
                    self.db.commit()
                    break

        return {"adapted": adapted, "message": message}

    def _build_roadmap_response(self, roadmap: Roadmap) -> RoadmapResponse:
        role = self.db.query(Role).filter(Role.id == roadmap.role_id).first()
        role_title = role.title if role else "Target Role"

        stages_dict: Dict[int, List[RoadmapMilestoneItem]] = {}
        total_milestones = len(roadmap.items)
        completed_milestones = 0

        for item in roadmap.items:
            if item.is_completed:
                completed_milestones += 1

            # Fetch resources for this skill if present
            res_summaries = []
            if item.skill_id:
                resources = (
                    self.db.query(LearningResource)
                    .filter(LearningResource.skill_id == item.skill_id)
                    .limit(2)
                    .all()
                )
                for r in resources:
                    res_summaries.append(
                        RoadmapResourceSummary(
                            title=r.title,
                            resource_type=r.resource_type,
                            url=r.url,
                            estimated_hours=r.estimated_hours
                        )
                    )

            skill_name = None
            if item.skill_id:
                sk = self.db.query(Skill).filter(Skill.id == item.skill_id).first()
                if sk:
                    skill_name = sk.name

            m_item = RoadmapMilestoneItem(
                id=item.id,
                stage_number=item.stage_number,
                stage_title=item.stage_title,
                title=item.title,
                learning_objective=item.learning_objective or "",
                priority=item.priority,
                estimated_hours=item.estimated_hours,
                is_completed=item.is_completed,
                skill_id=item.skill_id,
                skill_name=skill_name,
                resources=res_summaries
            )

            stages_dict.setdefault(item.stage_number, []).append(m_item)

        stages_list = []
        stage_names = {
            1: "Core Prerequisite Foundations",
            2: "Applied Tooling & Framework Proficiency",
            3: "Systems Architecture & Project Implementation",
            4: "Placement Readiness & Interview Mastery"
        }
        for st_num in sorted(stages_dict.keys()):
            stages_list.append(
                RoadmapStage(
                    stage_number=st_num,
                    stage_title=stages_dict[st_num][0].stage_title if stages_dict[st_num] else f"Stage {st_num}",
                    stage_description=stage_names.get(st_num, f"Preparation Milestones Phase {st_num}"),
                    items=stages_dict[st_num]
                )
            )

        pct = (
            round((completed_milestones / float(total_milestones)) * 100.0, 1)
            if total_milestones > 0
            else 0.0
        )

        return RoadmapResponse(
            roadmap_id=roadmap.id,
            role_id=roadmap.role_id,
            role_title=role_title,
            status=roadmap.status,
            total_stages=len(stages_list),
            total_milestones=total_milestones,
            completed_milestones=completed_milestones,
            completion_percentage=pct,
            stages=stages_list
        )
