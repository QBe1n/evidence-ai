"""Evidence triangulation engine — CoE/LoE algorithm implementation.

Implements the Convergence of Evidence (CoE) and Level of Evidence (LoE)
scoring algorithm from:

  Shi et al. (2024). LLM-based Evidence Triangulation across Study Designs.
  Peking University. medRxiv. https://github.com/xuanyshi/llm-evidence-triangulation

The algorithm:

1. For each paper, run two-step LLM extraction to get:
   - Exposure/outcome entities (Step 1)
   - Effect direction + significance (Step 2)

2. Run concept matching (Step 3, temperature=0) to filter papers where the
   extracted entities actually match the target clinical question.

3. Group triangulation-eligible findings by:
   study_design × effect_direction (6 cells: 3 designs × 2 directions)

4. Within each design category, weight by participant count.

5. Apply equal weighting across design categories to prevent observational
   studies from dominating (they have larger N but weaker causal evidence).

6. Compute CoE scores:
   - p_excitatory, p_no_change, p_inhibitory (sum to 1.0)

7. Compute Level of Evidence:
   LoE = (max(p) - 1/3) / (2/3)
   Normalized against a uniform prior (1/3 per direction).

Scale demonstrated in the original paper:
  2,436 papers → 11,667 extracted relationships → 793 triangulation-eligible
  findings from 446 studies (salt/sodium → cardiovascular disease).
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from typing import Any

from evidence_ai.extract.models import ExtractionBatch
from evidence_ai.ingest.models import IngestedDocument
from evidence_ai.triangulate.matching import ConceptMatcher, normalize_study_design
from evidence_ai.triangulate.models import (
    CoEScores,
    EffectDirection,
    ExtractedRelationship,
    SignificanceLabel,
    StudyDesignCategory,
    TriangulationResult,
)
from evidence_ai.triangulate.prompts import (
    build_entity_extraction_messages,
    build_relationship_extraction_messages,
)

logger = logging.getLogger(__name__)

# Study design categories used in CoE grouping
# Equal weights prevent large observational cohorts from dominating
COE_DESIGN_CATEGORIES = [
    StudyDesignCategory.RCT,
    StudyDesignCategory.OS,
    StudyDesignCategory.MR,
    StudyDesignCategory.META,
    StudyDesignCategory.SR,
    StudyDesignCategory.REVIEW,
]

# Uniform prior probability per direction (3 directions)
UNIFORM_PRIOR = 1.0 / 3.0


class TriangulationEngine:
    """Orchestrates the three-step LLM evidence triangulation pipeline.

    Args:
        llm_model: LLM model identifier (e.g. ``"gpt-4o-mini"``).
        api_key: OpenAI API key.
        temperature_extraction: Temperature for entity/relationship extraction.
            Higher = more varied but potentially less accurate. Default 0.
        include_non_significant: Whether to include non-significant findings
            in the triangulation. Default True (they contribute to p_no_change).
    """

    def __init__(
        self,
        llm_model: str = "gpt-4o-mini",
        api_key: str = "",
        temperature_extraction: float = 0.0,
        include_non_significant: bool = True,
    ) -> None:
        self._model = llm_model
        self._api_key = api_key
        self._temp = temperature_extraction
        self._include_non_sig = include_non_significant
        self._llm_client: Any = None
        self._concept_matcher: ConceptMatcher | None = None

    def _get_llm_client(self) -> Any:
        """Lazy-load and return the OpenAI client."""
        if self._llm_client is None:
            try:
                from openai import AsyncOpenAI
                self._llm_client = AsyncOpenAI(api_key=self._api_key)
            except ImportError as e:
                raise ImportError(
                    "openai package is required for triangulation. "
                    "Install with: pip install openai"
                ) from e
        return self._llm_client

    def _get_concept_matcher(self) -> ConceptMatcher:
        """Lazy-load and return the concept matcher."""
        if self._concept_matcher is None:
            self._concept_matcher = ConceptMatcher(
                llm_client=self._get_llm_client(),
                model=self._model,
            )
        return self._concept_matcher

    async def triangulate(
        self,
        pmids: list[str] | None = None,
        question: str = "",
        extracted_entities: ExtractionBatch | None = None,
        papers: list[IngestedDocument] | None = None,
        exposure: str | None = None,
        outcome: str | None = None,
        study_designs: list[str] | None = None,
    ) -> TriangulationResult:
        """Run the full three-step triangulation pipeline.

        Args:
            pmids: Optional list of PubMed IDs to look up (used with papers list).
            question: The clinical question in free text. Used to parse exposure
                and outcome if ``exposure`` and ``outcome`` are not provided.
            extracted_entities: Optional pre-computed PICO extraction batch.
                If provided, abstracts from these results are used for LLM extraction.
            papers: Optional list of already-fetched :class:`~evidence_ai.ingest.models.IngestedDocument` objects.
            exposure: Explicit exposure/intervention concept (overrides question parsing).
            outcome: Explicit outcome concept (overrides question parsing).
            study_designs: Optional filter to restrict triangulation to specific
                study design categories.

        Returns:
            :class:`~evidence_ai.triangulate.models.TriangulationResult` with
            CoE scores, LoE, and all extracted relationships.
        """
        # Parse exposure/outcome from question if not provided
        if not exposure or not outcome:
            exposure, outcome = self._parse_question(question)
            logger.info(
                "Parsed from question: exposure=%r, outcome=%r",
                exposure,
                outcome,
            )

        abstracts = self._collect_abstracts(papers, extracted_entities)
        logger.info(
            "Triangulating %d abstracts for: exposure=%r, outcome=%r",
            len(abstracts),
            exposure,
            outcome,
        )

        # Step 1 + 2: Extract relationships from each abstract
        relationships = await self._extract_relationships_batch(
            abstracts=abstracts,
            exposure=exposure,
            outcome=outcome,
        )
        logger.info(
            "Extracted %d relationships from %d abstracts",
            len(relationships),
            len(abstracts),
        )

        # Step 3: Concept matching to identify triangulation-eligible findings
        concept_cache: dict[tuple[str, str], bool] = {}
        matcher = self._get_concept_matcher()

        for rel in relationships:
            exposure_matches = await matcher.matches(
                rel.exposure, exposure, cache=concept_cache
            )
            outcome_matches = await matcher.matches(
                rel.outcome, outcome, cache=concept_cache
            )
            rel.is_triangulation_eligible = exposure_matches and outcome_matches
            rel.exposure_match_score = 1.0 if exposure_matches else 0.0
            rel.outcome_match_score = 1.0 if outcome_matches else 0.0

        eligible = [r for r in relationships if r.is_triangulation_eligible]
        logger.info(
            "%d of %d relationships are triangulation-eligible",
            len(eligible),
            len(relationships),
        )

        # CoE computation
        coe_scores = self._compute_coe_scores(eligible)
        loe = self._compute_loe(coe_scores)
        effect_direction = coe_scores.dominant_direction

        # Design breakdown for reporting
        design_counts = self._count_by_design(eligible)

        return TriangulationResult(
            question=question,
            exposure=exposure,
            outcome=outcome,
            coe_scores=coe_scores,
            loe=loe,
            effect_direction=effect_direction,
            relationships=relationships,
            papers_analyzed=len(abstracts),
            papers_eligible=len(eligible),
            rct_count=design_counts.get(StudyDesignCategory.RCT, 0),
            meta_count=design_counts.get(StudyDesignCategory.META, 0),
            os_count=design_counts.get(StudyDesignCategory.OS, 0),
            mr_count=design_counts.get(StudyDesignCategory.MR, 0),
        )

    # ── CoE/LoE algorithm ─────────────────────────────────────────────────────

    def _compute_coe_scores(
        self, eligible_relationships: list[ExtractedRelationship]
    ) -> CoEScores:
        """Compute Convergence of Evidence scores.

        Groups findings by study_design × effect_direction (6 cells).
        Weights by participant count within each design category.
        Applies equal weighting across design categories.

        Args:
            eligible_relationships: Relationships that passed concept matching.

        Returns:
            :class:`~evidence_ai.triangulate.models.CoEScores` with p_excitatory,
            p_no_change, and p_inhibitory.
        """
        if not eligible_relationships:
            # No evidence → uniform prior
            return CoEScores(
                p_excitatory=UNIFORM_PRIOR,
                p_no_change=UNIFORM_PRIOR,
                p_inhibitory=UNIFORM_PRIOR,
            )

        # Group by design category
        design_groups: dict[StudyDesignCategory, list[ExtractedRelationship]] = defaultdict(list)
        for rel in eligible_relationships:
            design_groups[rel.study_design].append(rel)

        # Within each design category, compute weighted direction scores
        # Weight by participant count (equal weight if count is unknown)
        direction_weights_per_design: list[dict[EffectDirection, float]] = []

        for design_category in COE_DESIGN_CATEGORIES:
            group = design_groups.get(design_category, [])
            if not group:
                continue

            direction_scores: dict[EffectDirection, float] = {
                EffectDirection.EXCITATORY: 0.0,
                EffectDirection.NO_CHANGE: 0.0,
                EffectDirection.INHIBITORY: 0.0,
            }

            for rel in group:
                # Weight = participant count, or 1.0 if unknown
                weight = float(rel.participant_count or 1)

                # Non-significant findings contribute to no_change
                if rel.significance == SignificanceLabel.NOT_SIGNIFICANT:
                    direction_scores[EffectDirection.NO_CHANGE] += weight
                else:
                    direction_scores[rel.effect_direction] += weight

            # Normalize within design category
            total = sum(direction_scores.values())
            if total > 0:
                normalized = {k: v / total for k, v in direction_scores.items()}
                direction_weights_per_design.append(normalized)

        if not direction_weights_per_design:
            return CoEScores(
                p_excitatory=UNIFORM_PRIOR,
                p_no_change=UNIFORM_PRIOR,
                p_inhibitory=UNIFORM_PRIOR,
            )

        # Average across design categories (equal weight per category)
        n_categories = len(direction_weights_per_design)
        p_excitatory = sum(
            d[EffectDirection.EXCITATORY] for d in direction_weights_per_design
        ) / n_categories
        p_no_change = sum(
            d[EffectDirection.NO_CHANGE] for d in direction_weights_per_design
        ) / n_categories
        p_inhibitory = sum(
            d[EffectDirection.INHIBITORY] for d in direction_weights_per_design
        ) / n_categories

        # Re-normalize to ensure sum = 1.0 (floating point safety)
        total = p_excitatory + p_no_change + p_inhibitory
        if total > 0:
            p_excitatory /= total
            p_no_change /= total
            p_inhibitory /= total

        return CoEScores(
            p_excitatory=p_excitatory,
            p_no_change=p_no_change,
            p_inhibitory=p_inhibitory,
        )

    @staticmethod
    def _compute_loe(coe_scores: CoEScores) -> float:
        """Compute Level of Evidence from CoE scores.

        Formula (from Shi et al. 2024):
            LoE = (max(p) - 1/3) / (2/3)

        This normalizes the max probability against a uniform prior (1/3).
        LoE = 0 when all three probabilities are equal (no evidence).
        LoE = 1 when all evidence points to a single direction.

        Args:
            coe_scores: Computed CoE scores.

        Returns:
            LoE value in [0, 1].
        """
        max_p = coe_scores.max_probability
        loe = (max_p - UNIFORM_PRIOR) / (1.0 - UNIFORM_PRIOR)
        return max(0.0, min(1.0, loe))

    # ── LLM extraction ────────────────────────────────────────────────────────

    async def _extract_relationships_batch(
        self,
        abstracts: list[tuple[str, str]],   # (pmid, abstract_text)
        exposure: str,
        outcome: str,
    ) -> list[ExtractedRelationship]:
        """Run two-step LLM extraction on a batch of abstracts.

        Args:
            abstracts: List of (pmid, abstract_text) tuples.
            exposure: Target exposure concept.
            outcome: Target outcome concept.

        Returns:
            List of :class:`~evidence_ai.triangulate.models.ExtractedRelationship`.
        """
        import asyncio

        # Process in batches to avoid rate limits
        batch_size = 10
        all_results: list[ExtractedRelationship] = []

        for i in range(0, len(abstracts), batch_size):
            batch = abstracts[i : i + batch_size]
            tasks = [
                self._extract_single(pmid, text, exposure, outcome)
                for pmid, text in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, ExtractedRelationship):
                    all_results.append(result)
                elif isinstance(result, Exception):
                    logger.debug("Extraction failed: %s", result)

        return all_results

    async def _extract_single(
        self,
        pmid: str,
        abstract: str,
        exposure: str,
        outcome: str,
    ) -> ExtractedRelationship | None:
        """Run two-step LLM extraction on a single abstract."""
        if not abstract.strip():
            return None

        client = self._get_llm_client()

        # Step 1: Entity extraction
        step1_messages = build_entity_extraction_messages(abstract, exposure, outcome)
        try:
            step1_response = await client.chat.completions.create(
                model=self._model,
                messages=step1_messages,
                temperature=self._temp,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            entities = json.loads(step1_response.choices[0].message.content)
        except Exception as e:  # noqa: BLE001
            logger.debug("Step 1 extraction failed for PMID %s: %s", pmid, e)
            return None

        if not entities.get("exposure_found") or not entities.get("outcome_found"):
            return None

        # Step 2: Relationship extraction
        step2_messages = build_relationship_extraction_messages(abstract, entities)
        try:
            step2_response = await client.chat.completions.create(
                model=self._model,
                messages=step2_messages,
                temperature=self._temp,
                max_tokens=200,
                response_format={"type": "json_object"},
            )
            relationship = json.loads(step2_response.choices[0].message.content)
        except Exception as e:  # noqa: BLE001
            logger.debug("Step 2 extraction failed for PMID %s: %s", pmid, e)
            return None

        # Build ExtractedRelationship
        try:
            return ExtractedRelationship(
                pmid=pmid,
                exposure=entities.get("exposure_text", ""),
                exposure_direction=entities.get("exposure_direction", "not_specified"),
                outcome=entities.get("outcome_text", ""),
                effect_direction=EffectDirection(
                    relationship.get("effect_direction", "no_change")
                ),
                significance=SignificanceLabel(
                    relationship.get("significance", "negative")
                ),
                study_design=StudyDesignCategory(
                    normalize_study_design(entities.get("study_design", "OTHER"))
                ),
                participant_count=entities.get("participant_count"),
                comparator=entities.get("comparator"),
                confidence=float(relationship.get("confidence", 0.5)),
            )
        except (ValueError, KeyError) as e:
            logger.debug("Failed to build ExtractedRelationship for PMID %s: %s", pmid, e)
            return None

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _parse_question(self, question: str) -> tuple[str, str]:
        """Parse exposure and outcome from a free-text clinical question.

        Naive implementation — returns the full question as exposure and
        an empty outcome. Override or extend for smarter parsing.

        TODO: Use an LLM or NLP pipeline for proper PICO-style parsing.
        """
        # Simple heuristic: look for common patterns
        question_lower = question.lower()
        for pattern in [" reduce ", " decrease ", " increase ", " improve ", " affect "]:
            idx = question_lower.find(pattern)
            if idx > 0:
                exposure = question[:idx].strip().lstrip("Does ").lstrip("do ")
                outcome = question[idx + len(pattern):].rstrip("?").strip()
                return exposure, outcome

        # Fallback: return whole question as exposure
        return question.strip("?"), "clinical outcome"

    @staticmethod
    def _collect_abstracts(
        papers: list[IngestedDocument] | None,
        extracted_entities: ExtractionBatch | None,
    ) -> list[tuple[str, str]]:
        """Collect (pmid, abstract_text) pairs from available sources."""
        abstracts: list[tuple[str, str]] = []

        if papers:
            for p in papers:
                text = p.full_abstract_text
                if text:
                    abstracts.append((p.pmid or p.source_id, text))

        elif extracted_entities:
            for result in extracted_entities.results:
                if result.abstract_text:
                    abstracts.append((result.source_id or "", result.abstract_text))

        return abstracts

    @staticmethod
    def _count_by_design(
        relationships: list[ExtractedRelationship],
    ) -> dict[StudyDesignCategory, int]:
        """Count relationships per study design category."""
        counts: dict[StudyDesignCategory, int] = defaultdict(int)
        for rel in relationships:
            counts[rel.study_design] += 1
        return dict(counts)
