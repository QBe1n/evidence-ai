"""High-level EvidenceAI client.

Provides a simple, user-facing interface to the full 6-stage synthesis pipeline.
This is the object imported in the top-level ``from evidence_ai import EvidenceAI``.

Example::

    from evidence_ai import EvidenceAI

    client = EvidenceAI(openai_api_key="sk-...")

    review = await client.synthesize(
        question="Does SGLT2 inhibition reduce HF hospitalization?",
        max_papers=500,
    )
    print(review.level_of_evidence)
    review.export_fda_package("./output/")
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from evidence_ai.config import Settings, get_settings

if TYPE_CHECKING:
    from evidence_ai.summarize.models import EvidenceReview

logger = logging.getLogger(__name__)


class EvidenceAI:
    """High-level client for the EvidenceAI platform.

    Args:
        openai_api_key: OpenAI API key for LLM-based triangulation and summarization.
        settings: Optional pre-configured :class:`~evidence_ai.config.Settings` object.
            If not provided, settings are loaded from the environment.
    """

    def __init__(
        self,
        openai_api_key: str | None = None,
        settings: Settings | None = None,
    ) -> None:
        if settings is not None:
            self._settings = settings
        else:
            self._settings = get_settings()

        if openai_api_key:
            self._settings.openai_api_key = openai_api_key  # type: ignore[misc]

        if not self._settings.openai_api_key:
            logger.warning(
                "No OpenAI API key configured. LLM-based triangulation and "
                "summarization will be unavailable. Set OPENAI_API_KEY in your "
                "environment or pass openai_api_key= to EvidenceAI()."
            )

    async def synthesize(
        self,
        question: str,
        databases: list[str] | None = None,
        date_range: dict[str, str] | None = None,
        study_designs: list[str] | None = None,
        max_papers: int = 1000,
        include_augmentation: bool = False,
    ) -> "EvidenceReview":
        """Run the full 6-stage evidence synthesis pipeline.

        Args:
            question: The clinical question in free text. Example:
                ``"Does semaglutide reduce cardiovascular mortality in T2DM?"``
            databases: List of databases to search. Options: ``"pubmed"``,
                ``"clinicaltrials"``, ``"fda"``. Defaults to all three.
            date_range: Optional date filter with ``"start"`` and ``"end"`` keys
                in ``"YYYY-MM-DD"`` format.
            study_designs: Filter by study design. Options: ``"RCT"``, ``"META"``,
                ``"SR"``, ``"OS"``, ``"MR"``. Defaults to all.
            max_papers: Maximum number of papers to ingest. Defaults to 1000.
            include_augmentation: Whether to run the TrialSynth augmentation stage.
                Increases runtime but improves evidence completeness for sparse topics.

        Returns:
            An :class:`~evidence_ai.summarize.models.EvidenceReview` object with
            structured results and export methods.

        Raises:
            ValueError: If ``question`` is empty or ``databases`` contains unknown values.
            RuntimeError: If the pipeline fails at any stage.
        """
        if not question.strip():
            raise ValueError("question must be a non-empty string")

        databases = databases or ["pubmed", "clinicaltrials", "fda"]
        valid_dbs = {"pubmed", "clinicaltrials", "fda"}
        unknown = set(databases) - valid_dbs
        if unknown:
            raise ValueError(f"Unknown databases: {unknown}. Valid: {valid_dbs}")

        logger.info("Starting evidence synthesis: %r", question[:80])

        # Stage 1: Ingest
        from evidence_ai.ingest.pubmed import PubMedFetcher

        fetcher = PubMedFetcher(settings=self._settings)
        papers = await fetcher.search_and_fetch(
            query=question,
            max_results=max_papers,
            date_range=date_range,
        )
        logger.info("Ingested %d papers", len(papers))

        # Stage 2: Extract PICO entities
        from evidence_ai.extract.pico import PICOExtractor

        extractor = PICOExtractor.from_pretrained(device=self._settings.device)
        extracted = extractor.extract_batch([p.abstract for p in papers if p.abstract])
        logger.info("Extracted PICO entities from %d abstracts", len(extracted))

        # Stage 3: Triangulate evidence
        from evidence_ai.triangulate.engine import TriangulationEngine

        engine = TriangulationEngine(
            llm_model=self._settings.openai_model,
            api_key=self._settings.openai_api_key,
        )
        pmids = [p.pmid for p in papers if p.pmid]
        triangulation_result = await engine.triangulate(
            pmids=pmids,
            question=question,
            extracted_entities=extracted,
            study_designs=study_designs,
        )
        logger.info(
            "Triangulation complete. LoE=%.3f, direction=%s",
            triangulation_result.loe,
            triangulation_result.effect_direction,
        )

        # Stage 4: Augment (optional)
        augmentation_result = None
        if include_augmentation and self._settings.enable_synthetic_augmentation:
            from evidence_ai.augment.synth import TrialSynthAugmentor

            augmentor = TrialSynthAugmentor()
            augmentation_result = await augmentor.augment(
                papers=papers,
                triangulation=triangulation_result,
            )
            logger.info("Augmentation complete")

        # Stage 5: Summarize
        from evidence_ai.summarize.narrative import NarrativeGenerator

        generator = NarrativeGenerator(
            llm_model=self._settings.openai_model,
            api_key=self._settings.openai_api_key,
        )
        review = await generator.generate(
            question=question,
            papers=papers,
            pico_entities=extracted,
            triangulation=triangulation_result,
            augmentation=augmentation_result,
        )
        logger.info("Evidence synthesis complete")

        return review

    async def search(self, query: str, max_results: int = 100) -> list[dict]:  # noqa: ANN001
        """Search the EvidenceAI evidence base.

        Args:
            query: Free-text search query.
            max_results: Maximum number of results to return.

        Returns:
            List of matching evidence documents with metadata.
        """
        # TODO: implement evidence base search with vector similarity
        raise NotImplementedError("search() will be implemented in v0.2")
