import pytest
from app.models.models import StudentProfile, Role
from app.services.skill_gap_service import SkillGapService

def test_skill_gap_analysis(db_session):
    profile = db_session.query(StudentProfile).first()
    role = db_session.query(Role).filter(Role.slug == "backend-developer").first()
    assert profile is not None
    assert role is not None

    gap_service = SkillGapService(db_session)
    report = gap_service.analyze_skill_gap(profile.id, role.id)

    assert report.role_id == role.id
    assert report.overall_coverage_pct > 0.0
    assert report.total_role_skills > 0
    assert len(report.gaps) == report.total_role_skills

    # Student has Python and FastAPI
    python_gap = next((g for g in report.gaps if g.skill_name == "Python"), None)
    assert python_gap is not None
    assert python_gap.status == "matched"

    # Verify prioritization order
    priorities = [g.priority_level for g in report.gaps]
    # Check that any Critical items appear before Medium/Low
    if "Critical" in priorities and "Low" in priorities:
        assert priorities.index("Critical") < priorities.index("Low")
