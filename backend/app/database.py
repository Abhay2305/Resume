import logging
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)

# PostgreSQL is the primary database
# Local development: postgresql://postgres:postgres@localhost:5432/resume_builder
# Production: Use DATABASE_URL environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/resume_builder"
)

# Adjust database URL for PostgreSQL (replace postgres:// with postgresql:// if needed for Heroku/Railway)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Connection pool settings for PostgreSQL
connect_args = {}
pool_settings = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_pre_ping": True,  # Verify connections before use
    "pool_recycle": 300,  # Recycle connections after 5 minutes
}

# SQLite fallback (for tests only)
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    pool_settings = {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    **pool_settings
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from .models import Base as ModelsBase
    ModelsBase.metadata.create_all(bind=engine)


def check_db_connection():
    """Check database connection health."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.debug("Database connection check failed: %s", e)
        return False
