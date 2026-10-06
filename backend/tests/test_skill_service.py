import pytest
from app.services.skill_service import SkillService

def test_skill_normalization(db_session):
    service = SkillService(db_session)
    
    # Test canonical
    res = service.normalize_skill_name("Python")
    assert res is not None
    assert res[0] == "Python"
    assert res[1] == "Programming"

    # Test alias
    res_alias = service.normalize_skill_name("py")
    assert res_alias is not None
    assert res_alias[0] == "Python"

    # Test reactjs alias
    res_react = service.normalize_skill_name("reactjs")
    assert res_react is not None
    assert res_react[0] == "React"

    # Test postgres alias
    res_pg = service.normalize_skill_name("postgres")
    assert res_pg is not None
    assert res_pg[0] == "PostgreSQL"

def test_skill_extraction_from_resume_text(db_session):
    service = SkillService(db_session)
    resume_text = """
    Software Engineering student proficient in Python, FastAPI, Docker, and PostgreSQL.
    Built full-stack applications with React, TypeScript, and Tailwind CSS.
    Experienced in Data Structures & Algorithms, Git, and automated Unit Testing.
    """
    extraction = service.extract_skills_from_text(resume_text)
    
    assert extraction.count >= 6
    canonical_names = {s.canonical_name for s in extraction.extracted_skills}
    
    assert "Python" in canonical_names
    assert "FastAPI" in canonical_names
    assert "Docker" in canonical_names
    assert "PostgreSQL" in canonical_names
    assert "React" in canonical_names
    assert "Data Structures & Algorithms" in canonical_names
