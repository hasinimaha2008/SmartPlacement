// SmartPlacement Frontend API Client
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export interface StudentProfile {
  id: string;
  user_id: string;
  full_name: string;
  email: string;
  headline?: string;
  degree: string;
  branch: string;
  graduation_year: number;
  cgpa: number;
  bio?: string;
  interests: string[];
  target_role_id?: string;
  skills: Array<{
    id: string;
    skill_id: string;
    name: string;
    category: string;
    proficiency: "Beginner" | "Intermediate" | "Advanced";
    verified: boolean;
  }>;
  projects: Array<{
    id: string;
    title: string;
    description?: string;
    technologies: string[];
    github_url?: string;
    live_url?: string;
  }>;
  certifications: Array<{
    id: string;
    title: string;
    issuing_organization?: string;
    issue_year?: number;
    credential_url?: string;
  }>;
  experiences: Array<{
    id: string;
    title: string;
    company: string;
    experience_type: string;
    start_date?: string;
    end_date?: string;
    description?: string;
    skills_used: string[];
  }>;
}

export interface RoleDetail {
  id: string;
  slug: string;
  title: string;
  category: string;
  description: string;
  academic_requirements?: string;
  career_outlook?: string;
  skills: Array<{
    skill_id: string;
    name: string;
    category: string;
    importance: "required" | "preferred" | "optional";
    minimum_proficiency: string;
    weight: number;
  }>;
}

export interface Recommendation {
  rank: number;
  role_id: string;
  role_slug: string;
  role_title: string;
  role_category: string;
  match_percentage: number;
  score_breakdown: {
    structured_skill_score: number;
    semantic_score: number;
    education_score: number;
    project_score: number;
    interest_score: number;
    final_score: number;
  };
  explanation: {
    matched_skills: string[];
    missing_skills: string[];
    proficiency_gaps: string[];
    relevant_projects: string[];
    academic_alignment: string;
    interest_alignment: string;
    rationale: string;
  };
}

export interface SkillGapItem {
  skill_id: string;
  skill_name: string;
  category: string;
  importance: string;
  required_proficiency: string;
  student_proficiency?: string;
  status: "matched" | "proficiency_gap" | "missing";
  priority_level: "Critical" | "High" | "Medium" | "Low";
  weight: number;
  guidance: string;
}

export interface SkillGapReport {
  role_id: string;
  role_title: string;
  overall_coverage_pct: number;
  total_role_skills: number;
  matched_skills_count: number;
  proficiency_gap_count: number;
  missing_skills_count: number;
  critical_missing: string[];
  gaps: SkillGapItem[];
}

export interface RoadmapMilestone {
  id: string;
  stage_number: number;
  stage_title: string;
  title: string;
  learning_objective: string;
  priority: string;
  estimated_hours: number;
  is_completed: boolean;
  skill_id?: string;
  skill_name?: string;
  resources: Array<{
    title: string;
    resource_type: string;
    url: string;
    estimated_hours: number;
  }>;
}

export interface RoadmapStage {
  stage_number: number;
  stage_title: string;
  stage_description: string;
  items: RoadmapMilestone[];
}

export interface RoadmapData {
  roadmap_id: string;
  role_id: string;
  role_title: string;
  status: string;
  total_stages: number;
  total_milestones: number;
  completed_milestones: number;
  completion_percentage: number;
  stages: RoadmapStage[];
}

export interface ReadinessFactor {
  factor_name: string;
  weight: number;
  score: number;
  weighted_score: number;
  benchmark: string;
  description: string;
}

export interface ReadinessData {
  student_id: string;
  role_id: string;
  role_title: string;
  readiness_score: number;
  readiness_band: "Beginning Preparation" | "Developing Readiness" | "Placement Ready" | "Highly Competitive";
  badge_variant: "default" | "warning" | "success" | "accent";
  interpretation: string;
  factors: ReadinessFactor[];
  strengths: string[];
  priority_focus_areas: string[];
  disclaimer: string;
}

export interface EvaluationReport {
  evaluation_dataset_size: number;
  evaluation_split: string;
  baselines: Array<{
    model_name: string;
    top_1_accuracy: number;
    top_3_accuracy: number;
    top_5_accuracy: number;
    mrr: number;
    ndcg_at_3: number;
    avg_latency_ms: number;
  }>;
  ablation_study: Array<{
    configuration: string;
    top_1_accuracy: number;
    top_3_accuracy: number;
    drop_from_full: number;
    significance: string;
  }>;
  academic_summary: string;
}

export interface DashboardData {
  profile: StudentProfile;
  target_role?: RoleDetail;
  top_recommendations: Recommendation[];
  readiness?: ReadinessData;
  active_roadmap?: RoadmapData;
  recent_assessments: Array<{
    id: string;
    category: string;
    score: number;
    total: number;
    percentage: number;
    passed: boolean;
    date?: string;
  }>;
  quick_stats: {
    verified_skills_count: number;
    projects_count: number;
    certifications_count: number;
    target_role_title: string;
    readiness_score: number;
    readiness_band: string;
    roadmap_progress: number;
  };
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json();
}

export const api = {
  getHealth: () => request<{ status: string; database: string }>("/health"),
  getDashboard: () => request<DashboardData>("/dashboard"),
  getProfile: () => request<StudentProfile>("/profile"),
  updateProfile: (data: any) => request<StudentProfile>("/profile", { method: "POST", body: JSON.stringify(data) }),
  getRoles: () => request<RoleDetail[]>("/roles"),
  getRole: (slugOrId: string) => request<RoleDetail>(`/roles/${slugOrId}`),
  getSkills: () => request<any[]>("/skills"),
  extractSkills: (text: string) => request<{ extracted_skills: any[]; count: number }>("/skills/extract", { method: "POST", body: JSON.stringify({ text }) }),
  getRecommendations: (topK = 5) => request<{ recommendations: Recommendation[] }>(`/recommendations?top_k=${topK}`),
  getEvaluationReport: () => request<EvaluationReport>("/recommendations/evaluate"),
  getSkillGap: (roleIdOrSlug: string) => request<SkillGapReport>(`/skill-gap/${roleIdOrSlug}`),
  getRoadmap: (roleIdOrSlug: string) => request<RoadmapData>(`/roadmap/${roleIdOrSlug}`),
  toggleRoadmapItem: (itemId: string) => request<{ is_completed: boolean; roadmap_progress_percentage: number }>(`/roadmap/item/${itemId}/toggle`, { method: "POST" }),
  getResources: (params?: { skill_name?: string; difficulty?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return request<any[]>(`/resources${qs ? `?${qs}` : ""}`);
  },
  getInterviewQuestions: (params?: { category?: string; role_id?: string }) => {
    const qs = new URLSearchParams(params as any).toString();
    return request<any[]>(`/interview/questions${qs ? `?${qs}` : ""}`);
  },
  startMockInterview: (studentId: string, roleId: string) =>
    request<{ interview_id: string; role_title: string; current_turn: any }>("/interview/mock/start", {
      method: "POST",
      body: JSON.stringify({ student_id: studentId, role_id: roleId }),
    }),
  submitMockAnswer: (payload: { interview_id: string; question_number: number; question_text: string; student_answer: string }) =>
    request<any>("/interview/mock/answer", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getSkillQuiz: (skillId: string) => request<any>(`/assessments/quiz/${skillId}`),
  submitSkillQuiz: (studentId: string, skillId: string, answers: Record<string, string>) =>
    request<any>("/assessments/submit", {
      method: "POST",
      body: JSON.stringify({ student_id: studentId, skill_id: skillId, answers }),
    }),
  getReadiness: (roleIdOrSlug: string) => request<ReadinessData>(`/readiness/${roleIdOrSlug}`),
};
