import pytest
from app.models.models import StudentProfile, Role
from app.services.readiness_service import ReadinessService

def test_readiness_indicator(db_session):
    profile = db_session.query(StudentProfile).first()
    role = db_session.query(Role).filter(Role.slug == "backend-developer").first()
    assert profile is not None
    assert role is not None

    service = ReadinessService(db_session)
    report = service.calculate_readiness_index(profile.id, role.id)

    assert report.role_id == role.id
    assert 0.0 <= report.readiness_score <= 100.0
    assert report.readiness_band in [
        "Beginning Preparation", "Developing Readiness", "Placement Ready", "Highly Competitive"
    ]
    assert len(report.factors) == 4
    assert sum(f.weight for f in report.factors) == pytest.approx(1.0, rel=1e-2)

    # Verify disclaimer prevents employment guarantee claims
    assert "does not guarantee employment" in report.disclaimer.lower()
