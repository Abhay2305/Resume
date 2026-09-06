# Backend - AI Resume Builder API

## Overview

Enterprise-grade FastAPI backend for the Prompt Resume SaaS platform. Features AI-powered resume generation, cover letter creation, ATS scoring, and a career intelligence engine with knowledge-based retrieval.

## Tech Stack

- **Framework**: FastAPI 0.110+ with Uvicorn
- **ORM**: SQLAlchemy 2.0 (synchronous, declarative base)
- **Database**: PostgreSQL (primary), SQLite (tests only)
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **AI**: Google Gemini (primary), Mock provider (fallback)
- **PDF**: Playwright headless Chromium
- **Validation**: Pydantic v2

## Architecture

```
Frontend
    ↓
API Layer (FastAPI Routers)
    ↓
Business Services (CareerEngine, ChatService)
    ↓
AI Orchestrator (Knowledge → Prompt → AI → Rules)
    ↓
AI Provider Layer (Gemini, OpenAI, Mock)
    ↓
Database (SQLAlchemy ORM → PostgreSQL)
```

**Key Principle**: Never bypass layers. Business logic lives in services, routers stay lightweight, AI providers are swappable.

## Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, startup event, router registration
│   ├── database.py          # SQLAlchemy engine, SessionLocal, get_db dependency
│   ├── auth.py              # JWT creation, password hashing, get_current_user dependency
│   ├── schemas.py           # Pydantic request/response models
│   ├── seed.py              # Seeds 24 templates, 5 rules, roles, permissions, audit configs
│   ├── models/              # SQLAlchemy ORM models (domain-split)
│   │   ├── base.py          # Shared declarative Base
│   │   ├── mixins.py        # UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin
│   │   ├── identity.py      # User, Profile, Subscription, Payment, Session, Device, OAuth, RBAC, Org
│   │   ├── resume.py        # Resume, ResumeSection, ResumeVersion, Template
│   │   ├── ai.py            # CoverLetter, AIRequest, ResumeRule
│   │   ├── analytics.py     # ATSResult
│   │   ├── audit.py         # AuditLog, AuditConfig, AuditArchive, AuditExport
│   │   ├── error.py         # ErrorLog, ErrorCategory, ErrorResolution, ErrorArchive, ErrorOccurrence
│   │   ├── conversation.py  # ChatSession, ChatMessage, AudioRecording, Transcript
│   │   ├── knowledge.py     # KnowledgeSource, KnowledgeChunk, Embedding, KnowledgeRetrieval
│   │   ├── ai_registry.py   # AIModel registry
│   │   ├── settings.py      # ActivityLog
│   │   └── __init__.py      # Re-exports all models
│   ├── routers/             # API endpoint definitions
│   │   ├── auth.py          # POST /api/auth/register, /login, /google, GET /me
│   │   ├── resumes.py       # CRUD + AI generation for resumes
│   │   ├── cover_letters.py # CRUD + AI generation for cover letters
│   │   ├── templates.py     # GET /api/templates
│   │   ├── ats.py           # POST /api/ats/analyze, /improve-text
│   │   ├── career.py        # POST /api/v1/career/bullets, /summary, /cover-letter, /ats-optimize
│   │   ├── chat.py          # Chat session and message endpoints
│   │   ├── pdf.py           # POST /api/pdf/export
│   │   └── users.py         # Profile, subscription, billing endpoints
│   ├── services/            # Business logic layer
│   │   ├── ai_service.py    # ResumeGeneratorService, CoverLetterGeneratorService, ATSScoreService
│   │   ├── llm_service.py   # LLMProviderService (Gemini wrapper), PromptBuilderService
│   │   ├── career_engine.py # CareerEngine - high-level API orchestrating all sub-services
│   │   ├── ai_orchestrator.py # AIOrchestrator - Knowledge→Prompt→AI→Rules pipeline
│   │   ├── prompt_builder.py  # Structured prompt construction with Harvard rules
│   │   ├── rules_engine.py    # Resume validation (verbs, quantification, ATS, style)
│   │   ├── chat_service.py    # Chat session management with AI conversation
│   │   ├── pdf_service.py     # Playwright-based HTML→PDF conversion
│   │   ├── audit_service.py   # Audit logging operations
│   │   ├── error_service.py   # Error logging, categorization, resolution workflows
│   │   ├── storage_service.py # LocalStorageProvider (swappable to S3/R2)
│   │   ├── ai_providers/      # Provider abstraction layer
│   │   │   ├── base.py        # AIProvider ABC, ProviderConfig, ProviderResponse, errors
│   │   │   ├── factory.py     # create_provider(), create_default_provider()
│   │   │   ├── gemini_provider.py  # Google Gemini implementation
│   │   │   ├── openai_provider.py  # OpenAI stub (not fully implemented)
│   │   │   └── mock_provider.py    # Offline fallback for testing
│   │   └── knowledge/         # Knowledge retrieval engine
│   │       └── engine.py      # PDF extraction, domain classification, retrieval
│   ├── repositories/        # Data access layer (generic CRUD)
│   │   ├── base.py          # BaseRepository with CRUD operations
│   │   ├── audit.py         # AuditLogRepository, AuditConfigRepository
│   │   ├── error.py         # ErrorLogRepository, ErrorCategoryRepository
│   │   └── identity.py      # Identity-specific repositories
│   └── middleware/          # HTTP middleware
│       ├── audit.py         # AuditMiddleware - auto-logs all HTTP requests
│       └── error.py         # ErrorMiddleware - captures unhandled exceptions
├── tests/
│   ├── test_ai_providers.py
│   ├── test_career_engine.py
│   └── test_error_domain.py
├── migrations/              # Alembic migrations (future)
├── requirements.txt
├── Dockerfile
├── run.py                   # Entry point: uvicorn app.main:app
├── .env                     # Environment variables (not committed)
└── PLAN.md                  # Implementation roadmap
```

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_builder

# AI Provider
AI_PROVIDER=gemini          # gemini | mock
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.0-flash

# AI Tuning
AI_TEMPERATURE=0.7
AI_MAX_TOKENS=8192
AI_TIMEOUT=60.0
AI_MAX_RETRIES=3

# Auth
JWT_SECRET_KEY=your_jwt_secret
```

## Key Models

### Identity Domain
- **User**: email, hashed_password, full_name, is_active, is_verified, is_superuser, avatar_url, security fields (locked_until, failed_login_attempts)
- **Profile**: job_title, phone, location, website, linkedin, summary, company, industry
- **Subscription**: plan_type (free/pro/enterprise), status
- **Payment**: amount, currency, status
- **RBAC**: Role, Permission, UserRole, RolePermission
- **Organization**: name, slug, owner_id, members
- **Sessions**: UserSession, Device, LoginHistory, OAuthAccount

### Resume Domain
- **Resume**: user_id, title, template_id → has many ResumeSection, ResumeVersion, ATSResult
- **ResumeSection**: section_type (personalInfo/summary/experience/education/skills/projects/certifications/achievements), content (JSON), position
- **ResumeVersion**: version_number, content (JSON) - snapshot history
- **Template**: id, name, category (ATS/Corporate/Technology/Creative), color_scheme, layout_schema

### AI Domain
- **CoverLetter**: user_id, title, job_role, company_name, content
- **AIRequest**: user_id, request_type, prompt, response (logged per AI call)
- **ResumeRule**: category, rule_name, rule_prompt_instruction (seeded: verbs, quantify, first_person, punctuation, ats)

### Analytics Domain
- **ATSResult**: resume_id, score (0-100), details (JSON), recommendations (JSON)

### Audit Domain
- **AuditLog**: immutable, user_id, entity_type, entity_id, action, previous/new_state, IP, endpoint, timing
- **AuditConfig**: per-entity audit settings, retention, redaction rules

### Error Domain
- **ErrorLog**: error_type, fingerprint (SHA-256 for dedup), stack_trace, severity, status, retry tracking
- **ErrorResolution**: resolution_type, root_cause, fix_commit, prevention_notes
- **ErrorOccurrence**: frequency tracking for same error

### Conversation Domain
- **ChatSession**: user_id, title, status, resume_id
- **ChatMessage**: session_id, role (user/assistant/system), content, sequence
- **AudioRecording**, **Transcript**: future voice flow

### Knowledge Domain
- **KnowledgeSource**: title, source, ingestion_status
- **KnowledgeChunk**: source_id, content, token_count
- **Embedding**: chunk_id, vector, backend (sqlite/pgvector/faiss/qdrant)
- **KnowledgeRetrieval**: links generation to chunks used, with score/rank

## API Endpoints

### Authentication (`/api/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Create account + profile + free subscription |
| POST | `/login` | Email/password login → JWT |
| POST | `/google` | Google OAuth login |
| GET | `/me` | Get current user |

### Resumes (`/api/resume`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/create` | Create empty resume (guest support) |
| GET | `/list` | List user's resumes |
| GET | `/{resume_id}` | Get resume with sections |
| PUT | `/{resume_id}` | Update title/template |
| DELETE | `/{resume_id}` | Delete resume |
| POST | `/generate` | AI-generate full resume from prompt |
| PUT | `/{resume_id}/sections` | Bulk update sections + version snapshot |

### Cover Letters (`/api/cover-letter`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/generate` | AI-generate cover letter |
| GET | `/list` | List user's cover letters |
| GET | `/{cl_id}` | Get cover letter |
| PUT | `/{cl_id}` | Update cover letter |
| DELETE | `/{cl_id}` | Delete cover letter |

### ATS (`/api/ats`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze/{resume_id}` | Score resume 0-100 with recommendations |
| POST | `/improve-text` | AI improve/shorten/expand/autofix text |

### Career Intelligence (`/api/v1/career`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/bullets` | Generate resume bullets (full pipeline) |
| POST | `/summary` | Generate professional summary |
| POST | `/cover-letter` | Generate cover letter |
| POST | `/bullet-feedback` | Review and improve a bullet |
| POST | `/ats-optimize` | Optimize for ATS systems |
| GET | `/knowledge/stats` | Knowledge base statistics |
| GET | `/health` | Health check |

### Chat (`/api/chat`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/sessions` | Create chat session |
| GET | `/sessions` | List user's sessions |
| GET | `/sessions/{id}` | Get session |
| GET | `/sessions/{id}/messages` | Get messages |
| POST | `/sessions/{id}/messages` | Send message → AI response |
| DELETE | `/sessions/{id}` | Delete session |
| POST | `/sessions/{id}/close` | Close session |

### Templates (`/api/templates`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | List all 24 templates |
| GET | `/{template_id}` | Get template by ID |

### PDF Export (`/api/pdf`)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/export` | HTML → PDF via Playwright |

### Users (`/api/user`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update profile |
| GET | `/subscription` | Get subscription |
| POST | `/subscription/upgrade` | Upgrade plan |
| GET | `/billing/history` | Payment history |

## Career Engine Pipeline

The CareerEngine orchestrates the full AI generation pipeline:

```
User Input (role info, job description)
        ↓
Knowledge Engine (retrieve PDF guidance from knowledge base)
        ↓
Prompt Builder (structured prompts with Harvard rules)
        ↓
AI Provider (Gemini/Mock generates content)
        ↓
Rules Engine (validate bullets: action verbs, quantification, no first-person)
        ↓
PipelineResult (content + validation + metrics)
```

**AI Orchestrator** (`ai_orchestrator.py`) coordinates:
1. Knowledge retrieval from PDFs
2. Prompt construction with domain knowledge
3. AI provider call
4. Response parsing
5. Rules validation

**Rules Engine** validates:
- Bullet starts with strong action verb
- No weak verbs (helped, worked, responsible for)
- Technology stack mentioned
- Quantifiable impact included
- No vague phrases (team player, results-driven)
- No first-person pronouns
- Bullet under 200 chars
- No special characters (ATS)

## Guest Access

The backend supports guest-first workflows:
- Guests can create resumes (limited to 2)
- Guests can use AI generation and ATS analysis
- Guests can chat with AI advisor
- Guest data stored with `user_id="guest"` sentinel
- No authentication required for guest operations

## Subscription Tiers

| Plan | Resumes | Cover Letters | AI Features |
|------|---------|---------------|-------------|
| Free | 1 | Limited | Basic |
| Pro ($29) | Unlimited | Unlimited | Enhanced |
| Enterprise ($99) | Unlimited | Unlimited | Full |

## Seeded Data

On startup, the system seeds:
- **24 Templates**: 6 ATS, 6 Corporate, 6 Technology, 6 Creative
- **5 Resume Rules**: verbs, quantify, first_person, punctuation, ats
- **5 System Roles**: admin, user, premium, viewer, organization_admin
- **16 Permissions**: resume/cover_letter CRUD, AI, billing, admin, org
- **Role-Permission mappings**: admin=all, user=basic, premium=user+unlimited_ai, viewer=read-only
- **12 Audit Configs**: per-entity audit settings with retention policies
- **12 Error Categories**: Authentication, Authorization, Validation, Database, API, AI Service, etc.

## Running

```bash
# Development
pip install -r requirements.txt
playwright install chromium
python run.py

# Docker
docker build -t resume-backend .
docker run -p 8000:8000 -e DATABASE_URL=... -e GEMINI_API_KEY=... resume-backend
```

## Testing

```bash
pytest tests/
```

## Key Design Decisions

1. **Provider-agnostic AI**: All AI calls go through `AIProvider` abstraction. Swap Gemini/OpenAI/Mock by changing env var.
2. **Knowledge before generation**: PDF knowledge is retrieved before every AI call. LLM is the writing engine, not the source of truth.
3. **Rules validation**: All generated content is validated against Harvard resume rules before returning.
4. **Domain-split models**: 30+ tables organized by bounded context (identity, resume, audit, error, conversation, knowledge).
5. **Generic repository pattern**: `BaseRepository` provides CRUD; domain repos extend with specific queries.
6. **Middleware stack**: AuditMiddleware logs all requests, ErrorMiddleware captures exceptions. Both fire-and-forget to avoid blocking.
7. **Guest-first**: Most features work without authentication. User data isolated by user_id.
8. **Version snapshots**: Every section update creates a ResumeVersion for history/undo.
