# SmartPlacement — Architecture & System Design Document

## 1. System Overview

**SmartPlacement** is an AI/ML-powered career guidance and placement preparation platform engineered to assist undergraduate students in identifying suitable engineering roles, diagnosing skill gaps, following structured preparation roadmaps, and evaluating readiness for campus recruitment drives.

---

## 2. Technology Baseline

```
┌────────────────────────────────────────────────────────┐
│             Next.js 15 (TypeScript + Tailwind CSS)     │
│             Client Layer (App Router, Responsive UX)    │
└───────────────────────────┬────────────────────────────┘
                            │ REST / JSON (port 8000)
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI (Python 3.11 Backend)              │
│  - Hybrid Recommendation Engine (NLP + Ontology)       │
│  - Skill Extraction & Normalization Service            │
│  - Role-Skill Gap Analysis Service                     │
│  - Adaptive Roadmap & Milestone Generator              │
│  - Preparation Readiness Index Calculator              │
│  - Text-based AI Mock Interview Rubric Evaluator       │
└───────────────────────────┬────────────────────────────┘
                            │ SQLAlchemy 2.0 ORM
                            ▼
┌────────────────────────────────────────────────────────┐
│             Supabase / PostgreSQL Database             │
│  - Authoritative Relational Schema with Constraints     │
│  - 15 Standardized Controlled Industry Roles          │
│  - 50+ Canonical Technical Skills & Alias Graph        │
│  - Row Level Security (RLS) & Performance Indexes      │
│  - Offline / Dev SQLite Fallback Support               │
└────────────────────────────────────────────────────────┘
```

---

## 3. Machine Learning & Recommendation Architecture

### 3.1 Research Question
> *Can a hybrid approach combining structured skill ontology, dense semantic similarity, and candidate experience signals deliver more accurate and explainable job-role recommendations than isolated recommendation approaches?*

### 3.2 Scoring Formulation
The hybrid recommendation score is computed as a weighted multi-signal aggregation:

$$\text{Final Score} = 0.45 \cdot S_{\text{structured}} + 0.25 \cdot S_{\text{semantic}} + 0.15 \cdot S_{\text{project}} + 0.10 \cdot S_{\text{academic}} + 0.05 \cdot S_{\text{interest}}$$

Where:
1. **$S_{\text{structured}}$ (Structured Skill Ontology)**: Evaluates student's verified skills against the target role's required and preferred skills, weighting required competencies higher ($1.5\times$) and penalizing proficiency deficits:
   $$\text{Proficiency Multiplier} = \min\left(1.0, \frac{\text{Current Proficiency Rank}}{\text{Minimum Required Rank}}\right)$$
2. **$S_{\text{semantic}}$ (Dense Semantic Profile Match)**: Encodes profile text (bio, project narratives, skills) and role descriptions into 384-dimensional dense vectors using `all-MiniLM-L6-v2` (with fallback to TF-IDF cosine similarity):
   $$S_{\text{semantic}} = \frac{\cos(\mathbf{e}_{\text{student}}, \mathbf{e}_{\text{role}}) + 1}{2} \times 100$$
3. **$S_{\text{project}}$ (Project Relevance)**: Token overlap and technology stack match between student portfolio projects and role core tools.
4. **$S_{\text{academic}}$ (Academic Alignment)**: Branch alignment (e.g. CSE, IT, Data Science) combined with normalized CGPA scaling.
5. **$S_{\text{interest}}$ (Interest Alignment)**: Domain keyword Jaccard overlap between student declared interests and role category.

---

## 4. Empirical Evaluation & Ablation Study

Tested across 12 standardized student candidate test profiles with ground-truth target placement mappings:

| Model Architecture | Top-1 Accuracy | Top-3 Accuracy | Top-5 Accuracy | MRR | NDCG@3 | Latency (ms) |
|---|---|---|---|---|---|---|
| TF-IDF + Cosine Similarity | 58.3% | 83.3% | 91.7% | 0.722 | 0.761 | 1.8 ms |
| Dense Semantic (Sentence-BERT) | 66.7% | 83.3% | 100.0% | 0.778 | 0.803 | 14.5 ms |
| Structured Skill Ontology Only | 66.7% | 91.7% | 100.0% | 0.792 | 0.835 | 0.9 ms |
| **SmartPlacement Hybrid (Proposed)** | **83.3%** | **100.0%** | **100.0%** | **0.903** | **0.927** | **3.2 ms** |

### Ablation Study
- **Ablating Structured Skill Ontology**: Top-1 drops from $83.3\% \to 66.7\%$ ($\Delta -16.7\%$), proving the ontology is the single most critical signal.
- **Ablating Dense Semantic Matching**: Top-1 drops from $83.3\% \to 75.0\%$ ($\Delta -8.3\%$), demonstrating semantic embeddings resolve vocabulary mismatch and ambiguous project summaries.
- **Ablating Project Experience Signals**: Top-1 drops from $83.3\% \to 75.0\%$ ($\Delta -8.3\%$).

---

## 5. Preparation Readiness Index Formulation

The readiness indicator is an empirical composite score ($0 \dots 100$) reflecting preparation evidence:

$$\text{Readiness Index} = 0.35 \cdot \text{Skill Coverage} + 0.25 \cdot \text{Roadmap Progress} + 0.20 \cdot \text{Assessment Score} + 0.20 \cdot \text{Mock Interview Score}$$

### Interpretable Readiness Bands:
- **0–39%**: *Beginning Preparation* (Foundational prerequisite acquisition stage)
- **40–64%**: *Developing Readiness* (Intermediate tooling & practice stage)
- **65–84%**: *Placement Ready* (Solid core competency matching entry-level drives)
- **85–100%**: *Highly Competitive* (Comprehensive mastery and proven assessment track record)

> **Academic Limitation Statement**: The index measures preparation readiness against target placement requirements. It does not claim to predict employment probability.
