"""Evidence narrative generation using LLM.

Generates structured regulatory-ready narrative summaries from triangulation
results. The summarization model can be either:

1. A fine-tuned open-source model trained on the MedReview dataset
   (PRIMERA, LongT5, or Llama-2 fine-tuned on 7,472 Cochrane pairs)
2. A general-purpose LLM (GPT-4o-mini, Claude) as a fallback

Key finding from the MedReview paper (npj Digital Medicine 2024):
  Fine-tuned open-source LLMs match or exceed GPT-4 on this task,
  making a self-hosted fine-tuned model the preferred production approach
  for cost, latency, and data privacy reasons.

Based on:
  https://github.com/ebmlab/MedReview
  (Columbia University ebmlab, npj Digital Medicine 2024, MIT License)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from evidence_ai.augment.models import AugmentationResult
from evidence_ai.extract.models import ExtractionBatch
from evidence_ai.ingest.models import IngestedDocument
from evidence_ai.summarize.models import (
    EvidenceReview,
    EvidenceTable,
    PRISMAStats,
)
from evidence_ai.triangulate.models import TriangulationResult

logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = """You are a clinical evidence synthesis expert preparing \
regulatory submission documents for the FDA. Generate a structured, objective \
evidence narrative based on the provided triangulation results.

Requirements:
- Use precise clinical language suitable for FDA reviewers
- Cite study designs and participant counts
- Report effect sizes and confidence intervals where available
- Include the Level of Evidence score and its interpretation
- Note any important limitations or heterogeneity
- Follow PRISMA 2020 reporting standards"""

SUMMARY_USER_TEMPLATE = """Generate a regulatory-grade evidence narrative for the following \
systematic review results:

CLINICAL QUESTION: {question}

TRIANGULATION RESULTS:
- Level of Evidence (LoE): {loe:.2f} ({loe_label})
- Effect direction: {effect_direction}
- p(inhibitory): {p_inhibitory:.3f}
- p(no_change): {p_no_change:.3f}
- p(excitatory): {p_excitatory:.3f}
- Papers analyzed: {papers_analyzed}
- Papers included: {papers_eligible}
- RCTs: {rct_count}
- Meta-analyses: {meta_count}
- Observational studies: {os_count}

TOP EVIDENCE ITEMS:
{top_evidence}

Generate:
1. A 3-5 sentence evidence summary paragraph
2. 3-5 key findings as bullet points
3. A limitations paragraph

Format as JSON: {{"summary": "...", "key_findings": ["...", "..."], "limitations": "..."}}"""


class NarrativeGenerator:
    """Generate structured evidence narratives from triangulation results.

    Args:
        llm_model: LLM model identifier.
        api_key: OpenAI API key. If empty, attempts to use a locally fine-tuned
            MedReview model.
        use_fine_tuned_model: Whether to prefer the locally fine-tuned MedReview
            model over the general-purpose LLM.
    """

    def __init__(
        self,
        llm_model: str = "gpt-4o-mini",
        api_key: str = "",
        use_fine_tuned_model: bool = False,
    ) -> None:
        self._model = llm_model
        self._api_key = api_key
        self._use_fine_tuned = use_fine_tuned_model
        self._llm_client: Any = None
        self._local_model: Any = None

    async def generate(
        self,
        question: str,
        papers: list[IngestedDocument],
        pico_entities: ExtractionBatch | None,
        triangulation: TriangulationResult,
        augmentation: AugmentationResult | None = None,
    ) -> EvidenceReview:
        """Generate a complete evidence review from pipeline outputs.

        Args:
            question: The clinical question.
            papers: Ingested papers from Stage 1.
            pico_entities: PICO extraction results from Stage 2.
            triangulation: Triangulation result from Stage 3.
            augmentation: Optional augmentation result from Stage 4.

        Returns:
            Complete :class:`~evidence_ai.summarize.models.EvidenceReview` object.
        """
        review_id = str(uuid.uuid4())[:8]

        # Generate narrative summary
        summary, key_findings = await self._generate_narrative(
            question=question,
            triangulation=triangulation,
        )

        # Build evidence table
        evidence_table = self._build_evidence_table(papers, triangulation)

        # PRISMA stats
        prisma = PRISMAStats(
            records_identified=len(papers),
            records_screened=len(papers),
            records_excluded_title_abstract=len(papers) - triangulation.papers_analyzed,
            full_texts_assessed=triangulation.papers_analyzed,
            full_texts_excluded=triangulation.papers_analyzed - triangulation.papers_eligible,
            studies_included=triangulation.papers_eligible,
        )

        review = EvidenceReview(
            review_id=review_id,
            question=question,
            level_of_evidence=triangulation.loe,
            effect_direction=triangulation.effect_direction,
            coe_scores=triangulation.coe_scores,
            summary=summary,
            key_findings=key_findings,
            papers_screened=len(papers),
            papers_included=triangulation.papers_eligible,
            evidence_table=evidence_table,
            prisma=prisma,
            triangulation=triangulation,
        )

        return review

    async def _generate_narrative(
        self,
        question: str,
        triangulation: TriangulationResult,
    ) -> tuple[str, list[str]]:
        """Generate summary narrative using LLM or fine-tuned model."""
        if not self._api_key and not self._use_fine_tuned:
            # Return template-based fallback
            return self._template_summary(triangulation), self._template_findings(triangulation)

        if self._use_fine_tuned:
            # TODO: Use locally fine-tuned MedReview model
            # from transformers import pipeline
            # summarizer = pipeline("summarization", model=settings.medreview_model_path)
            # result = summarizer(input_text, max_length=300)
            logger.warning("Fine-tuned model not yet configured. Using LLM fallback.")

        # LLM-based generation
        try:
            client = self._get_llm_client()

            top_evidence = "\n".join(
                f"- PMID {r.pmid}: {r.exposure} → {r.outcome} "
                f"({r.effect_direction.value}, {r.study_design.value}, n={r.participant_count})"
                for r in triangulation.relationships[:10]
                if r.is_triangulation_eligible
            )

            user_content = SUMMARY_USER_TEMPLATE.format(
                question=question,
                loe=triangulation.loe,
                loe_label=triangulation.loe_label,
                effect_direction=triangulation.effect_direction.value,
                p_inhibitory=triangulation.coe_scores.p_inhibitory,
                p_no_change=triangulation.coe_scores.p_no_change,
                p_excitatory=triangulation.coe_scores.p_excitatory,
                papers_analyzed=triangulation.papers_analyzed,
                papers_eligible=triangulation.papers_eligible,
                rct_count=triangulation.rct_count,
                meta_count=triangulation.meta_count,
                os_count=triangulation.os_count,
                top_evidence=top_evidence or "(no eligible studies found)",
            )

            response = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"},
            )

            import json
            content = json.loads(response.choices[0].message.content)
            return content.get("summary", ""), content.get("key_findings", [])

        except Exception as e:  # noqa: BLE001
            logger.warning("LLM narrative generation failed: %s. Using template.", e)
            return self._template_summary(triangulation), self._template_findings(triangulation)

    def _template_summary(self, triangulation: TriangulationResult) -> str:
        """Generate a template-based summary when LLM is unavailable."""
        return (
            f"This systematic review analyzed {triangulation.papers_analyzed} papers "
            f"addressing the question: {triangulation.question}. "
            f"Evidence triangulation across {triangulation.papers_eligible} eligible studies "
            f"({triangulation.rct_count} RCTs, {triangulation.meta_count} meta-analyses, "
            f"{triangulation.os_count} observational studies) yielded a Level of Evidence "
            f"(LoE) of {triangulation.loe:.2f}, indicating {triangulation.loe_label} evidence. "
            f"The dominant effect direction is {triangulation.effect_direction.value} "
            f"(p={triangulation.coe_scores.max_probability:.3f}). "
            f"{triangulation.summary_sentence}"
        )

    @staticmethod
    def _template_findings(triangulation: TriangulationResult) -> list[str]:
        """Generate template key findings."""
        return [
            f"Level of Evidence: {triangulation.loe:.2f} ({triangulation.loe_label})",
            f"Effect direction: {triangulation.effect_direction.value} "
            f"(p={triangulation.coe_scores.max_probability:.3f})",
            f"Evidence base: {triangulation.papers_eligible} eligible studies "
            f"from {triangulation.papers_analyzed} screened",
            f"Study composition: {triangulation.rct_count} RCTs, "
            f"{triangulation.meta_count} meta-analyses, {triangulation.os_count} observational",
        ]

    def _build_evidence_table(
        self,
        papers: list[IngestedDocument],
        triangulation: TriangulationResult,
    ) -> list[EvidenceTable]:
        """Build a structured evidence table from papers and extracted relationships."""
        relationship_by_pmid = {r.pmid: r for r in triangulation.relationships}

        rows: list[EvidenceTable] = []
        for paper in papers[:50]:  # Cap at 50 rows for the table
            rel = relationship_by_pmid.get(paper.pmid or "")
            if rel is None or not rel.is_triangulation_eligible:
                continue

            rows.append(
                EvidenceTable(
                    pmid=paper.pmid,
                    authors=", ".join(paper.authors[:3]) + (" et al." if len(paper.authors) > 3 else ""),
                    year=paper.publication_date.year if paper.publication_date else None,
                    study_design=rel.study_design.value,
                    sample_size=rel.participant_count,
                    intervention=rel.exposure,
                    comparator=rel.comparator or "",
                    primary_outcome=rel.outcome,
                    effect_estimate=f"{rel.effect_direction.value} ({rel.significance.value})",
                    conclusion=f"LoE contribution: {rel.confidence:.2f}",
                )
            )

        return rows

    def _get_llm_client(self) -> Any:
        """Lazy-load the OpenAI client."""
        if self._llm_client is None:
            from openai import AsyncOpenAI
            self._llm_client = AsyncOpenAI(api_key=self._api_key)
        return self._llm_client
