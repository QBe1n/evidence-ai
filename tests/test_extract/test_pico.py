"""Tests for PICO entity extraction.

Tests cover:
- PICOResult model validation and properties
- ExtractionBatch operations
- EntitySpan model
- NMS (Non-Maximum Suppression) logic
- Span merging between PICOX and EvidenceOutcomes
- OutcomeExtractor IOB2 → span conversion
"""

from __future__ import annotations

import pytest

from evidence_ai.extract.models import (
    EntitySpan,
    ExtractionBatch,
    PICOResult,
    SpanLabel,
)
from evidence_ai.extract.outcomes import OutcomeExtractor
from evidence_ai.extract.pico import PICOExtractor, SpanClassifier


# ── EntitySpan tests ──────────────────────────────────────────────────────────

class TestEntitySpan:
    """Test EntitySpan model."""

    def test_str_representation(self):
        """Should format as label:text (confidence)."""
        span = EntitySpan(
            text="type 2 diabetes",
            start=0,
            end=15,
            label=SpanLabel.POPULATION,
            confidence=0.92,
        )
        result = str(span)
        assert "P:" in result
        assert "type 2 diabetes" in result
        assert "0.92" in result

    def test_confidence_bounds(self):
        """Confidence must be in [0, 1]."""
        with pytest.raises(ValueError):
            EntitySpan(
                text="test",
                start=0,
                end=4,
                label=SpanLabel.INTERVENTION,
                confidence=1.5,  # Out of bounds
            )

    def test_normalized_is_optional(self):
        """Normalized form should be optional."""
        span = EntitySpan(
            text="semaglutide",
            start=0,
            end=11,
            label=SpanLabel.INTERVENTION,
            confidence=0.88,
        )
        assert span.normalized is None


# ── PICOResult tests ──────────────────────────────────────────────────────────

class TestPICOResult:
    """Test PICOResult model and properties."""

    def test_all_spans_returns_all_entities(self, sample_pico_result):
        """all_spans should return population + intervention + comparator + outcomes."""
        all_spans = sample_pico_result.all_spans
        total = (
            len(sample_pico_result.population)
            + len(sample_pico_result.intervention)
            + len(sample_pico_result.comparator)
            + len(sample_pico_result.outcomes)
        )
        assert len(all_spans) == total

    def test_has_rct_structure_true(self, sample_pico_result):
        """has_rct_structure should be True when P, I, and O are present."""
        assert sample_pico_result.has_rct_structure is True

    def test_has_rct_structure_false_missing_population(self, sample_pico_result):
        """has_rct_structure should be False when population is missing."""
        sample_pico_result.population = []
        assert sample_pico_result.has_rct_structure is False

    def test_has_rct_structure_false_missing_outcomes(self, sample_pico_result):
        """has_rct_structure should be False when outcomes are missing."""
        sample_pico_result.outcomes = []
        assert sample_pico_result.has_rct_structure is False

    def test_top_outcomes_returns_sorted_by_confidence(self, sample_pico_result):
        """top_outcomes should return outcomes sorted by confidence descending."""
        top = sample_pico_result.top_outcomes(n=5)
        if len(top) > 1:
            for i in range(len(top) - 1):
                assert top[i].confidence >= top[i + 1].confidence

    def test_top_outcomes_respects_n_limit(self, sample_pico_result):
        """top_outcomes should return at most n results."""
        top = sample_pico_result.top_outcomes(n=1)
        assert len(top) <= 1

    def test_empty_pico_result(self, sample_pubmed_abstract):
        """Should handle empty extraction gracefully."""
        result = PICOResult(abstract_text=sample_pubmed_abstract)
        assert result.all_spans == []
        assert result.has_rct_structure is False


# ── ExtractionBatch tests ─────────────────────────────────────────────────────

class TestExtractionBatch:
    """Test ExtractionBatch model."""

    def test_success_rate_all_successful(self, sample_extraction_batch):
        """Success rate should be 1.0 when failed_count is 0."""
        assert sample_extraction_batch.success_rate == 1.0

    def test_success_rate_with_failures(self, sample_extraction_batch):
        """Success rate should account for failures."""
        batch = ExtractionBatch(
            results=sample_extraction_batch.results,
            total_processed=10,
            failed_count=2,
        )
        assert batch.success_rate == 0.8

    def test_success_rate_zero_processed(self):
        """Should return 0.0 when nothing was processed."""
        batch = ExtractionBatch(total_processed=0, failed_count=0)
        assert batch.success_rate == 0.0

    def test_filter_high_confidence(self, sample_pico_result):
        """filter_high_confidence should remove low-confidence spans."""
        # Add a low-confidence span
        low_conf_span = EntitySpan(
            text="low confidence outcome",
            start=500,
            end=522,
            label=SpanLabel.OUTCOME,
            confidence=0.2,  # Below threshold
        )
        sample_pico_result.outcomes.append(low_conf_span)

        batch = ExtractionBatch(
            results=[sample_pico_result],
            total_processed=1,
        )
        filtered = batch.filter_high_confidence(min_confidence=0.7)

        for result in filtered.results:
            for span in result.outcomes:
                assert span.confidence >= 0.7


# ── NMS tests ─────────────────────────────────────────────────────────────────

class TestNonMaximumSuppression:
    """Test the NMS overlap removal logic in SpanClassifier."""

    def test_nms_keeps_non_overlapping(self, test_settings):
        """NMS should keep all spans that don't overlap."""
        classifier = SpanClassifier(model_path="test", device="cpu")
        spans = [
            {"start": 0, "end": 10, "confidence": 0.9},
            {"start": 20, "end": 30, "confidence": 0.8},
            {"start": 40, "end": 50, "confidence": 0.7},
        ]
        kept = classifier._apply_nms(spans)
        assert len(kept) == 3

    def test_nms_removes_lower_confidence_overlap(self, test_settings):
        """NMS should remove the lower-confidence span when IoU > threshold."""
        classifier = SpanClassifier(model_path="test", device="cpu")
        spans = [
            {"start": 0, "end": 20, "confidence": 0.9},   # Higher confidence
            {"start": 5, "end": 25, "confidence": 0.5},   # Overlaps with first, lower conf
        ]
        kept = classifier._apply_nms(spans, iou_threshold=0.3)
        assert len(kept) == 1
        assert kept[0]["confidence"] == 0.9

    def test_iou_identical_spans(self, test_settings):
        """IoU of identical spans should be 1.0."""
        classifier = SpanClassifier(model_path="test", device="cpu")
        span = {"start": 10, "end": 20}
        iou = classifier._compute_iou(span, span)
        assert abs(iou - 1.0) < 1e-6

    def test_iou_non_overlapping_spans(self, test_settings):
        """IoU of non-overlapping spans should be 0.0."""
        classifier = SpanClassifier(model_path="test", device="cpu")
        a = {"start": 0, "end": 10}
        b = {"start": 20, "end": 30}
        iou = classifier._compute_iou(a, b)
        assert iou == 0.0

    def test_nms_empty_input(self, test_settings):
        """NMS on empty list should return empty list."""
        classifier = SpanClassifier(model_path="test", device="cpu")
        assert classifier._apply_nms([]) == []


# ── IOB2 to spans conversion tests ───────────────────────────────────────────

class TestIOB2Conversion:
    """Test IOB2 label → EntitySpan conversion."""

    def test_single_outcome_span(self):
        """Should convert a single B-Outcome I-Outcome sequence to one span."""
        tokens = ["cardiovascular", "death"]
        labels = ["B-Outcome", "I-Outcome"]
        confidences = [0.92, 0.88]
        offsets = [(0, 14), (15, 20)]

        spans = OutcomeExtractor._iob2_to_spans(tokens, labels, confidences, offsets)

        assert len(spans) == 1
        assert spans[0].label == SpanLabel.OUTCOME
        assert spans[0].start == 0
        assert spans[0].end == 20
        assert abs(spans[0].confidence - 0.9) < 0.01

    def test_multiple_outcome_spans(self):
        """Should produce separate spans for non-adjacent B-Outcome tokens."""
        tokens = ["mortality", "and", "hospitalization"]
        labels = ["B-Outcome", "O", "B-Outcome"]
        confidences = [0.9, 0.1, 0.85]
        offsets = [(0, 9), (10, 13), (14, 27)]

        spans = OutcomeExtractor._iob2_to_spans(tokens, labels, confidences, offsets)

        assert len(spans) == 2

    def test_no_outcomes(self):
        """Should return empty list when no outcome tokens exist."""
        tokens = ["In", "this", "study"]
        labels = ["O", "O", "O"]
        confidences = [0.95, 0.95, 0.95]
        offsets = [(0, 2), (3, 7), (8, 13)]

        spans = OutcomeExtractor._iob2_to_spans(tokens, labels, confidences, offsets)
        assert spans == []


# ── PICOExtractor integration tests ──────────────────────────────────────────

class TestPICOExtractorFromPretrained:
    """Test PICOExtractor.from_pretrained() constructor."""

    def test_from_pretrained_returns_extractor(self, test_settings):
        """from_pretrained should return a PICOExtractor instance."""
        extractor = PICOExtractor.from_pretrained(device="cpu")
        assert isinstance(extractor, PICOExtractor)

    def test_extract_stub_returns_pico_result(
        self, test_settings, sample_pubmed_abstract
    ):
        """extract() should return a PICOResult even with stub models."""
        extractor = PICOExtractor.from_pretrained(device="cpu")
        result = extractor.extract(sample_pubmed_abstract, source_id="26378978")

        assert isinstance(result, PICOResult)
        assert result.abstract_text == sample_pubmed_abstract
        assert result.source_id == "26378978"

    def test_extract_batch_handles_errors(
        self, test_settings, sample_pubmed_abstract
    ):
        """extract_batch should handle individual failures gracefully."""
        extractor = PICOExtractor.from_pretrained(device="cpu")
        # Include an empty abstract that might cause issues
        abstracts = [sample_pubmed_abstract, "", sample_pubmed_abstract]
        batch = extractor.extract_batch(abstracts, source_ids=["1", "2", "3"])

        assert isinstance(batch, ExtractionBatch)
        assert batch.total_processed == 3
