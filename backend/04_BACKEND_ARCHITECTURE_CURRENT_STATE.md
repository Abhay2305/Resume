# 04 — Backend Architecture: Current State

## Post-SPEC-001 + SPEC-002 Architecture Audit

**Date:** 2026-08-09
**Auditor:** opencode (automated)
**Scope:** Full backend service layer, API routing layer, and their interconnections

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack](#2-technology-stack)
3. [Layered Architecture](#3-layered-architecture)
4. [Engine Inventory](#4-engine-inventory)
5. [Universal AI Engine (SPEC-001)](#5-universal-ai-engine-spec-001)
6. [Prompt Intelligence Engine (SPEC-002)](#6-prompt-intelligence-engine-spec-002)
7. [Intelligence Engines (Deterministic)](#7-intelligence-engines-deterministic)
8. [Legacy/Dead Code](#8-legacydead-code)
9. [API Routing Layer](#9-api-routing-layer)
10. [Call Graph — Who Calls What](#10-call-graph--who-calls-what)
11. [Dependency Rules](#11-dependency-rules)
12. [Data Flow — The Canonical Pipeline](#12-data-flow--the-canonical-pipeline)
13. [Database Schema (Key Relationships)](#13-database-schema-key-relationships)
14. [Middleware Stack](#14-middleware-stack)
15. [Authentication & Authorization](#15-authentication--authorization)
16. [Configuration](#16-configuration)
17. [Testing State](#17-testing-state)
18. [Known Gaps & Risks](#18-known-gaps--risks)
19. [Files Read During Audit](#19-files-read-during-audit)

---

## 1. Executive Summary

The Prompt Resume backend is a **FastAPI + SQLAlchemy + PostgreSQL** application organized as a domain-driven engine ecosystem. After SPEC-001, SPEC-002, and SPEC-003 implementation:

- **Universal AI Engine** is fully decomposed into 10 composable components (types, error classifier, cost tracker, retry policy, provider factory, provider registry, token budget, response cache, universal service, utils) plus a providers sub-package (Gemini, OpenAI, Anthropic). All production-critical features — fallback chain, token budgeting, response caching, streaming, and cost tracking — are implemented and integrated into the orchestrator.

- **Prompt Intelligence v2** is fully operational with 8 components (registry, templates, interpolator, instructions, builder, errors, types, token estimator). It supports 16 prompt types, composable construction, variable validation, token estimation, and versioning. Legacy PromptBuilder is deprecated.

- **Intelligence Engines** (Resume Intelligence, Opportunity, Gap Analysis, Knowledge Intelligence) are fully implemented and deterministic (no AI calls).

- **Intelligence Pipeline** (SPEC-003) connects all 7 intelligence services into a single executable pipeline. The thin orchestration layer composes existing services without modifying them. AI Response Intelligence is now wired as Stage 7 — no longer dead code.

- **Legacy engines** (Knowledge Engine with FAISS, CareerEngine) exist as superseded code.

---

## 2. Technology Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| ORM | SQLAlchemy (async-compatible) |
| Database | PostgreSQL (production), SQLite (tests) |
| Auth | JWT (jose), bcrypt (passlib) |
| AI Providers | google-generativeai, openai, anthropic |
| PDF Extraction | PyPDF2 |
| Vector Search | FAISS (imported but unused) |
| Validation | Pydantic |
| Async | asyncio + run_async helper |

---

## 3. Layered Architecture

```
┌─────────────────────────────────────────┐
│         API Routers (28+)               │  ← HTTP layer, thin delegation
├─────────────────────────────────────────┤
│        Services Layer (30+)             │  ← Business logic, orchestration
├─────────────────────────────────────────┤
│     Repository Layer (15+)              │  ← Data access (BaseRepository pattern)
├─────────────────────────────────────────┤
│    Database (SQLAlchemy ORM)            │  ← Persistence (50+ models)
└─────────────────────────────────────────┘
```

**Conventions:**
- Routers are thin: instantiate a service, call one or two methods, return the result
- Services contain business logic; they own their domain
- Repositories encapsulate DB queries; services never touch SQLAlchemy directly
- No dependency injection framework — services instantiate repositories directly

---

## 4. Engine Inventory

| Engine | Location | Status | AI Calls? |
|--------|----------|--------|-----------|
| **Intelligence Pipeline** | `services/intelligence_pipeline/` | ACTIVE, SPEC-003 complete | No (orchestrates other services) |
| **Universal AI Engine** | `services/ai/` | ACTIVE, SPEC-001 complete | YES (provider abstraction) |
| **Prompt Intelligence v2** | `services/prompt_intelligence_v2/` | ACTIVE, SPEC-002 complete | No (produces prompt packages) |
| **Prompt Intelligence (legacy wrapper)** | `services/prompt_intelligence/` | ACTIVE (uses v2 internally) | No |
| **Resume Intelligence** | `services/resume_intelligence/` | ACTIVE | No (deterministic NLP) |
| **Opportunity Intelligence** | `services/opportunity/` | ACTIVE | No (deterministic parsing) |
| **Gap Analysis** | `services/gap_analysis/` | ACTIVE | No (deterministic matching) |
| **Knowledge Intelligence** | `services/knowledge_intelligence/` | ACTIVE | No (deterministic retrieval) |
| **ATS Engine** | `routers/ats.py` + `services/` | ACTIVE | No (rule-based scoring) |
| **ChatService** | `services/chat_service.py` | ACTIVE (uses UniversalAI) | YES (via UniversalAI) |
| **CareerEngine** | `services/career_engine.py` | ACTIVE (legacy, uses old PromptBuilder) | YES (via UniversalAI) |
| **AIOrchestrator** | `services/ai_orchestrator.py` | ACTIVE (dual mode, uses v2 for construction) | YES (via UniversalAI) |
| **AI Execution** | `services/ai_execution/` | ACTIVE (stub service) | YES (via UniversalAI) |
| **AI Response Intelligence** | `services/ai_response_intelligence/` | ACTIVE (wired into Intelligence Pipeline as Stage 7) | No |
| **Knowledge Engine (legacy)** | `services/knowledge/engine.py` | DEAD CODE (FAISS unused) | No |
| **ResumeGeneratorService** | `services/ai_service.py` | ACTIVE (hardcoded prompts) | YES (via UniversalAI) |
| **CoverLetterGeneratorService** | `services/ai_service.py` | ACTIVE (hardcoded prompts) | YES (via UniversalAI) |

---

## 5. Universal AI Engine (SPEC-001)

### Package Structure

```
services/ai/
├── __init__.py              # Package marker
├── types.py                 # ProviderType, ProviderConfig, ProviderResponse, ProviderMetrics
├── error_classifier.py      # Error hierarchy + SDK exception classification
├── cost_tracker.py          # CostTracker, MODEL_COSTS, estimate_cost(), FallbackMetrics
├── retry_policy.py          # RetryPolicy — exponential backoff with jitter
├── provider_factory.py      # ProviderFactory — creates provider instances from config
├── provider_registry.py     # ProviderRegistry — discovery, selection, fallback chain
├── token_budget.py          # TokenBudget — per-request, per-user daily/monthly limits
├── response_cache.py        # ResponseCache — async-safe exact-match cache with TTL + LRU
├── universal_service.py     # UniversalAIService — public orchestrator (439 lines)
├── utils.py                 # run_async() helper
└── providers/
    ├── base.py              # AIProvider Protocol
    ├── gemini.py            # GeminiProvider
    ├── openai.py            # OpenAIProvider
    └── anthropic.py         # AnthropicProvider
```

### Public API

```python
service = get_ai_service()
response = await service.generate(messages, temperature=0.7, max_tokens=8192)
response = await service.generate(messages, user_id="user-123")  # per-user budgeting
async for token in service.generate_stream(messages): ...       # streaming
service.health_check()
service.get_metrics_history()
service.get_metrics_summary()
service.get_budget_status(user_id="user-123")
service.get_budget_usage(user_id="user-123")
service.parse_json_response(content)
```

### Implemented Features

| Feature | Status | Implementation |
|---------|--------|----------------|
| Provider abstraction | DONE | AIProvider protocol, ProviderFactory, 3 providers |
| Fallback chain | DONE | ProviderRegistry.get_fallback_chain(), AI_FALLBACK_CHAIN env var |
| Token budgeting | DONE | TokenBudget — per-request + per-user daily/monthly |
| Response caching | DONE | ResponseCache — async-safe, TTL, LRU, user-aware keys |
| Streaming | DONE | generate_stream() with fallback chain support |
| Retry with jitter | DONE | RetryPolicy — exponential backoff, retry_after support |
| Cost tracking | DONE | CostTracker — per-request estimation, aggregation, fallback metrics |
| Error classification | DONE | ErrorClassifier — 8 error types, SDK exception mapping |
| Backward compatibility | DONE | ai_service.py re-exports all symbols from ai/ package |
| Structured logging | DONE | Every request logs: request_id, provider, model, tokens, cost, latency |

### Known Limitations (v1)

- In-memory cache — lost on process restart
- In-memory metrics — cost history lost on restart
- In-memory token budgets — per-user counters reset on restart
- No semantic caching — only exact-match deduplication
- No circuit breaker — degraded providers retried on every request
- Token estimation uses `len(text) // 4` — rough approximation

---

## 6. Prompt Intelligence Engine (SPEC-002)

### Package Structure

```
services/prompt_intelligence_v2/
├── __init__.py          # Package marker
├── types.py             # PromptRequest, PromptPackage, PromptTemplateMeta, ValidationResult
├── errors.py            # UnknownPromptType, MissingVariables, InvalidTemplate, TokenLimitExceeded
├── registry.py          # PromptRegistry — 16 prompt types with metadata
├── templates.py         # Template loading from JSON + hardcoded sources
├── interpolator.py      # Variable substitution with {{variable}} syntax
├── instructions.py      # Instruction composer with deduplication
├── builder.py           # PromptBuilder — orchestrates all components
└── token_estimator.py   # (embedded in builder) approximate token counting
```

### Supported Prompt Types (16)

| Category | Types |
|----------|-------|
| Generation | resume_bullets, resume_summary, cover_letter, resume_generation |
| Context-Driven | resume_tailoring, ats_optimization_pi, chat |
| Optimization | ats_optimization |
| Improvement | text_improve, text_shorten, text_expand, text_professional, text_autofix |
| Feedback | bullet_feedback |
| Formatting | structured_resume, cover_letter_direct |

### Construction Pipeline

```
PromptRequest (type + context)
    ↓
Registry Lookup → Template Loading → Variable Interpolation
    ↓
Instruction Composition → Constraint Assembly → Output Schema
    ↓
Token Estimation → Validation → PromptPackage
```

### Boundary

```
Prompt Intelligence produces: PromptPackage (messages + metadata)
Caller passes PromptPackage.messages to: UniversalAIService.generate()
```

Prompt Intelligence **never** calls Universal AI Engine directly.

### Migration Status

| Caller | Status |
|--------|--------|
| ChatService | Migrated to v2 PromptBuilder |
| ATS router | Migrated to v2 PromptBuilder |
| ResumeGeneratorService | Migrated to v2 PromptBuilder |
| PromptIntelligenceService | Uses v2 internally |
| CareerEngine | Retains old PromptBuilder via AIOrchestrator |
| AIOrchestrator | Dual mode — old types preserved, v2 used for construction |

---

## 7. Intelligence Engines (Deterministic)

### Resume Intelligence (`services/resume_intelligence/`)

- Parses resume text into structured data using 11 extractors
- Deterministic: same input → same output, no LLM calls
- Components: ResumeParser, ResumeNormalizer, 11 extractors (contact, skills, experience, education, certifications, projects, achievements, languages, metrics, summary, technology), ResumeKnowledgeBuilder
- Limitations: dictionary-only skills, hardcoded year extraction, no PDF parsing

### Opportunity Intelligence (`services/opportunity/`)

- Parses job descriptions using 5 extractors
- Deterministic: same JD → same output
- Components: OpportunityParser, OpportunityNormalizer, 5 extractors (skill, experience, technology, location, metadata)
- Limitations: dictionary-only skills, naive TF keyword extraction, no URL scraping

### Gap Analysis (`services/gap_analysis/`)

- Compares resume against job description to identify gaps
- 6 specialized analyzers: skill, technology, experience, education, certification, keyword
- Weighted scoring: skills 30%, technology 25%, experience 20%, education 10%, certifications 10%, keywords 5%
- Limitations: no fuzzy matching, simple year comparison, generic recommendations

### Knowledge Intelligence (`services/knowledge_intelligence/`)

- Database-driven knowledge retrieval with gap-aware scoring
- Components: KnowledgeRetriever, KnowledgeRanker, KnowledgeIndexer, KnowledgeContextBuilder, KnowledgeDocumentService, KnowledgeRuleExtractor
- 22 rules from 5 sources (Harvard, MIT, Yale, ATS best practices, platform internal)
- Limitations: heuristic weights, no personalization, loads all rules per request

---

## 8. Legacy/Dead Code

| Component | Location | Status | Risk |
|-----------|----------|--------|------|
| Knowledge Engine (legacy) | `services/knowledge/engine.py` | DEAD CODE — FAISS imported but unused | Dependency bloat, confusion |
| AI Response Intelligence | `services/ai_response_intelligence/` | ACTIVE — wired into Intelligence Pipeline as Stage 7 | Non-pipeline paths still bypass validation |
| CareerEngine | `services/career_engine.py` | SUPERSEDED but still callable | Depends on legacy Knowledge Engine |
| PromptBuilder (old) | `services/prompt_builder.py` | DEPRECATED — still importable | Confusion about which to use |
| AI Execution Engine | `services/ai_execution/` | STUB — only `execution_boundary.py` exists | Pipeline step incomplete |
| `prompt_templates.json` | `data/prompt_templates.json` | OLD template data | Stale if v2 templates diverge |

---

## 9. Intelligence Pipeline (SPEC-003)

### Architecture

```
services/intelligence_pipeline/
├── __init__.py          # Package marker
├── service.py           # IntelligencePipelineService — thin orchestration layer
└── types.py             # PipelineRequest, PipelineResult, StageResult
```

### Pipeline Stages

| Stage | Name | Service | Required? | Non-Fatal? |
|-------|------|---------|-----------|------------|
| 1 | resume_intelligence | ResumeIntelligenceService | Yes | No |
| 2 | opportunity_intelligence | OpportunityService | Yes | No |
| 3 | gap_analysis | GapAnalysisService | Yes | No |
| 4 | knowledge_intelligence | KnowledgeIntelligenceService | No | Yes |
| 5 | prompt_intelligence | PromptIntelligenceService | Yes | No |
| 6 | ai_execution | AIExecutionService | Yes | No |
| 7 | ai_response_intelligence | AIResponseIntelligenceService | No | Yes (skippable) |

### Design Principles

- **Composition, not modification** — composes existing services; does not modify them
- **Constructor injection** — all 9 dependencies injected via `__init__` (no direct instantiation)
- **Thin orchestration** — `service.py` is ~530 lines; stage logic delegates to injected services
- **Boundary preservation** — pipeline does NOT import UniversalAIService, PromptBuilderV2, or any AI provider SDK

### ID Threading

```
Stage 1 → run.resume_profile_id → Stage 3 (gap_analysis)
Stage 2 → run.opportunity_id → Stage 3 (gap_analysis)
Stage 3 → run.gap_analysis_id → Stage 4 (knowledge), Stage 5 (prompt)
Stage 5 → run.prompt_package_id → Stage 6 (execution)
Stage 6 → run.ai_execution_id → Stage 7 (validation)
```

### Database Models

```
PipelineRun (pipeline_runs)
├── id, user_id, status, resume_text, opportunity_text
├── 7 entity ID columns (resume_profile_id ... ai_validation_id)
├── total_latency_ms, error_message, metadata, timestamps
└── stages relationship → PipelineStage (1:N)

PipelineStage (pipeline_stages)
├── id, pipeline_run_id (FK), stage_name, stage_order
├── status, entity_id, latency_ms, error_message
├── metadata, started_at, completed_at
└── pipeline_run relationship → PipelineRun (N:1)
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/pipeline/execute` | POST | Execute full 7-stage pipeline |
| `/api/pipeline/{id}` | GET | Get pipeline status + stages |
| `/api/pipeline/{id}/stages` | GET | Get stage results only |

All endpoints require authentication via `Depends(require_auth)`.

---

## 10. API Routing Layer

### Router Inventory (29 routers)

| Router | Path Prefix | Service(s) Called | Pattern |
|--------|-------------|-------------------|---------|
| `auth.py` | `/api/auth` | AuthService | Direct |
| `admin_auth.py` | `/api/auth/admin` | AuthService | Direct |
| `resumes.py` | `/api/resume` | ResumeGeneratorService + DB | Mixed |
| `cover_letters.py` | `/api/cover-letter` | CoverLetterGeneratorService | Direct |
| `ats.py` | `/api/ats` | ATSScoreService + UniversalAIService | Direct + inline AI |
| `career.py` | `/api/v1/career` | CareerEngine (singleton) | Engine delegation |
| `chat.py` | `/api/chat` | ChatService (singleton) | Engine delegation |
| `resume_intelligence.py` | `/api/resume-intelligence` | ResumeIntelligenceService | Single service |
| `opportunities.py` | `/api/opportunities` | OpportunityService | Single service |
| `gap_analysis.py` | `/api/gap-analysis` | GapAnalysisService | Single service |
| `knowledge_intelligence.py` | `/api/knowledge` | KnowledgeIntelligenceService + KnowledgeDocumentService | Two services |
| `prompt_intelligence.py` | `/api/prompt-intelligence` | PromptIntelligenceService | Single service |
| `ai_execution.py` | `/api/ai` | AIExecutionService | Single service |
| `ai_response_intelligence.py` | `/api/ai-response` | AIResponseIntelligenceService | Single service |
| `pipeline.py` | `/api/pipeline` | IntelligencePipelineService | Orchestration pipeline |
| `pdf.py` | `/api/pdf` | PDFExportService | Direct |
| `health.py` | `/api/health` | Direct | Health checks |
| `config.py` | `/api/config` | ConfigService | Direct |
| `rbac.py` | `/api/rbac` | RBACService | Direct |
| `audit.py` | `/api/audit` | AuditService | Direct |
| `metrics.py` | `/api/metrics` | MetricsService | Direct |
| `errors.py` | `/api/errors` | ErrorService | Direct |
| `ai_monitoring.py` | `/api/ai-monitoring` | MetricsService | Direct |
| `analytics.py` | `/api/analytics` | Direct | Analytics |
| `users.py` | `/api/users` | UserManagementService | Legacy |
| `procs_users.py` | `/api/procs/users` | UserManagementService | Admin |
| `procs_resumes.py` | `/api/procs/resumes` | ResumeManagementService | Admin |
| `procs_dashboard.py` | `/api/procs/dashboard` | DashboardService | Admin |
| `procs_templates.py` | `/api/procs/templates` | Direct | Admin |

### Orchestration Pattern

**One router orchestrates multi-engine flows:** `pipeline.py` chains all 7 intelligence services into a single pipeline execution. All other routers follow the same pattern:
1. Instantiate a service
2. Call one or two methods
3. Return the result

The Intelligence Pipeline replaces the previous pattern where the frontend had to make sequential API calls, threading entity IDs between steps.

**One exception:** `ats.py` `/improve-text` endpoint directly calls `UniversalAIService.generate()` (line 109), bypassing all prompt infrastructure.

---

## 10. Call Graph — Who Calls What

```
routers/pipeline.py
  └── IntelligencePipelineService  [SPEC-003 orchestrator]
        ├── ResumeIntelligenceService  [Stage 1]
        ├── OpportunityService  [Stage 2]
        ├── GapAnalysisService  [Stage 3]
        ├── KnowledgeIntelligenceService  [Stage 4, non-fatal]
        ├── PromptIntelligenceService  [Stage 5]
        ├── AIExecutionService → UniversalAIService.generate()  [Stage 6]
        └── AIResponseIntelligenceService  [Stage 7, non-fatal, skippable]

routers/resumes.py
  └── ResumeGeneratorService → UniversalAIService.generate()  [hardcoded prompts]

routers/cover_letters.py
  └── CoverLetterGeneratorService → UniversalAIService.generate()  [hardcoded prompts]

routers/ats.py
  ├── ATSScoreService.calculate_score()  [rule-based, no AI]
  └── UniversalAIService.generate()  [direct call, inline prompts]

routers/career.py
  └── CareerEngine (singleton)
        └── AIOrchestrator
              ├── KnowledgeEngine  [legacy, keyword-only]
              ├── PromptBuilder  [old, deprecated]
              ├── UniversalAIService.generate()
              └── RulesEngine  [9 validation rules]

routers/chat.py
  └── ChatService (singleton)
        └── UniversalAIService.generate()  [v2 PromptBuilder for system prompt]

routers/resume_intelligence.py
  └── ResumeIntelligenceService  [deterministic, no AI]

routers/opportunities.py
  └── OpportunityService  [deterministic, no AI]

routers/gap_analysis.py
  └── GapAnalysisService  [deterministic, no AI]

routers/knowledge_intelligence.py
  └── KnowledgeIntelligenceService  [deterministic, no AI]

routers/prompt_intelligence.py
  └── PromptIntelligenceService  [uses v2 internally, no AI]

routers/ai_execution.py
  └── AIExecutionService → UniversalAIService.generate()

routers/ai_response_intelligence.py
  └── AIResponseIntelligenceService  [also wired as Stage 7 of pipeline]
```

### Who Imports UniversalAIService

| Caller | Import Path |
|--------|-------------|
| ResumeGeneratorService | `app.services.ai_service` → re-exports from `ai/` |
| CoverLetterGeneratorService | `app.services.ai_service` → re-exports from `ai/` |
| ChatService | `app.services.ai_service` |
| AIOrchestrator | `app.services.ai_service` |
| AIExecutionService | `app.services.ai_service` |
| CareerEngine | `app.services.ai_service` |
| LLMProviderService | `app.services.ai_service` |
| ats.py router | `app.services.ai_service` (direct) |

---

## 11. Dependency Rules

### Enforced (by SPEC-001 design)

| Allowed | Forbidden |
|---------|-----------|
| Any engine → `UniversalAIService.generate()` | `UniversalAIService` → any engine |
| `UniversalAIService` → ProviderRegistry, ProviderFactory, RetryPolicy, CostTracker, TokenBudget, ResponseCache | Any engine → AI provider SDKs directly |
| `ProviderFactory` → AI provider SDKs | `UniversalAIService` → AI provider SDKs directly |
| Prompt Intelligence → (no AI calls) | Prompt Intelligence → `UniversalAIService.generate()` |

### Not Enforced (violations)

| Violation | Location | Risk |
|-----------|----------|------|
| `ats.py` calls UniversalAI directly | `routers/ats.py:109` | Bypasses prompt infrastructure |
| `ResumeGeneratorService` has hardcoded prompts | `services/ai_service.py:79-87` | Bypasses Prompt Intelligence |
| `CoverLetterGeneratorService` has hardcoded prompts | `services/ai_service.py:152-158` | Bypasses Prompt Intelligence |
| `CareerEngine` depends on legacy Knowledge Engine | `services/career_engine.py` | Dead dependency |
| Services instantiate repositories directly | All services | No DI, hard to test |
| `require_role` creates own DB sessions | `middleware/auth.py` | Connection pool exhaustion |

---

## 12. Data Flow — The Canonical Pipeline

### What SPEC-000 Intended

```
Request → Resume Intelligence → Opportunity Intelligence → Gap Analysis →
Knowledge Intelligence → Prompt Intelligence → AI Execution →
AI Response Intelligence → Resume Engine → Persistence
```

### What Actually Exists (Post-SPEC-003)

```
POST /api/pipeline/execute  →  IntelligencePipelineService.execute_pipeline()

  Stage 1: ResumeIntelligenceService.create_profile() + trigger_parse()
  Stage 2: OpportunityService.create_opportunity() + trigger_parse()
  Stage 3: GapAnalysisService.create() + analyze()
  Stage 4: KnowledgeIntelligenceService.retrieve_knowledge()  [non-fatal]
  Stage 5: PromptIntelligenceService.build_prompt()
  Stage 6: AIExecutionService.execute_prompt_package()
  Stage 7: AIResponseIntelligenceService.validate_ai_response()  [non-fatal, skippable]
```

**The Intelligence Pipeline (SPEC-003) provides the backend orchestrator.** The frontend no longer needs to thread IDs between sequential API calls.

### What Still Exists (Non-Pipeline Paths)

Individual engine endpoints remain available for direct access:
- `POST /api/resume-intelligence/` — standalone resume intelligence
- `POST /api/opportunities/` — standalone opportunity intelligence
- `POST /api/gap-analysis/` — standalone gap analysis
- `POST /api/knowledge/retrieve` — standalone knowledge retrieval
- `POST /api/prompt-intelligence/build` — standalone prompt building
- `POST /api/ai/execute` — standalone AI execution (bypasses validation)
- `POST /api/ai-response/validate` — standalone validation

### What's Still Missing

- No event-driven pipeline (step N triggers step N+1) — pipeline is synchronous
- No job queue for long-running multi-step operations
- Non-pipeline AI execution paths still bypass AI Response Intelligence validation

---

## 13. Database Schema (Key Relationships)

```
User ──┬── Profile
       ├── Subscription
       ├── UserRole ── Role ── RolePermission ── Permission
       ├── Resume ── ResumeSection (1:N)
       │         └── ResumeVersion (1:N)
       ├── CoverLetter
       ├── ATSResult
       ├── ResumeProfile ── ParsedResumeData (1:1)
       │                 ├── ResumeEntity (1:N)
       │                 └── ResumeKnowledge (1:1)
       ├── Opportunity ── ParsedOpportunityData (1:1)
       │               └── OpportunityEntity (1:N)
       ├── GapAnalysis ── GapResult (1:N)
       │               └── Recommendation (1:N)
       ├── KnowledgeDocument ── KnowledgeSection (1:N)
       │                     └── KnowledgeRule (1:N)
       ├── KnowledgeRetrieval ── KnowledgeContext (1:1)
       ├── PromptTemplate ── PromptPackage (1:N)
       │                   └── PromptVersion (1:N)
        ├── AIExecution (linked to PromptPackage)
        ├── AIResponseValidation ── ResumeDiff (1:N)
        │                         ├── ChangeSet (1:N)
        │                         ├── ValidationReport (1:N)
        │                         └── ConfidenceScore (1:N)
        ├── PipelineRun (orchestration tracking)
        │             └── PipelineStage (1:N, 7 stages per run)
        └── ...
```

---

## 14. Middleware Stack

Registered in `main.py` (last added = first executed):

| Order | Middleware | Purpose |
|-------|-----------|---------|
| 1 (outermost) | ErrorHandlerMiddleware | Catches unhandled exceptions |
| 2 | ErrorMiddleware | Captures errors for logging |
| 3 | AuditMiddleware | Logs all HTTP requests |
| 4 | MetricsMiddleware | Records request metrics (fire-and-forget) |
| 5 (innermost) | AuditContextMiddleware | Extracts user context from JWT |
| 6 | RateLimitMiddleware | Rate limiting (configurable per-route) |
| 7 | CORSMiddleware | CORS headers |

---

## 15. Authentication & Authorization

- JWT tokens with 24-hour expiry (30 days for remember-me)
- Bearer token in Authorization header
- Guest access support (anonymous browsing with authenticated upgrade)
- RBAC: require_auth(), require_role(), require_permission(), require_admin()
- **Known issue:** Hardcoded JWT secret fallback (critical security vulnerability)
- **Known issue:** `require_role` creates independent DB sessions (connection pool exhaustion risk)

---

## 16. Configuration

Environment variables (key ones):

| Variable | Purpose | Default |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | postgresql://... |
| `JWT_SECRET_KEY` | JWT signing key | (hardcoded fallback — vulnerability) |
| `AI_PROVIDER` | Which AI to use | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required if gemini |
| `OPENAI_API_KEY` | OpenAI API key | Required if openai |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required if anthropic |
| `AI_TEMPERATURE` | Generation temperature | 0.7 |
| `AI_MAX_TOKENS` | Max output tokens | 8192 |
| `AI_TIMEOUT` | Request timeout (seconds) | 60 |
| `AI_MAX_RETRIES` | Max retry attempts | 3 |
| `AI_FALLBACK_CHAIN` | Fallback provider order | (none) |
| `AI_CACHE_ENABLED` | Enable response caching | true |
| `AI_CACHE_TTL` | Cache TTL in seconds | 3600 |
| `AI_CACHE_MAX_ENTRIES` | Max cache entries | 1000 |
| `AI_MAX_INPUT_TOKENS` | Per-request input limit | 8000 |
| `AI_USER_DAILY_TOKEN_LIMIT` | Per-user daily limit | 100000 |
| `AI_USER_MONTHLY_TOKEN_LIMIT` | Per-user monthly limit | 1000000 |

---

## 17. Testing State

### SPEC-003 Tests

| Test File | Count | Status |
|-----------|-------|--------|
| `test_intelligence_pipeline.py` | 38 | PASSING |
| `test_intelligence_pipeline_service.py` | 128 | PASSING |
| `test_intelligence_pipeline_repositories.py` | 14 | PASSING |
| `test_intelligence_pipeline_schemas.py` | 22 | PASSING |
| `test_intelligence_pipeline_models.py` | 20 | PASSING |
| `test_intelligence_pipeline_types.py` | 13 | PASSING |
| `test_intelligence_pipeline_migration.py` | 14 | PASSING |
| `test_pipeline_router.py` | 8 | PASSING |
| **Total SPEC-003** | **269** | **PASSING** |

### SPEC-002 Tests

| Test File | Count | Status |
|-----------|-------|--------|
| `test_prompt_intelligence_v2_*.py` | 180 | PASSING |
| `test_prompt_intelligence_validation.py` | 68 | PASSING |
| `test_prompt_intelligence_snapshots.py` | 42 | PASSING |
| `test_task_2_5_integration.py` | 21 | PASSING |
| Other SPEC-002 tests | 60 | PASSING |
| **Total SPEC-002** | **371** | **PASSING** |

### Pre-existing Failures

| Category | Count | Root Cause |
|----------|-------|------------|
| Auth tests | ~15 | Hardcoded JWT secret, missing env vars |
| Config tests | ~8 | Missing system config seed data |
| Metrics middleware | ~15 | `_extract_router` bug in MetricsMiddleware |
| Other | ~10 | Various pre-existing issues |
| **Total pre-existing** | **48** | **Unrelated to SPEC-001/SPEC-002** |

---

## 18. Known Gaps & Risks

### Architectural Gaps

| Gap | Severity | Description |
|-----|----------|-------------|
| Resume/CoverLetter generators use hardcoded prompts | MEDIUM | Bypass Prompt Intelligence, changes require code deployment |
| CareerEngine depends on legacy Knowledge Engine | MEDIUM | Dead dependency, keyword-only retrieval |
| No backend job queue | MEDIUM | Multi-step operations block the request |
| Non-pipeline paths bypass validation | LOW | Standalone AI Execution endpoints skip AI Response Intelligence |
| `ats.py` calls UniversalAI directly | LOW | Bypasses prompt infrastructure for text improvement |

### Security Risks

| Risk | Severity | Description |
|------|----------|-------------|
| Hardcoded JWT secret fallback | CRITICAL | Anyone with source code can forge tokens |
| Inconsistent ownership checks | HIGH | Some endpoints skip `resume.user_id` validation |
| `require_role` creates DB sessions | MEDIUM | Connection pool exhaustion under load |

### Technical Debt

| Debt | Impact |
|------|--------|
| Legacy + Intelligence engines coexist | Confusion about which to use |
| No dependency injection | Services instantiate repositories directly, hard to test |
| In-memory cache/metrics/budgets | Lost on process restart |
| No integration tests for Intelligence engines | End-to-end behavior unvalidated |
| `prompt_templates.json` (old) vs v2 templates | Potential drift |

---

## 19. Files Read During Audit

### Documentation
- `01_BACKEND_NON_TECH.md` (248 lines)
- `02_BACKEND_TECHNICAL.md` (722 lines)
- `03_BACKEND_REALITY_CHECK.md` (802 lines)

### OpenSpec Design/Proposal/Tasks
- `openspec/changes/universal-ai-engine/design.md` (853 lines)
- `openspec/changes/universal-ai-engine/proposal.md` (135 lines)
- `openspec/changes/universal-ai-engine/tasks.md` (383 lines)
- `openspec/changes/prompt-intelligence/design.md` (482 lines)
- `openspec/changes/prompt-intelligence/proposal.md` (129 lines)
- `openspec/changes/prompt-intelligence/tasks.md` (199 lines)
- `openspec/changes/backend-architecture/proposal.md` (108 lines)
- `openspec/specs/architecture.md` (142 lines)
- `openspec/specs/backend-modules.md` (306 lines)

### Source Code
- `backend/app/services/ai/universal_service.py` (439 lines — full implementation)
- `backend/app/services/ai/` (directory listing — 13 files)
- `backend/app/services/prompt_intelligence_v2/` (directory listing — 9 files)
- `backend/app/services/` (directory listing — 31 entries)

### Exploration Agent Results
- Full services architecture analysis (all engines, dependencies, dead code)
- Prompt Intelligence v2 deep dive (all components, integration points)
- Resume/Cover Letter generator analysis (hardcoded prompts, bypass)
- Chat service analysis (v2 migration status)
- CareerEngine/AIOrchestrator analysis (dual mode, old PromptBuilder dependency)
- ATS router analysis (direct UniversalAI call)
- All 10 router analyses (endpoints, services called, orchestration patterns)

---

*End of architecture audit.*
