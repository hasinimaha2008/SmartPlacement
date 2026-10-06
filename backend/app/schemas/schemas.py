from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# ============================================================================
# Skill Schemas
# ============================================================================
class SkillBase(BaseModel):
    name: str
    category: str
    aliases: List[str] = []
    description: Optional[str] = None

class SkillResponse(SkillBase):
    id: str

    class Config:
        from_attributes = True

class StudentSkillInput(BaseModel):
    skill_name: str
    proficiency: str = Field(default="Intermediate", description="Beginner, Intermediate, Advanced")

class StudentSkillResponse(BaseModel):
    id: str
    skill_id: str
    name: str
    category: str
    proficiency: str
    verified: bool = False

# Skill Extraction
class SkillExtractionRequest(BaseModel):
    text: str

class ExtractedSkill(BaseModel):
    original_term: str
    canonical_name: str
    category: str
    confidence: float
    matched_via: str  # 'exact_canonical', 'alias', 'fuzzy'

class SkillExtractionResponse(BaseModel):
    extracted_skills: List[ExtractedSkill]
    raw_text_length: int
    count: int

# ============================================================================
# Project, Certification, Experience Schemas
# ============================================================================
class ProjectInput(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = []
    github_url: Optional[str] = None
    live_url: Optional[str] = None

class ProjectResponse(ProjectInput):
    id: str

class CertificationInput(BaseModel):
    title: str
    issuing_organization: Optional[str] = None
    issue_year: Optional[int] = None
    credential_url: Optional[str] = None

class CertificationResponse(CertificationInput):
    id: str

class ExperienceInput(BaseModel):
    title: str
    company: str
    experience_type: str = "Internship"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    skills_used: List[str] = []

class ExperienceResponse(ExperienceInput):
    id: str

# ============================================================================
# Student Profile Schemas
# ============================================================================
class StudentProfileCreate(BaseModel):
    full_name: str
    email: str
    headline: Optional[str] = None
    degree: str = "B.Tech"
    branch: str = "Computer Science and Engineering"
    graduation_year: int = 2026
    cgpa: float = 8.0
    bio: Optional[str] = None
    interests: List[str] = []
    skills: List[StudentSkillInput] = []
    projects: List[ProjectInput] = []
    certifications: List[CertificationInput] = []
    experiences: List[ExperienceInput] = []
    target_role_id: Optional[str] = None

class StudentProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    email: str
    headline: Optional[str] = None
    degree: str
    branch: str
    graduation_year: int
    cgpa: float
    bio: Optional[str] = None
    interests: List[str] = []
    target_role_id: Optional[str] = None
    skills: List[StudentSkillResponse] = []
    projects: List[ProjectResponse] = []
    certifications: List[CertificationResponse] = []
    experiences: List[ExperienceResponse] = []

# ============================================================================
# Role Schemas
# ============================================================================
class RoleSkillInfo(BaseModel):
    skill_id: str
    name: str
    category: str
    importance: str  # 'required', 'preferred', 'optional'
    minimum_proficiency: str
    weight: float

class RoleDetailResponse(BaseModel):
    id: str
    slug: str
    title: str
    category: str
    description: str
    academic_requirements: Optional[str] = None
    career_outlook: Optional[str] = None
    skills: List[RoleSkillInfo] = []

# ============================================================================
# Recommendation Schemas
# ============================================================================
class RecommendationScoreBreakdown(BaseModel):
    structured_skill_score: float = Field(..., description="Normalized match against required & preferred role skills")
    semantic_score: float = Field(..., description="Dense semantic profile-to-role embedding similarity")
    education_score: float = Field(..., description="Alignment with academic requirements and degree/branch")
    project_score: float = Field(..., description="Relevance of student projects to role technologies")
    interest_score: float = Field(..., description="Alignment of student interests to role domain")
    final_score: float = Field(..., description="Weighted hybrid confidence score (0 to 100)")

class RecommendationExplanation(BaseModel):
    matched_skills: List[str]
    missing_skills: List[str]
    proficiency_gaps: List[str]
    relevant_projects: List[str]
    academic_alignment: str
    interest_alignment: str
    rationale: str

class RoleRecommendationResponse(BaseModel):
    rank: int
    role_id: str
    role_slug: str
    role_title: str
    role_category: str
    match_percentage: float
    score_breakdown: RecommendationScoreBreakdown
    explanation: RecommendationExplanation

class RecommendationListResponse(BaseModel):
    student_id: str
    recommendations: List[RoleRecommendationResponse]
    algorithm_architecture: str = "Hybrid (Structured Skill Ontology + Sentence-Transformers Dense Semantic + Heuristic Multi-Signal Alignment)"
    baseline_comparisons: Optional[Dict[str, Any]] = None

# Evaluation & Benchmark
class ModelEvaluationMetrics(BaseModel):
    model_name: str
    top_1_accuracy: float
    top_3_accuracy: float
    top_5_accuracy: float
    mrr: float
    ndcg_at_3: float
    avg_latency_ms: float

class AblationStudyResult(BaseModel):
    configuration: str
    top_1_accuracy: float
    top_3_accuracy: float
    drop_from_full: float
    significance: str

class EvaluationReportResponse(BaseModel):
    evaluation_dataset_size: int
    evaluation_split: str
    baselines: List[ModelEvaluationMetrics]
    ablation_study: List[AblationStudyResult]
    academic_summary: str

# ============================================================================
# Skill Gap Schemas
# ============================================================================
class SkillGapItem(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    importance: str
    required_proficiency: str
    student_proficiency: Optional[str] = None
    status: str  # 'matched', 'proficiency_gap', 'missing'
    priority_level: str  # 'Critical', 'High', 'Medium', 'Low'
    weight: float
    guidance: str

class SkillGapAnalysisResponse(BaseModel):
    role_id: str
    role_title: str
    overall_coverage_pct: float
    total_role_skills: int
    matched_skills_count: int
    proficiency_gap_count: int
    missing_skills_count: int
    critical_missing: List[str]
    gaps: List[SkillGapItem]

# ============================================================================
# Roadmap Schemas
# ============================================================================
class RoadmapResourceSummary(BaseModel):
    title: str
    resource_type: str
    url: str
    estimated_hours: int

class RoadmapMilestoneItem(BaseModel):
    id: str
    stage_number: int
    stage_title: str
    title: str
    learning_objective: str
    priority: str
    estimated_hours: int
    is_completed: bool
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    resources: List[RoadmapResourceSummary] = []

class RoadmapStage(BaseModel):
    stage_number: int
    stage_title: str
    stage_description: str
    items: List[RoadmapMilestoneItem]

class RoadmapResponse(BaseModel):
    roadmap_id: str
    role_id: str
    role_title: str
    status: str
    total_stages: int
    total_milestones: int
    completed_milestones: int
    completion_percentage: float
    stages: List[RoadmapStage]

class RoadmapItemToggleResponse(BaseModel):
    item_id: str
    is_completed: bool
    roadmap_progress_percentage: float

# ============================================================================
# Learning Resources
# ============================================================================
class LearningResourceResponse(BaseModel):
    id: str
    title: str
    category: Optional[str] = None
    skill_name: Optional[str] = None
    difficulty: str
    resource_type: str
    url: str
    estimated_hours: int
    rating: float

# ============================================================================
# Interview & Assessment Schemas
# ============================================================================
class QuestionResponse(BaseModel):
    id: str
    category: str
    sub_category: Optional[str] = None
    difficulty: str
    question_text: str
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    skill_name: Optional[str] = None

class MockInterviewStartRequest(BaseModel):
    student_id: str
    role_id: str

class MockInterviewTurn(BaseModel):
    question_number: int
    question: str
    category: str

class MockInterviewAnswerSubmit(BaseModel):
    interview_id: str
    question_number: int
    question_text: str
    student_answer: str

class MockInterviewFeedbackResponse(BaseModel):
    interview_id: str
    question_number: int
    overall_score: float  # out of 10
    relevance_score: float
    technical_accuracy_score: float
    clarity_score: float
    strengths: List[str]
    areas_to_improve: List[str]
    model_improved_answer: str
    is_complete: bool
    next_question: Optional[MockInterviewTurn] = None

class AssessmentQuizQuestion(BaseModel):
    id: str
    question_text: str
    options: List[str]
    difficulty: str

class AssessmentQuizResponse(BaseModel):
    skill_id: str
    skill_name: str
    category: str
    questions: List[AssessmentQuizQuestion]

class AssessmentSubmitRequest(BaseModel):
    student_id: str
    skill_id: str
    answers: Dict[str, str]  # question_id -> chosen option string

class AssessmentResultResponse(BaseModel):
    student_id: str
    skill_id: str
    skill_name: str
    score: int
    total_questions: int
    percentage: float
    passed: bool
    feedback: str
    roadmap_adapted: bool
    adaptation_note: str

# ============================================================================
# Preparation Readiness Schemas
# ============================================================================
class ReadinessFactorDetail(BaseModel):
    factor_name: str
    weight: float
    score: float  # 0 to 100
    weighted_score: float
    benchmark: str
    description: str

class PreparationReadinessResponse(BaseModel):
    student_id: str
    role_id: str
    role_title: str
    readiness_score: float  # 0 to 100
    readiness_band: str     # "Beginning Preparation", "Developing Readiness", "Placement Ready", "Highly Competitive"
    badge_variant: str      # 'default', 'warning', 'success', 'accent'
    interpretation: str
    factors: List[ReadinessFactorDetail]
    strengths: List[str]
    priority_focus_areas: List[str]
    disclaimer: str = "This metric reflects placement preparation readiness based on skill coverage, practice attempts, and roadmap milestones. It does not guarantee employment outcomes."

# ============================================================================
# Unified Student Dashboard Schema
# ============================================================================
class UnifiedDashboardResponse(BaseModel):
    profile: StudentProfileResponse
    target_role: Optional[RoleDetailResponse] = None
    top_recommendations: List[RoleRecommendationResponse]
    readiness: Optional[PreparationReadinessResponse] = None
    active_roadmap: Optional[RoadmapResponse] = None
    recent_assessments: List[Dict[str, Any]] = []
    quick_stats: Dict[str, Any]
