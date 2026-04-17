"""Pydantic models for PICO extraction results."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class SpanLabel(str, Enum):
    """Entity type for a PICO span."""

    POPULATION = "P"
    INTERVENTION = "I"
    COMPARATOR = "C"
    OUTCOME = "O"


class EntitySpan(BaseModel):
    """A single extracted entity span from an abstract.

    Represents a text span identified as a Population, Intervention,
    Comparator, or Outcome entity.
    """

    text: str = Field(description="The extracted text span")
    start: int = Field(description="Character start offset in the source text")
    end: int = Field(description="Character end offset in the source text")
    label: SpanLabel = Field(description="Entity type (P, I, C, or O)")
    confidence: float = Field(
        description="Model confidence score in [0, 1]",
        ge=0.0,
        le=1.0,
    )
    normalized: str | None = Field(
        default=None,
        description="Optional normalized form (MeSH term, UMLS concept ID, etc.)",
    )

    def __str__(self) -> str:
        return f"{self.label.value}:{self.text!r} ({self.confidence:.2f})"


class PICOResult(BaseModel):
    """PICO extraction result for a single abstract.

    Contains all extracted entities across Population, Intervention,
    Comparator, and Outcome categories.
    """

    abstract_text: str = Field(description="The source abstract text")
    source_id: str | None = Field(
        default=None,
        description="PMID or other source identifier",
    )

    population: list[EntitySpan] = Field(
        default_factory=list,
        description="Population / Patient entities",
    )
    intervention: list[EntitySpan] = Field(
        default_factory=list,
        description="Intervention entities",
    )
    comparator: list[EntitySpan] = Field(
        default_factory=list,
        description="Comparator / control entities",
    )
    outcomes: list[EntitySpan] = Field(
        default_factory=list,
        description="Outcome entities (merged from PICOX + EvidenceOutcomes)",
    )

    model_version: str = Field(
        default="picox-v1",
        description="Model version used for extraction",
    )

    @property
    def all_spans(self) -> list[EntitySpan]:
        """Return all extracted spans across all categories."""
        return self.population + self.intervention + self.comparator + self.outcomes

    @property
    def has_rct_structure(self) -> bool:
        """Return True if the abstract has the minimum PICO structure for RCT inclusion."""
        return bool(self.population and self.intervention and self.outcomes)

    def top_outcomes(self, n: int = 5) -> list[EntitySpan]:
        """Return the top-n outcomes by confidence score."""
        return sorted(self.outcomes, key=lambda s: s.confidence, reverse=True)[:n]


class ExtractionBatch(BaseModel):
    """Results from batch PICO extraction across multiple abstracts."""

    results: list[PICOResult] = Field(default_factory=list)
    total_processed: int = 0
    failed_count: int = 0
    model_version: str = "picox-v1"

    @property
    def success_rate(self) -> float:
        """Fraction of abstracts successfully processed."""
        if self.total_processed == 0:
            return 0.0
        return (self.total_processed - self.failed_count) / self.total_processed

    def filter_high_confidence(self, min_confidence: float = 0.7) -> "ExtractionBatch":
        """Return a new batch with only high-confidence spans retained."""
        filtered_results = []
        for result in self.results:
            filtered = PICOResult(
                abstract_text=result.abstract_text,
                source_id=result.source_id,
                population=[s for s in result.population if s.confidence >= min_confidence],
                intervention=[s for s in result.intervention if s.confidence >= min_confidence],
                comparator=[s for s in result.comparator if s.confidence >= min_confidence],
                outcomes=[s for s in result.outcomes if s.confidence >= min_confidence],
                model_version=result.model_version,
            )
            filtered_results.append(filtered)

        return ExtractionBatch(
            results=filtered_results,
            total_processed=self.total_processed,
            failed_count=self.failed_count,
            model_version=self.model_version,
        )
