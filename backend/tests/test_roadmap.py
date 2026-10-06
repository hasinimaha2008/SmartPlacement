import pytest
from app.models.models import StudentProfile, Role, RoadmapItem
from app.services.roadmap_service import RoadmapService

def test_roadmap_generation_and_toggle(db_session):
    profile = db_session.query(StudentProfile).first()
    role = db_session.query(Role).filter(Role.slug == "backend-developer").first()
    assert profile is not None
    assert role is not None

    service = RoadmapService(db_session)
    roadmap = service.get_or_create_roadmap(profile.id, role.id)

    assert roadmap.role_id == role.id
    assert roadmap.total_stages >= 2
    assert roadmap.total_milestones > 0

    first_item = roadmap.stages[0].items[0]
    assert first_item.is_completed is False

    # Test toggle
    toggle_resp = service.toggle_item_completion(first_item.id)
    assert toggle_resp.is_completed is True
    assert toggle_resp.roadmap_progress_percentage > 0.0

def test_adaptive_roadmap_update(db_session):
    profile = db_session.query(StudentProfile).first()
    role = db_session.query(Role).filter(Role.slug == "backend-developer").first()
    service = RoadmapService(db_session)
    roadmap = service.get_or_create_roadmap(profile.id, role.id)

    # Pick a milestone with a skill
    item_with_skill = next((i for s in roadmap.stages for i in s.items if i.skill_id is not None), None)
    if item_with_skill:
        # Simulate failing assessment (< 70%)
        result = service.adapt_roadmap_on_assessment_result(profile.id, item_with_skill.skill_id, 50.0)
        assert result["adapted"] is True

        # Refresh item
        updated = db_session.query(RoadmapItem).filter(RoadmapItem.id == item_with_skill.id).first()
        assert updated.priority == "Critical"
        assert "REMEDIAL" in updated.learning_objective
