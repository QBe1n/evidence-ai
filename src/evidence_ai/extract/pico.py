"""PICO entity extraction using PubMedBERT (inspired by Columbia's PICOX).

Implements a two-stage boundary-then-span architecture:

**Stage 1 — Boundary Detection**: A token-level classifier identifies span
start/end positions using labels: OUT, START, END, BOTH, IN. Built on
PubMedBERT-large.

**Stage 2 — Span Classification**: A multi-label sigmoid classifier determines
entity type (P, I, C, O) with Non-Maximum Suppression (NMS) for overlapping
spans.

PICOX reported performance on the EBM-NLP corpus:
- Precision: 53.49%
- Recall: 48.50%
- F1: 50.87%

Based on:
  https://github.com/ebmlab/PICOX (Columbia University ebmlab, JAMIA 2024, MIT License)

Production notes:
- Requires transformers and torch
- Models are lazy-loaded on first call; use ``from_pretrained()`` to pre-load
- For production, serve via a dedicated ML serving process (e.g. vLLM, BentoML)
  to avoid blocking the FastAPI event loop
"""

from __future__ import annotations

import logging
from typing import Any

from evidence_ai.extract.models import (
    EntitySpan,
    ExtractionBatch,
    PICOResult,
    SpanLabel,
)

logger = logging.getLogger(__name__)

# Label definitions from the PICOX paper
BOUNDARY_LABELS = ["OUT", "START", "END", "BOTH", "IN"]
SPAN_LABELS = ["P", "I", "C", "O"]

# NMS overlap threshold
NMS_IOU_THRESHOLD = 0.5

# Confidence threshold for span inclusion
DEFAULT_CONFIDENCE_THRESHOLD = 0.3


class BoundaryDetector:
    """Stage 1: Token-level boundary detection using PubMedBERT-large.

    Identifies span start/end positions in the abstract text using IOB-style
    boundary labels (OUT, START, END, BOTH, IN).
    """

    def __init__(self, model_path: str, device: str = "cpu") -> None:
        self.model_path = model_path
        self.device = device
        self._model: Any = None
        self._tokenizer: Any = None

    def _load_model(self) -> None:
        """Lazy-load the model and tokenizer on first call."""
        # TODO: Load fine-tuned PubMedBERT boundary detector
        # The fine-tuned weights are available after training on the EBM-NLP corpus
        # following the PICOX step_1_1 training notebook.
        #
        # from transformers import AutoTokenizer, AutoModelForTokenClassification
        # self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # self._model = AutoModelForTokenClassification.from_pretrained(
        #     self.model_path,
        #     num_labels=len(BOUNDARY_LABELS),
        # )
        # self._model.to(self.device)
        # self._model.eval()
        logger.warning(
            "BoundaryDetector using stub implementation. "
            "Load fine-tuned PICOX weights for production use."
        )

    def predict(self, texts: list[str]) -> list[list[dict[str, Any]]]:
        """Predict boundary labels for a batch of texts.

        Args:
            texts: List of abstract texts to process.

        Returns:
            For each text, a list of token-level predictions with keys:
            ``token``, ``start``, ``end``, ``label``, ``confidence``.
        """
        if self._model is None:
            self._load_model()

        # TODO: Implement actual model inference
        # Stub implementation returns empty predictions
        return [[] for _ in texts]


class SpanClassifier:
    """Stage 2: Multi-label span classification.

    Given candidate spans from the BoundaryDetector, classifies each span
    as P (Population), I (Intervention), C (Comparator), and/or O (Outcome)
    using a multi-label sigmoid classifier built on PubMedBERT-large.

    Non-Maximum Suppression (NMS) is applied to resolve overlapping spans.
    """

    def __init__(self, model_path: str, device: str = "cpu") -> None:
        self.model_path = model_path
        self.device = device
        self._model: Any = None
        self._tokenizer: Any = None

    def _load_model(self) -> None:
        """Lazy-load the span classification model."""
        # TODO: Load fine-tuned span classifier
        # from transformers import AutoTokenizer, AutoModelForSequenceClassification
        # self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # self._model = AutoModelForSequenceClassification.from_pretrained(
        #     self.model_path,
        #     num_labels=len(SPAN_LABELS),
        #     problem_type="multi_label_classification",
        # )
        # self._model.to(self.device)
        # self._model.eval()
        logger.warning(
            "SpanClassifier using stub implementation. "
            "Load fine-tuned PICOX weights for production use."
        )

    def classify(
        self,
        text: str,
        candidate_spans: list[dict[str, Any]],
    ) -> list[EntitySpan]:
        """Classify candidate spans into PICO categories.

        Args:
            text: Source text for context.
            candidate_spans: Candidate spans from BoundaryDetector.

        Returns:
            List of :class:`~evidence_ai.extract.models.EntitySpan` objects
            after NMS filtering.
        """
        if self._model is None:
            self._load_model()

        # TODO: Implement actual span classification + NMS
        # Steps:
        # 1. For each candidate span, extract context window from `text`
        # 2. Run through multi-label sigmoid classifier
        # 3. Apply NMS to remove overlapping spans
        # 4. Return spans above DEFAULT_CONFIDENCE_THRESHOLD

        return []

    @staticmethod
    def _compute_iou(span_a: dict[str, Any], span_b: dict[str, Any]) -> float:
        """Compute Intersection over Union for two character-offset spans."""
        start_a, end_a = span_a["start"], span_a["end"]
        start_b, end_b = span_b["start"], span_b["end"]

        intersection = max(0, min(end_a, end_b) - max(start_a, start_b))
        union = (end_a - start_a) + (end_b - start_b) - intersection
        return intersection / union if union > 0 else 0.0

    def _apply_nms(
        self, spans: list[dict[str, Any]], iou_threshold: float = NMS_IOU_THRESHOLD
    ) -> list[dict[str, Any]]:
        """Apply Non-Maximum Suppression to remove overlapping spans.

        Iterates spans sorted by confidence (descending), greedily keeping
        each span if it doesn't overlap too much with already-kept spans.
        """
        if not spans:
            return []

        sorted_spans = sorted(spans, key=lambda s: s["confidence"], reverse=True)
        kept: list[dict[str, Any]] = []

        for span in sorted_spans:
            if all(self._compute_iou(span, k) < iou_threshold for k in kept):
                kept.append(span)

        return kept


class PICOExtractor:
    """Two-stage PICO entity extractor.

    Combines the BoundaryDetector and SpanClassifier into a single pipeline.
    This is the main entry point for Stage 2 (Extract) of the EvidenceAI
    pipeline.

    Args:
        boundary_detector: Stage 1 boundary detection model.
        span_classifier: Stage 2 span classification model.
        outcome_extractor: Optional EvidenceOutcomes refiner for higher-precision
            outcome detection. If provided, outcome spans from ``span_classifier``
            are merged with results from the outcome extractor.
        confidence_threshold: Minimum confidence score for including spans.
    """

    def __init__(
        self,
        boundary_detector: BoundaryDetector,
        span_classifier: SpanClassifier,
        outcome_extractor: Any | None = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> None:
        self._boundary = boundary_detector
        self._classifier = span_classifier
        self._outcome_extractor = outcome_extractor
        self._threshold = confidence_threshold

    @classmethod
    def from_pretrained(
        cls,
        model_path: str = "sultan/BiomedNLP-PubMedBERT-large-uncased-abstract",
        device: str = "cpu",
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ) -> "PICOExtractor":
        """Instantiate a PICOExtractor with the specified model.

        Args:
            model_path: HuggingFace model ID or local path for PubMedBERT-large.
                After fine-tuning on EBM-NLP, replace this with the fine-tuned
                model path.
            device: Compute device (``"cpu"``, ``"cuda"``, or ``"mps"``).
            confidence_threshold: Minimum confidence for span inclusion.

        Returns:
            Configured :class:`PICOExtractor` instance.
        """
        boundary = BoundaryDetector(model_path=model_path, device=device)
        classifier = SpanClassifier(model_path=model_path, device=device)

        try:
            from evidence_ai.extract.outcomes import OutcomeExtractor
            outcome_extractor = OutcomeExtractor.from_pretrained(device=device)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not load OutcomeExtractor: %s", e)
            outcome_extractor = None

        return cls(
            boundary_detector=boundary,
            span_classifier=classifier,
            outcome_extractor=outcome_extractor,
            confidence_threshold=confidence_threshold,
        )

    def extract(self, abstract: str, source_id: str | None = None) -> PICOResult:
        """Extract PICO entities from a single abstract.

        Args:
            abstract: The abstract text to process.
            source_id: Optional PMID or identifier for provenance tracking.

        Returns:
            :class:`~evidence_ai.extract.models.PICOResult` with all extracted spans.
        """
        # Stage 1: Boundary detection
        boundary_preds = self._boundary.predict([abstract])
        candidate_spans = boundary_preds[0] if boundary_preds else []

        # Stage 2: Span classification
        spans = self._classifier.classify(abstract, candidate_spans)

        # Split spans by category
        population = [s for s in spans if s.label == SpanLabel.POPULATION]
        intervention = [s for s in spans if s.label == SpanLabel.INTERVENTION]
        comparator = [s for s in spans if s.label == SpanLabel.COMPARATOR]
        outcomes_pico = [s for s in spans if s.label == SpanLabel.OUTCOME]

        # Optionally refine outcomes with EvidenceOutcomes model
        outcomes_final = outcomes_pico
        if self._outcome_extractor is not None:
            try:
                refined = self._outcome_extractor.extract(abstract)
                outcomes_final = self._merge_outcome_spans(outcomes_pico, refined)
            except Exception as e:  # noqa: BLE001
                logger.warning("OutcomeExtractor refinement failed: %s", e)

        return PICOResult(
            abstract_text=abstract,
            source_id=source_id,
            population=population,
            intervention=intervention,
            comparator=comparator,
            outcomes=outcomes_final,
        )

    def extract_batch(
        self,
        abstracts: list[str],
        source_ids: list[str] | None = None,
    ) -> ExtractionBatch:
        """Extract PICO entities from a batch of abstracts.

        Args:
            abstracts: List of abstract texts.
            source_ids: Optional list of PMID/identifiers aligned with ``abstracts``.

        Returns:
            :class:`~evidence_ai.extract.models.ExtractionBatch` with results
            for all processed abstracts.
        """
        ids = source_ids or [None] * len(abstracts)  # type: ignore[list-item]
        results: list[PICOResult] = []
        failed = 0

        for abstract, source_id in zip(abstracts, ids):
            try:
                result = self.extract(abstract, source_id=source_id)
                results.append(result)
            except Exception as e:  # noqa: BLE001
                logger.warning(
                    "PICO extraction failed for source_id=%s: %s", source_id, e
                )
                failed += 1

        return ExtractionBatch(
            results=results,
            total_processed=len(abstracts),
            failed_count=failed,
        )

    def _merge_outcome_spans(
        self,
        pico_outcomes: list[EntitySpan],
        refined_outcomes: list[EntitySpan],
    ) -> list[EntitySpan]:
        """Merge PICO outcome spans with EvidenceOutcomes refined spans.

        Uses a confidence-weighted ensemble:
        - Keep all EvidenceOutcomes spans (higher precision model)
        - Add any PICO outcomes that don't overlap with EvidenceOutcomes spans
        """
        if not refined_outcomes:
            return pico_outcomes
        if not pico_outcomes:
            return refined_outcomes

        merged = list(refined_outcomes)
        refined_set = {(s.start, s.end) for s in refined_outcomes}

        for span in pico_outcomes:
            # Add PICO outcomes that don't exactly overlap with refined outcomes
            if (span.start, span.end) not in refined_set:
                # Check for significant overlap
                overlaps = any(
                    min(span.end, r.end) - max(span.start, r.start) > 0
                    for r in refined_outcomes
                )
                if not overlaps:
                    merged.append(span)

        return merged
