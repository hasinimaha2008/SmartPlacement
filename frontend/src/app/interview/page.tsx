"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api, RoleDetail, StudentProfile } from "@/lib/api";
import {
  MessageSquare,
  Sparkles,
  HelpCircle,
  CheckCircle2,
  AlertCircle,
  Send,
  RefreshCw,
  Award,
  BookOpen,
  ChevronDown,
  ChevronUp
} from "lucide-react";

export default function InterviewPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-slate-400">Loading interview preparation...</div>}>
      <InterviewContent />
    </Suspense>
  );
}

function InterviewContent() {
  const searchParams = useSearchParams();
  const skillParam = searchParams.get("skill");

  const [activeTab, setActiveTab] = useState<"mock" | "bank" | "quiz">("mock");
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [roles, setRoles] = useState<RoleDetail[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>("");

  // Question Bank State
  const [questions, setQuestions] = useState<any[]>([]);
  const [bankCategory, setBankCategory] = useState<string>("All");
  const [revealedQuestions, setRevealedQuestions] = useState<Record<string, boolean>>({});

  // Mock Interview State
  const [mockSessionId, setMockSessionId] = useState<string | null>(null);
  const [currentTurn, setCurrentTurn] = useState<any>(null);
  const [studentAnswer, setStudentAnswer] = useState("");
  const [evaluating, setEvaluating] = useState(false);
  const [feedbacks, setFeedbacks] = useState<any[]>([]);
  const [isInterviewComplete, setIsInterviewComplete] = useState(false);

  // Skill Quiz State
  const [quizSkillId, setQuizSkillId] = useState<string>("");
  const [quizData, setQuizData] = useState<any>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<string, string>>({});
  const [quizResult, setQuizResult] = useState<any>(null);
  const [submittingQuiz, setSubmittingQuiz] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        const [profData, rolesData, qData] = await Promise.all([
          api.getProfile(),
          api.getRoles(),
          api.getInterviewQuestions(),
        ]);
        setProfile(profData);
        setRoles(rolesData);
        setQuestions(qData);

        const initialRole = profData.target_role_id || (rolesData[0] ? rolesData[0].id : "");
        setSelectedRole(initialRole);

        // If skill query param is passed, switch to quiz tab
        if (skillParam) {
          setActiveTab("quiz");
          setQuizSkillId(skillParam);
          loadQuiz(skillParam);
        } else if (profData.skills.length > 0) {
          setQuizSkillId(profData.skills[0].skill_id);
        }
      } catch (err) {
        console.error(err);
      }
    }
    init();
  }, [skillParam]);

  // Load questions for bank
  const handleCategoryFilter = async (cat: string) => {
    setBankCategory(cat);
    try {
      const q = await api.getInterviewQuestions({
        category: cat === "All" ? undefined : cat,
        role_id: selectedRole || undefined,
      });
      setQuestions(q);
    } catch (err) {
      console.error(err);
    }
  };

  // Start Mock Interview
  const handleStartMockInterview = async () => {
    if (!profile || !selectedRole) return;
    try {
      setFeedbacks([]);
      setIsInterviewComplete(false);
      setStudentAnswer("");
      const session = await api.startMockInterview(profile.id, selectedRole);
      setMockSessionId(session.interview_id);
      setCurrentTurn(session.current_turn);
    } catch (err: any) {
      alert("Error starting mock interview: " + err.message);
    }
  };

  // Submit Answer
  const handleSubmitAnswer = async () => {
    if (!mockSessionId || !currentTurn || !studentAnswer.trim()) return;
    try {
      setEvaluating(true);
      const res = await api.submitMockAnswer({
        interview_id: mockSessionId,
        question_number: currentTurn.question_number,
        question_text: currentTurn.question,
        student_answer: studentAnswer,
      });
      setFeedbacks((prev) => [...prev, { ...res, student_answer: studentAnswer, question_text: currentTurn.question }]);
      setStudentAnswer("");

      if (res.is_complete) {
        setIsInterviewComplete(true);
        setCurrentTurn(null);
      } else {
        setCurrentTurn(res.next_question);
      }
    } catch (err: any) {
      alert("Error evaluating answer: " + err.message);
    } finally {
      setEvaluating(false);
    }
  };

  // Load Quiz
  const loadQuiz = async (skillId: string) => {
    try {
      setQuizResult(null);
      setQuizAnswers({});
      const data = await api.getSkillQuiz(skillId);
      setQuizData(data);
    } catch (err) {
      console.error(err);
    }
  };

  // Submit Quiz
  const handleSubmitQuiz = async () => {
    if (!profile || !quizData) return;
    try {
      setSubmittingQuiz(true);
      const res = await api.submitSkillQuiz(profile.id, quizData.skill_id, quizAnswers);
      setQuizResult(res);
    } catch (err: any) {
      alert("Error submitting quiz: " + err.message);
    } finally {
      setSubmittingQuiz(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <MessageSquare className="w-7 h-7 text-purple-400" />
            Interview Preparation & Assessment
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Simulate text AI mock interviews, practice role-specific technical/HR questions, and verify skills.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-2xl shrink-0">
          <button
            onClick={() => setActiveTab("mock")}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-colors ${
              activeTab === "mock" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
            }`}
          >
            AI Mock Studio
          </button>
          <button
            onClick={() => setActiveTab("bank")}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-colors ${
              activeTab === "bank" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
            }`}
          >
            Question Bank
          </button>
          <button
            onClick={() => setActiveTab("quiz")}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-colors ${
              activeTab === "quiz" ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30" : "text-slate-400 hover:text-white"
            }`}
          >
            Skill Diagnostics
          </button>
        </div>
      </div>

      {/* TAB 1: AI MOCK INTERVIEW */}
      {activeTab === "mock" && (
        <div className="space-y-6">
          {/* Header Controls */}
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                  Text AI Interview Simulator
                </span>
                <h2 className="text-xl font-bold text-white mt-1">
                  Role-Specific Technical & Behavioral Interview
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Receives your answers, evaluates technical accuracy, relevance, and clarity against industry standards.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  {roles.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.title}
                    </option>
                  ))}
                </select>

                <button
                  onClick={handleStartMockInterview}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-1.5 shrink-0"
                >
                  <Sparkles className="w-4 h-4" />
                  {mockSessionId ? "Restart Session" : "Start Mock Interview"}
                </button>
              </div>
            </div>
          </div>

          {/* Active Question & Answer Box */}
          {currentTurn && (
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300">
                  Round {currentTurn.question_number} • {currentTurn.category}
                </span>
                <span className="text-xs text-slate-400">Question 3 Rounds Total</span>
              </div>

              <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-sm font-semibold text-white leading-relaxed">
                {currentTurn.question}
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-400">Your Response</label>
                <textarea
                  rows={5}
                  value={studentAnswer}
                  onChange={(e) => setStudentAnswer(e.target.value)}
                  placeholder="Articulate your technical response. Detail architectural approaches, specific tools, edge-case handling, and results..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleSubmitAnswer}
                  disabled={evaluating || !studentAnswer.trim()}
                  className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {evaluating ? "Evaluating Answer Rubric..." : "Submit Answer for Evaluation"}
                </button>
              </div>
            </div>
          )}

          {/* Completed Session Banner */}
          {isInterviewComplete && (
            <div className="p-6 rounded-3xl bg-emerald-950/40 border border-emerald-800/80 text-center space-y-2">
              <Award className="w-10 h-10 text-emerald-400 mx-auto" />
              <h3 className="text-lg font-bold text-white">Mock Interview Completed!</h3>
              <p className="text-xs text-slate-300 max-w-md mx-auto">
                All 3 rounds evaluated. Inspect your round-by-round rubric scores and improvement areas below.
              </p>
            </div>
          )}

          {/* Feedback History Cards */}
          {feedbacks.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
                Evaluation Transcripts & Rubric Results ({feedbacks.length})
              </h3>
              {feedbacks.map((fb, idx) => (
                <div key={idx} className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold px-2.5 py-0.5 rounded-md bg-slate-800 text-slate-300">
                      Round #{fb.question_number}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-400">Overall Score:</span>
                      <span className="text-lg font-black text-indigo-400">{fb.overall_score} / 10</span>
                    </div>
                  </div>

                  <div className="text-xs text-slate-400">
                    <strong className="text-white">Question: </strong>
                    {fb.question_text}
                  </div>

                  {/* Rubric scores */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400">Relevance</div>
                      <div className="text-sm font-bold text-white mt-0.5">{fb.relevance_score}/10</div>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400">Technical Depth</div>
                      <div className="text-sm font-bold text-white mt-0.5">{fb.technical_accuracy_score}/10</div>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800 text-center">
                      <div className="text-[10px] text-slate-400">Clarity & Structure</div>
                      <div className="text-sm font-bold text-white mt-0.5">{fb.clarity_score}/10</div>
                    </div>
                  </div>

                  {/* Strengths & Improvements */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-900/40 space-y-1">
                      <div className="font-bold text-emerald-400">Key Strengths</div>
                      <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                        {fb.strengths.map((s: string, sIdx: number) => (
                          <li key={sIdx}>{s}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-900/40 space-y-1">
                      <div className="font-bold text-amber-400">Targeted Improvements</div>
                      <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                        {fb.areas_to_improve.map((imp: string, iIdx: number) => (
                          <li key={iIdx}>{imp}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Model Answer */}
                  <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs text-slate-400 leading-relaxed">
                    <strong className="text-white">Model Answer Guidance: </strong>
                    {fb.model_improved_answer}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: QUESTION BANK */}
      {activeTab === "bank" && (
        <div className="space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              {["All", "Technical", "Aptitude", "HR"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => handleCategoryFilter(cat)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-colors ${
                    bankCategory === cat
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            <div className="text-xs text-slate-400">{questions.length} curated questions</div>
          </div>

          <div className="space-y-3">
            {questions.map((q) => {
              const isRevealed = revealedQuestions[q.id];
              return (
                <div
                  key={q.id}
                  className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300">
                        {q.category}
                      </span>
                      {q.sub_category && (
                        <span className="text-[11px] text-slate-400">• {q.sub_category}</span>
                      )}
                    </div>
                    <span className="text-[11px] text-slate-500 font-medium">{q.difficulty}</span>
                  </div>

                  <p className="text-sm font-semibold text-white leading-relaxed">{q.question_text}</p>

                  {q.options && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                      {q.options.map((opt: string, idx: number) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs text-slate-300"
                        >
                          {opt}
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="pt-2">
                    <button
                      onClick={() =>
                        setRevealedQuestions({
                          ...revealedQuestions,
                          [q.id]: !isRevealed,
                        })
                      }
                      className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                    >
                      {isRevealed ? "Hide Answer & Explanation" : "Reveal Answer & Explanation"}
                      {isRevealed ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                    </button>

                    {isRevealed && (
                      <div className="mt-3 p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-1 text-xs">
                        <div className="text-emerald-400 font-bold">Answer: {q.correct_answer || "N/A"}</div>
                        <div className="text-slate-300 leading-relaxed">{q.explanation}</div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 3: SKILL DIAGNOSTIC QUIZ */}
      {activeTab === "quiz" && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Adaptive Skill Assessment
                </span>
                <h2 className="text-xl font-bold text-white mt-1">Skill Verification Quiz</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Passing (≥ 70%) automatically updates your profile verification and advances your preparation roadmap.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={quizSkillId}
                  onChange={(e) => {
                    setQuizSkillId(e.target.value);
                    loadQuiz(e.target.value);
                  }}
                  className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="">-- Choose Skill --</option>
                  {profile?.skills.map((s) => (
                    <option key={s.skill_id} value={s.skill_id}>
                      {s.name} ({s.proficiency})
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => quizSkillId && loadQuiz(quizSkillId)}
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                  title="Reload Quiz"
                >
                  <RefreshCw className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Quiz Questions */}
          {quizData && (
            <div className="space-y-6">
              {quizResult && (
                <div
                  className={`p-6 rounded-3xl border text-center space-y-2 ${
                    quizResult.passed
                      ? "bg-emerald-950/40 border-emerald-800 text-emerald-300"
                      : "bg-rose-950/40 border-rose-800 text-rose-300"
                  }`}
                >
                  <div className="text-2xl font-black">{quizResult.percentage}% Score</div>
                  <div className="font-bold text-sm">
                    {quizResult.passed ? "Skill Verified Successfully!" : "Remedial Study Needed"}
                  </div>
                  <p className="text-xs max-w-md mx-auto">{quizResult.feedback}</p>
                  {quizResult.roadmap_adapted && (
                    <div className="text-xs font-semibold mt-2 px-3 py-1 bg-slate-900/60 rounded-full inline-block text-white">
                      Roadmap update: {quizResult.adaptation_note}
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-4">
                {quizData.questions.map((q: any, idx: number) => (
                  <div key={q.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
                    <div className="text-xs font-bold text-indigo-400">Question {idx + 1}</div>
                    <p className="text-sm font-semibold text-white leading-relaxed">{q.question_text}</p>

                    <div className="space-y-2 pt-1">
                      {q.options.map((opt: string, optIdx: number) => (
                        <label
                          key={optIdx}
                          className={`flex items-start gap-3 p-3 rounded-xl border text-xs cursor-pointer transition-colors ${
                            quizAnswers[q.id] === opt
                              ? "bg-indigo-600/20 border-indigo-500 text-white font-medium"
                              : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700"
                          }`}
                        >
                          <input
                            type="radio"
                            name={`quiz_${q.id}`}
                            value={opt}
                            checked={quizAnswers[q.id] === opt}
                            onChange={() => setQuizAnswers({ ...quizAnswers, [q.id]: opt })}
                            className="mt-0.5 accent-indigo-500"
                          />
                          <span>{opt}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleSubmitQuiz}
                  disabled={submittingQuiz || Object.keys(quizAnswers).length === 0}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/30 transition-all"
                >
                  {submittingQuiz ? "Submitting Quiz..." : "Submit & Grade Quiz"}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
