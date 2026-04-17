"""Tests for the PubMed fetcher module.

Tests cover:
- XML parsing of PubMed records
- esearch query building
- Rate limiting behavior
- Redis cache hit/miss
- Error handling for malformed XML
"""

from __future__ import annotations

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx
import httpx

from tests.conftest import SAMPLE_PUBMED_XML
from evidence_ai.ingest.models import DocumentSource, IngestedDocument, StudyDesign
from evidence_ai.ingest.pubmed import (
    PubMedFetcher,
    build_clinical_question_query,
)


# ── XML parsing tests ─────────────────────────────────────────────────────────

class TestPubMedXMLParsing:
    """Test the XML parsing logic without network calls."""

    def test_parse_single_article(self, test_settings):
        """Should parse a PubMed XML record into an IngestedDocument."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml(SAMPLE_PUBMED_XML)

        assert len(docs) == 1
        doc = docs[0]

        assert doc.pmid == "26378978"
        assert doc.doi == "10.1056/NEJMoa1504720"
        assert "Empagliflozin" in doc.title
        assert doc.journal == "New England Journal of Medicine"
        assert doc.publication_date == date(2015, 11, 26)
        assert doc.source == DocumentSource.PUBMED

    def test_parse_authors(self, test_settings):
        """Should correctly extract author names."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml(SAMPLE_PUBMED_XML)
        doc = docs[0]

        assert "Zinman, Bernard" in doc.authors

    def test_parse_publication_types(self, test_settings):
        """Should extract publication type as RCT."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml(SAMPLE_PUBMED_XML)
        doc = docs[0]

        assert "Randomized Controlled Trial" in doc.publication_types
        assert doc.study_design == StudyDesign.RCT

    def test_parse_mesh_terms(self, test_settings):
        """Should extract MeSH terms with major topic indicator."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml(SAMPLE_PUBMED_XML)
        doc = docs[0]

        assert len(doc.mesh_terms) >= 1
        major_terms = [t for t in doc.mesh_terms if t.is_major]
        assert any("Diabetes" in t.descriptor for t in major_terms)

    def test_parse_abstract_sections(self, test_settings):
        """Should parse structured abstract sections."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml(SAMPLE_PUBMED_XML)
        doc = docs[0]

        assert len(doc.abstract_sections) == 4
        labels = {s.label for s in doc.abstract_sections}
        assert "BACKGROUND" in labels
        assert "RESULTS" in labels

    def test_parse_malformed_xml_returns_empty(self, test_settings):
        """Should return empty list for malformed XML without raising."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml("<not valid xml!")

        assert docs == []

    def test_parse_empty_pubmed_set(self, test_settings):
        """Should return empty list for PubMedArticleSet with no articles."""
        fetcher = PubMedFetcher(settings=test_settings)
        docs = fetcher._parse_pubmed_xml(
            '<?xml version="1.0"?><PubmedArticleSet></PubmedArticleSet>'
        )
        assert docs == []


# ── Query building tests ───────────────────────────────────────────────────────

class TestQueryBuilding:
    """Test query construction utilities."""

    def test_basic_question_query(self, test_settings):
        """Should build a correct PubMed query from PICO components."""
        query = build_clinical_question_query(
            exposure="SGLT2 inhibitor",
            outcome="heart failure hospitalization",
        )
        assert "SGLT2 inhibitor" in query
        assert "heart failure hospitalization" in query

    def test_query_with_population(self, test_settings):
        """Should include population filter when provided."""
        query = build_clinical_question_query(
            exposure="empagliflozin",
            outcome="cardiovascular mortality",
            population="type 2 diabetes",
        )
        assert "type 2 diabetes" in query
        assert "empagliflozin" in query
        assert "cardiovascular mortality" in query

    def test_query_with_study_design_filter(self, test_settings):
        """Should include publication type filters."""
        query = build_clinical_question_query(
            exposure="semaglutide",
            outcome="weight loss",
            study_designs=["Randomized Controlled Trial", "Meta-Analysis"],
        )
        assert "Randomized Controlled Trial" in query
        assert "Meta-Analysis" in query
        assert "Publication Type" in query

    def test_query_with_date_range(self, test_settings):
        """Should add date range to the query."""
        fetcher = PubMedFetcher(settings=test_settings)
        full_query = fetcher._build_query(
            query="empagliflozin cardiovascular",
            date_range={"start": "2015-01-01", "end": "2020-12-31"},
            study_design_filter=None,
        )
        assert "2015" in full_query
        assert "2020" in full_query
        assert "Date - Publication" in full_query


# ── Network call tests ────────────────────────────────────────────────────────

class TestPubMedNetworkCalls:
    """Test PubMed API calls with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_efetch_chunk_parses_response(self, test_settings):
        """Should fetch and parse articles for a list of PMIDs."""
        fetcher = PubMedFetcher(settings=test_settings)

        with respx.mock:
            respx.get(url__startswith="https://eutils.ncbi.nlm.nih.gov").mock(
                return_value=httpx.Response(200, text=SAMPLE_PUBMED_XML)
            )

            docs = await fetcher._efetch_chunk(["26378978"])

        assert len(docs) == 1
        assert docs[0].pmid == "26378978"

    @pytest.mark.asyncio
    async def test_esearch_returns_pmid_list(self, test_settings):
        """Should return a list of PMIDs from esearch response."""
        fetcher = PubMedFetcher(settings=test_settings)

        mock_esearch = {
            "esearchresult": {
                "count": "3",
                "retmax": "3",
                "idlist": ["26378978", "29874584", "31007106"],
            }
        }

        with respx.mock:
            respx.get(url__startswith="https://eutils.ncbi.nlm.nih.gov").mock(
                return_value=httpx.Response(200, json=mock_esearch)
            )

            pmids = await fetcher._esearch("empagliflozin cardiovascular", 100)

        assert len(pmids) == 3
        assert "26378978" in pmids

    @pytest.mark.asyncio
    async def test_http_error_raises_after_retries(self, test_settings):
        """Should raise after max retries on persistent 500 errors."""
        fetcher = PubMedFetcher(settings=test_settings)

        with respx.mock:
            respx.get(url__startswith="https://eutils.ncbi.nlm.nih.gov").mock(
                return_value=httpx.Response(500, text="Internal Server Error")
            )

            with pytest.raises(httpx.HTTPStatusError):
                await fetcher._efetch_chunk(["26378978"])


# ── Cache tests ────────────────────────────────────────────────────────────────

class TestPubMedCache:
    """Test Redis caching behavior."""

    @pytest.mark.asyncio
    async def test_cache_miss_falls_through(self, test_settings, sample_document):
        """Should return empty cache and all PMIDs as uncached on miss."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)  # Cache miss

        fetcher = PubMedFetcher(settings=test_settings, redis_client=mock_redis)
        cached, uncached = await fetcher._check_cache(["26378978"])

        assert cached == []
        assert uncached == ["26378978"]

    @pytest.mark.asyncio
    async def test_cache_hit_returns_document(self, test_settings, sample_document):
        """Should return cached document and empty uncached list on hit."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_document.model_dump_json())

        fetcher = PubMedFetcher(settings=test_settings, redis_client=mock_redis)
        cached, uncached = await fetcher._check_cache(["26378978"])

        assert len(cached) == 1
        assert cached[0].pmid == "26378978"
        assert uncached == []


# ── IngestedDocument model tests ──────────────────────────────────────────────

class TestIngestedDocument:
    """Test IngestedDocument model properties."""

    def test_full_abstract_text_from_abstract(self, sample_document):
        """Should return abstract text directly when abstract field is set."""
        assert len(sample_document.full_abstract_text) > 100
        assert "empagliflozin" in sample_document.full_abstract_text.lower()

    def test_is_rct_from_publication_type(self, sample_document):
        """Should correctly identify RCTs from publication types."""
        assert sample_document.is_rct is True

    def test_is_not_rct_for_review(self, sample_document):
        """Should return False for non-RCT publication types."""
        sample_document.publication_types = ["Review"]
        sample_document.study_design = StudyDesign.REVIEW
        assert sample_document.is_rct is False
