import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .seed import seed_db

# Import routers
from .routers import auth, resumes, cover_letters, templates, ats, users, pdf

app = FastAPI(
    title="Prompt Resume SaaS Builder API",
    description="Enterprise-grade resume writing assistant, cover letter generator, and ATS scoring engine API.",
    version="1.0.0"
)

# Configure CORS for Vite frontend
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"  # Fallback for deployment
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Automated DB initialization and seeding on startup
@app.on_event("startup")
def startup_event():
    print("Starting up FastAPI application...")
    try:
        # Create database tables if they do not exist
        Base.metadata.create_all(bind=engine)
        print("Database schema verified.")
        # Seed standard rules and 24 templates
        seed_db()
    except Exception as e:
        print(f"Database initialization failed: {e}")

# Register routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(cover_letters.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(ats.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(pdf.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Prompt Resume SaaS API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
