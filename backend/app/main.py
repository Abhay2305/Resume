import logging
import os
import traceback
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .database import engine, init_db, check_db_connection
from .models import Base
from .seed import seed_db
from .context import get_request_id, get_user_id
from .exceptions import ApplicationException, ErrorDetail
from .notifications import notify_critical_error

logger = logging.getLogger(__name__)

# Import routers
from .routers import auth, resumes, cover_letters, ats, users, pdf, career, chat, opportunities, resume_intelligence, gap_analysis, knowledge_intelligence, prompt_intelligence, ai_execution, ai_response_intelligence, health, procs_users, procs_resumes, procs_dashboard, config, admin_auth, rbac, audit, metrics, errors, ai_monitoring, analytics, procs_templates, pipeline

# Import middleware
from .middleware import AuditContextMiddleware, AuditMiddleware, ErrorMiddleware, ErrorHandlerMiddleware, MetricsMiddleware, SecurityHeadersMiddleware
from .middleware.rate_limit import RateLimitMiddleware

# Import AI service for startup validation
from .services.ai_service import validate_provider_config, log_provider_info, ConfigurationError


def _startup():
    """Synchronous startup logic: DB init, schema, seeding, AI provider validation."""
    logger.info("Starting up FastAPI application...")

    # Validate AI provider configuration (fail fast)
    try:
        ai_config = validate_provider_config()
        log_provider_info(ai_config)
    except ConfigurationError as e:
        logger.error("FATAL: AI Provider configuration error: %s", e)
        raise
    except Exception as e:
        logger.error("FATAL: Unexpected error validating AI configuration: %s", e)
        raise

    try:
        if not check_db_connection():
            logger.warning("Database connection failed. Check DATABASE_URL.")
            return

        db_url = str(engine.url)
        if db_url.startswith("postgresql"):
            logger.info("Connected to PostgreSQL: %s:%s/%s", engine.url.host, engine.url.port, engine.url.database)
        elif db_url.startswith("sqlite"):
            logger.info("Connected to SQLite: %s", db_url)
        else:
            logger.info("Connected to database: %s", db_url)

        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verified.")
        seed_db()
    except Exception as e:
        logger.error("Database initialization failed: %s", e)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Modern FastAPI lifespan context manager (replaces on_event)."""
    _startup()

    # Initialize MetricsService singleton
    from .database import SessionLocal
    from .repositories.metric import MetricRepository
    from .services.metrics_service import MetricsService

    db = SessionLocal()
    try:
        metric_repo = MetricRepository(db)
        metrics_service = MetricsService(db, metric_repo)
        application.state.metrics_service = metrics_service
        metrics_service.start_flush_thread()
        logger.info("MetricsService initialized and flush thread started")
    except Exception as e:
        logger.error("Failed to initialize MetricsService: %s", e)
        application.state.metrics_service = None

    yield

    # Shutdown: stop flush thread
    if hasattr(application.state, "metrics_service") and application.state.metrics_service:
        application.state.metrics_service.stop_flush_thread()
        logger.info("MetricsService shut down")
    try:
        db.close()
    except Exception:
        pass


app = FastAPI(
    title="Prompt Resume SaaS Builder API",
    description="Enterprise-grade resume writing assistant, cover letter generator, and ATS scoring engine API.",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Global Exception Handlers
# ---------------------------------------------------------------------------

@app.exception_handler(ApplicationException)
async def application_exception_handler(request: Request, exc: ApplicationException):
    """Handle ApplicationException with standardized response."""
    request_id = get_request_id()
    exc.request_id = request_id
    response = exc.to_dict()
    response["success"] = False
    logger.warning(
        "ApplicationException [%s] %s %s - %s (request_id=%s)",
        exc.code,
        request.method,
        request.url.path,
        exc.message,
        request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Standardize FastAPI validation errors to match ApplicationException format."""
    request_id = get_request_id()
    errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        field = " -> ".join(str(part) for part in loc)
        msg = error.get("msg", "Invalid value")
        errors.append({"field": field, "message": msg})
    response = {
        "success": False,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Validation failed",
            "details": {},
            "errors": errors,
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    return JSONResponse(
        status_code=422,
        content=response,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardize FastAPI HTTPException responses."""
    request_id = get_request_id()
    response = {
        "success": False,
        "error": {
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "details": {},
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    logger.warning(
        "HTTPException [%d] %s %s (request_id=%s)",
        exc.status_code,
        request.method,
        request.url.path,
        request_id,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response,
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    request_id = get_request_id()
    user_id = get_user_id()
    logger.error(
        "SQLAlchemyError %s %s - %s (request_id=%s, user_id=%s)\n%s",
        request.method,
        request.url.path,
        str(exc),
        request_id,
        user_id,
        traceback.format_exc(),
    )
    notify_critical_error(
        error_code="DATABASE_ERROR",
        message=str(exc),
        endpoint=request.url.path,
        http_method=request.method,
        request_id=request_id,
        user_id=user_id,
        status_code=500,
    )
    response = {
        "success": False,
        "error": {
            "code": "DATABASE_ERROR",
            "message": "A database error occurred",
            "details": {},
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    return JSONResponse(
        status_code=500,
        content=response,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unexpected exceptions."""
    request_id = get_request_id()
    user_id = get_user_id()
    logger.error(
        "UnhandledException %s %s - %s (request_id=%s, user_id=%s)\n%s",
        request.method,
        request.url.path,
        str(exc),
        request_id,
        user_id,
        traceback.format_exc(),
    )

    notify_critical_error(
        error_code="INTERNAL_ERROR",
        message=str(exc),
        endpoint=request.url.path,
        http_method=request.method,
        request_id=request_id,
        user_id=user_id,
        status_code=500,
    )
    response = {
        "success": False,
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    return JSONResponse(
        status_code=500,
        content=response,
    )


# Configure CORS for Vite frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # PROCS frontend
    "http://127.0.0.1:5174",  # PROCS frontend
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register middleware in correct order (last added = first executed)
# 1. ErrorHandlerMiddleware - catches unhandled exceptions (outermost)
# 2. ErrorMiddleware - captures errors for logging
# 3. AuditMiddleware - logs all HTTP requests
# 4. MetricsMiddleware - records request metrics (fire-and-forget)
# 5. SecurityHeadersMiddleware - adds security headers to responses
# 6. AuditContextMiddleware - extracts user context from JWT (innermost)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(ErrorMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditContextMiddleware)

# Rate limiting middleware (login: 5/min, register: 3/min, auth: 10/min, default: 100/min)
app.add_middleware(
    RateLimitMiddleware,
    default_max_requests=100,
    default_window_seconds=60,
    auth_max_requests=10,
    auth_window_seconds=60,
    login_max_requests=5,
    login_window_seconds=60,
    register_max_requests=3,
    register_window_seconds=60,
)

# Register routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(cover_letters.router, prefix="/api")
app.include_router(ats.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(pdf.router, prefix="/api")
app.include_router(career.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(opportunities.router, prefix="/api")
app.include_router(resume_intelligence.router, prefix="/api")
app.include_router(gap_analysis.router, prefix="/api")
app.include_router(knowledge_intelligence.router, prefix="/api")
app.include_router(prompt_intelligence.router, prefix="/api")
app.include_router(ai_execution.router, prefix="/api")
app.include_router(ai_response_intelligence.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(procs_users.router, prefix="/api/procs")
app.include_router(procs_resumes.router, prefix="/api/procs")
app.include_router(procs_dashboard.router, prefix="/api/procs")
app.include_router(config.router, prefix="/api")
app.include_router(admin_auth.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(errors.router, prefix="/api")
app.include_router(rbac.router, prefix="/api")
app.include_router(ai_monitoring.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(procs_templates.router, prefix="/api/procs")
app.include_router(pipeline.router, prefix="/api")

# Mount static file serving for uploaded template assets
import os
from fastapi.staticfiles import StaticFiles

_storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
os.makedirs(_storage_dir, exist_ok=True)
app.mount("/storage", StaticFiles(directory=_storage_dir), name="storage")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Prompt Resume SaaS API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
