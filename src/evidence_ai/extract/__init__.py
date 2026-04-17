"""PICO entity extraction module.

Extracts Population, Intervention, Comparator, and Outcome entities from
clinical trial abstracts using a two-stage pipeline:

1. **PICOX** (Columbia University): PubMedBERT-based overlapping span extraction
   for Population, Intervention, and Outcome entities.

2. **EvidenceOutcomes** (Columbia University): Specialized BiomedBERT-based
   model for high-precision clinical outcome detection. Used as a refinement
   layer on top of PICOX output.

Based on:
- https://github.com/ebmlab/PICOX (JAMIA 2024, MIT License)
- https://github.com/ebmlab/EvidenceOutcomes (Dataset 2024, MIT License)
"""

from evidence_ai.extract.outcomes import OutcomeExtractor
from evidence_ai.extract.pico import PICOExtractor

__all__ = ["PICOExtractor", "OutcomeExtractor"]
