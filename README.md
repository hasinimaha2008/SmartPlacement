# SmartPlacement — AI/ML Student Placement Preparation Platform

> An explainable, hybrid AI/ML career guidance and placement preparation system featuring standardized skill taxonomies, role-skill gap diagnosis, adaptive milestones, and preparation readiness indicators.

---

## 🚀 Key Features

1. **Student Profiling & Skill Extraction**:
   - Manage academic degrees, branch, CGPA, verified skills with proficiency ratings (`Beginner`, `Intermediate`, `Advanced`), projects, certifications, and career interests.
   - AI/NLP Skill Extractor: Paste resume text or GitHub bio to automatically extract and normalize canonical skills via exact and alias matching.
2. **Hybrid Role Recommendations & Explainability**:
   - Controlled taxonomy of 15 industry roles (Software Developer, Frontend, Backend, Full-Stack, Data Analyst, Data Scientist, ML Engineer, DevOps, Cloud Engineer, Cybersecurity, QA Engineer, Business Analyst, DBA, UI/UX Designer, Systems Engineer).
   - Weighted multi-signal ranking: Structured Skill Match (45%), Dense Semantic Similarity (25%), Project Relevance (15%), Academic Alignment (10%), Interest Alignment (5%).
   - Transparent rationales explaining *why* roles were recommended, matched competencies, and prioritized gaps.
3. **Role-Skill Gap Analyzer**:
   - Precise diagnostic breakdown classifying competencies into: Matched Skills, Proficiency Gaps, and Missing Prerequisites.
   - Priority rankings (`Critical`, `High`, `Medium`, `Low`) with targeted learning guidance.
4. **Personalized Preparation Roadmap & Adaptive Learning**:
   - 4-stage sequential milestone roadmap: Core Foundations → Applied Frameworks → Systems & Projects → Mock Interview Drills.
   - Interactive milestone checklist with curated documentation, courses, and practice platforms.
   - Adaptive feedback mechanism: Assessment scores automatically elevate topic priorities or mark items completed.
5. **Interview & Aptitude Practice**:
   - Text AI Mock Interview Studio: Interactive, role-specific 3-round interview simulator evaluating responses on technical depth, relevance, and clarity.
   - Comprehensive Question Bank across Technical, Aptitude, and HR categories.
   - Timed Diagnostic Quizzes with instant scoring and profile verification.
6. **Preparation Readiness Index**:
   - Transparent 0–100 score across 4 pillars (Skill Coverage 35%, Roadmap Progress 25%, Assessments 20%, Mock Practice 20%).
   - Categorized into clear readiness bands: *Beginning Preparation*, *Developing Readiness*, *Placement Ready*, and *Highly Competitive*.
7. **Empirical Evaluation & Research Sandbox**:
   - Interactive academic benchmark comparing TF-IDF, Sentence-BERT, Structured Ontology, and Hybrid models.
   - Full ablation study proving component contributions.

---

## 🛠️ Technology Stack

- **Frontend**: Next.js 15 (App Router), TypeScript, React 18, Tailwind CSS, Lucide Icons.
- **Backend**: FastAPI (Python 3.11), Pydantic v2, SQLAlchemy 2.0, Uvicorn.
- **AI / ML**: Sentence-Transformers (`all-MiniLM-L6-v2`), Scikit-Learn, NumPy, PyTorch.
- **Database**: Supabase PostgreSQL with reproducible migrations in `supabase/migrations/` and SQLite local development fallback.

---

## 🏁 Getting Started

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API docs available at: `http://127.0.0.1:8000/docs`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run start
```
Frontend application accessible at: `http://localhost:3000`

### 4. Running Backend Automated Tests
```bash
cd backend
python -m pytest tests -v
```

---

## 📁 Repository Structure

```
SmartPlacement/
├── ARCHITECTURE.md                 # System architecture & research defense document
├── README.md                       # Main project overview and setup
├── .env.example                    # Environment configuration template
├── backend/
│   ├── app/
│   │   ├── config.py               # Pydantic settings & environment configuration
│   │   ├── database.py             # SQLAlchemy engine & session factory
│   │   ├── main.py                 # FastAPI application & router mounting
│   │   ├── seed_data.py            # 15 roles, canonical skills, questions seed module
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── services/               # ML recommender, skill gap, roadmap, readiness
│   │   └── routers/                # REST API route handlers
│   ├── tests/                      # Pytest automated test suite (14 tests)
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # App Router layout with navigation
│   │   │   ├── page.tsx            # Unified student dashboard
│   │   │   ├── profile/            # Profile & skill extraction page
│   │   │   ├── recommendations/    # Role recommendations & explainability
│   │   │   ├── skill-gap/          # Skill-gap analyzer
│   │   │   ├── roadmap/            # Personalized roadmap
│   │   │   ├── interview/          # Interview prep & text mock AI studio
│   │   │   └── evaluation/         # Empirical research & ablation sandbox
│   │   └── lib/api.ts              # Typed API client
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
└── supabase/
    └── migrations/
        ├── 20261005_000001_initial_schema.sql  # Production PostgreSQL DDL with RLS
        └── 20261005_000002_seed_data.sql       # Seed data SQL script
```
