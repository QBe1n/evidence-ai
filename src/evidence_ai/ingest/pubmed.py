"""PubMed eUtils connector — search and fetch with rate limiting and caching.

Implements:
- ``esearch``: Query PubMed for matching PMIDs
- ``efetch``: Fetch full XML records by PMID list
- Rate limiting: respects NCBI's 3 req/s (10 req/s with API key)
- Exponential backoff retry via ``tenacity``
- Redis caching to avoid repeat fetches during a session

Based on the PubMed fetcher from:
  https://github.com/xuanyshi/llm-evidence-triangulation
  (Peking University, MIT License)

Enhancements over the source:
- Added ``esearch`` for dynamic query-based discovery (original only accepted PMID lists)
- Replaced ``time.sleep`` with async rate limiting
- Added Redis caching with configurable TTL
- Added proper retry logic with exponential backoff
- Returns ``IngestedDocument`` Pydantic models instead of DataFrames
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from datetime import date
from typing import Any
from xml.etree import ElementTree as ET

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from evidence_ai.config import Settings, get_settings
from evidence_ai.ingest.models import (
    AbstractSection,
    DocumentSource,
    IngestedDocument,
    MeshTerm,
    StudyDesign,
)

logger = logging.getLogger(__name__)

# NCBI eUtils base URL
EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ESEARCH_URL = f"{EUTILS_BASE}/esearch.fcgi"
EFETCH_URL = f"{EUTILS_BASE}/efetch.fcgi"

# Publication type → StudyDesign mapping
PUBTYPE_TO_DESIGN: dict[str, StudyDesign] = {
    "Randomized Controlled Trial": StudyDesign.RCT,
    "Clinical Trial, Phase III": StudyDesign.RCT,
    "Meta-Analysis": StudyDesign.META,
    "Systematic Review": StudyDesign.SR,
    "Review": StudyDesign.REVIEW,
    "Observational Study": StudyDesign.OS,
    "Case Reports": StudyDesign.CASE_REPORT,
}

# Chunk size for efetch requests (NCBI recommends ≤ 500)
FETCH_CHUNK_SIZE = 200


class PubMedFetcher:
    """Fetch and parse PubMed records using the NCBI eUtils API.

    Args:
        settings: Application settings. Defaults to the global settings singleton.
        redis_client: Optional Redis client for result caching. If None, caching
            is disabled.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        redis_client: Any | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._redis = redis_client
        self._last_request_time = 0.0
        self._min_interval = 1.0 / self._settings.ncbi_rate_limit

        self._base_params: dict[str, str] = {
            "db": "pubmed",
            "retmode": "json",
            "tool": "EvidenceAI",
            "email": self._settings.ncbi_email,
        }
        if self._settings.ncbi_api_key:
            self._base_params["api_key"] = self._settings.ncbi_api_key

    # ── Public API ─────────────────────────────────────────────────────────────

    async def search_and_fetch(
        self,
        query: str,
        max_results: int = 1000,
        date_range: dict[str, str] | None = None,
        study_design_filter: list[str] | None = None,
    ) -> list[IngestedDocument]:
        """Search PubMed and fetch full records for matching papers.

        Args:
            query: PubMed search query (MeSH terms, boolean operators supported).
            max_results: Maximum number of papers to return. Capped at 10,000.
            date_range: Optional dict with ``"start"`` and ``"end"`` keys in
                ``"YYYY-MM-DD"`` format to filter by publication date.
            study_design_filter: Optional list of publication types to restrict
                the search (e.g. ``["Randomized Controlled Trial"]``).

        Returns:
            List of :class:`~evidence_ai.ingest.models.IngestedDocument` objects.
        """
        max_results = min(max_results, 10_000)

        # Build the full query with optional filters
        full_query = self._build_query(query, date_range, study_design_filter)
        logger.info("PubMed search: %r (max=%d)", full_query[:120], max_results)

        # Step 1: Search for PMIDs
        pmids = await self._esearch(full_query, max_results)
        logger.info("esearch returned %d PMIDs", len(pmids))

        if not pmids:
            return []

        # Step 2: Fetch full records
        documents = await self.fetch_by_pmids(pmids)
        logger.info("Fetched %d documents from PubMed", len(documents))

        return documents

    async def fetch_by_pmids(self, pmids: list[str]) -> list[IngestedDocument]:
        """Fetch PubMed records for a list of PMIDs.

        Chunks requests into groups of :data:`FETCH_CHUNK_SIZE` to respect
        NCBI limits. Results from Redis cache are returned immediately without
        making network requests.

        Args:
            pmids: List of PubMed IDs as strings.

        Returns:
            List of parsed :class:`~evidence_ai.ingest.models.IngestedDocument` objects.
        """
        if not pmids:
            return []

        # Check cache first
        cached, uncached_pmids = await self._check_cache(pmids)
        logger.debug(
            "Cache: %d hits, %d misses for %d PMIDs",
            len(cached),
            len(uncached_pmids),
            len(pmids),
        )

        # Fetch uncached PMIDs in chunks
        fetched: list[IngestedDocument] = []
        for i in range(0, len(uncached_pmids), FETCH_CHUNK_SIZE):
            chunk = uncached_pmids[i : i + FETCH_CHUNK_SIZE]
            chunk_docs = await self._efetch_chunk(chunk)
            fetched.extend(chunk_docs)

            # Cache fetched results
            await self._cache_documents(chunk_docs)

        return cached + fetched

    # ── Private methods ────────────────────────────────────────────────────────

    def _build_query(
        self,
        query: str,
        date_range: dict[str, str] | None,
        study_design_filter: list[str] | None,
    ) -> str:
        """Build the full PubMed query string with optional filters."""
        parts = [query]

        if date_range:
            start = date_range.get("start", "1990/01/01").replace("-", "/")
            end = date_range.get("end", date.today().strftime("%Y/%m/%d")).replace("-", "/")
            parts.append(f'("{start}"[Date - Publication] : "{end}"[Date - Publication])')

        if study_design_filter:
            type_terms = " OR ".join(
                f'"{pt}"[Publication Type]' for pt in study_design_filter
            )
            parts.append(f"({type_terms})")

        return " AND ".join(parts)

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _esearch(self, query: str, max_results: int) -> list[str]:
        """Run PubMed esearch and return a list of PMIDs."""
        await self._rate_limit()

        params = {
            **self._base_params,
            "retmode": "json",
            "retmax": str(max_results),
            "term": query,
            "usehistory": "n",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(ESEARCH_URL, params=params)
            response.raise_for_status()

        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _efetch_chunk(self, pmids: list[str]) -> list[IngestedDocument]:
        """Fetch full XML records for a chunk of PMIDs and parse them."""
        await self._rate_limit()

        params = {
            **self._base_params,
            "retmode": "xml",
            "rettype": "abstract",
            "id": ",".join(pmids),
        }
        # Override retmode for efetch
        params["retmode"] = "xml"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(EFETCH_URL, params=params)
            response.raise_for_status()

        return self._parse_pubmed_xml(response.text)

    def _parse_pubmed_xml(self, xml_text: str) -> list[IngestedDocument]:
        """Parse PubMed XML response into IngestedDocument objects."""
        documents = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            logger.error("Failed to parse PubMed XML: %s", e)
            return []

        for article in root.findall(".//PubmedArticle"):
            try:
                doc = self._parse_article(article)
                if doc:
                    documents.append(doc)
            except Exception as e:  # noqa: BLE001
                pmid = article.findtext(".//PMID", default="unknown")
                logger.warning("Failed to parse article PMID=%s: %s", pmid, e)

        return documents

    def _parse_article(self, article: ET.Element) -> IngestedDocument | None:
        """Parse a single PubmedArticle XML element."""
        medline = article.find("MedlineCitation")
        if medline is None:
            return None

        # PMID
        pmid_el = medline.find("PMID")
        pmid = pmid_el.text.strip() if pmid_el is not None and pmid_el.text else None

        article_el = medline.find("Article")
        if article_el is None:
            return None

        # Title
        title_el = article_el.find("ArticleTitle")
        title = self._collect_text(title_el) if title_el is not None else ""

        # Abstract
        abstract_text, abstract_sections = self._parse_abstract(article_el)

        # Authors
        authors = self._parse_authors(article_el)

        # Journal
        journal_el = article_el.find("Journal/Title")
        journal = journal_el.text.strip() if journal_el is not None and journal_el.text else None

        # Publication date
        pub_date = self._parse_pub_date(article_el)

        # Publication types
        pub_types = [
            pt.text.strip()
            for pt in article_el.findall("PublicationTypeList/PublicationType")
            if pt.text
        ]

        # MeSH terms
        mesh_terms = self._parse_mesh_terms(medline)

        # Comment / corrections count
        comment_count = len(article.findall(".//CommentsCorrections"))

        # DOI
        doi = None
        for eid in article_el.findall("ELocationID"):
            if eid.get("EIdType") == "doi" and eid.text:
                doi = eid.text.strip()
                break

        # Infer study design from publication types
        study_design = None
        for pt in pub_types:
            if pt in PUBTYPE_TO_DESIGN:
                study_design = PUBTYPE_TO_DESIGN[pt]
                break

        return IngestedDocument(
            source=DocumentSource.PUBMED,
            source_id=pmid or "",
            pmid=pmid,
            doi=doi,
            title=title,
            abstract=abstract_text,
            abstract_sections=abstract_sections,
            authors=authors,
            journal=journal,
            publication_date=pub_date,
            publication_types=pub_types,
            mesh_terms=mesh_terms,
            study_design=study_design,
            comment_count=comment_count,
        )

    def _parse_abstract(
        self, article_el: ET.Element
    ) -> tuple[str | None, list[AbstractSection]]:
        """Parse abstract text and structured sections."""
        abstract_el = article_el.find("Abstract")
        if abstract_el is None:
            return None, []

        sections: list[AbstractSection] = []
        plain_texts: list[str] = []

        for text_el in abstract_el.findall("AbstractText"):
            text = self._collect_text(text_el)
            if not text:
                continue
            label = text_el.get("Label")
            if label:
                sections.append(AbstractSection(label=label, text=text))
            plain_texts.append(text)

        full_text = " ".join(plain_texts) if plain_texts else None
        return full_text, sections

    def _parse_authors(self, article_el: ET.Element) -> list[str]:
        """Parse author names from AuthorList."""
        authors = []
        for author in article_el.findall("AuthorList/Author"):
            last = author.findtext("LastName", default="")
            first = author.findtext("ForeName", default="")
            if last:
                authors.append(f"{last}, {first}".strip(", "))
            else:
                collective = author.findtext("CollectiveName", default="")
                if collective:
                    authors.append(collective)
        return authors

    def _parse_pub_date(self, article_el: ET.Element) -> date | None:
        """Parse publication date from the article."""
        pub_date_el = article_el.find("Journal/JournalIssue/PubDate")
        if pub_date_el is None:
            return None

        year_text = pub_date_el.findtext("Year")
        month_text = pub_date_el.findtext("Month", default="Jan")
        day_text = pub_date_el.findtext("Day", default="1")

        if not year_text:
            return None

        try:
            month_map = {
                "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
            }
            month = int(month_text) if month_text.isdigit() else month_map.get(month_text[:3], 1)
            return date(int(year_text), month, int(day_text))
        except (ValueError, TypeError):
            try:
                return date(int(year_text), 1, 1)
            except ValueError:
                return None

    def _parse_mesh_terms(self, medline: ET.Element) -> list[MeshTerm]:
        """Parse MeSH terms from MedlineCitation."""
        terms: list[MeshTerm] = []
        for heading in medline.findall("MeshHeadingList/MeshHeading"):
            descriptor_el = heading.find("DescriptorName")
            if descriptor_el is None or not descriptor_el.text:
                continue

            is_major = descriptor_el.get("MajorTopicYN") == "Y"
            qualifiers = [
                q.text.strip()
                for q in heading.findall("QualifierName")
                if q.text
            ]
            terms.append(
                MeshTerm(
                    descriptor=descriptor_el.text.strip(),
                    is_major=is_major,
                    qualifiers=qualifiers,
                )
            )
        return terms

    def _collect_text(self, element: ET.Element | None) -> str:
        """Collect all text content from an element, including nested tags."""
        if element is None:
            return ""
        return "".join(element.itertext()).strip()

    async def _rate_limit(self) -> None:
        """Enforce NCBI rate limiting between consecutive requests."""
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = time.monotonic()

    async def _check_cache(
        self, pmids: list[str]
    ) -> tuple[list[IngestedDocument], list[str]]:
        """Check Redis cache for previously fetched documents.

        Returns:
            Tuple of (cached_documents, uncached_pmids).
        """
        if self._redis is None:
            return [], pmids

        cached: list[IngestedDocument] = []
        uncached: list[str] = []

        for pmid in pmids:
            cache_key = f"pubmed:doc:{pmid}"
            try:
                data = await self._redis.get(cache_key)
                if data:
                    doc = IngestedDocument.model_validate_json(data)
                    cached.append(doc)
                else:
                    uncached.append(pmid)
            except Exception as e:  # noqa: BLE001
                logger.warning("Cache read error for PMID %s: %s", pmid, e)
                uncached.append(pmid)

        return cached, uncached

    async def _cache_documents(self, documents: list[IngestedDocument]) -> None:
        """Store fetched documents in Redis cache."""
        if self._redis is None:
            return

        for doc in documents:
            if not doc.pmid:
                continue
            cache_key = f"pubmed:doc:{doc.pmid}"
            try:
                await self._redis.setex(
                    cache_key,
                    self._settings.cache_ttl_seconds,
                    doc.model_dump_json(),
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("Cache write error for PMID %s: %s", doc.pmid, e)

    def _cache_key(self, query: str, max_results: int) -> str:
        """Generate a deterministic cache key for a search query."""
        h = hashlib.md5(f"{query}:{max_results}".encode()).hexdigest()[:12]
        return f"pubmed:search:{h}"


def build_clinical_question_query(
    exposure: str,
    outcome: str,
    population: str | None = None,
    study_designs: list[str] | None = None,
) -> str:
    """Build a PubMed query from clinical question components.

    Generates a structured PubMed query suitable for triangulation.

    Args:
        exposure: The intervention or exposure (e.g. "semaglutide").
        outcome: The clinical outcome (e.g. "cardiovascular mortality").
        population: Optional population restriction (e.g. "type 2 diabetes").
        study_designs: Optional list of publication types to restrict.

    Returns:
        PubMed-formatted query string.

    Example::

        query = build_clinical_question_query(
            exposure="SGLT2 inhibitor",
            outcome="heart failure hospitalization",
            population="type 2 diabetes",
            study_designs=["Randomized Controlled Trial", "Meta-Analysis"],
        )
        # '(SGLT2 inhibitor) AND (heart failure hospitalization) AND ...'
    """
    parts = [f"({exposure})", f"({outcome})"]

    if population:
        parts.append(f"({population})")

    if study_designs:
        type_filter = " OR ".join(f'"{pt}"[Publication Type]' for pt in study_designs)
        parts.append(f"({type_filter})")

    return " AND ".join(parts)
