"""Pytest configuration and shared fixtures for EvidenceAI tests.

Provides:
- Mock HTTP responses for PubMed, ClinicalTrials.gov, and FDA APIs
- Sample documents, PICO results, and triangulation results
- In-memory SQLite database for DB tests
- Configured test settings
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from evidence_ai.config import Settings
from evidence_ai.extract.models import EntitySpan, ExtractionBatch, PICOResult, SpanLabel
from evidence_ai.ingest.models import (
    AbstractSection,
    DocumentSource,
    IngestedDocument,
    MeshTerm,
    StudyDesign,
)
from evidence_ai.triangulate.models import (
    CoEScores,
    EffectDirection,
    ExtractedRelationship,
    SignificanceLabel,
    StudyDesignCategory,
    TriangulationResult,
)

# ── Test fixtures directory ────────────────────────────────────────────────────
FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ── Settings ──────────────────────────────────────────────────────────────────

@pytest.fixture
def test_settings() -> Settings:
    """Return test settings with all external services mocked."""
    return Settings(
        app_env="test",
        secret_key="test-secret-key-for-testing-only",
        database_url="sqlite+aiosqlite:///./test.db",
        redis_url="redis://localhost:6379/15",  # Use a separate test DB
        openai_api_key="sk-test-key",
        ncbi_api_key="",
        ncbi_email="test@evidenceai.com",
        log_level="DEBUG",
    )


# ── Sample documents ──────────────────────────────────────────────────────────

@pytest.fixture
def sample_pubmed_abstract() -> str:
    """Return a realistic PubMed abstract for testing."""
    return (
        "Background: The cardiovascular effects of SGLT2 inhibitors in patients "
        "with type 2 diabetes and established cardiovascular disease remain an area "
        "of active investigation. Methods: We conducted a randomized, double-blind, "
        "placebo-controlled trial (EMPA-REG OUTCOME) enrolling 7,020 patients with "
        "type 2 diabetes and high cardiovascular risk. Patients were randomly assigned "
        "to empagliflozin 10mg, empagliflozin 25mg, or placebo once daily. The primary "
        "outcome was a composite of cardiovascular death, nonfatal myocardial infarction, "
        "or nonfatal stroke. Results: After a median follow-up of 3.1 years, the primary "
        "outcome occurred in 10.5% of empagliflozin-treated patients vs 12.1% in the "
        "placebo group (HR 0.86, 95% CI 0.74-0.99, p=0.04). Cardiovascular death was "
        "reduced by 38% (HR 0.62, p<0.001). Hospitalization for heart failure was "
        "reduced by 35% (HR 0.65, p<0.001). Conclusion: Empagliflozin added to standard "
        "care significantly reduced the composite of cardiovascular death, nonfatal MI, "
        "or nonfatal stroke in patients with type 2 diabetes and high cardiovascular risk."
    )


@pytest.fixture
def sample_document(sample_pubmed_abstract: str) -> IngestedDocument:
    """Return a sample IngestedDocument for testing."""
    return IngestedDocument(
        source=DocumentSource.PUBMED,
        source_id="26378978",
        pmid="26378978",
        doi="10.1056/NEJMoa1504720",
        title=(
            "Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes"
        ),
        abstract=sample_pubmed_abstract,
        abstract_sections=[
            AbstractSection(label="BACKGROUND", text="The cardiovascular effects of SGLT2 inhibitors..."),
            AbstractSection(label="METHODS", text="We conducted a randomized, double-blind..."),
            AbstractSection(label="RESULTS", text="After a median follow-up of 3.1 years..."),
            AbstractSection(label="CONCLUSIONS", text="Empagliflozin added to standard care..."),
        ],
        authors=["Zinman, Bernard", "Wanner, Christoph", "Lachin, John M."],
        journal="New England Journal of Medicine",
        publication_date=date(2015, 9, 17),
        publication_types=["Randomized Controlled Trial", "Clinical Trial, Phase III"],
        mesh_terms=[
            MeshTerm(descriptor="Diabetes Mellitus, Type 2", is_major=True),
            MeshTerm(descriptor="Cardiovascular Diseases", is_major=True),
            MeshTerm(descriptor="Glucosides", is_major=False),
        ],
        study_design=StudyDesign.RCT,
        participant_count=7020,
    )


@pytest.fixture
def sample_documents(sample_document: IngestedDocument) -> list[IngestedDocument]:
    """Return a list of sample documents for batch testing."""
    return [sample_document] * 3  # Duplicate for simplicity


# ── PICO extraction fixtures ──────────────────────────────────────────────────

@pytest.fixture
def sample_pico_result(sample_pubmed_abstract: str) -> PICOResult:
    """Return a sample PICOResult for testing."""
    return PICOResult(
        abstract_text=sample_pubmed_abstract,
        source_id="26378978",
        population=[
            EntitySpan(
                text="patients with type 2 diabetes",
                start=60,
                end=91,
                label=SpanLabel.POPULATION,
                confidence=0.92,
            )
        ],
        intervention=[
            EntitySpan(
                text="empagliflozin 10mg",
                start=200,
                end=218,
                label=SpanLabel.INTERVENTION,
                confidence=0.95,
            )
        ],
        comparator=[
            EntitySpan(
                text="placebo",
                start=220,
                end=227,
                label=SpanLabel.COMPARATOR,
                confidence=0.88,
            )
        ],
        outcomes=[
            EntitySpan(
                text="cardiovascular death",
                start=300,
                end=320,
                label=SpanLabel.OUTCOME,
                confidence=0.91,
            ),
            EntitySpan(
                text="hospitalization for heart failure",
                start=400,
                end=432,
                label=SpanLabel.OUTCOME,
                confidence=0.89,
            ),
        ],
    )


@pytest.fixture
def sample_extraction_batch(sample_pico_result: PICOResult) -> ExtractionBatch:
    """Return a sample ExtractionBatch for testing."""
    return ExtractionBatch(
        results=[sample_pico_result],
        total_processed=1,
        failed_count=0,
    )


# ── Triangulation fixtures ────────────────────────────────────────────────────

@pytest.fixture
def sample_relationship() -> ExtractedRelationship:
    """Return a sample ExtractedRelationship for testing."""
    return ExtractedRelationship(
        pmid="26378978",
        exposure="empagliflozin",
        exposure_direction="administration",
        outcome="cardiovascular mortality",
        effect_direction=EffectDirection.INHIBITORY,
        significance=SignificanceLabel.SIGNIFICANT,
        study_design=StudyDesignCategory.RCT,
        participant_count=7020,
        comparator="placebo",
        confidence=0.95,
        is_triangulation_eligible=True,
        exposure_match_score=0.95,
        outcome_match_score=0.90,
    )


@pytest.fixture
def sample_relationships(sample_relationship: ExtractedRelationship) -> list[ExtractedRelationship]:
    """Return a list of relationships for triangulation testing."""
    # Mix of directions for realistic testing
    relationships = [sample_relationship]
    relationships.append(
        ExtractedRelationship(
            pmid="12345678",
            exposure="empagliflozin",
            exposure_direction="administration",
            outcome="cardiovascular mortality",
            effect_direction=EffectDirection.INHIBITORY,
            significance=SignificanceLabel.SIGNIFICANT,
            study_design=StudyDesignCategory.META,
            participant_count=15000,
            confidence=0.88,
            is_triangulation_eligible=True,
            exposure_match_score=0.92,
            outcome_match_score=0.88,
        )
    )
    relationships.append(
        ExtractedRelationship(
            pmid="87654321",
            exposure="empagliflozin",
            exposure_direction="administration",
            outcome="cardiovascular mortality",
            effect_direction=EffectDirection.NO_CHANGE,
            significance=SignificanceLabel.NOT_SIGNIFICANT,
            study_design=StudyDesignCategory.OS,
            participant_count=3000,
            confidence=0.72,
            is_triangulation_eligible=True,
            exposure_match_score=0.85,
            outcome_match_score=0.80,
        )
    )
    return relationships


@pytest.fixture
def sample_triangulation_result(
    sample_relationships: list[ExtractedRelationship],
) -> TriangulationResult:
    """Return a sample TriangulationResult for testing."""
    return TriangulationResult(
        question="Does empagliflozin reduce cardiovascular mortality in T2DM?",
        exposure="empagliflozin",
        outcome="cardiovascular mortality",
        coe_scores=CoEScores(
            p_excitatory=0.05,
            p_no_change=0.12,
            p_inhibitory=0.83,
        ),
        loe=0.745,
        effect_direction=EffectDirection.INHIBITORY,
        relationships=sample_relationships,
        papers_analyzed=50,
        papers_eligible=3,
        rct_count=1,
        meta_count=1,
        os_count=1,
    )


# ── Mock fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Return a mock OpenAI client for LLM-dependent tests."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()

    # Default response for entity extraction
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "exposure_found": True,
        "exposure_text": "empagliflozin",
        "exposure_direction": "administration",
        "outcome_found": True,
        "outcome_text": "cardiovascular mortality",
        "study_design": "RCT",
        "participant_count": 7020,
        "comparator": "placebo",
    })
    client.chat.completions.create = AsyncMock(return_value=mock_response)
    return client


SAMPLE_PUBMED_XML = """<?xml version="1.0" ?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2019//EN"
  "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_190101.dtd">
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation Status="MEDLINE" Owner="NLM">
      <PMID Version="1">26378978</PMID>
      <Article PubModel="Print">
        <Journal>
          <Title>New England Journal of Medicine</Title>
          <JournalIssue>
            <PubDate><Year>2015</Year><Month>Nov</Month><Day>26</Day></PubDate>
          </JournalIssue>
        </Journal>
        <ArticleTitle>Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes</ArticleTitle>
        <Abstract>
          <AbstractText Label="BACKGROUND">The cardiovascular effects of SGLT2 inhibitors remain an active area.</AbstractText>
          <AbstractText Label="METHODS">Randomized double-blind trial, n=7020.</AbstractText>
          <AbstractText Label="RESULTS">Empagliflozin reduced cardiovascular death (HR 0.62, p&lt;0.001).</AbstractText>
          <AbstractText Label="CONCLUSIONS">Empagliflozin significantly reduced cardiovascular outcomes.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author ValidYN="Y">
            <LastName>Zinman</LastName>
            <ForeName>Bernard</ForeName>
          </Author>
        </AuthorList>
        <PublicationTypeList>
          <PublicationType UI="D016449">Randomized Controlled Trial</PublicationType>
        </PublicationTypeList>
        <ELocationID EIdType="doi">10.1056/NEJMoa1504720</ELocationID>
      </Article>
      <MeshHeadingList>
        <MeshHeading>
          <DescriptorName UI="D003924" MajorTopicYN="Y">Diabetes Mellitus, Type 2</DescriptorName>
        </MeshHeading>
      </MeshHeadingList>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="pubmed">26378978</ArticleId>
        <ArticleId IdType="doi">10.1056/NEJMoa1504720</ArticleId>
      </ArticleIdList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>"""
