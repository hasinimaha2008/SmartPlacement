"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, DashboardData } from "@/lib/api";
import {
  Compass,
  Sparkles,
  TrendingUp,
  MapPin,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  BookOpen,
  Award,
  Briefcase,
  Layers,
  ChevronRight
} from "lucide-react";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const dashboard = await api.getDashboard();
        setData(dashboard);
      } catch (err: any) {
        setError(err.message || "Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <div className="w-10 h-10 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Synthesizing personalized student career metrics...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-rose-950/30 border border-rose-800 rounded-2xl p-8 text-center max-w-xl mx-auto my-12">
        <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-3" />
        <h2 className="text-lg font-bold text-white mb-2">Unable to Load Dashboard</h2>
        <p className="text-sm text-slate-300 mb-6">{error || "Backend API connection unavailable"}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-sm font-medium transition-colors"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const { profile, readiness, active_roadmap, top_recommendations, quick_stats } = data;

  return (
    <div className="space-y-8">
      {/* Student Profile Header & Welcome */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 p-6 sm:p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                {profile.degree} • {profile.branch} (Class of {profile.graduation_year})
              </span>
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300">
                CGPA: {profile.cgpa}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {profile.full_name}
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              {profile.headline || profile.bio}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/profile"
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium transition-colors border border-slate-700/60"
            >
              Edit Profile
            </Link>
            <Link
              href="/recommendations"
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5"
            >
              <Sparkles className="w-4 h-4" />
              Explore Recommendations
            </Link>
          </div>
        </div>
      </div>

      {/* Top Metrics Strip */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Verified Skills</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{quick_stats.verified_skills_count}</div>
          <div className="text-xs text-slate-400 mt-1">From profile & extraction</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Target Role</span>
            <Briefcase className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-lg font-bold text-white truncate" title={quick_stats.target_role_title}>
            {quick_stats.target_role_title}
          </div>
          <div className="text-xs text-slate-400 mt-1">Active career target</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Readiness Index</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{quick_stats.readiness_score}%</div>
          <div className="text-xs text-slate-400 mt-1">{quick_stats.readiness_band}</div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5">
          <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
            <span>Roadmap Progress</span>
            <MapPin className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-white">{quick_stats.roadmap_progress}%</div>
          <div className="text-xs text-slate-400 mt-1">Milestones completed</div>
        </div>
      </div>

      {/* Main Grid: Readiness Indicator & Top Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Preparation Readiness Breakdown (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-emerald-400" />
                  Preparation Readiness Index
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Multi-factor empirical evaluation for {readiness?.role_title || quick_stats.target_role_title}
                </p>
              </div>
              <span className="px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {readiness?.readiness_band || "In Progress"}
              </span>
            </div>

            {/* Score Ring / Gauge */}
            <div className="p-6 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-center space-y-2">
              <div className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-300">
                {readiness?.readiness_score || 0}%
              </div>
              <div className="text-sm font-semibold text-slate-200">
                {readiness?.readiness_band}
              </div>
              <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                {readiness?.interpretation}
              </p>
            </div>

            {/* Factor Breakdown Bars */}
            <div className="space-y-4">
              <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Contributing Evidence Factors
              </div>
              {readiness?.factors.map((f, idx) => (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-300">{f.factor_name}</span>
                    <span className="text-slate-400 font-semibold">{f.score}% (wt. {Math.round(f.weight * 100)}%)</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-indigo-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(5, f.score))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Academic Disclaimer */}
            <div className="bg-slate-950/40 border border-slate-800/60 rounded-xl p-3 text-[11px] text-slate-500 leading-relaxed">
              <strong>Notice:</strong> {readiness?.disclaimer || "Measures preparation readiness, not employment probability."}
            </div>

            <Link
              href={`/skill-gap?role=${profile.target_role_id || ""}`}
              className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium transition-colors flex items-center justify-center gap-1.5"
            >
              Analyze Role Skill Gaps
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Right Column: Top Recommendations & Active Roadmap (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Top Hybrid Recommendations */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  Top Recommended Career Roles
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Ranked via Hybrid (Structured Skill Graph + Semantic Profile Match + Education Alignment)
                </p>
              </div>
              <Link
                href="/recommendations"
                className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
              >
                View All
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-4">
              {top_recommendations.map((rec) => (
                <div
                  key={rec.role_id}
                  className="p-5 rounded-2xl bg-slate-950/70 border border-slate-800/90 hover:border-indigo-500/40 transition-colors space-y-3"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-400 text-xs font-bold flex items-center justify-center">
                          #{rec.rank}
                        </span>
                        <h3 className="font-bold text-white text-base">{rec.role_title}</h3>
                        <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                          {rec.role_category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 mt-1 line-clamp-2">
                        {rec.explanation.rationale}
                      </p>
                    </div>

                    <div className="text-right shrink-0">
                      <div className="text-xl font-black text-indigo-400">{rec.match_percentage}%</div>
                      <div className="text-[10px] text-slate-500 uppercase font-semibold">Hybrid Match</div>
                    </div>
                  </div>

                  {/* Matched skills pill preview */}
                  <div className="flex flex-wrap items-center gap-1.5 pt-1">
                    <span className="text-[11px] text-slate-500 font-medium mr-1">Matched:</span>
                    {rec.explanation.matched_skills.slice(0, 3).map((ms, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 px-2 py-0.5 rounded-md"
                      >
                        ✓ {ms}
                      </span>
                    ))}
                    {rec.explanation.missing_skills.length > 0 && (
                      <span className="text-[11px] bg-rose-950/40 border border-rose-800/60 text-rose-300 px-2 py-0.5 rounded-md">
                        Gap: {rec.explanation.missing_skills[0].split("(")[0]}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Active Roadmap Preview */}
          {active_roadmap && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-emerald-400" />
                    Preparation Roadmap Milestones
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {active_roadmap.completed_milestones} of {active_roadmap.total_milestones} milestones completed ({active_roadmap.completion_percentage}%)
                  </p>
                </div>
                <Link
                  href="/roadmap"
                  className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                >
                  Full Roadmap
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(5, active_roadmap.completion_percentage)}%` }}
                />
              </div>

              {/* Immediate Upcoming Milestones */}
              <div className="space-y-3">
                {active_roadmap.stages.flatMap((s) => s.items).slice(0, 3).map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800"
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                          item.is_completed
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : "bg-slate-800 text-slate-400 border border-slate-700"
                        }`}
                      >
                        {item.is_completed ? <CheckCircle2 className="w-4 h-4" /> : "○"}
                      </div>
                      <div>
                        <div className={`text-sm font-semibold ${item.is_completed ? "text-slate-400 line-through" : "text-white"}`}>
                          {item.title}
                        </div>
                        <div className="text-xs text-slate-400">
                          {item.stage_title} • Est. {item.estimated_hours}h
                        </div>
                      </div>
                    </div>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                        item.priority === "Critical"
                          ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      }`}
                    >
                      {item.priority}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
