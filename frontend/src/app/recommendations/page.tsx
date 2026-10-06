"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, Recommendation, StudentProfile } from "@/lib/api";
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  TrendingUp,
  GraduationCap,
  Briefcase,
  Layers,
  ChevronDown,
  ChevronUp
} from "lucide-react";

export default function RecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedRole, setExpandedRole] = useState<string | null>(null);

  useEffect(() => {
    async function loadRecs() {
      try {
        setLoading(true);
        const [recData, profData] = await Promise.all([
          api.getRecommendations(8),
          api.getProfile(),
        ]);
        setRecommendations(recData.recommendations);
        setProfile(profData);
        if (recData.recommendations.length > 0) {
          setExpandedRole(recData.recommendations[0].role_id);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load recommendations");
      } finally {
        setLoading(false);
      }
    }
    loadRecs();
  }, []);

  const handleSetTargetRole = async (roleId: string) => {
    if (!profile) return;
    try {
      await api.updateProfile({ ...profile, target_role_id: roleId });
      setProfile({ ...profile, target_role_id: roleId });
      alert("Target career role updated successfully!");
    } catch (err: any) {
      alert("Error setting target role: " + err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Evaluating hybrid ranking and ontology alignment...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-950/30 border border-rose-800 rounded-2xl p-6 text-center max-w-lg mx-auto">
        <AlertCircle className="w-10 h-10 text-rose-400 mx-auto mb-2" />
        <p className="text-sm text-slate-300">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title & Architecture Note */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Hybrid Recommendation Architecture
          </span>
          <span className="text-xs text-slate-400">
            Structured Skill Graph + Dense Semantic Similarity + Project Alignment
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          <Sparkles className="w-7 h-7 text-amber-400" />
          Explainable Role Recommendations
        </h1>
        <p className="text-sm text-slate-300 max-w-3xl leading-relaxed">
          Every recommendation provides transparent multi-factor evidence. Inspect matched competencies,
          unmet requirements, and project relevance to choose your optimal placement target.
        </p>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {recommendations.map((rec) => {
          const isExpanded = expandedRole === rec.role_id;
          const isTarget = profile?.target_role_id === rec.role_id;

          return (
            <div
              key={rec.role_id}
              className={`rounded-3xl border transition-all ${
                isTarget
                  ? "bg-slate-900 border-indigo-500/60 shadow-lg shadow-indigo-500/10"
                  : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
              }`}
            >
              {/* Header card summary */}
              <div
                onClick={() => setExpandedRole(isExpanded ? null : rec.role_id)}
                className="p-6 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4 select-none"
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`w-10 h-10 rounded-2xl flex items-center justify-center font-black text-sm shrink-0 ${
                      rec.rank === 1
                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                        : rec.rank === 2
                        ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                        : "bg-slate-800 text-slate-400 border border-slate-700"
                    }`}
                  >
                    #{rec.rank}
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-white">{rec.role_title}</h3>
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300">
                        {rec.role_category}
                      </span>
                      {isTarget && (
                        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                          Active Target
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 mt-1 max-w-2xl">
                      {rec.explanation.rationale}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6 sm:self-center shrink-0">
                  <div className="text-right">
                    <div className="text-2xl font-black text-indigo-400">{rec.match_percentage}%</div>
                    <div className="text-[10px] text-slate-400 uppercase font-semibold">Match Score</div>
                  </div>

                  <div className="p-2 rounded-xl bg-slate-800/80 text-slate-400">
                    {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </div>
                </div>
              </div>

              {/* Detailed Explainability Panel */}
              {isExpanded && (
                <div className="px-6 pb-6 pt-2 border-t border-slate-800/80 space-y-6">
                  {/* Score Breakdown Radar/Bar Grid */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                      Transparent Score Composition
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                      <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                        <div className="text-[11px] text-slate-400">Skill Graph (45%)</div>
                        <div className="text-base font-bold text-white mt-0.5">
                          {rec.score_breakdown.structured_skill_score}%
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                        <div className="text-[11px] text-slate-400">Semantic (25%)</div>
                        <div className="text-base font-bold text-white mt-0.5">
                          {rec.score_breakdown.semantic_score}%
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                        <div className="text-[11px] text-slate-400">Projects (15%)</div>
                        <div className="text-base font-bold text-white mt-0.5">
                          {rec.score_breakdown.project_score}%
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                        <div className="text-[11px] text-slate-400">Education (10%)</div>
                        <div className="text-base font-bold text-white mt-0.5">
                          {rec.score_breakdown.education_score}%
                        </div>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800">
                        <div className="text-[11px] text-slate-400">Interests (5%)</div>
                        <div className="text-base font-bold text-white mt-0.5">
                          {rec.score_breakdown.interest_score}%
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Competency Alignment Analysis */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Matched Skills */}
                    <div className="p-4 rounded-2xl bg-emerald-950/20 border border-emerald-900/40 space-y-2">
                      <div className="text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4" />
                        Matched Skills & Sufficient Proficiency ({rec.explanation.matched_skills.length})
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {rec.explanation.matched_skills.length > 0 ? (
                          rec.explanation.matched_skills.map((ms, idx) => (
                            <span
                              key={idx}
                              className="text-xs bg-emerald-950/80 border border-emerald-800 text-emerald-300 px-2 py-0.5 rounded-lg"
                            >
                              ✓ {ms}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-slate-400">No core required skills matched yet.</span>
                        )}
                      </div>
                    </div>

                    {/* Missing Skills */}
                    <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-900/40 space-y-2">
                      <div className="text-xs font-bold text-rose-400 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" />
                        Unmet Role Prerequisites ({rec.explanation.missing_skills.length})
                      </div>
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {rec.explanation.missing_skills.length > 0 ? (
                          rec.explanation.missing_skills.map((ms, idx) => (
                            <span
                              key={idx}
                              className="text-xs bg-rose-950/80 border border-rose-800 text-rose-300 px-2 py-0.5 rounded-lg"
                            >
                              ✕ {ms}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-emerald-400">All required role skills matched!</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Contextual Narrative */}
                  <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-2 text-xs leading-relaxed text-slate-300">
                    <div>
                      <strong className="text-white">Academic Alignment: </strong>
                      {rec.explanation.academic_alignment}
                    </div>
                    <div>
                      <strong className="text-white">Interest Alignment: </strong>
                      {rec.explanation.interest_alignment}
                    </div>
                    {rec.explanation.relevant_projects.length > 0 && (
                      <div>
                        <strong className="text-white">Relevant Projects: </strong>
                        {rec.explanation.relevant_projects.join("; ")}
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                    <div className="flex items-center gap-3">
                      <Link
                        href={`/skill-gap?role=${rec.role_id}`}
                        className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition-colors flex items-center gap-1.5"
                      >
                        Deep Skill Gap Analysis
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                      <Link
                        href={`/roadmap?role=${rec.role_id}`}
                        className="px-4 py-2 rounded-xl bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-colors flex items-center gap-1.5"
                      >
                        Generate Preparation Roadmap
                      </Link>
                    </div>

                    {!isTarget && (
                      <button
                        onClick={() => handleSetTargetRole(rec.role_id)}
                        className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/20 transition-colors"
                      >
                        Set as Active Target Role
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
