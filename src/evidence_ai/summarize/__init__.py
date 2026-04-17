"""Evidence summarization module.

Generates regulatory-ready evidence narratives from triangulation results
using a fine-tuned LLM (based on the MedReview dataset from Columbia ebmlab).

Based on:
  https://github.com/ebmlab/MedReview
  (Columbia University ebmlab, npj Digital Medicine 2024, MIT License)

Dataset: 8,575 abstract-conclusion pairs from the Cochrane Library
(37 medical topics, 1996–2023).

Key finding from the MedReview paper:
  Fine-tuned open-source LLMs (PRIMERA, LongT5, Llama-2) match or exceed
  GPT-4 on medical evidence summarization — critical for production where
  cost, latency, and data privacy matter.
"""

from evidence_ai.summarize.models import EvidenceReview
from evidence_ai.summarize.narrative import NarrativeGenerator
from evidence_ai.summarize.regulatory import RegulatoryFormatter

__all__ = ["NarrativeGenerator", "EvidenceReview", "RegulatoryFormatter"]
