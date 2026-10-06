from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Role, StudentProfile, RoleSkill
from app.schemas.schemas import SkillGapItem, SkillGapAnalysisResponse

PROFICIENCY_RANK = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

class SkillGapService:
    def __init__(self, db: Session):
        self.db = db

    def analyze_skill_gap(self, student_id: str, role_id: str) -> SkillGapAnalysisResponse:
        """
        Calculates exact role-skill gaps for a student against a chosen target role.
        Distinguishes:
        - Matched skills
        - Proficiency gaps (has skill, but below required level)
        - Missing skills (does not have skill)
        Provides priority level ('Critical', 'High', 'Medium', 'Low') and concrete learning guidance.
        """
        profile = self.db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
        if not profile:
            raise ValueError(f"Student profile {student_id} not found")

        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role {role_id} not found")

        student_skills_map: Dict[str, str] = {
            ss.skill.name: ss.proficiency
            for ss in profile.skills
            if ss.skill
        }

        role_skills: List[RoleSkill] = role.role_skills

        gaps: List[SkillGapItem] = []
        matched_count = 0
        proficiency_gap_count = 0
        missing_count = 0
        critical_missing = []

        total_weight = sum(rs.weight for rs in role_skills) if role_skills else 1.0
        earned_weight = 0.0

        for rs in role_skills:
            sk_name = rs.skill.name if rs.skill else "Unknown"
            sk_cat = rs.skill.category if rs.skill else "General"
            req_prof = rs.minimum_proficiency
            req_rank = PROFICIENCY_RANK.get(req_prof, 2)

            if sk_name in student_skills_map:
                cur_prof = student_skills_map[sk_name]
                cur_rank = PROFICIENCY_RANK.get(cur_prof, 1)

                if cur_rank >= req_rank:
                    # Fully matched
                    matched_count += 1
                    earned_weight += rs.weight
                    status = "matched"
                    priority = "Low"
                    guidance = f"You meet or exceed the target {req_prof} proficiency for {sk_name}. Continue to maintain your knowledge through advanced problem-solving."
                else:
                    # Proficiency gap
                    proficiency_gap_count += 1
                    earned_weight += rs.weight * (cur_rank / float(req_rank))
                    status = "proficiency_gap"
                    priority = "Critical" if rs.importance == "required" else "High"
                    guidance = f"Elevate from {cur_prof} to {req_prof} level by building hands-on implementations and completing intermediate-to-advanced project milestones."
            else:
                # Completely missing
                missing_count += 1
                status = "missing"
                if rs.importance == "required":
                    priority = "Critical"
                    critical_missing.append(sk_name)
                    guidance = f"Core prerequisite missing! Dedicate immediate study to acquire foundational and practical proficiency in {sk_name}."
                elif rs.importance == "preferred":
                    priority = "High"
                    guidance = f"Strongly recommended for competitive edge. Master {sk_name} after addressing critical prerequisites."
                else:
                    priority = "Medium"
                    guidance = f"Optional competency that adds breadth to your profile."

            gaps.append(
                SkillGapItem(
                    skill_id=rs.skill_id,
                    skill_name=sk_name,
                    category=sk_cat,
                    importance=rs.importance,
                    required_proficiency=req_prof,
                    student_proficiency=student_skills_map.get(sk_name),
                    status=status,
                    priority_level=priority,
                    weight=rs.weight,
                    guidance=guidance
                )
            )

        # Sort gaps by priority order: Critical -> High -> Medium -> Low
        priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
        gaps.sort(key=lambda x: (priority_order.get(x.priority_level, 5), -x.weight))

        coverage_pct = round((earned_weight / total_weight) * 100.0, 1) if total_weight > 0 else 0.0

        return SkillGapAnalysisResponse(
            role_id=role.id,
            role_title=role.title,
            overall_coverage_pct=min(100.0, coverage_pct),
            total_role_skills=len(role_skills),
            matched_skills_count=matched_count,
            proficiency_gap_count=proficiency_gap_count,
            missing_skills_count=missing_count,
            critical_missing=critical_missing,
            gaps=gaps
        )
