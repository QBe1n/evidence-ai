"""Literature ingestion module.

Connects to PubMed eUtils, ClinicalTrials.gov API v2, and FDA Drugs@FDA
to collect research papers, trial records, and regulatory documents.

Exportable classes::

    from evidence_ai.ingest import PubMedFetcher, ClinicalTrialsFetcher, FDAFetcher
"""

from evidence_ai.ingest.clinicaltrials import ClinicalTrialsFetcher
from evidence_ai.ingest.fda import FDAFetcher
from evidence_ai.ingest.pubmed import PubMedFetcher

__all__ = ["PubMedFetcher", "ClinicalTrialsFetcher", "FDAFetcher"]
