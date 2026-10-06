"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, SkillGapReport, RoleDetail, StudentProfile } from "@/lib/api";
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  HelpCircle,
  ArrowRight,
  TrendingUp,
  MapPin,
  Sparkles
} from "lucide-react";

export default function SkillGapPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-slate-400">Loading skill gap analyzer...</div>}>
      <SkillGapContent />
    </Suspense>
  );
}

function SkillGapContent() {
  const searchParams = useSearchParams();
  const roleParam = searchParams.get("role");

  const [roles, setRoles] = useState<RoleDetail[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [report, setReport] = useState<SkillGapReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "missing" | "proficiency_gap" | "matched">("all");

  useEffect(() => {
    async function init() {
      try {
        setLoading(true);
        const [rolesData, profData] = await Promise.all([
          api.getRoles(),
          api.getProfile(),
        ]);
        setRoles(rolesData);
        setProfile(profData);

        const initialRole = roleParam || profData.target_role_id || (rolesData[0] ? rolesData[0].id : "");
        setSelectedRoleId(initialRole);

        if (initialRole) {
          const gapData = await api.getSkillGap(initialRole);
          setReport(gapData);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [roleParam]);

  const handleRoleChange = async (newRoleId: string) => {
    setSelectedRoleId(newRoleId);
    try {
      setLoading(true);
      const gapData = await api.getSkillGap(newRoleId);
      setReport(gapData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredGaps = (report?.gaps || []).filter((g) => {
    if (filter === "all") return true;
    return g.status === filter;
  });

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header and Role Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="w-7 h-7 text-rose-400" />
            Role-Skill Gap Analyzer
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Pinpoint missing competencies, insufficient proficiency levels, and prioritized preparation targets.
          </p>
        </div>

        {/* Role Selector */}
        <div className="w-full sm:w-72">
          <label className="block text-xs font-semibold text-slate-400 mb-1">Target Role</label>
          <select
            value={selectedRoleId}
            onChange={(e) => handleRoleChange(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center min-h-[40vh] gap-3">
          <div className="w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
          <p className="text-slate-400 text-sm">Evaluating role-skill knowledge graph mappings...</p>
        </div>
      ) : report ? (
        <div className="space-y-6">
          {/* Summary Strip Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  Gap Analysis Report
                </span>
                <h2 className="text-xl sm:text-2xl font-bold text-white mt-1">
                  {report.role_title}
                </h2>
              </div>

              <div className="flex items-center gap-6 sm:self-center">
                <div className="text-right">
                  <div className="text-3xl font-black text-rose-400">
                    {report.overall_coverage_pct}%
                  </div>
                  <div className="text-[10px] text-slate-400 uppercase font-semibold">
                    Skill Coverage
                  </div>
                </div>
                <Link
                  href={`/roadmap?role=${report.role_id}`}
                  className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5"
                >
                  <MapPin className="w-4 h-4" />
                  View Roadmap
                </Link>
              </div>
            </div>

            {/* Coverage bar */}
            <div className="space-y-1.5">
              <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
                <div
                  className="bg-gradient-to-r from-rose-500 via-amber-500 to-emerald-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.max(5, report.overall_coverage_pct)}%` }}
                />
              </div>
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>0% Start</span>
                <span>Minimum Target: 75% Coverage</span>
                <span>100% Mastery</span>
              </div>
            </div>

            {/* Category breakdown boxes */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800">
                <div className="text-[11px] text-slate-400">Total Role Skills</div>
                <div className="text-xl font-bold text-white mt-0.5">{report.total_role_skills}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800">
                <div className="text-[11px] text-emerald-400">Fully Matched</div>
                <div className="text-xl font-bold text-emerald-400 mt-0.5">{report.matched_skills_count}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800">
                <div className="text-[11px] text-amber-400">Proficiency Gaps</div>
                <div className="text-xl font-bold text-amber-400 mt-0.5">{report.proficiency_gap_count}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800">
                <div className="text-[11px] text-rose-400">Missing Skills</div>
                <div className="text-xl font-bold text-rose-400 mt-0.5">{report.missing_skills_count}</div>
              </div>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-2">
            <button
              onClick={() => setFilter("all")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                filter === "all" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-white"
              }`}
            >
              All Skills ({report.gaps.length})
            </button>
            <button
              onClick={() => setFilter("missing")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                filter === "missing" ? "bg-rose-950/80 text-rose-300 border border-rose-800" : "text-slate-400 hover:text-white"
              }`}
            >
              <AlertCircle className="w-3.5 h-3.5" />
              Missing Skills ({report.missing_skills_count})
            </button>
            <button
              onClick={() => setFilter("proficiency_gap")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                filter === "proficiency_gap" ? "bg-amber-950/80 text-amber-300 border border-amber-800" : "text-slate-400 hover:text-white"
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              Proficiency Gaps ({report.proficiency_gap_count})
            </button>
            <button
              onClick={() => setFilter("matched")}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5 ${
                filter === "matched" ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800" : "text-slate-400 hover:text-white"
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Matched Skills ({report.matched_skills_count})
            </button>
          </div>

          {/* Gaps List */}
          <div className="space-y-3">
            {filteredGaps.map((item) => (
              <div
                key={item.skill_id}
                className={`p-5 rounded-2xl border transition-all ${
                  item.status === "missing"
                    ? "bg-slate-900/90 border-rose-900/40"
                    : item.status === "proficiency_gap"
                    ? "bg-slate-900/90 border-amber-900/40"
                    : "bg-slate-900/60 border-slate-800"
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-white text-base">{item.skill_name}</h3>
                      <span className="text-[11px] px-2 py-0.5 rounded-md bg-slate-800 text-slate-300">
                        {item.category}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-md uppercase ${
                          item.priority_level === "Critical"
                            ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                            : item.priority_level === "High"
                            ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                            : "bg-slate-800 text-slate-400"
                        }`}
                      >
                        {item.priority_level} Priority
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mt-1.5 leading-relaxed">
                      {item.guidance}
                    </p>
                  </div>

                  <div className="flex items-center gap-3 self-start sm:self-center shrink-0">
                    <div className="text-right">
                      <div className="text-xs text-slate-400">
                        Required: <strong className="text-white">{item.required_proficiency}</strong>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        Current:{" "}
                        <strong
                          className={
                            item.student_proficiency
                              ? "text-indigo-400"
                              : "text-rose-400 font-semibold"
                          }
                        >
                          {item.student_proficiency || "Not Acquired"}
                        </strong>
                      </div>
                    </div>

                    {item.skill_id && (
                      <Link
                        href={`/interview?skill=${item.skill_id}`}
                        className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                        title="Practice Assessment Quiz"
                      >
                        <Sparkles className="w-4 h-4 text-indigo-400" />
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
