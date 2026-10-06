import pytest
from app.models.models import StudentProfile
from app.services.recommendation_service import RecommendationService
from app.services.evaluation_service import EvaluationService

def test_recommendation_generation(db_session):
    profile = db_session.query(StudentProfile).first()
    assert profile is not None

    rec_service = RecommendationService(db_session)
    result = rec_service.generate_recommendations(profile.id, top_k=5)

    assert result.student_id == profile.id
    assert len(result.recommendations) == 5

    # Check top recommendation properties
    top_rec = result.recommendations[0]
    assert top_rec.rank == 1
    assert top_rec.match_percentage > 0.0
    assert top_rec.score_breakdown.structured_skill_score >= 0.0
    assert top_rec.score_breakdown.semantic_score >= 0.0
    assert top_rec.score_breakdown.final_score == top_rec.match_percentage

    # Check explainability
    assert len(top_rec.explanation.matched_skills) > 0
    assert len(top_rec.explanation.rationale) > 10
    assert "alignment" in top_rec.explanation.academic_alignment.lower()

def test_evaluation_benchmark_and_ablation(db_session):
    eval_service = EvaluationService(db_session)
    report = eval_service.run_benchmark_and_ablation()

    assert report.evaluation_dataset_size > 0
    assert len(report.baselines) >= 3

    # Check that proposed hybrid model achieves high top-1 and top-3 accuracy
    hybrid_baseline = next(b for b in report.baselines if "Hybrid" in b.model_name)
    assert hybrid_baseline.top_1_accuracy >= 0.70
    assert hybrid_baseline.top_3_accuracy >= 0.85

    # Check ablation study entries
    assert len(report.ablation_study) >= 4
    full_ablation = report.ablation_study[0]
    assert full_ablation.drop_from_full == 0.0
