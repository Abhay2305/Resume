"""Knowledge domain models (new in Phase 2).

The persistence layer for the future Knowledge Engine / RAG pipeline. A
knowledge source (e.g. the Harvard guide PDF) is chunked into many chunks; each
chunk has one embedding. Retrievals link an AI generation to the chunks it
actually used, with score and rank, so retrieval decisions are debuggable.

IMPORTANT: the ``embeddings.vector`` column stores the raw vector for the
development SQLite backend only. The application MUST access embeddings through
the EmbeddingStore abstraction (see app/repositories/embedding_store.py); the
storage backend is swappable to pgvector / FAISS / Qdrant by adding one
implementation, without touching callers or this schema.
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    MetadataMixin,
    SoftDeleteMixin,
)


class KnowledgeSource(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """A source document for the knowledge base (e.g. a university resume guide).

    Rich metadata is captured up front; the ingestion pipeline (future) fills in
    ``ingestion_status`` / ``ingested_at`` and creates the chunks.
    """

    __tablename__ = "knowledge_sources"

    title = Column(String(512), nullable=False)
    source = Column(String(512), nullable=True)  # filename / URL / origin
    university = Column(String(255), nullable=True)
    version = Column(String(50), nullable=True)
    language = Column(String(20), nullable=True, default="en")
    document_type = Column(String(100), nullable=True)  # guide|examples|ats_guide|book
    checksum = Column(String(128), nullable=True)  # content hash for dedupe/change detection
    ingestion_status = Column(
        String(50), nullable=False, default="pending"
    )  # pending|processing|ingested|failed
    ingested_at = Column(String(64), nullable=True)

    chunks = relationship(
        "KnowledgeChunk", back_populates="source", cascade="all, delete-orphan"
    )


class KnowledgeChunk(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """A retrievable text chunk extracted from a knowledge source."""

    __tablename__ = "knowledge_chunks"

    source_id = Column(
        String(36),
        ForeignKey("knowledge_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False, default=0)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)

    source = relationship("KnowledgeSource", back_populates="chunks")
    embedding = relationship(
        "Embedding",
        back_populates="chunk",
        uselist=False,
        cascade="all, delete-orphan",
    )
    retrievals = relationship(
        "KnowledgeRetrieval", back_populates="chunk", cascade="all, delete-orphan"
    )


class Embedding(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """Vector embedding for a knowledge chunk.

    The ``vector`` column is the development (SQLite) storage location. Access is
    mediated by the EmbeddingStore abstraction so the backend can be swapped to
    pgvector/FAISS/Qdrant later by changing one implementation only.
    """

    __tablename__ = "embeddings"

    chunk_id = Column(
        String(36),
        ForeignKey("knowledge_chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    model_id = Column(
        String(36), ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True
    )
    dim = Column(Integer, nullable=True)
    vector = Column(JSON, nullable=True)  # dev backend only; abstracted by EmbeddingStore
    backend = Column(String(50), nullable=False, default="sqlite")  # sqlite|pgvector|faiss|qdrant

    chunk = relationship("KnowledgeChunk", back_populates="embedding")


class KnowledgeRetrieval(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, Base
):
    """Records that a given AI generation retrieved a given chunk.

    Links a generation to each chunk it used, with similarity ``score`` and
    ``rank``, so retrieval quality is independently debuggable.
    """

    __tablename__ = "knowledge_retrievals"

    generation_id = Column(
        String(36),
        ForeignKey("ai_generations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_id = Column(
        String(36),
        ForeignKey("knowledge_chunks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score = Column(Float, nullable=True)
    rank = Column(Integer, nullable=True)

    chunk = relationship("KnowledgeChunk", back_populates="retrievals")
    generation = relationship("AIGeneration", back_populates="retrievals")
