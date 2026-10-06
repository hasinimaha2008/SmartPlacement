"use client";

import { useEffect, useState } from "react";
import { api, StudentProfile, RoleDetail } from "@/lib/api";
import {
  User,
  Sparkles,
  Layers,
  GraduationCap,
  Briefcase,
  Plus,
  Trash2,
  CheckCircle2,
  FileText,
  Save,
  AlertCircle
} from "lucide-react";

export default function ProfilePage() {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [roles, setRoles] = useState<RoleDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Resume extraction state
  const [resumeText, setResumeText] = useState("");
  const [extracting, setExtracting] = useState(false);
  const [extractedSkills, setExtractedSkills] = useState<any[]>([]);

  // Add skill state
  const [newSkillName, setNewSkillName] = useState("");
  const [newSkillProficiency, setNewSkillProficiency] = useState<"Beginner" | "Intermediate" | "Advanced">("Intermediate");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [profData, rolesData] = await Promise.all([
          api.getProfile(),
          api.getRoles(),
        ]);
        setProfile(profData);
        setRoles(rolesData);
      } catch (err: any) {
        setMessage({ type: "error", text: err.message || "Failed to load profile data" });
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleExtractSkills = async () => {
    if (!resumeText.trim()) return;
    try {
      setExtracting(true);
      const res = await api.extractSkills(resumeText);
      setExtractedSkills(res.extracted_skills);
      setMessage({ type: "success", text: `Extracted ${res.count} canonical technical skills from text.` });
    } catch (err: any) {
      setMessage({ type: "error", text: err.message || "Skill extraction failed." });
    } finally {
      setExtracting(false);
    }
  };

  const handleAddExtractedToProfile = () => {
    if (!profile) return;
    const existing = new Set(profile.skills.map((s) => s.name.toLowerCase()));
    const newItems = extractedSkills
      .filter((es) => !existing.has(es.canonical_name.toLowerCase()))
      .map((es) => ({
        id: `temp_${Math.random()}`,
        skill_id: es.canonical_name,
        name: es.canonical_name,
        category: es.category,
        proficiency: "Intermediate" as const,
        verified: true,
      }));

    setProfile({
      ...profile,
      skills: [...profile.skills, ...newItems],
    });
    setExtractedSkills([]);
    setMessage({ type: "success", text: `Added ${newItems.length} extracted skills to profile! Don't forget to save.` });
  };

  const handleAddManualSkill = () => {
    if (!profile || !newSkillName.trim()) return;
    const exists = profile.skills.some((s) => s.name.toLowerCase() === newSkillName.trim().toLowerCase());
    if (exists) {
      setMessage({ type: "error", text: "Skill already exists on profile." });
      return;
    }

    setProfile({
      ...profile,
      skills: [
        ...profile.skills,
        {
          id: `manual_${Date.now()}`,
          skill_id: newSkillName.trim(),
          name: newSkillName.trim(),
          category: "General",
          proficiency: newSkillProficiency,
          verified: false,
        },
      ],
    });
    setNewSkillName("");
  };

  const handleRemoveSkill = (skillName: string) => {
    if (!profile) return;
    setProfile({
      ...profile,
      skills: profile.skills.filter((s) => s.name !== skillName),
    });
  };

  const handleSaveProfile = async () => {
    if (!profile) return;
    try {
      setSaving(true);
      setMessage(null);
      const payload = {
        full_name: profile.full_name,
        email: profile.email,
        headline: profile.headline,
        degree: profile.degree,
        branch: profile.branch,
        graduation_year: profile.graduation_year,
        cgpa: profile.cgpa,
        bio: profile.bio,
        interests: profile.interests,
        target_role_id: profile.target_role_id,
        skills: profile.skills.map((s) => ({
          skill_name: s.name,
          proficiency: s.proficiency,
        })),
        projects: profile.projects.map((p) => ({
          title: p.title,
          description: p.description,
          technologies: p.technologies,
          github_url: p.github_url,
          live_url: p.live_url,
        })),
        certifications: profile.certifications.map((c) => ({
          title: c.title,
          issuing_organization: c.issuing_organization,
          issue_year: c.issue_year,
          credential_url: c.credential_url,
        })),
        experiences: profile.experiences.map((e) => ({
          title: e.title,
          company: e.company,
          experience_type: e.experience_type,
          start_date: e.start_date,
          end_date: e.end_date,
          description: e.description,
          skills_used: e.skills_used,
        })),
      };

      const updated = await api.updateProfile(payload);
      setProfile(updated);
      setMessage({ type: "success", text: "Student profile saved and updated successfully!" });
    } catch (err: any) {
      setMessage({ type: "error", text: err.message || "Failed to save profile." });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <div className="w-8 h-8 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
        <p className="text-slate-400 text-sm">Loading student profile...</p>
      </div>
    );
  }

  if (!profile) return null;

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Page Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
            <User className="w-7 h-7 text-indigo-400" />
            Student Profile & Skill Inventory
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage your academic credentials, verified skills, and target placement role.
          </p>
        </div>

        <button
          onClick={handleSaveProfile}
          disabled={saving}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold shadow-lg shadow-indigo-600/30 transition-all flex items-center gap-2 shrink-0"
        >
          <Save className="w-4 h-4" />
          {saving ? "Saving Changes..." : "Save Profile"}
        </button>
      </div>

      {/* Alert Banner */}
      {message && (
        <div
          className={`p-4 rounded-2xl flex items-center gap-3 text-sm ${
            message.type === "success"
              ? "bg-emerald-950/60 border border-emerald-800 text-emerald-300"
              : "bg-rose-950/60 border border-rose-800 text-rose-300"
          }`}
        >
          {message.type === "success" ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <AlertCircle className="w-5 h-5 shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Academic & Target Role Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <GraduationCap className="w-5 h-5 text-indigo-400" />
          Academic Information & Target Role
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Full Name</label>
            <input
              type="text"
              value={profile.full_name}
              onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Email Address</label>
            <input
              type="email"
              disabled
              value={profile.email}
              className="w-full bg-slate-950/50 border border-slate-800/60 rounded-xl px-3.5 py-2.5 text-sm text-slate-400 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Degree</label>
            <input
              type="text"
              value={profile.degree}
              onChange={(e) => setProfile({ ...profile, degree: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Branch / Specialization</label>
            <input
              type="text"
              value={profile.branch}
              onChange={(e) => setProfile({ ...profile, branch: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Graduation Year</label>
            <input
              type="number"
              value={profile.graduation_year}
              onChange={(e) => setProfile({ ...profile, graduation_year: parseInt(e.target.value) || 2026 })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">CGPA (out of 10.0)</label>
            <input
              type="number"
              step="0.01"
              value={profile.cgpa}
              onChange={(e) => setProfile({ ...profile, cgpa: parseFloat(e.target.value) || 8.0 })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="sm:col-span-2 lg:col-span-3">
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Target Placement Role</label>
            <select
              value={profile.target_role_id || ""}
              onChange={(e) => setProfile({ ...profile, target_role_id: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="">-- Select Target Career Role --</option>
              {roles.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title} ({r.category})
                </option>
              ))}
            </select>
          </div>

          <div className="sm:col-span-2 lg:col-span-3">
            <label className="block text-xs font-semibold text-slate-400 mb-1.5">Professional Headline / Bio</label>
            <textarea
              rows={2}
              value={profile.headline || ""}
              onChange={(e) => setProfile({ ...profile, headline: e.target.value })}
              placeholder="e.g. Aspiring Full-Stack & Backend Engineer interested in microservices and distributed APIs..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* AI/NLP Resume Skill Extractor */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              AI Skill Extraction from Resume / Text
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Paste your resume text, GitHub summary, or project descriptions. The system automatically normalizes terms into standardized canonical skills.
            </p>
          </div>
        </div>

        <textarea
          rows={4}
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
          placeholder="Paste resume excerpt or skills summary here (e.g. Developed backend microservices using Python, FastAPI, Docker, and PostgreSQL. Experienced in React, Tailwind, and Data Structures...)"
          className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-sm text-white focus:outline-none focus:border-indigo-500"
        />

        <div className="flex items-center justify-between">
          <button
            onClick={handleExtractSkills}
            disabled={extracting || !resumeText.trim()}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5"
          >
            <FileText className="w-4 h-4" />
            {extracting ? "Extracting Canonical Skills..." : "Extract & Normalize Skills"}
          </button>

          {extractedSkills.length > 0 && (
            <button
              onClick={handleAddExtractedToProfile}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" />
              Add All ({extractedSkills.length}) to Profile
            </button>
          )}
        </div>

        {/* Extracted preview */}
        {extractedSkills.length > 0 && (
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800 space-y-2">
            <div className="text-xs font-semibold text-slate-400">Extracted Canonical Skills:</div>
            <div className="flex flex-wrap gap-2">
              {extractedSkills.map((es, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg bg-indigo-950/60 border border-indigo-800/60 text-indigo-300 text-xs font-medium flex items-center gap-1"
                >
                  ✓ {es.canonical_name}
                  <span className="text-[10px] text-slate-400">({es.category})</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Verified Skills & Proficiency Inventory */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              Skill Inventory ({profile.skills.length})
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Specify your proficiency level (Beginner, Intermediate, Advanced) for each competency.
            </p>
          </div>

          {/* Quick add manual */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Add skill (e.g. Docker)"
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            />
            <select
              value={newSkillProficiency}
              onChange={(e) => setNewSkillProficiency(e.target.value as any)}
              className="bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Advanced">Advanced</option>
            </select>
            <button
              onClick={handleAddManualSkill}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-indigo-400 transition-colors"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Skills Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {profile.skills.map((skill) => (
            <div
              key={skill.id || skill.name}
              className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80"
            >
              <div>
                <div className="text-sm font-semibold text-white">{skill.name}</div>
                <div className="text-[11px] text-slate-400">{skill.category}</div>
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={skill.proficiency}
                  onChange={(e) => {
                    const updated = profile.skills.map((s) =>
                      s.name === skill.name ? { ...s, proficiency: e.target.value as any } : s
                    );
                    setProfile({ ...profile, skills: updated });
                  }}
                  className={`text-xs font-semibold px-2 py-1 rounded-lg border focus:outline-none ${
                    skill.proficiency === "Advanced"
                      ? "bg-emerald-950/50 border-emerald-800 text-emerald-400"
                      : skill.proficiency === "Intermediate"
                      ? "bg-indigo-950/50 border-indigo-800 text-indigo-300"
                      : "bg-slate-800 border-slate-700 text-slate-300"
                  }`}
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>

                <button
                  onClick={() => handleRemoveSkill(skill.name)}
                  className="p-1 text-slate-500 hover:text-rose-400 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Projects Showcase */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 space-y-5">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <Briefcase className="w-5 h-5 text-sky-400" />
          Technical Projects ({profile.projects.length})
        </h2>

        <div className="space-y-3">
          {profile.projects.map((proj) => (
            <div
              key={proj.id}
              className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-2"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-white text-sm">{proj.title}</h3>
                {proj.github_url && (
                  <a
                    href={proj.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-indigo-400 hover:underline"
                  >
                    View Repo
                  </a>
                )}
              </div>
              <p className="text-xs text-slate-300">{proj.description}</p>
              <div className="flex flex-wrap gap-1.5 pt-1">
                {proj.technologies.map((t, idx) => (
                  <span
                    key={idx}
                    className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md font-mono"
                  >
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
