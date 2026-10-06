"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { api, RoadmapData, RoleDetail, StudentProfile } from "@/lib/api";
import {
  MapPin,
  CheckCircle2,
  Circle,
  ExternalLink,
  Clock,
  Sparkles,
  BookOpen,
  ArrowRight,
  TrendingUp,
  Layers
} from "lucide-react";

export default function RoadmapPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-slate-400">Loading preparation roadmap...</div>}>
      <RoadmapContent />
    </Suspense>
  );
}

function RoadmapContent() {
  const searchParams = useSearchParams();
  const roleParam = searchParams.get("role");

  const [roles, setRoles] = useState<RoleDetail[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<string>("");
  const [roadmap, setRoadmap] = useState<RoadmapData | null>(null);
  const [loading, setLoading] = useState(true);

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

        const target = roleParam || profData.target_role_id || (rolesData[0] ? rolesData[0].id : "");
        setSelectedRoleId(target);

        if (target) {
          const rm = await api.getRoadmap(target);
          setRoadmap(rm);
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
      const rm = await api.getRoadmap(newRoleId);
      setRoadmap(rm);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleItem = async (itemId: string) => {
    try {
      const res = await api.toggleRoadmapItem(itemId);
      // Update local state
      if (!roadmap) return;
      const updatedStages = roadmap.stages.map((stage) => ({
        ...stage,
        items: stage.items.map((item) =>
          item.id === itemId ? { ...item, is_completed: res.is_completed } : item
        ),
      }));

      const total = roadmap.total_milestones;
      const completed = updatedStages.flatMap((s) => s.items).filter((i) => i.is_completed).length;

      setRoadmap({
        ...roadmap,
        stages: updatedStages,
        completed_milestones: completed,
        completion_percentage: res.roadmap_progress_percentage,
      });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title & Role Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <MapPin className="w-7 h-7 text-emerald-400" />
            Personalized Preparation Roadmap
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Actionable milestone stages tailored specifically to bridge your verified skill gaps.
          </p>
        </div>

        {/* Role Selector */}
        <div className="w-full sm:w-72">
          <label className="block text-xs font-semibold text-slate-400 mb-1">Roadmap Role</label>
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
          <p className="text-slate-400 text-sm">Synthesizing personalized preparation stages...</p>
        </div>
      ) : roadmap ? (
        <div className="space-y-8">
          {/* Progress Header Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Adaptive Learning Roadmap
                </span>
                <h2 className="text-xl sm:text-2xl font-bold text-white mt-1">
                  {roadmap.role_title}
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  {roadmap.completed_milestones} of {roadmap.total_milestones} milestones achieved across {roadmap.total_stages} stages
                </p>
              </div>

              <div className="text-right shrink-0">
                <div className="text-3xl font-black text-emerald-400">
                  {roadmap.completion_percentage}%
                </div>
                <div className="text-[10px] text-slate-400 uppercase font-semibold">
                  Stage Completion
                </div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden p-0.5 border border-slate-800">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.max(5, roadmap.completion_percentage)}%` }}
              />
            </div>
          </div>

          {/* Sequential Stages */}
          <div className="space-y-8">
            {roadmap.stages.map((stage) => (
              <div key={stage.stage_number} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-xl bg-indigo-500/20 border border-indigo-500/30 text-indigo-400 flex items-center justify-center font-bold text-sm">
                    {stage.stage_number}
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">{stage.stage_title}</h3>
                    <p className="text-xs text-slate-400">{stage.stage_description}</p>
                  </div>
                </div>

                {/* Milestones inside stage */}
                <div className="space-y-3 pl-0 sm:pl-11">
                  {stage.items.map((item) => (
                    <div
                      key={item.id}
                      className={`p-5 rounded-2xl border transition-all ${
                        item.is_completed
                          ? "bg-slate-950/40 border-slate-800/60 opacity-80"
                          : "bg-slate-900 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                        <div className="flex items-start gap-3">
                          <button
                            onClick={() => handleToggleItem(item.id)}
                            className="mt-0.5 text-slate-400 hover:text-emerald-400 transition-colors shrink-0"
                          >
                            {item.is_completed ? (
                              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                            ) : (
                              <Circle className="w-5 h-5" />
                            )}
                          </button>

                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h4
                                className={`text-base font-bold ${
                                  item.is_completed ? "text-slate-400 line-through" : "text-white"
                                }`}
                              >
                                {item.title}
                              </h4>
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

                            <p className="text-xs text-slate-300 leading-relaxed">
                              {item.learning_objective}
                            </p>

                            <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
                              <span className="flex items-center gap-1">
                                <Clock className="w-3.5 h-3.5 text-slate-500" />
                                Est. {item.estimated_hours} hours
                              </span>
                              {item.skill_name && (
                                <span className="flex items-center gap-1">
                                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                                  Competency: {item.skill_name}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Resource links & Actions */}
                        <div className="flex flex-wrap sm:flex-col items-end gap-2 shrink-0 self-end sm:self-center">
                          {item.resources.map((res, rIdx) => (
                            <a
                              key={rIdx}
                              href={res.url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[11px] px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 flex items-center gap-1 transition-colors"
                            >
                              <BookOpen className="w-3.5 h-3.5" />
                              {res.title.slice(0, 24)}...
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          ))}

                          {item.skill_id && (
                            <Link
                              href={`/interview?skill=${item.skill_id}`}
                              className="text-[11px] px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-800/80 text-emerald-300 hover:bg-emerald-900/60 flex items-center gap-1 transition-colors"
                            >
                              <Sparkles className="w-3.5 h-3.5" />
                              Take Skill Quiz
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
