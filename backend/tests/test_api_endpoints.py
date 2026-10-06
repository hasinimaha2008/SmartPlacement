import pytest

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert data["database"] == "healthy"
    assert data["taxonomy"]["roles_loaded"] >= 15

def test_roles_endpoints(client):
    res = client.get("/api/roles")
    assert res.status_code == 200
    roles = res.json()
    assert len(roles) >= 15

    # Test single role
    first_slug = roles[0]["slug"]
    res_single = client.get(f"/api/roles/{first_slug}")
    assert res_single.status_code == 200
    assert res_single.json()["slug"] == first_slug

def test_skills_extract_endpoint(client):
    payload = {"text": "I develop in Python, FastAPI, and PostgreSQL with Docker."}
    res = client.post("/api/skills/extract", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 3

def test_profile_endpoint(client):
    res = client.get("/api/profile")
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Aarav Sharma"
    assert len(data["skills"]) >= 5

def test_recommendations_endpoint(client):
    res = client.get("/api/recommendations?top_k=3")
    assert res.status_code == 200
    data = res.json()
    assert len(data["recommendations"]) == 3
    assert data["recommendations"][0]["match_percentage"] > 0

def test_dashboard_endpoint(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "profile" in data
    assert "top_recommendations" in data
    assert "quick_stats" in data
    assert data["quick_stats"]["target_role_title"] != ""
