"""Tests for the evidence triangulation engine.

Tests cover:
- CoE/LoE algorithm correctness
- Edge cases (no evidence, all same direction, mixed evidence)
- Concept matching logic
- Study design grouping
- TriangulationResult model properties
"""

from __future__ import annotations

import pytest

from evidence_ai.triangulate.engine import TriangulationEngine, UNIFORM_PRIOR
from evidence_ai.triangulate.matching import ConceptMatcher, normalize_study_design
from evidence_ai.triangulate.models import (
    CoEScores,
    EffectDirection,
    ExtractedRelationship,
    SignificanceLabel,
    StudyDesignCategory,
    TriangulationResult,
)


# ── CoE score computation tests ────────────────────────────────────────────────

class TestCoEScoreComputation:
    """Test the core CoE scoring algorithm."""

    def test_no_evidence_returns_uniform_prior(self):
        """With no eligible relationships, should return uniform prior (1/3 each)."""
        engine = TriangulationEngine()
        scores = engine._compute_coe_scores([])

        assert abs(scores.p_excitatory - UNIFORM_PRIOR) < 1e-6
        assert abs(scores.p_no_change - UNIFORM_PRIOR) < 1e-6
        assert abs(scores.p_inhibitory - UNIFORM_PRIOR) < 1e-6

    def test_all_inhibitory_rcts(self):
        """All RCTs showing inhibitory effects should yield high p_inhibitory."""
        relationships = [
            ExtractedRelationship(
                pmid=f"pmid_{i}",
                exposure="empagliflozin",
                exposure_direction="administration",
                outcome="cardiovascular death",
                effect_direction=EffectDirection.INHIBITORY,
                significance=SignificanceLabel.SIGNIFICANT,
                study_design=StudyDesignCategory.RCT,
                participant_count=1000,
                confidence=0.9,
                is_triangulation_eligible=True,
            )
            for i in range(5)
        ]

        engine = TriangulationEngine()
        scores = engine._compute_coe_scores(relationships)

        assert scores.p_inhibitory > 0.8
        assert scores.p_excitatory < 0.1
        assert scores.dominant_direction == EffectDirection.INHIBITORY

    def test_mixed_evidence_lowers_loe(self):
        """Mixed evidence across directions should lower LoE."""
        relationships = [
            ExtractedRelationship(
                pmid="rct_1",
                exposure="drug",
                exposure_direction="treatment",
                outcome="outcome",
                effect_direction=EffectDirection.INHIBITORY,
                significance=SignificanceLabel.SIGNIFICANT,
                study_design=StudyDesignCategory.RCT,
                participant_count=500,
                confidence=0.85,
                is_triangulation_eligible=True,
            ),
            ExtractedRelationship(
                pmid="os_1",
                exposure="drug",
                exposure_direction="treatment",
                outcome="outcome",
                effect_direction=EffectDirection.EXCITATORY,
                significance=SignificanceLabel.SIGNIFICANT,
                study_design=StudyDesignCategory.OS,
                participant_count=500,
                confidence=0.75,
                is_triangulation_eligible=True,
            ),
        ]

        engine = TriangulationEngine()
        scores = engine._compute_coe_scores(relationships)
        loe = engine._compute_loe(scores)

        # Mixed evidence should yield low LoE
        assert loe < 0.5

    def test_non_significant_contributes_to_no_change(self):
        """Non-significant findings should increase p_no_change."""
        relationships = [
            ExtractedRelationship(
                pmid="os_1",
                exposure="drug",
                exposure_direction="treatment",
                outcome="outcome",
                effect_direction=EffectDirection.INHIBITORY,
                significance=SignificanceLabel.NOT_SIGNIFICANT,  # Not significant
                study_design=StudyDesignCategory.OS,
                participant_count=200,
                confidence=0.7,
                is_triangulation_eligible=True,
            ),
        ]

        engine = TriangulationEngine()
        scores = engine._compute_coe_scores(relationships)

        # Non-significant should contribute to no_change
        assert scores.p_no_change > scores.p_inhibitory

    def test_coe_probabilities_sum_to_one(self, sample_relationships):
        """CoE scores should always sum to 1.0 (± floating point epsilon)."""
        engine = TriangulationEngine()
        scores = engine._compute_coe_scores(sample_relationships)

        total = scores.p_excitatory + scores.p_no_change + scores.p_inhibitory
        assert abs(total - 1.0) < 1e-6

    def test_participant_weight_affects_result(self):
        """Higher participant count should have more influence on the score."""
        # Two relationships: one inhibitory with large N, one excitatory with small N
        relationships = [
            ExtractedRelationship(
                pmid="large_rct",
                exposure="drug",
                exposure_direction="treatment",
                outcome="outcome",
                effect_direction=EffectDirection.INHIBITORY,
                significance=SignificanceLabel.SIGNIFICANT,
                study_design=StudyDesignCategory.RCT,
                participant_count=10000,  # Very large trial
                confidence=0.9,
                is_triangulation_eligible=True,
            ),
            ExtractedRelationship(
                pmid="small_rct",
                exposure="drug",
                exposure_direction="treatment",
                outcome="outcome",
                effect_direction=EffectDirection.EXCITATORY,
                significance=SignificanceLabel.SIGNIFICANT,
                study_design=StudyDesignCategory.RCT,
                participant_count=50,  # Small trial
                confidence=0.8,
                is_triangulation_eligible=True,
            ),
        ]

        engine = TriangulationEngine()
        scores = engine._compute_coe_scores(relationships)

        # Large trial (inhibitory) should dominate
        assert scores.p_inhibitory > scores.p_excitatory


# ── LoE computation tests ─────────────────────────────────────────────────────

class TestLoEComputation:
    """Test Level of Evidence calculation."""

    def test_loe_formula_perfect_consensus(self):
        """LoE should be 1.0 when all probability is in one direction."""
        scores = CoEScores(p_excitatory=1.0, p_no_change=0.0, p_inhibitory=0.0)
        loe = TriangulationEngine._compute_loe(scores)
        assert abs(loe - 1.0) < 1e-6

    def test_loe_formula_uniform_prior(self):
        """LoE should be 0.0 for uniform distribution (no evidence)."""
        scores = CoEScores(
            p_excitatory=UNIFORM_PRIOR,
            p_no_change=UNIFORM_PRIOR,
            p_inhibitory=UNIFORM_PRIOR,
        )
        loe = TriangulationEngine._compute_loe(scores)
        assert abs(loe - 0.0) < 1e-6

    def test_loe_is_always_between_0_and_1(self, sample_relationships):
        """LoE should always be in [0, 1]."""
        engine = TriangulationEngine()
        scores = engine._compute_coe_scores(sample_relationships)
        loe = engine._compute_loe(scores)

        assert 0.0 <= loe <= 1.0

    def test_loe_label_strong(self):
        """LoE >= 0.75 should be labeled 'strong'."""
        result = TriangulationResult(
            question="test",
            exposure="drug",
            outcome="outcome",
            coe_scores=CoEScores(p_excitatory=0.05, p_no_change=0.05, p_inhibitory=0.90),
            loe=0.85,
            effect_direction=EffectDirection.INHIBITORY,
            papers_analyzed=100,
            papers_eligible=50,
        )
        assert result.loe_label == "strong"

    def test_loe_label_insufficient(self):
        """LoE < 0.25 should be labeled 'insufficient'."""
        result = TriangulationResult(
            question="test",
            exposure="drug",
            outcome="outcome",
            coe_scores=CoEScores(
                p_excitatory=UNIFORM_PRIOR,
                p_no_change=UNIFORM_PRIOR,
                p_inhibitory=UNIFORM_PRIOR,
            ),
            loe=0.1,
            effect_direction=EffectDirection.NO_CHANGE,
            papers_analyzed=5,
            papers_eligible=2,
        )
        assert result.loe_label == "insufficient"


# ── TriangulationResult tests ─────────────────────────────────────────────────

class TestTriangulationResult:
    """Test TriangulationResult model properties."""

    def test_summary_sentence_inhibitory(self, sample_triangulation_result):
        """Summary sentence should correctly describe inhibitory effect."""
        sentence = sample_triangulation_result.summary_sentence
        assert "decreases" in sentence or "reduces" in sentence or "inhibitory" in sentence.lower()

    def test_coe_scores_dominant_direction(self):
        """dominant_direction should return the direction with highest probability."""
        scores = CoEScores(
            p_excitatory=0.1,
            p_no_change=0.2,
            p_inhibitory=0.7,
        )
        assert scores.dominant_direction == EffectDirection.INHIBITORY

    def test_coe_scores_str_representation(self):
        """CoEScores __str__ should include all three probabilities."""
        scores = CoEScores(
            p_excitatory=0.05,
            p_no_change=0.12,
            p_inhibitory=0.83,
        )
        s = str(scores)
        assert "0.05" in s or "0.050" in s
        assert "0.83" in s or "0.830" in s


# ── Question parsing tests ────────────────────────────────────────────────────

class TestQuestionParsing:
    """Test extraction of exposure/outcome from clinical questions."""

    def test_parse_question_with_reduce(self):
        """Should extract exposure before 'reduce' and outcome after."""
        engine = TriangulationEngine()
        exposure, outcome = engine._parse_question(
            "Does semaglutide reduce cardiovascular mortality?"
        )
        assert "semaglutide" in exposure.lower()
        assert "cardiovascular" in outcome.lower() or "mortality" in outcome.lower()

    def test_parse_question_with_increase(self):
        """Should extract exposure and outcome around 'increase'."""
        engine = TriangulationEngine()
        exposure, outcome = engine._parse_question(
            "Does sodium increase blood pressure?"
        )
        assert "sodium" in exposure.lower()
        assert "blood pressure" in outcome.lower()

    def test_parse_question_fallback(self):
        """Should return whole question as exposure on unrecognized pattern."""
        engine = TriangulationEngine()
        exposure, outcome = engine._parse_question("What is the effect of drug X?")
        assert len(exposure) > 0


# ── Concept matching tests ────────────────────────────────────────────────────

class TestConceptMatching:
    """Test the ConceptMatcher trivial matching logic."""

    def test_trivial_exact_match(self):
        """Exact same strings should match trivially."""
        # We test the private method directly since the public one requires async
        mock_client = object()
        matcher = ConceptMatcher(llm_client=mock_client)
        assert matcher._trivial_match("semaglutide", "semaglutide") is True

    def test_trivial_substring_match(self):
        """Substring matches should return True trivially."""
        mock_client = object()
        matcher = ConceptMatcher(llm_client=mock_client)
        assert matcher._trivial_match("cardiovascular mortality", "cardiovascular") is True

    def test_trivial_abbreviation_match(self):
        """Known abbreviations should match their expansions."""
        mock_client = object()
        matcher = ConceptMatcher(llm_client=mock_client)
        assert matcher._trivial_match("t2dm", "type 2 diabetes") is True

    def test_trivial_no_match(self):
        """Unrelated terms should not trivially match."""
        mock_client = object()
        matcher = ConceptMatcher(llm_client=mock_client)
        assert matcher._trivial_match("sodium", "cardiovascular mortality") is False


# ── Study design normalization ────────────────────────────────────────────────

class TestStudyDesignNormalization:
    """Test study design normalization."""

    def test_normalize_rct_variations(self):
        """Various RCT descriptions should normalize to 'RCT'."""
        assert normalize_study_design("Randomized Controlled Trial") == "RCT"
        assert normalize_study_design("RANDOMIZED") == "RCT"
        assert normalize_study_design("rct") == "RCT"
        assert normalize_study_design("Clinical Trial") == "RCT"

    def test_normalize_meta_analysis(self):
        """Meta-analysis variations should normalize to 'META'."""
        assert normalize_study_design("Meta-Analysis") == "META"
        assert normalize_study_design("META ANALYSIS") == "META"

    def test_normalize_observational(self):
        """Observational study variations should normalize to 'OS'."""
        assert normalize_study_design("Observational Study") == "OS"
        assert normalize_study_design("cohort") == "OS"
        assert normalize_study_design("case-control") == "OS"

    def test_normalize_unknown_defaults_to_other(self):
        """Unknown study types should normalize to 'OTHER'."""
        assert normalize_study_design("qualitative research") == "OTHER"
        assert normalize_study_design("") == "OTHER"
