# Production Resume Generation Pipeline — Implementation Plan

## Current State Analysis

### What Already Exists (DO NOT redesign)
| Component | File | Status |
|-----------|------|--------|
| Knowledge Engine | `app/services/knowledge/engine.py` | Complete — PDF extraction, domain classification, retrieval |
| Prompt Builder | `app/services/prompt_builder.py` | Complete — Structured prompts with knowledge injection |
| Rules Engine | `app/services/rules_engine.py` | Complete — Bullet, summary, resume validation |
| AI Orchestrator | `app/services/ai_orchestrator.py` | Complete — Knowledge → Prompt → AI → Rules pipeline |
| Career Engine | `app/services/career_engine.py` | Complete — High-level API, audit logging |
| Provider Layer | `app/services/ai_providers/` | Complete — Base, Gemini, Mock, Factory |
| PostgreSQL Models | `app/models/resume.py` | Complete — Resume, ResumeSection, ResumeVersion, Template |
| ATS Model | `app/models/analytics.py` | Complete — ATSResult with score, details, recommendations |
| Career Router | `app/routers/career.py` | Partial — Has bullets, summary, cover letter, ATS optimize endpoints |

### What's MISSING (the pipeline gap)
1. **Resume Quality Scorer** — Detailed multi-category scoring (Harvard, ATS, Technical Depth, Action Verbs, Metrics, Readability, Conciseness, Tone)
2. **Resume Critic** — Detect weak bullets, provide internal reasoning
3. **Automatic Rewrite Loop** — Rewrite weak bullets until quality threshold met
4. **Full Resume Generation Pipeline** — Single endpoint that generates complete resume JSON from user input
5. **Persistence Integration** — Store generated resumes + scores + provider metrics in PostgreSQL
6. **Integration Tests** — Full pipeline tests

---

## Architecture — Connecting Existing Components

```
User Input (raw text / role info / job description)
        ↓
   Knowledge Engine (retrieve PDF guidance)
        ↓
   Prompt Builder (build structured prompts)
        ↓
   Gemini Provider (generate content)
        ↓
   Rules Engine (validate bullets/summary)
        ↓
   Resume Quality Scorer (NEW — multi-category scoring)
        ↓
   Resume Critic (NEW — detect weak bullets, suggest rewrites)
        ↓
   Rewrite Loop (NEW — auto-rewrite until threshold met)
        ↓
   ATS Validation (existing ATSResult scoring)
        ↓
   PostgreSQL (store resume + scores + metadata)
        ↓
   Return structured Resume JSON
```

---

## Files to CREATE

### 1. `app/services/resume_scorer.py` — Resume Quality Scorer
New service that scores a complete resume across 8 categories:
- **Harvard Compliance** (action verbs, quantification, no first-person) — Uses RulesEngine
- **ATS Compliance** (keywords, formatting, section completeness) — Uses ATSScoreService patterns
- **Technical Depth** (technology mentions, specificity)
- **Action Verbs** (strong verbs ratio)
- **Metrics** (quantifiable impact ratio)
- **Readability** (sentence length, complexity)
- **Conciseness** (bullet length, word count)
- **Professional Tone** (vague phrases, marketing language)

Returns `QualityScore` dataclass with per-category scores (0-100), overall score, and actionable feedback.

### 2. `app/services/resume_critique.py` — Resume Critic
New service that:
- Detects weak bullets using RulesEngine violations
- Classifies weakness type (no verb, vague, no metrics, too long, generic)
- Generates specific rewrite suggestions
- Provides reasoning for each critique

Returns `CritiqueResult` with list of `BulletCritique` objects.

### 3. `app/services/resume_pipeline.py` — Full Pipeline Service
New service that orchestrates the complete flow:
1. Receive user input (role info, job description, optional existing resume)
2. Knowledge retrieval (via existing KnowledgeEngine)
3. Generate summary (via CareerEngine/orchestrator)
4. Generate bullets per role (via CareerEngine/orchestrator)
5. Score with ResumeScorer
6. Critique with ResumeCritique
7. Auto-rewrite weak bullets (loop until quality >= threshold)
8. ATS validation (via existing ATSScoreService)
9. Store in PostgreSQL (resume + sections + scores + metadata)
10. Return structured resume JSON

### 4. `app/models/ai_generation.py` — AI Generation Tracking Model
New SQLAlchemy model to store:
- `id`, `user_id`, `resume_id`
- `task_type` (resume_generation, bullet_rewrite, ats_optimization)
- `provider`, `model`, `prompt_tokens`, `completion_tokens`, `estimated_cost`
- `latency_ms`, `success`, `error_code`
- `quality_score`, `ats_score`
- `metadata_json`, `created_at`

### 5. `app/routers/resume_pipeline.py` — Pipeline API Router
New router with endpoints:
- `POST /api/v1/pipeline/generate` — Full resume generation
- `POST /api/v1/pipeline/generate-bullets` — Generate bullets with scoring
- `POST /api/v1/pipeline/rewrite-bullet` — Single bullet rewrite with critic
- `POST /api/v1/pipeline/score` — Score existing resume
- `POST /api/v1/pipeline/critique` — Critique existing resume
- `GET /api/v1/pipeline/health` — Health check

### 6. `tests/test_resume_pipeline.py` — Integration Tests
Full pipeline integration tests covering:
- Resume only (no job description)
- Resume + Job Description
- Resume + Existing Resume (improvement)
- Full Pipeline (all features)
- Invalid Input handling
- Retry Logic (mocked provider failures)
- Validation (RulesEngine integration)
- Rewrite Loop (weak bullets → rewritten bullets)

---

## Files to MODIFY

### 7. `app/services/career_engine.py` — Add pipeline method
Add `generate_full_resume()` method that:
- Accepts role info + job description + optional existing resume
- Orchestrates all sub-generations (summary, bullets per role)
- Returns structured resume dict

### 8. `app/routers/career.py` — Add pipeline endpoint
Add endpoint that calls CareerEngine.generate_full_resume()
Wire up the full pipeline endpoint.

### 9. `app/models/__init__.py` — Export new model
Add `AIGeneration` to the model exports.

### 10. `app/main.py` — Register new router
Include the new pipeline router.

---

## Database Changes

### New Table: `ai_generations`
```sql
CREATE TABLE ai_generations (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    resume_id VARCHAR(36) REFERENCES resumes(id) ON DELETE SET NULL,
    task_type VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100),
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    estimated_cost FLOAT DEFAULT 0.0,
    latency_ms FLOAT DEFAULT 0.0,
    success BOOLEAN DEFAULT TRUE,
    error_code VARCHAR(50),
    quality_score FLOAT,
    ats_score INTEGER,
    metadata_json TEXT,
    created_at DATETIME NOT NULL
);
```

No existing tables are modified. This is additive only.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/pipeline/generate` | Full resume generation with scoring |
| POST | `/api/v1/pipeline/generate-bullets` | Generate bullets + score + critique |
| POST | `/api/v1/pipeline/rewrite-bullet` | Single bullet rewrite with critic |
| POST | `/api/v1/pipeline/score` | Score existing resume |
| POST | `/api/v1/pipeline/critique` | Critique existing resume |
| GET | `/api/v1/pipeline/health` | Health check |

Existing endpoints remain unchanged:
- `POST /api/v1/career/bullets` — Still works
- `POST /api/v1/career/summary` — Still works
- `POST /api/v1/career/cover-letter` — Still works
- `POST /api/v1/career/ats-optimize` — Still works

---

## Implementation Order

1. **Resume Quality Scorer** (`resume_scorer.py`) — No dependencies on other new code
2. **Resume Critic** (`resume_critique.py`) — Depends on RulesEngine + Scorer
3. **AI Generation Model** (`ai_generation.py`) — Standalone DB model
4. **Full Pipeline Service** (`resume_pipeline.py`) — Depends on 1, 2, 3 + existing CareerEngine
5. **Pipeline Router** (`resume_pipeline.py` router) — Depends on 4
6. **CareerEngine update** — Add `generate_full_resume()` method
7. **Wiring** — Register router in main.py, export models
8. **Integration Tests** — Full pipeline tests

---

## Constraints Respected

- NO redesign of existing architecture
- NO new frameworks or libraries
- All existing components reused as-is
- Gemini-specific code stays in provider layer only
- Knowledge Engine called before every generation
- Rules Engine validates all output
- Provider metrics tracked for every AI call
- PostgreSQL for all persistence
- All changes additive (no existing tables modified)
