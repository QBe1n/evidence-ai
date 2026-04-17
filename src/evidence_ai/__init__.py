"""EvidenceAI — AI-powered clinical evidence synthesis for FDA submissions.

EvidenceAI automates systematic literature reviews (SLRs) for biotech and
pharmaceutical companies preparing FDA submissions. The platform runs a
6-stage pipeline: Ingest → Extract → Triangulate → Augment → Summarize → Deliver.

Built on MIT-licensed academic research from:
- Columbia University ebmlab (PICOX, EvidenceOutcomes, MedReview)
- Peking University (llm-evidence-triangulation)
- Georgia Tech (TrialSynth)

Example usage::

    from evidence_ai import EvidenceAI

    client = EvidenceAI(openai_api_key="sk-...")
    review = await client.synthesize(
        question="Does semaglutide reduce cardiovascular mortality in T2DM?",
        max_papers=500,
    )
    print(review.level_of_evidence)  # 0.91
    review.export_fda_package("./output/")

"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "EvidenceAI Contributors"
__license__ = "MIT"

from evidence_ai.client import EvidenceAI

__all__ = ["EvidenceAI", "__version__"]
