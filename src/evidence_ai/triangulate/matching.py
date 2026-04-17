"""Concept matching and normalization for evidence triangulation.

Implements deterministic LLM-based concept matching (temperature=0) to
determine whether extracted exposure and outcome terms match the target
clinical question concepts.

Based on Step 3 of the llm-evidence-triangulation pipeline:
  https://github.com/xuanyshi/llm-evidence-triangulation
  (Peking University, medRxiv 2024, MIT License)
"""

from __future__ import annotations

import logging
from functools import lru_cache

from evidence_ai.triangulate.prompts import build_concept_matching_messages

logger = logging.getLogger(__name__)


class ConceptMatcher:
    """Deterministic LLM-based concept matching.

    Uses a temperature=0 LLM call to determine whether an extracted term
    matches a target canonical concept. Results are cached to avoid redundant
    API calls.

    Args:
        llm_client: An async LLM client with a ``chat_complete`` method.
            Compatible with the OpenAI Python client interface.
        model: LLM model to use for matching (temperature=0).
    """

    def __init__(self, llm_client: object, model: str = "gpt-4o-mini") -> None:
        self._client = llm_client
        self._model = model

    async def matches(
        self,
        extracted_term: str,
        target_concept: str,
        cache: dict[tuple[str, str], bool] | None = None,
    ) -> bool:
        """Determine whether extracted_term matches the target_concept.

        Uses a deterministic (temperature=0) LLM call. Result is cached
        by (extracted_term, target_concept) pair to avoid repeated API calls.

        Args:
            extracted_term: The term as extracted from a paper abstract.
            target_concept: The canonical concept from the clinical question.
            cache: Optional external dict cache. Keys are (extracted, target) tuples.

        Returns:
            True if the terms are considered to refer to the same concept.
        """
        cache_key = (extracted_term.lower().strip(), target_concept.lower().strip())

        if cache is not None and cache_key in cache:
            return cache[cache_key]

        # Also check simple string matching to avoid unnecessary LLM calls
        if self._trivial_match(extracted_term, target_concept):
            result = True
        else:
            result = await self._llm_match(extracted_term, target_concept)

        if cache is not None:
            cache[cache_key] = result

        return result

    def _trivial_match(self, term: str, concept: str) -> bool:
        """Check for trivial string-based matches to avoid LLM calls."""
        t = term.lower().strip()
        c = concept.lower().strip()

        if t == c:
            return True
        if t in c or c in t:
            return True

        # Common abbreviation handling
        abbreviations: dict[str, list[str]] = {
            "t2dm": ["type 2 diabetes", "type 2 diabetes mellitus", "diabetes mellitus"],
            "cvd": ["cardiovascular disease", "cardiovascular"],
            "bp": ["blood pressure"],
            "mi": ["myocardial infarction", "heart attack"],
            "hf": ["heart failure"],
            "rct": ["randomized controlled trial"],
            "os": ["observational study"],
        }

        for abbrev, expansions in abbreviations.items():
            if (t == abbrev and c in expansions) or (c == abbrev and t in expansions):
                return True

        return False

    async def _llm_match(self, extracted_term: str, target_concept: str) -> bool:
        """Run a temperature=0 LLM call for concept matching."""
        messages = build_concept_matching_messages(extracted_term, target_concept)

        try:
            # TODO: Replace with actual LLM client call
            # The interface expects an OpenAI-compatible async client
            #
            # response = await self._client.chat.completions.create(
            #     model=self._model,
            #     messages=messages,
            #     temperature=0,
            #     max_tokens=5,
            # )
            # answer = response.choices[0].message.content.strip().lower()
            # return answer.startswith("yes")
            logger.debug(
                "Concept matching stub: %r vs %r",
                extracted_term,
                target_concept,
            )
            return False  # Stub returns False until LLM client is wired
        except Exception as e:  # noqa: BLE001
            logger.warning("Concept matching LLM call failed: %s", e)
            return False

    async def match_batch(
        self,
        pairs: list[tuple[str, str]],
        cache: dict[tuple[str, str], bool] | None = None,
    ) -> list[bool]:
        """Match a batch of (extracted_term, target_concept) pairs.

        Args:
            pairs: List of (extracted_term, target_concept) tuples.
            cache: Optional external cache.

        Returns:
            List of bool values, one per input pair.
        """
        import asyncio
        results = await asyncio.gather(*[
            self.matches(extracted, target, cache=cache)
            for extracted, target in pairs
        ])
        return list(results)


@lru_cache(maxsize=256)
def normalize_study_design(raw_design: str) -> str:
    """Normalize a raw study design string to a canonical category.

    Args:
        raw_design: Raw study design string from LLM extraction.

    Returns:
        Canonical study design category (``"RCT"``, ``"OS"``, etc.).
    """
    design = raw_design.upper().strip()
    mappings = {
        "RCT": "RCT",
        "RANDOMIZED": "RCT",
        "RANDOMIZED CONTROLLED TRIAL": "RCT",
        "CLINICAL TRIAL": "RCT",
        "OS": "OS",
        "OBSERVATIONAL": "OS",
        "OBSERVATIONAL STUDY": "OS",
        "COHORT": "OS",
        "CASE-CONTROL": "OS",
        "CROSS-SECTIONAL": "OS",
        "MR": "MR",
        "MENDELIAN RANDOMIZATION": "MR",
        "META": "META",
        "META-ANALYSIS": "META",
        "META ANALYSIS": "META",
        "SR": "SR",
        "SYSTEMATIC REVIEW": "SR",
        "REVIEW": "REVIEW",
        "NARRATIVE REVIEW": "REVIEW",
    }
    return mappings.get(design, "OTHER")
