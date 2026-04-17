"""API request and response schemas.

All request/response objects are defined as Pydantic models here,
separate from the internal domain models. This allows the API contract
to evolve independently of the internal representation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class DatabaseChoice(str, Enum):
    """Available literature databases for search."""

    PUBMED = "pubmed"
    CLINICALTRIALS = "clinicaltrials"
    FDA = "fda"


class StudyDesignChoice(str, Enum):
    """Study design filters."""

    RCT = "RCT"
    META = "META"
    SR = "SR"
    OS = "OS"
    MR = "MR"


class ReviewStatus(str, Enum):
    """Status of a systematic review job."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ── Request schemas ────────────────────────────────────────────────────────────

class DateRange(BaseModel):
    """Date range filter for literature search."""

    start: str = Field(
        default="2000-01-01",
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end: str = Field(
        default="2025-12-31",
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class CreateReviewRequest(BaseModel):
    """Request body for creating a new systematic review."""

    question: str = Field(
        description="The clinical question in free text.",
        min_length=10,
        max_length=1000,
        examples=[
            "Does semaglutide reduce cardiovascular mortality in type 2 diabetes patients?"
        ],
    )
    databases: list[DatabaseChoice] = Field(
        default=[DatabaseChoice.PUBMED, DatabaseChoice.CLINICALTRIALS],
        description="Databases to search.",
    )
    date_range: DateRange | None = Field(
        default=None,
        description="Optional publication date range filter.",
    )
    study_designs: list[StudyDesignChoice] | None = Field(
        default=None,
        description="Optional study design filter. If None, all designs are included.",
    )
    max_results: int = Field(
        default=500,
        description="Maximum number of papers to ingest.",
        ge=10,
        le=10000,
    )
    include_augmentation: bool = Field(
        default=False,
        description="Whether to run the TrialSynth augmentation stage.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Does SGLT2 inhibition reduce hospitalization for heart failure?",
                "databases": ["pubmed", "clinicaltrials"],
                "date_range": {"start": "2015-01-01", "end": "2025-12-31"},
                "study_designs": ["RCT", "META"],
                "max_results": 500,
            }
        }
    }


class SearchRequest(BaseModel):
    """Request body for evidence base search."""

    query: str = Field(
        description="Free-text search query.",
        min_length=3,
        max_length=500,
    )
    limit: int = Field(default=20, ge=1, le=100)
    databases: list[DatabaseChoice] = Field(
        default=[DatabaseChoice.PUBMED],
    )


# ── Response schemas ───────────────────────────────────────────────────────────

class ReviewCreatedResponse(BaseModel):
    """Response returned when a new review job is created."""

    review_id: str
    status: ReviewStatus = ReviewStatus.QUEUED
    estimated_minutes: int
    job_url: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "review_id": "rev_a1b2c3d4",
                "status": "queued",
                "estimated_minutes": 12,
                "job_url": "/api/v1/status/rev_a1b2c3d4",
            }
        }
    }


class ReviewStatusResponse(BaseModel):
    """Status response for an in-progress or completed review."""

    review_id: str
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime
    question: str | None = None
    stages_completed: list[str] = Field(default_factory=list)
    papers_found: int | None = None
    papers_included: int | None = None
    level_of_evidence: float | None = None
    effect_direction: str | None = None
    confidence: str | None = None
    error_message: str | None = None


class CoEScoresResponse(BaseModel):
    """Convergence of Evidence scores."""

    p_excitatory: float
    p_no_change: float
    p_inhibitory: float
    dominant_direction: str


class ReviewResultResponse(BaseModel):
    """Complete review result response."""

    review_id: str
    question: str
    status: ReviewStatus
    level_of_evidence: float
    loe_label: str
    effect_direction: str
    coe_scores: CoEScoresResponse
    summary: str
    key_findings: list[str]
    papers_screened: int
    papers_included: int
    generated_at: datetime


class EvidenceSearchResult(BaseModel):
    """A single search result from the evidence base."""

    pmid: str | None = None
    title: str
    authors: list[str] = Field(default_factory=list)
    journal: str | None = None
    year: int | None = None
    abstract_snippet: str
    relevance_score: float
    study_design: str | None = None
    source_url: str | None = None


class SearchResponse(BaseModel):
    """Response from evidence base search."""

    query: str
    total_results: int
    results: list[EvidenceSearchResult]


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] | None = None
