"use client";

import { useEffect, useState } from "react";
import { api, EvaluationReport } from "@/lib/api";
import {
  FlaskConical,
  BarChart2,
  TrendingUp,
  Award,
  Layers,
  Sparkles,
  Info,
  CheckCircle2,
  RefreshCw
} from "lucide-react";

export default function EvaluationPage() {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [runningBenchmark, setRunningBenchmark] = useState(false);

  const fetchBenchmark = async () => {
    try {
      setRunningBenchmark(true);
      const data = await api.getEvaluationReport();
      setReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setRunningBenchmark(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBenchmark();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-4 border-teal-500/20 border-t-teal-500 rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Running empirical evaluation on test benchmark...</p>
      </div>
    );
  }

  if (!report) return null;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Title & Research Defense Abstract */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
              Academic Research & Empirical Evaluation
            </span>
            <span className="text-xs text-slate-400">Section 39 & 40 Defense Suite</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <FlaskConical className="w-7 h-7 text-teal-400" />
            Algorithm Benchmark & Ablation Study
          </h1>
          <p className="text-sm text-slate-300 mt-1 max-w-3xl leading-relaxed">
            Empirical comparative analysis evaluating the SmartPlacement Hybrid Recommendation Engine
            against standard baselines (TF-IDF, Dense Semantic, and Isolated Ontology) on ground-truth placement test data.
          </p>
        </div>

        <button
          onClick={fetchBenchmark}
          disabled={runningBenchmark}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-teal-300 border border-teal-500/30 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shrink-0 self-start sm:self-center"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${runningBenchmark ? "animate-spin" : ""}`} />
          Re-Run Benchmark
        </button>
      </div>

      {/* Summary Abstract Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-400" />
          Empirical Research Findings
        </h2>
        <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/70 border border-slate-800 p-4 rounded-2xl">
          {report.academic_summary}
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-500">Benchmark Profiles</div>
            <div className="text-base font-bold text-white mt-0.5">{report.evaluation_dataset_size} Candidates</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-slate-500">Validation Split</div>
            <div className="text-base font-bold text-white mt-0.5">Held-out Ground Truth</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-teal-400 font-semibold">Hybrid Top-1 Accuracy</div>
            <div className="text-base font-bold text-teal-300 mt-0.5">
              {(report.baselines.find((b) => b.model_name.includes("Hybrid"))?.top_1_accuracy || 0) * 100}%
            </div>
          </div>
          <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800">
            <div className="text-indigo-400 font-semibold">Hybrid Top-3 Accuracy</div>
            <div className="text-base font-bold text-indigo-300 mt-0.5">
              {(report.baselines.find((b) => b.model_name.includes("Hybrid"))?.top_3_accuracy || 0) * 100}%
            </div>
          </div>
        </div>
      </div>

      {/* Baseline Performance Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-indigo-400" />
            Model Baseline Comparison Matrix
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Standard Information Retrieval & Ranking Metrics across 12 standardized candidate profiles.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Recommendation Architecture</th>
                <th className="py-3 px-3">Top-1 Acc</th>
                <th className="py-3 px-3">Top-3 Acc</th>
                <th className="py-3 px-3">Top-5 Acc</th>
                <th className="py-3 px-3">MRR</th>
                <th className="py-3 px-3">NDCG@3</th>
                <th className="py-3 px-3">Avg Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {report.baselines.map((b, idx) => {
                const isProposed = b.model_name.includes("Hybrid");
                return (
                  <tr
                    key={idx}
                    className={`transition-colors ${
                      isProposed ? "bg-indigo-950/20 font-medium text-white" : "hover:bg-slate-950/40 text-slate-300"
                    }`}
                  >
                    <td className="py-3.5 px-4 flex items-center gap-2">
                      {isProposed && <span className="w-2 h-2 rounded-full bg-teal-400"></span>}
                      <span className={isProposed ? "font-bold text-white" : ""}>{b.model_name}</span>
                    </td>
                    <td className="py-3.5 px-3 font-semibold text-slate-200">{(b.top_1_accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-3 font-semibold text-slate-200">{(b.top_3_accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-3 font-semibold text-slate-200">{(b.top_5_accuracy * 100).toFixed(1)}%</td>
                    <td className="py-3.5 px-3 text-slate-300">{b.mrr.toFixed(3)}</td>
                    <td className="py-3.5 px-3 text-slate-300">{b.ndcg_at_3.toFixed(3)}</td>
                    <td className="py-3.5 px-3 text-slate-400">{b.avg_latency_ms} ms</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ablation Study Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-amber-400" />
            Component Ablation Analysis
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Systematically isolates individual sub-modules to prove feature importance and architectural justification.
          </p>
        </div>

        <div className="space-y-3">
          {report.ablation_study.map((item, idx) => (
            <div
              key={idx}
              className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-2xl bg-slate-950/70 border border-slate-800 gap-3"
            >
              <div>
                <div className="text-sm font-bold text-white">{item.configuration}</div>
                <div className="text-xs text-slate-400 mt-0.5">{item.significance}</div>
              </div>

              <div className="flex items-center gap-6 shrink-0">
                <div className="text-right">
                  <div className="text-xs text-slate-400">Top-1 Acc</div>
                  <div className="text-sm font-bold text-white">{(item.top_1_accuracy * 100).toFixed(1)}%</div>
                </div>

                <div className="text-right">
                  <div className="text-xs text-slate-400">Accuracy Impact</div>
                  <div
                    className={`text-sm font-extrabold ${
                      item.drop_from_full < 0 ? "text-rose-400" : "text-emerald-400"
                    }`}
                  >
                    {item.drop_from_full === 0 ? "0.0% (Ref)" : `${item.drop_from_full}%`}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Academic Ethics & Data Limitations Statement */}
      <div className="p-5 rounded-2xl bg-slate-950/50 border border-slate-800/80 text-xs text-slate-400 space-y-1.5 leading-relaxed">
        <div className="font-bold text-slate-200 flex items-center gap-1.5">
          <Info className="w-4 h-4 text-indigo-400" />
          Academic Integrity & Limitations Notice
        </div>
        <p>
          SmartPlacement is designed as an explainable educational preparation system.
          Candidate scores measure readiness against standardized role competencies rather than predicting actual hiring probability.
          The evaluation dataset consists of controlled synthetic benchmark profiles mapped to target job roles,
          preventing demographic bias and honoring Section 41 & 61 research ethics standards.
        </p>
      </div>
    </div>
  );
}
