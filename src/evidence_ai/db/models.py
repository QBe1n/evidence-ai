"""SQLAlchemy ORM models for EvidenceAI.

Database schema:
  reviews       — Systematic review jobs and results
  documents     — Ingested literature documents
  evidence      — Extracted evidence relationships
  users         — User accounts (if self-hosted)

All timestamps are stored in UTC.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from evidence_ai.db.database import Base


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(Base, TimestampMixin):
    """User account for the EvidenceAI platform."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)

    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")


class Review(Base, TimestampMixin):
    """A systematic review job and its results."""

    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. "rev_a1b2c3d4"
    user_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=True, index=True
    )

    # Input
    question: Mapped[str] = mapped_column(Text, nullable=False)
    databases: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    max_results: Mapped[int] = mapped_column(Integer, default=500)
    request_params: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="queued", index=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Progress tracking
    papers_found: Mapped[int | None] = mapped_column(Integer, nullable=True)
    papers_screened: Mapped[int | None] = mapped_column(Integer, nullable=True)
    papers_included: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    stages_completed: Mapped[list] = mapped_column(JSONB, default=list)

    # Results
    level_of_evidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    effect_direction: Mapped[str | None] = mapped_column(String(50), nullable=True)
    coe_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_findings: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    full_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User | None"] = relationship("User", back_populates="reviews")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="review")
    evidence_items: Mapped[list["EvidenceItem"]] = relationship(
        "EvidenceItem", back_populates="review"
    )

    def __repr__(self) -> str:
        return f"<Review id={self.id!r} status={self.status!r}>"


class Document(Base, TimestampMixin):
    """An ingested literature document."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    review_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("reviews.id"), nullable=True, index=True
    )

    # Identification
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    pmid: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    doi: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nct_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)

    # Content
    title: Mapped[str] = mapped_column(Text, nullable=False)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    authors: Mapped[list] = mapped_column(JSONB, default=list)
    journal: Mapped[str | None] = mapped_column(String(500), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    study_design: Mapped[str | None] = mapped_column(String(50), nullable=True)
    participant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    publication_types: Mapped[list] = mapped_column(JSONB, default=list)
    mesh_terms: Mapped[list] = mapped_column(JSONB, default=list)

    # PICO extraction results
    pico_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    review: Mapped["Review | None"] = relationship("Review", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document pmid={self.pmid!r} title={self.title[:40]!r}>"


class EvidenceItem(Base, TimestampMixin):
    """An extracted evidence relationship from a document."""

    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    review_id: Mapped[str | None] = mapped_column(
        String(50), ForeignKey("reviews.id"), nullable=True, index=True
    )
    document_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("documents.id"), nullable=True, index=True
    )

    # Extracted relationship
    pmid: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    exposure: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    effect_direction: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    significance: Mapped[str] = mapped_column(String(50), nullable=False)
    study_design: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    participant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)

    # Triangulation eligibility
    is_triangulation_eligible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    exposure_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    outcome_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    review: Mapped["Review | None"] = relationship("Review", back_populates="evidence_items")

    def __repr__(self) -> str:
        return (
            f"<EvidenceItem pmid={self.pmid!r} "
            f"direction={self.effect_direction!r} "
            f"eligible={self.is_triangulation_eligible}>"
        )
