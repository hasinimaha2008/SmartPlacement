-- ============================================================================
-- SmartPlacement Database Migration: Initial Schema
-- PostgreSQL / Supabase Migration
-- File: supabase/migrations/20261005_000001_initial_schema.sql
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------------------
-- 1. Users & Authentication Reference Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'placement_officer', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 2. Student Profiles
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    headline VARCHAR(255),
    degree VARCHAR(100) NOT NULL DEFAULT 'B.Tech',
    branch VARCHAR(100) NOT NULL DEFAULT 'Computer Science and Engineering',
    graduation_year INT NOT NULL DEFAULT 2026,
    cgpa NUMERIC(4, 2) CHECK (cgpa >= 0.0 AND cgpa <= 10.0),
    bio TEXT,
    interests TEXT[] DEFAULT '{}',
    target_role_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 3. Skills Canonical Taxonomy
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL, -- 'Programming', 'Frontend', 'Backend', 'Data & AI', 'DevOps & Cloud', 'Testing', 'Database', 'Soft Skills'
    aliases TEXT[] DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 4. Student Skills (with verified proficiency levels)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency VARCHAR(20) NOT NULL DEFAULT 'Beginner' CHECK (proficiency IN ('Beginner', 'Intermediate', 'Advanced')),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_profile_id, skill_id)
);

-- ----------------------------------------------------------------------------
-- 5. Student Projects, Certifications, Experience
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    technologies TEXT[] DEFAULT '{}',
    github_url VARCHAR(500),
    live_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS student_certifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    issuing_organization VARCHAR(255),
    issue_year INT,
    credential_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS student_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    experience_type VARCHAR(50) DEFAULT 'Internship' CHECK (experience_type IN ('Internship', 'Part-time', 'Full-time', 'Freelance')),
    start_date DATE,
    end_date DATE,
    description TEXT,
    skills_used TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 6. Job Roles Taxonomy (Controlled 15 Target Roles)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    academic_requirements TEXT,
    career_outlook TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 7. Role-Skill Knowledge Graph Mappings
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS role_skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    importance VARCHAR(20) NOT NULL DEFAULT 'required' CHECK (importance IN ('required', 'preferred', 'optional')),
    minimum_proficiency VARCHAR(20) NOT NULL DEFAULT 'Intermediate' CHECK (minimum_proficiency IN ('Beginner', 'Intermediate', 'Advanced')),
    weight NUMERIC(3, 2) NOT NULL DEFAULT 1.0 CHECK (weight > 0.0 AND weight <= 2.0),
    UNIQUE(role_id, skill_id)
);

-- ----------------------------------------------------------------------------
-- 8. Learning Resources
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learning_resources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    category VARCHAR(100),
    difficulty VARCHAR(20) DEFAULT 'Beginner' CHECK (difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    resource_type VARCHAR(50) DEFAULT 'Documentation' CHECK (resource_type IN ('Documentation', 'Course', 'Tutorial', 'Video', 'Book', 'Practice')),
    url VARCHAR(500) NOT NULL,
    estimated_hours INT DEFAULT 4,
    rating NUMERIC(3, 2) DEFAULT 4.5,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 9. Interview & Practice Questions
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('Technical', 'Aptitude', 'HR')),
    sub_category VARCHAR(100), -- e.g., 'Quantitative', 'Logical', 'System Design', 'Behavioral'
    difficulty VARCHAR(20) DEFAULT 'Intermediate' CHECK (difficulty IN ('Easy', 'Intermediate', 'Hard')),
    question_text TEXT NOT NULL,
    options JSONB, -- For multiple-choice aptitude or quizzes: ["A", "B", "C", "D"]
    correct_answer TEXT,
    explanation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 10. Student Assessment Attempts & Activity
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assessment_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    total_questions INT NOT NULL,
    score INT NOT NULL,
    percentage NUMERIC(5, 2) NOT NULL,
    passed BOOLEAN NOT NULL DEFAULT FALSE,
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 11. Mock Interview Sessions
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mock_interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'in_progress' CHECK (status IN ('in_progress', 'completed')),
    overall_score NUMERIC(5, 2),
    strengths TEXT[] DEFAULT '{}',
    areas_for_improvement TEXT[] DEFAULT '{}',
    feedback TEXT,
    transcript JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 12. Personalized Roadmaps & Milestones
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roadmaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_profile_id, role_id)
);

CREATE TABLE IF NOT EXISTS roadmap_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    skill_id UUID REFERENCES skills(id) ON DELETE SET NULL,
    stage_number INT NOT NULL DEFAULT 1,
    stage_title VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    learning_objective TEXT,
    priority VARCHAR(20) DEFAULT 'High' CHECK (priority IN ('Critical', 'High', 'Medium', 'Low')),
    estimated_hours INT DEFAULT 6,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    order_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 13. Preparation Readiness Metrics Log
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS readiness_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_profile_id UUID NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    readiness_score NUMERIC(5, 2) NOT NULL,
    readiness_band VARCHAR(50) NOT NULL,
    skill_coverage_score NUMERIC(5, 2) NOT NULL,
    roadmap_completion_score NUMERIC(5, 2) NOT NULL,
    assessment_score NUMERIC(5, 2) NOT NULL,
    interview_practice_score NUMERIC(5, 2) NOT NULL,
    snapshot_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ----------------------------------------------------------------------------
-- 14. Indexes for Performance
-- ----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_student_skills_profile_id ON student_skills(student_profile_id);
CREATE INDEX IF NOT EXISTS idx_student_skills_skill_id ON student_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_role_skills_role_id ON role_skills(role_id);
CREATE INDEX IF NOT EXISTS idx_role_skills_skill_id ON role_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_questions_role_id ON questions(role_id);
CREATE INDEX IF NOT EXISTS idx_questions_category ON questions(category);
CREATE INDEX IF NOT EXISTS idx_resources_skill_id ON learning_resources(skill_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_items_roadmap_id ON roadmap_items(roadmap_id);
CREATE INDEX IF NOT EXISTS idx_assessment_attempts_profile ON assessment_attempts(student_profile_id);
CREATE INDEX IF NOT EXISTS idx_readiness_profile_role ON readiness_snapshots(student_profile_id, role_id);

-- ----------------------------------------------------------------------------
-- 15. Row Level Security (RLS) Policies
-- ----------------------------------------------------------------------------
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_experiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE roadmaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE roadmap_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE mock_interviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE readiness_snapshots ENABLE ROW LEVEL SECURITY;

-- Public reference tables (read-only for all authenticated/anon users)
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;

CREATE POLICY skills_read_all ON skills FOR SELECT USING (true);
CREATE POLICY roles_read_all ON roles FOR SELECT USING (true);
CREATE POLICY role_skills_read_all ON role_skills FOR SELECT USING (true);
CREATE POLICY resources_read_all ON learning_resources FOR SELECT USING (true);
CREATE POLICY questions_read_all ON questions FOR SELECT USING (true);

-- Student profiles and related items: allow owner to view/modify
CREATE POLICY student_profiles_owner ON student_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY student_skills_owner ON student_skills
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM student_profiles sp 
            WHERE sp.id = student_skills.student_profile_id AND sp.user_id = auth.uid()
        )
    );

CREATE POLICY roadmaps_owner ON roadmaps
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM student_profiles sp 
            WHERE sp.id = roadmaps.student_profile_id AND sp.user_id = auth.uid()
        )
    );
