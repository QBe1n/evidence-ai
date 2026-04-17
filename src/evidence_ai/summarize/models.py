"""Pydantic models for evidence review and summaries."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from evidence_ai.triangulate.models import CoEScores, EffectDirection, TriangulationResult


class PRISMAStats(BaseModel):
    """PRISMA 2020 flow statistics for systematic review reporting."""

    records_identified: int = 0
    records_removed_duplicates: int = 0
    records_screened: int = 0
    records_excluded_title_abstract: int = 0
    full_texts_assessed: int = 0
    full_texts_excluded: int = 0
    studies_included: int = 0


class EvidenceTable(BaseModel):
    """A structured evidence table row for a single included study."""

    pmid: str | None = None
    nct_id: str | None = None
    authors: str = ""
    year: int | None = None
    study_design: str = ""
    sample_size: int | None = None
    intervention: str = ""
    comparator: str = ""
    primary_outcome: str = ""
    effect_estimate: str = ""
    p_value: str = ""
    conclusion: str = ""
    risk_of_bias: str = "Not assessed"


class EvidenceReview(BaseModel):
    """Complete evidence review output from the EvidenceAI pipeline.

    This is the final output object from Stage 6 (Deliver) and the return
    type of :meth:`~evidence_ai.client.EvidenceAI.synthesize`.
    """

    # Identification
    review_id: str = Field(description="Unique review identifier")
    question: str = Field(description="The clinical question answered")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # Core results
    level_of_evidence: float = Field(
        description="Level of Evidence score [0, 1]. See LoE formula in triangulate module.",
        ge=0.0,
        le=1.0,
    )
    effect_direction: EffectDirection
    coe_scores: CoEScores

    # Narrative summary
    summary: str = Field(description="Evidence narrative suitable for regulatory submission")
    key_findings: list[str] = Field(
        default_factory=list,
        description="Bullet-point key findings for executive summary",
    )

    # Evidence base
    papers_screened: int
    papers_included: int
    evidence_table: list[EvidenceTable] = Field(default_factory=list)

    # PRISMA statistics
    prisma: PRISMAStats = Field(default_factory=PRISMAStats)

    # Regulatory formats (populated by RegulatoryFormatter)
    module_25_text: str | None = Field(
        default=None,
        description="FDA eCTD Module 2.5 Clinical Overview text",
    )
    module_273_text: str | None = Field(
        default=None,
        description="FDA eCTD Module 2.7.3 Summary of Clinical Efficacy text",
    )
    module_274_text: str | None = Field(
        default=None,
        description="FDA eCTD Module 2.7.4 Summary of Clinical Safety text",
    )
    plausible_mechanism_text: str | None = Field(
        default=None,
        description="FDA Plausible Mechanism Framework evidence package (Feb 2026)",
    )

    # Raw data
    triangulation: TriangulationResult | None = None

    @property
    def loe_label(self) -> str:
        """Human-readable LoE interpretation."""
        if self.level_of_evidence >= 0.75:
            return "strong"
        elif self.level_of_evidence >= 0.50:
            return "moderate"
        elif self.level_of_evidence >= 0.25:
            return "weak"
        else:
            return "insufficient"

    def export_fda_package(
        self,
        output_dir: str | Path,
        format: str = "ectd",  # noqa: A002
        include_bibliography: bool = True,
        include_prisma_diagram: bool = False,
    ) -> Path:
        """Export an FDA evidence package to the specified directory.

        Args:
            output_dir: Directory to write output files.
            format: Output format. ``"ectd"`` (default) generates eCTD Module
                2.5/2.7-formatted Word documents. ``"json"`` exports raw data.
            include_bibliography: Whether to include a full bibliography.
            include_prisma_diagram: Whether to generate a PRISMA flow diagram.
                Requires the ``matplotlib`` package.

        Returns:
            Path to the output directory containing generated files.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if format == "json":
            output_file = output_path / f"evidence_review_{self.review_id}.json"
            output_file.write_text(self.model_dump_json(indent=2))
            return output_path

        # eCTD format
        from evidence_ai.summarize.regulatory import RegulatoryFormatter
        formatter = RegulatoryFormatter()

        if self.module_25_text:
            formatter.write_module_25(self, output_path)
        if self.module_273_text:
            formatter.write_module_273(self, output_path)
        if self.module_274_text:
            formatter.write_module_274(self, output_path)

        # Always write the evidence table as CSV
        table_file = output_path / "evidence_table.json"
        table_file.write_text(
            json.dumps([t.model_dump() for t in self.evidence_table], indent=2)
        )

        return output_path
