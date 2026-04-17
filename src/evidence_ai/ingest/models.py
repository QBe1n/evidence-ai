"""Pydantic models for ingested documents.

These models represent the raw output of the ingest stage before PICO
extraction. They are passed to the extract stage as input.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class DocumentSource(str, Enum):
    """Source database for an ingested document."""

    PUBMED = "pubmed"
    CLINICALTRIALS = "clinicaltrials"
    FDA = "fda"
    PREPRINT = "preprint"


class StudyDesign(str, Enum):
    """Study design classification used throughout the pipeline."""

    RCT = "RCT"                # Randomized Controlled Trial
    META = "META"              # Meta-analysis
    SR = "SR"                  # Systematic Review
    OS = "OS"                  # Observational Study
    MR = "MR"                  # Mendelian Randomization
    REVIEW = "REVIEW"          # Narrative Review
    CASE_SERIES = "CASE_SERIES"
    CASE_REPORT = "CASE_REPORT"
    OTHER = "OTHER"


class AbstractSection(BaseModel):
    """A single structured section of an abstract (Background, Methods, etc.)."""

    label: str = Field(description="Section label, e.g. 'BACKGROUND', 'METHODS'")
    text: str = Field(description="Section text content")


class MeshTerm(BaseModel):
    """A MeSH (Medical Subject Headings) term from PubMed."""

    descriptor: str = Field(description="MeSH descriptor name")
    is_major: bool = Field(default=False, description="Whether this is a major MeSH topic")
    qualifiers: list[str] = Field(default_factory=list, description="MeSH subheadings")


class IngestedDocument(BaseModel):
    """A single document ingested from any supported database.

    This is the canonical input to the Extract stage.
    """

    # Identification
    source: DocumentSource
    source_id: str = Field(description="Primary ID in source system (PMID, NCT ID, etc.)")
    pmid: str | None = Field(default=None, description="PubMed ID if available")
    doi: str | None = Field(default=None, description="Digital Object Identifier")
    nct_id: str | None = Field(default=None, description="ClinicalTrials.gov NCT number")

    # Content
    title: str
    abstract: str | None = None
    abstract_sections: list[AbstractSection] = Field(
        default_factory=list,
        description="Structured abstract sections if available",
    )
    full_text_url: HttpUrl | None = None

    # Metadata
    authors: list[str] = Field(default_factory=list)
    journal: str | None = None
    publication_date: date | None = None
    publication_types: list[str] = Field(
        default_factory=list,
        description="PubMed publication types, e.g. 'Randomized Controlled Trial'",
    )
    mesh_terms: list[MeshTerm] = Field(default_factory=list)
    study_design: StudyDesign | None = None

    # Statistics
    participant_count: int | None = None
    comment_count: int = Field(
        default=0,
        description="Number of comments/corrections (from PubMed; signals controversy)",
    )

    # Pipeline metadata
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw source data for debugging and provenance",
        exclude=True,
    )

    @property
    def full_abstract_text(self) -> str:
        """Return the full abstract text, concatenating sections if needed."""
        if self.abstract:
            return self.abstract
        if self.abstract_sections:
            return " ".join(
                f"{s.label}: {s.text}" for s in self.abstract_sections
            )
        return ""

    @property
    def is_rct(self) -> bool:
        """Return True if document is classified as an RCT."""
        if self.study_design == StudyDesign.RCT:
            return True
        rct_types = {"Randomized Controlled Trial", "Clinical Trial, Phase III", "Clinical Trial"}
        return bool(rct_types.intersection(set(self.publication_types)))

    model_config = {"use_enum_values": True}


class IngestResult(BaseModel):
    """Aggregated result from an ingest operation across one or more databases."""

    query: str
    databases_searched: list[DocumentSource]
    documents: list[IngestedDocument]
    total_found: int = Field(description="Total matching records in the database(s)")
    total_returned: int = Field(description="Number of records actually returned")
    search_date: datetime = Field(default_factory=datetime.utcnow)
    errors: list[str] = Field(default_factory=list)

    @property
    def pubmed_docs(self) -> list[IngestedDocument]:
        """Return only PubMed-sourced documents."""
        return [d for d in self.documents if d.source == DocumentSource.PUBMED]

    @property
    def trial_docs(self) -> list[IngestedDocument]:
        """Return only ClinicalTrials.gov documents."""
        return [d for d in self.documents if d.source == DocumentSource.CLINICALTRIALS]
