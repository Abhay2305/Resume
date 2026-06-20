"""Conversation domain models (new in Phase 2).

The persistence backbone for the future chat-first experience. A user holds
many chat sessions; a session holds an ordered stream of messages; messages may
have an associated audio recording, and a recording has one transcript.

All tables are new and additive. They use the shared future-proof mixins so
they can evolve without repeated redesigns.
"""
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .mixins import (
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    MetadataMixin,
    SoftDeleteMixin,
)


class ChatSession(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """A single conversation between a user and the assistant."""

    __tablename__ = "chat_sessions"

    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="active")  # active|archived|closed
    # Optional link to the resume this conversation is building/editing.
    resume_id = Column(
        String(36), ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.sequence",
    )


class ChatMessage(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """A single message in a chat session.

    ``role`` follows the conventional user|assistant|system taxonomy. ``sequence``
    gives a stable in-session ordering independent of timestamp resolution.
    """

    __tablename__ = "chat_messages"

    session_id = Column(
        String(36),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # user|assistant|system
    content = Column(Text, nullable=True)
    sequence = Column(Integer, nullable=False, default=0)
    # If this message originated an AI run, it can be traced via ai_requests.
    ai_request_id = Column(
        String(36), ForeignKey("ai_requests.id", ondelete="SET NULL"), nullable=True
    )

    session = relationship("ChatSession", back_populates="messages")
    audio_recording = relationship(
        "AudioRecording",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AudioRecording(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """A captured audio input (future voice flow). Binary lives in object storage;
    only a reference/URI and descriptive metadata are stored here."""

    __tablename__ = "audio_recordings"

    message_id = Column(
        String(36),
        ForeignKey("chat_messages.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    storage_uri = Column(String(1024), nullable=True)  # path/URI via StorageProvider
    mime_type = Column(String(100), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending|stored|failed

    message = relationship("ChatMessage", back_populates="audio_recording")
    transcript = relationship(
        "Transcript",
        back_populates="audio_recording",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Transcript(
    UUIDPrimaryKeyMixin, TimestampMixin, MetadataMixin, SoftDeleteMixin, Base
):
    """Text transcription of an audio recording (future speech-to-text)."""

    __tablename__ = "transcripts"

    audio_recording_id = Column(
        String(36),
        ForeignKey("audio_recordings.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    text = Column(Text, nullable=True)
    language = Column(String(20), nullable=True)
    provider = Column(String(100), nullable=True)
    confidence = Column(String(20), nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending|done|failed

    audio_recording = relationship("AudioRecording", back_populates="transcript")
