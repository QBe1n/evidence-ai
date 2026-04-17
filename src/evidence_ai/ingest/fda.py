"""FDA Drugs@FDA and clinical review document connector.

Interfaces with:
- openFDA drugs API (https://api.fda.gov/drug/): drug approvals, labels
- Drugs@FDA database: application numbers, approval histories
- FDA clinical review documents (PDF extraction — TODO)

API docs: https://open.fda.gov/apis/drug/
"""

from __future__ import annotations

import logging
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from evidence_ai.config import Settings, get_settings
from evidence_ai.ingest.models import DocumentSource, IngestedDocument, StudyDesign

logger = logging.getLogger(__name__)

OPENFDA_DRUG_EVENT = "https://api.fda.gov/drug/event.json"
OPENFDA_DRUG_LABEL = "https://api.fda.gov/drug/label.json"
OPENFDA_DRUG_APPROVAL = "https://api.fda.gov/drug/drugsfda.json"

FDA_APPROVAL_TYPE_MAP: dict[str, str] = {
    "NDA": "New Drug Application",
    "BLA": "Biologics License Application",
    "ANDA": "Abbreviated New Drug Application",
    "NDA authorized generic": "Authorized Generic",
}


class FDAFetcher:
    """Fetch drug approval data and regulatory documents from openFDA.

    Args:
        settings: Application settings. Defaults to the global settings singleton.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

        self._base_params: dict[str, str] = {}
        if self._settings.fda_openfda_api_key:
            self._base_params["api_key"] = self._settings.fda_openfda_api_key

    async def search_drug_approvals(
        self,
        drug_name: str,
        max_results: int = 50,
    ) -> list[IngestedDocument]:
        """Search FDA Drugs@FDA for approved applications containing the drug.

        Args:
            drug_name: Drug name (generic or brand).
            max_results: Maximum number of records to return.

        Returns:
            List of :class:`~evidence_ai.ingest.models.IngestedDocument` objects
            representing FDA drug applications.
        """
        query = f'openfda.generic_name:"{drug_name}" OR openfda.brand_name:"{drug_name}"'

        try:
            results = await self._query_openfda(
                OPENFDA_DRUG_APPROVAL,
                search=query,
                limit=max_results,
            )
        except httpx.HTTPStatusError as e:
            logger.warning("FDA approval search failed for %r: %s", drug_name, e)
            return []

        documents = []
        for result in results.get("results", []):
            doc = self._parse_approval(result)
            if doc:
                documents.append(doc)

        logger.info(
            "FDA Drugs@FDA: found %d applications for %r",
            len(documents),
            drug_name,
        )
        return documents

    async def get_drug_label(self, drug_name: str) -> dict[str, Any] | None:
        """Fetch the current FDA drug label (prescribing information).

        Args:
            drug_name: Generic or brand name of the drug.

        Returns:
            Label data as a dictionary or None if not found.
        """
        query = (
            f'openfda.generic_name:"{drug_name}" OR openfda.brand_name:"{drug_name}"'
        )
        try:
            results = await self._query_openfda(OPENFDA_DRUG_LABEL, search=query, limit=1)
            return results.get("results", [None])[0]
        except httpx.HTTPStatusError:
            return None

    @retry(
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(4),
        reraise=True,
    )
    async def _query_openfda(
        self,
        endpoint: str,
        search: str,
        limit: int = 100,
        skip: int = 0,
    ) -> dict[str, Any]:
        """Query an openFDA API endpoint."""
        params: dict[str, Any] = {
            **self._base_params,
            "search": search,
            "limit": min(limit, 1000),
            "skip": skip,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()

        return response.json()  # type: ignore[no-any-return]

    def _parse_approval(self, data: dict[str, Any]) -> IngestedDocument | None:
        """Parse a single Drugs@FDA application record."""
        try:
            app_number = data.get("application_number", "")
            openfda = data.get("openfda", {})

            brand_names = openfda.get("brand_name", [])
            generic_names = openfda.get("generic_name", [])
            sponsor = data.get("sponsor_name", "")
            submissions = data.get("submissions", [])

            title = (
                f"{brand_names[0] if brand_names else 'Unknown'} "
                f"({generic_names[0] if generic_names else 'Unknown'}) — "
                f"FDA {app_number}"
            )

            # Build abstract from submissions
            abstract_parts = [
                f"Application: {app_number}",
                f"Sponsor: {sponsor}",
            ]
            if brand_names:
                abstract_parts.append(f"Brand name(s): {', '.join(brand_names)}")
            if generic_names:
                abstract_parts.append(f"Generic name(s): {', '.join(generic_names)}")

            # Most recent submission
            if submissions:
                latest = submissions[-1]
                submission_type = latest.get("submission_type", "")
                submission_status = latest.get("submission_status", "")
                submission_date = latest.get("submission_status_date", "")
                abstract_parts.append(
                    f"Latest submission: {submission_type} ({submission_status}) "
                    f"as of {submission_date}"
                )

            abstract = "\n".join(abstract_parts)

            return IngestedDocument(
                source=DocumentSource.FDA,
                source_id=app_number,
                title=title,
                abstract=abstract,
                study_design=StudyDesign.OTHER,
                raw_data=data,
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("Failed to parse FDA approval record: %s", e)
            return None
