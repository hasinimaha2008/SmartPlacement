import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="student")  # 'student', 'placement_officer', 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    headline = Column(String(255), nullable=True)
    degree = Column(String(100), default="B.Tech")
    branch = Column(String(100), default="Computer Science and Engineering")
    graduation_year = Column(Integer, default=2026)
    cgpa = Column(Float, default=8.2)
    bio = Column(Text, nullable=True)
    interests = Column(JSON, default=list)  # list of string interest tags
    target_role_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")
    skills = relationship("StudentSkill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("StudentProject", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("StudentCertification", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("StudentExperience", back_populates="profile", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="profile", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="profile", cascade="all, delete-orphan")
    mock_interviews = relationship("MockInterview", back_populates="profile", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    aliases = Column(JSON, default=list)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student_skills = relationship("StudentSkill", back_populates="skill")
    role_skills = relationship("RoleSkill", back_populates="skill")
    resources = relationship("LearningResource", back_populates="skill")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency = Column(String(20), default="Beginner")  # 'Beginner', 'Intermediate', 'Advanced'
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="student_skills")


class StudentProject(Base):
    __tablename__ = "student_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)
    github_url = Column(String(500), nullable=True)
    live_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="projects")


class StudentCertification(Base):
    __tablename__ = "student_certifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    issuing_organization = Column(String(255), nullable=True)
    issue_year = Column(Integer, nullable=True)
    credential_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="certifications")


class StudentExperience(Base):
    __tablename__ = "student_experiences"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    experience_type = Column(String(50), default="Internship")  # 'Internship', 'Part-time', 'Full-time'
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    skills_used = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="experiences")


class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    academic_requirements = Column(Text, nullable=True)
    career_outlook = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role_skills = relationship("RoleSkill", back_populates="role", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="role")


class RoleSkill(Base):
    __tablename__ = "role_skills"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    importance = Column(String(20), default="required")  # 'required', 'preferred', 'optional'
    minimum_proficiency = Column(String(20), default="Intermediate")
    weight = Column(Float, default=1.0)

    role = relationship("Role", back_populates="role_skills")
    skill = relationship("Skill", back_populates="role_skills")


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String(100), nullable=True)
    difficulty = Column(String(20), default="Beginner")
    resource_type = Column(String(50), default="Documentation")  # 'Documentation', 'Course', 'Tutorial', 'Video', 'Book'
    url = Column(String(500), nullable=False)
    estimated_hours = Column(Integer, default=4)
    rating = Column(Float, default=4.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    skill = relationship("Skill", back_populates="resources")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="SET NULL"), nullable=True, index=True)
    skill_id = Column(String(36), ForeignKey("skills.id", ondelete="SET NULL"), nullable=True, index=True)
    category = Column(String(50), nullable=False, index=True)  # 'Technical', 'Aptitude', 'HR'
    sub_category = Column(String(100), nullable=True)
    difficulty = Column(String(20), default="Intermediate")
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)  # List of strings for MCQs
    correct_answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="questions")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    skill_id = Column(String(36), nullable=True)
    total_questions = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    passed = Column(Boolean, default=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="assessment_attempts")


class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="in_progress")
    overall_score = Column(Float, nullable=True)
    strengths = Column(JSON, default=list)
    areas_for_improvement = Column(JSON, default=list)
    feedback = Column(Text, nullable=True)
    transcript = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="mock_interviews")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("StudentProfile", back_populates="roadmaps")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapItem.order_index")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    roadmap_id = Column(String(36), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id = Column(String(36), nullable=True)
    stage_number = Column(Integer, default=1)
    stage_title = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    learning_objective = Column(Text, nullable=True)
    priority = Column(String(20), default="High")
    estimated_hours = Column(Integer, default=6)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    roadmap = relationship("Roadmap", back_populates="items")


class ReadinessSnapshot(Base):
    __tablename__ = "readiness_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_profile_id = Column(String(36), ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    readiness_score = Column(Float, nullable=False)
    readiness_band = Column(String(50), nullable=False)
    skill_coverage_score = Column(Float, nullable=False)
    roadmap_completion_score = Column(Float, nullable=False)
    assessment_score = Column(Float, nullable=False)
    interview_practice_score = Column(Float, nullable=False)
    snapshot_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
