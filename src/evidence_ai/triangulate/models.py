"""Pydantic models for evidence triangulation results."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class EffectDirection(str, Enum):
    """Direction of the effect of an exposure on an outcome."""

    EXCITATORY = "excitatory"    # exposure increases the outcome
    INHIBITORY = "inhibitory"    # exposure decreases the outcome
    NO_CHANGE = "no_change"      # no significant effect


class StudyDesignCategory(str, Enum):
    """Broad study design categories used in CoE grouping."""

    RCT = "RCT"
    OS = "OS"                    # Observational Study
    MR = "MR"                    # Mendelian Randomization
    META = "META"
    SR = "SR"
    REVIEW = "REVIEW"
    OTHER = "OTHER"


class SignificanceLabel(str, Enum):
    """Statistical significance classification."""

    SIGNIFICANT = "positive"
    NOT_SIGNIFICANT = "negative"
    UNCLEAR = "unclear"


class ExtractedRelationship(BaseModel):
    """A single exposure-outcome relationship extracted from one paper."""

    pmid: str = Field(description="PubMed ID of the source paper")
    exposure: str = Field(description="The exposure or intervention")
    exposure_direction: str = Field(
        description="Direction of exposure change (e.g. 'increased', 'decreased')"
    )
    outcome: str = Field(description="The clinical outcome")
    effect_direction: EffectDirection = Field(
        description="Direction of the effect: excitatory, inhibitory, or no_change"
    )
    significance: SignificanceLabel = Field(
        description="Statistical significance of the finding"
    )
    study_design: StudyDesignCategory = Field(description="Study design classification")
    participant_count: int | None = Field(
        default=None, description="Number of participants in the study"
    )
    comparator: str | None = Field(default=None, description="Control or comparator group")
    confidence: float = Field(
        default=0.5,
        description="LLM extraction confidence score",
        ge=0.0,
        le=1.0,
    )

    # Concept matching results (Stage 3, Step 3)
    exposure_match_score: float | None = Field(
        default=None,
        description="Concept matching score for the exposure",
    )
    outcome_match_score: float | None = Field(
        default=None,
        description="Concept matching score for the outcome",
    )
    is_triangulation_eligible: bool = Field(
        default=False,
        description="Whether this relationship passes concept matching for triangulation",
    )


class CoEScores(BaseModel):
    """Convergence of Evidence scores across the three effect directions.

    These scores are normalized probabilities representing the evidence
    weight supporting each effect direction.

    Reference:
        Shi et al. (2024), llm-evidence-triangulation, medRxiv.
    """

    p_excitatory: float = Field(
        description="Probability mass supporting excitatory (increasing) effect",
        ge=0.0,
        le=1.0,
    )
    p_no_change: float = Field(
        description="Probability mass supporting no effect",
        ge=0.0,
        le=1.0,
    )
    p_inhibitory: float = Field(
        description="Probability mass supporting inhibitory (decreasing) effect",
        ge=0.0,
        le=1.0,
    )

    @field_validator("p_excitatory", "p_no_change", "p_inhibitory")
    @classmethod
    def round_probability(cls, v: float) -> float:
        return round(v, 6)

    @property
    def dominant_direction(self) -> EffectDirection:
        """Return the direction with the highest probability mass."""
        scores = {
            EffectDirection.EXCITATORY: self.p_excitatory,
            EffectDirection.NO_CHANGE: self.p_no_change,
            EffectDirection.INHIBITORY: self.p_inhibitory,
        }
        return max(scores, key=lambda k: scores[k])

    @property
    def max_probability(self) -> float:
        """Return the probability of the dominant direction."""
        return max(self.p_excitatory, self.p_no_change, self.p_inhibitory)

    def __str__(self) -> str:
        return (
            f"CoE(excitatory={self.p_excitatory:.3f}, "
            f"no_change={self.p_no_change:.3f}, "
            f"inhibitory={self.p_inhibitory:.3f})"
        )


class TriangulationResult(BaseModel):
    """Result of evidence triangulation for a clinical question.

    Contains the CoE scores, Level of Evidence (LoE), and all extracted
    relationships used in the analysis.
    """

    question: str = Field(description="The clinical question that was triangulated")
    exposure: str = Field(description="The exposure/intervention")
    outcome: str = Field(description="The clinical outcome")

    # Core results
    coe_scores: CoEScores = Field(description="Convergence of Evidence probabilities")
    loe: float = Field(
        description=(
            "Level of Evidence score in [0, 1]. "
            "Computed as (max_p - 1/3) / (2/3), normalized against uniform prior. "
            "0.0 = no evidence beyond chance; 1.0 = all evidence agrees."
        ),
        ge=0.0,
        le=1.0,
    )
    effect_direction: EffectDirection = Field(
        description="Dominant effect direction based on CoE scores"
    )

    # Evidence base
    relationships: list[ExtractedRelationship] = Field(
        default_factory=list,
        description="All extracted relationships used in triangulation",
    )
    papers_analyzed: int = Field(description="Total number of papers analyzed")
    papers_eligible: int = Field(
        description="Number of papers that passed concept matching"
    )

    # Design breakdown
    rct_count: int = Field(default=0, description="Number of RCTs in the evidence base")
    meta_count: int = Field(default=0, description="Number of meta-analyses")
    os_count: int = Field(default=0, description="Number of observational studies")
    mr_count: int = Field(default=0, description="Number of Mendelian randomization studies")

    @property
    def loe_label(self) -> str:
        """Human-readable LoE interpretation."""
        if self.loe >= 0.75:
            return "strong"
        elif self.loe >= 0.50:
            return "moderate"
        elif self.loe >= 0.25:
            return "weak"
        else:
            return "insufficient"

    @property
    def summary_sentence(self) -> str:
        """One-sentence summary of the triangulation result."""
        direction_str = {
            EffectDirection.EXCITATORY: "increases",
            EffectDirection.INHIBITORY: "decreases",
            EffectDirection.NO_CHANGE: "does not significantly affect",
        }[self.effect_direction]

        return (
            f"{self.loe_label.title()} evidence (LoE={self.loe:.2f}) suggests "
            f"{self.exposure} {direction_str} {self.outcome} "
            f"(based on {self.papers_eligible} eligible studies; "
            f"{self.rct_count} RCTs, {self.meta_count} meta-analyses)."
        )
