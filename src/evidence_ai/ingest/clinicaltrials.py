"""ClinicalTrials.gov API v2 connector.

Fetches clinical trial records from ClinicalTrials.gov using the v2 REST API
(https://clinicaltrials.gov/data-api/api). Supports full-text search, filtering
by status, phase, condition, and intervention.

API documentation: https://clinicaltrials.gov/data-api/about-api/v2-api-migration
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from evidence_ai.config import Settings, get_settings
from evidence_ai.ingest.models import DocumentSource, IngestedDocument, StudyDesign

logger = logging.getLogger(__name__)

CT_API_BASE = "https://clinicaltrials.gov/api/v2"
CT_STUDIES_URL = f"{CT_API_BASE}/studies"

# ClinicalTrials study type → StudyDesign mapping
CT_STUDY_TYPE_MAP: dict[str, StudyDesign] = {
    "INTERVENTIONAL": StudyDesign.RCT,
    "OBSERVATIONAL": StudyDesign.OS,
    "EXPANDED_ACCESS": StudyDesign.OTHER,
}

# Fields to request from the API
CT_FIELDS = [
    "NCTId",
    "BriefTitle",
    "OfficialTitle",
    "BriefSummary",
    "DetailedDescription",
    "OverallStatus",
    "Phase",
    "StudyType",
    "StartDate",
    "PrimaryCompletionDate",
    "LeadSponsorName",
    "Condition",
    "InterventionName",
    "PrimaryOutcomeMeasure",
    "SecondaryOutcomeMeasure",
    "EnrollmentCount",
    "LocationCountry",
]


class ClinicalTrialsFetcher:
    """Fetch clinical trial records from ClinicalTrials.gov API v2.

    Args:
        settings: Application settings. Defaults to the global settings singleton.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def search(
        self,
        query: str,
        max_results: int = 200,
        status_filter: list[str] | None = None,
        phase_filter: list[str] | None = None,
    ) -> list[IngestedDocument]:
        """Search ClinicalTrials.gov for matching studies.

        Args:
            query: Free-text search query. Searches condition, intervention,
                title, and brief summary fields.
            max_results: Maximum number of records to return (capped at 1000).
            status_filter: Optional list of recruitment statuses to filter by.
                Options: ``"RECRUITING"``, ``"COMPLETED"``, ``"ACTIVE_NOT_RECRUITING"``.
            phase_filter: Optional list of trial phases.
                Options: ``"PHASE1"``, ``"PHASE2"``, ``"PHASE3"``, ``"PHASE4"``.

        Returns:
            List of :class:`~evidence_ai.ingest.models.IngestedDocument` objects.
        """
        max_results = min(max_results, 1000)
        all_docs: list[IngestedDocument] = []
        page_token: str | None = None

        while len(all_docs) < max_results:
            batch_size = min(100, max_results - len(all_docs))
            results, next_token = await self._fetch_page(
                query=query,
                page_size=batch_size,
                page_token=page_token,
                status_filter=status_filter,
                phase_filter=phase_filter,
            )
            all_docs.extend(results)

            if not next_token or not results:
                break
            page_token = next_token

        logger.info(
            "ClinicalTrials.gov: found %d studies for query %r",
            len(all_docs),
            query[:80],
        )
        return all_docs

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    async def _fetch_page(
        self,
        query: str,
        page_size: int = 100,
        page_token: str | None = None,
        status_filter: list[str] | None = None,
        phase_filter: list[str] | None = None,
    ) -> tuple[list[IngestedDocument], str | None]:
        """Fetch a single page of results from the ClinicalTrials API v2."""
        params: dict[str, Any] = {
            "query.term": query,
            "pageSize": page_size,
            "fields": ",".join(CT_FIELDS),
            "format": "json",
        }

        if page_token:
            params["pageToken"] = page_token

        if status_filter:
            params["filter.overallStatus"] = "|".join(status_filter)

        if phase_filter:
            params["filter.phase"] = "|".join(phase_filter)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(CT_STUDIES_URL, params=params)
            response.raise_for_status()

        data = response.json()
        studies = data.get("studies", [])
        next_page_token = data.get("nextPageToken")

        documents = [
            self._parse_study(study)
            for study in studies
            if study
        ]
        return [d for d in documents if d is not None], next_page_token

    def _parse_study(self, study: dict[str, Any]) -> IngestedDocument | None:
        """Parse a single ClinicalTrials.gov study record."""
        try:
            protocol = study.get("protocolSection", {})
            id_module = protocol.get("identificationModule", {})
            desc_module = protocol.get("descriptionModule", {})
            status_module = protocol.get("statusModule", {})
            design_module = protocol.get("designModule", {})
            arms_module = protocol.get("armsInterventionsModule", {})
            outcomes_module = protocol.get("outcomesModule", {})
            eligibility_module = protocol.get("eligibilityModule", {})

            nct_id = id_module.get("nctId", "")
            title = id_module.get("briefTitle") or id_module.get("officialTitle", "")
            abstract = desc_module.get("briefSummary") or desc_module.get("detailedDescription")

            # Study type → design
            study_type = design_module.get("studyType", "").upper()
            study_design = CT_STUDY_TYPE_MAP.get(study_type, StudyDesign.OTHER)

            # For interventional trials, refine based on phase
            phases = design_module.get("phases", [])
            if "PHASE3" in phases or "PHASE4" in phases:
                study_design = StudyDesign.RCT

            # Enrollment count
            enrollment_info = design_module.get("enrollmentInfo", {})
            enrollment = enrollment_info.get("count")

            # Primary outcome as pseudo-abstract
            primary_outcomes = [
                o.get("measure", "")
                for o in outcomes_module.get("primaryOutcomes", [])
                if o.get("measure")
            ]

            # Build interventions list
            interventions = [
                i.get("name", "")
                for i in arms_module.get("interventions", [])
                if i.get("name")
            ]

            # Conditions
            conditions = protocol.get("conditionsModule", {}).get("conditions", [])

            return IngestedDocument(
                source=DocumentSource.CLINICALTRIALS,
                source_id=nct_id,
                nct_id=nct_id,
                title=title,
                abstract=abstract,
                study_design=study_design,
                participant_count=enrollment,
                publication_types=phases,
                raw_data={
                    "interventions": interventions,
                    "conditions": conditions,
                    "primary_outcomes": primary_outcomes,
                    "overall_status": status_module.get("overallStatus"),
                    "phase": phases,
                },
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to parse ClinicalTrials study: %s", e)
            return None

    async def get_by_nct_id(self, nct_id: str) -> IngestedDocument | None:
        """Fetch a single trial by NCT ID.

        Args:
            nct_id: ClinicalTrials.gov identifier (e.g. ``"NCT03819153"``).

        Returns:
            Parsed :class:`~evidence_ai.ingest.models.IngestedDocument` or None.
        """
        url = f"{CT_STUDIES_URL}/{nct_id}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params={"format": "json"})
                response.raise_for_status()
            return self._parse_study(response.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
