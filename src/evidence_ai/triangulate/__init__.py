"""Evidence triangulation module.

Implements the Convergence of Evidence (CoE) and Level of Evidence (LoE)
algorithm from the Peking University llm-evidence-triangulation paper.

The algorithm:
1. Extracts exposure-outcome relationships from abstracts using LLM
2. Groups findings by study design × effect direction
3. Weights by participant count within design categories
4. Computes p_excitatory, p_no_change, p_inhibitory
5. Computes LoE = (max(p) - 1/3) / (2/3)

Based on:
  https://github.com/xuanyshi/llm-evidence-triangulation
  (Peking University, medRxiv 2024, MIT License)
"""

from evidence_ai.triangulate.engine import TriangulationEngine
from evidence_ai.triangulate.models import TriangulationResult

__all__ = ["TriangulationEngine", "TriangulationResult"]
