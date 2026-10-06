import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Role, Skill, StudentProfile, StudentSkill, RoleSkill
from app.schemas.schemas import (
    RoleRecommendationResponse,
    RecommendationScoreBreakdown,
    RecommendationExplanation,
    RecommendationListResponse
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Global cache for sentence transformer model to avoid slow reloads
_SENTENCE_MODEL = None
_SENTENCE_MODEL_FAILED = False

def get_sentence_transformer():
    global _SENTENCE_MODEL, _SENTENCE_MODEL_FAILED
    if _SENTENCE_MODEL is None and not _SENTENCE_MODEL_FAILED:
        try:
            from sentence_transformers import SentenceTransformer
            # Using lightweight, fast standard model
            _SENTENCE_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _SENTENCE_MODEL_FAILED = True
            _SENTENCE_MODEL = None
    return _SENTENCE_MODEL

PROFICIENCY_LEVELS = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db

    def calculate_structured_skill_score(
        self, student_skills_map: Dict[str, str], role: Role
    ) -> Dict[str, Any]:
        """
        Calculates structured score based on role-skill knowledge graph.
        Returns:
            {
                "score": float (0-100),
                "matched_skills": list of str,
                "missing_skills": list of str,
                "proficiency_gaps": list of str
            }
        """
        role_skills: List[RoleSkill] = role.role_skills
        if not role_skills:
            return {"score": 50.0, "matched_skills": [], "missing_skills": [], "proficiency_gaps": []}

        total_weight = 0.0
        earned_weight = 0.0
        matched_skills = []
        missing_skills = []
        proficiency_gaps = []

        for rs in role_skills:
            sk_name = rs.skill.name if rs.skill else "Unknown"
            imp_multiplier = 1.5 if rs.importance == "required" else (1.0 if rs.importance == "preferred" else 0.6)
            effective_weight = rs.weight * imp_multiplier
            total_weight += effective_weight

            req_level = PROFICIENCY_LEVELS.get(rs.minimum_proficiency, 2)

            if sk_name in student_skills_map:
                student_level_str = student_skills_map[sk_name]
                student_level = PROFICIENCY_LEVELS.get(student_level_str, 1)

                if student_level >= req_level:
                    earned_weight += effective_weight
                    matched_skills.append(f"{sk_name} ({student_level_str})")
                else:
                    # Partial credit for having the skill but lower proficiency
                    ratio = student_level / float(req_level)
                    earned_weight += effective_weight * ratio
                    proficiency_gaps.append(f"{sk_name} (Current: {student_level_str}, Target: {rs.minimum_proficiency})")
            else:
                if rs.importance in ("required", "preferred"):
                    missing_skills.append(f"{sk_name} (Required: {rs.minimum_proficiency})")

        score = (earned_weight / total_weight) * 100.0 if total_weight > 0 else 50.0
        return {
            "score": min(round(score, 2), 100.0),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "proficiency_gaps": proficiency_gaps
        }

    def calculate_semantic_similarity(
        self, student_profile_text: str, role_text: str
    ) -> float:
        """
        Computes dense semantic cosine similarity between student text and role description.
        Falls back to TF-IDF cosine if dense embedding model is unavailable.
        """
        model = get_sentence_transformer()
        if model is not None:
            try:
                embeddings = model.encode([student_profile_text, role_text])
                emb1 = embeddings[0] / (np.linalg.norm(embeddings[0]) + 1e-9)
                emb2 = embeddings[1] / (np.linalg.norm(embeddings[1]) + 1e-9)
                sim = float(np.dot(emb1, emb2))
                # Map [-1, 1] to [0, 100]
                return max(0.0, min(round(float((sim + 1.0) / 2.0 * 100.0), 2), 100.0))
            except Exception:
                pass

        # Fallback: TF-IDF Cosine Similarity
        try:
            tfidf = TfidfVectorizer(stop_words="english")
            matrix = tfidf.fit_transform([student_profile_text, role_text])
            sim = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
            return round(sim * 100.0, 2)
        except Exception:
            return 50.0

    def calculate_academic_score(self, profile: StudentProfile, role: Role) -> float:
        """
        Scores academic alignment: degree match, branch match, and normalized CGPA.
        """
        score = 60.0 # base score
        branch_lower = (profile.branch or "").lower()
        degree_lower = (profile.degree or "").lower()

        # CS/IT bonus for tech roles
        if any(term in branch_lower for term in ["computer", "cs", "it", "information technology", "software", "data"]):
            score += 25.0
        elif "engineer" in branch_lower:
            score += 15.0

        # CGPA factor (normalized around 8.0/10)
        cgpa = profile.cgpa or 7.0
        cgpa_bonus = min(15.0, max(0.0, (cgpa - 6.0) * 3.75))
        score += cgpa_bonus

        return min(round(score, 2), 100.0)

    def calculate_project_relevance(self, profile: StudentProfile, role: Role) -> Dict[str, Any]:
        """
        Evaluates student projects against role technologies.
        """
        if not profile.projects:
            return {"score": 40.0, "relevant_projects": []}

        role_skill_names = {rs.skill.name.lower() for rs in role.role_skills if rs.skill}
        relevant_projects = []
        matched_project_count = 0

        for p in profile.projects:
            proj_techs = [t.lower() for t in (p.technologies or [])]
            tech_overlap = set(proj_techs).intersection(role_skill_names)

            # Also check title/desc
            desc_text = f"{p.title} {p.description or ''}".lower()
            text_overlap = {sk for sk in role_skill_names if sk in desc_text}

            total_overlap = tech_overlap.union(text_overlap)
            if total_overlap:
                matched_project_count += 1
                relevant_projects.append(f"{p.title} (Utilized: {', '.join(list(total_overlap)[:3])})")

        coverage_ratio = matched_project_count / len(profile.projects)
        project_score = min(100.0, 50.0 + (coverage_ratio * 50.0))
        return {
            "score": round(project_score, 2),
            "relevant_projects": relevant_projects
        }

    def calculate_interest_score(self, profile: StudentProfile, role: Role) -> float:
        """
        Scores alignment between student interests and role category/domain.
        """
        interests = [i.lower() for i in (profile.interests or [])]
        if not interests:
            return 60.0

        role_text = f"{role.category} {role.title} {role.description}".lower()
        matched = sum(1 for item in interests if item in role_text or any(w in role_text for w in item.split()))

        ratio = matched / len(interests)
        return min(100.0, round(50.0 + (ratio * 50.0), 2))

    def generate_recommendations(
        self, profile_id: str, top_k: int = 5
    ) -> RecommendationListResponse:
        """
        Generates top-K explainable job-role recommendations for a student profile
        using the hybrid multi-signal scoring model.
        """
        profile: StudentProfile = self.db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
        if not profile:
            raise ValueError(f"Student profile with id {profile_id} not found")

        roles: List[Role] = self.db.query(Role).all()

        # Map student skills for quick lookup
        student_skills_map = {
            ss.skill.name: ss.proficiency
            for ss in profile.skills
            if ss.skill
        }

        # Build student profile corpus text
        skills_str = ", ".join([f"{k} ({v})" for k, v in student_skills_map.items()])
        projects_str = " ".join([f"{p.title}: {p.description} Tech: {', '.join(p.technologies or [])}" for p in (profile.projects or [])])
        interests_str = ", ".join(profile.interests or [])
        student_corpus = f"{profile.headline or ''} {profile.bio or ''} Skills: {skills_str}. Projects: {projects_str}. Interests: {interests_str}."

        ranked_results = []

        for role in roles:
            # 1. Structured skill score
            struct_result = self.calculate_structured_skill_score(student_skills_map, role)
            struct_score = struct_result["score"]

            # 2. Semantic score
            role_skill_names = ", ".join([rs.skill.name for rs in role.role_skills if rs.skill])
            role_corpus = f"{role.title} in {role.category}. {role.description}. Academic Requirements: {role.academic_requirements}. Required Skills: {role_skill_names}."
            semantic_score = self.calculate_semantic_similarity(student_corpus, role_corpus)

            # 3. Academic score
            academic_score = self.calculate_academic_score(profile, role)

            # 4. Project score
            proj_result = self.calculate_project_relevance(profile, role)
            proj_score = proj_result["score"]

            # 5. Interest score
            interest_score = self.calculate_interest_score(profile, role)

            # Weighted Hybrid Score
            # Structured (45%), Semantic (25%), Project (15%), Academic (10%), Interest (5%)
            final_hybrid_score = (
                0.45 * struct_score +
                0.25 * semantic_score +
                0.15 * proj_score +
                0.10 * academic_score +
                0.05 * interest_score
            )
            final_hybrid_score = min(100.0, max(0.0, round(final_hybrid_score, 1)))

            # Academic alignment narrative
            academic_alignment = f"Strong academic alignment: Your {profile.degree} in {profile.branch} (CGPA: {profile.cgpa or 'N/A'}) meets requirements for {role.title}."

            # Interest alignment narrative
            interest_alignment = (
                f"Matches your specified interest in {', '.join(profile.interests[:2])}."
                if profile.interests else "General interest profile aligned."
            )

            # Explainability rationale
            top_matched = struct_result["matched_skills"][:3]
            top_missing = struct_result["missing_skills"][:2]
            matched_str = ", ".join(top_matched) if top_matched else "foundational competencies"
            missing_str = ", ".join(top_missing) if top_missing else "none"

            rationale = (
                f"Your profile demonstrates strong alignment ({final_hybrid_score}%) with {role.title} "
                f"based on your core skills in {matched_str}. "
                f"Prioritizing preparation in {missing_str} will accelerate placement readiness."
            )

            explanation = RecommendationExplanation(
                matched_skills=struct_result["matched_skills"],
                missing_skills=struct_result["missing_skills"],
                proficiency_gaps=struct_result["proficiency_gaps"],
                relevant_projects=proj_result["relevant_projects"],
                academic_alignment=academic_alignment,
                interest_alignment=interest_alignment,
                rationale=rationale
            )

            score_breakdown = RecommendationScoreBreakdown(
                structured_skill_score=round(struct_score, 1),
                semantic_score=round(semantic_score, 1),
                education_score=round(academic_score, 1),
                project_score=round(proj_score, 1),
                interest_score=round(interest_score, 1),
                final_score=final_hybrid_score
            )

            ranked_results.append({
                "role_id": role.id,
                "role_slug": role.slug,
                "role_title": role.title,
                "role_category": role.category,
                "match_percentage": final_hybrid_score,
                "score_breakdown": score_breakdown,
                "explanation": explanation
            })

        # Sort descending by final hybrid score
        ranked_results.sort(key=lambda x: x["match_percentage"], reverse=True)

        recommendations = []
        for i, item in enumerate(ranked_results[:top_k], start=1):
            recommendations.append(
                RoleRecommendationResponse(
                    rank=i,
                    role_id=item["role_id"],
                    role_slug=item["role_slug"],
                    role_title=item["role_title"],
                    role_category=item["role_category"],
                    match_percentage=item["match_percentage"],
                    score_breakdown=item["score_breakdown"],
                    explanation=item["explanation"]
                )
            )

        return RecommendationListResponse(
            student_id=profile.id,
            recommendations=recommendations,
            algorithm_architecture="Hybrid (Structured Skill Knowledge + Sentence-Transformers Semantic + Project & Academic Alignment)"
        )
