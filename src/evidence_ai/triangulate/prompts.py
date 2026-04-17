"""Parameterized LLM prompt templates for evidence triangulation.

The original llm-evidence-triangulation repo hard-coded prompts for the
salt/sodium → CVD domain. This module generalizes all prompts to accept
arbitrary exposure-outcome specifications.

Based on:
  https://github.com/xuanyshi/llm-evidence-triangulation
  (Peking University, medRxiv 2024, MIT License)

Prompt engineering principles used:
- Two-step decomposition (entities first, then relationships)
- Few-shot examples with real PubMed abstracts
- Structured JSON output enforcement
- Constrained vocabularies for study design and significance
- Temperature=0 for concept matching (deterministic classification)
"""

from __future__ import annotations

from typing import Any


# ── Step 1: Entity Extraction ─────────────────────────────────────────────────

ENTITY_EXTRACTION_SYSTEM = """You are a biomedical NLP expert specializing in \
clinical evidence extraction. Extract exposure and outcome information from \
clinical study abstracts as structured JSON.

Always output valid JSON with the exact schema specified. Do not include \
explanatory text outside the JSON object."""

ENTITY_EXTRACTION_USER_TEMPLATE = """Extract the exposure and outcome from the \
following clinical study abstract.

EXPOSURE OF INTEREST: {exposure}
OUTCOME OF INTEREST: {outcome}

Abstract:
{abstract}

Return JSON with this exact schema:
{{
  "exposure_found": true/false,
  "exposure_text": "exact text from abstract describing the exposure",
  "exposure_direction": "increased" | "decreased" | "unchanged" | "not_specified",
  "outcome_found": true/false,
  "outcome_text": "exact text from abstract describing the outcome",
  "study_design": "RCT" | "OS" | "MR" | "META" | "SR" | "REVIEW" | "OTHER",
  "participant_count": number or null,
  "comparator": "control group description or null"
}}"""

ENTITY_EXTRACTION_FEW_SHOT_EXAMPLES = [
    {
        "abstract": (
            "Background: High sodium intake has been associated with elevated blood "
            "pressure. We conducted a randomized trial of sodium reduction in 412 "
            "adults with hypertension. After 6 weeks, participants in the low-sodium "
            "group (n=206) showed a 5.1 mmHg reduction in systolic BP vs placebo "
            "(p=0.002). Conclusion: Reducing dietary sodium significantly lowers "
            "systolic blood pressure in hypertensive adults."
        ),
        "exposure": "sodium intake",
        "outcome": "blood pressure",
        "output": {
            "exposure_found": True,
            "exposure_text": "sodium reduction",
            "exposure_direction": "decreased",
            "outcome_found": True,
            "outcome_text": "systolic BP",
            "study_design": "RCT",
            "participant_count": 412,
            "comparator": "placebo",
        },
    }
]


# ── Step 2: Relationship Extraction ───────────────────────────────────────────

RELATIONSHIP_EXTRACTION_SYSTEM = """You are a biomedical NLP expert. Given an \
abstract and extracted entities, determine the causal direction of the effect \
and its statistical significance.

Always output valid JSON. Use only the allowed values for each field."""

RELATIONSHIP_EXTRACTION_USER_TEMPLATE = """Given these extracted entities from a \
clinical study:

Exposure: {exposure_text} ({exposure_direction})
Outcome: {outcome_text}
Study design: {study_design}

Full abstract:
{abstract}

Determine the relationship and return JSON with this schema:
{{
  "effect_direction": "excitatory" | "inhibitory" | "no_change",
  "significance": "positive" | "negative",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation of your classification"
}}

Definitions:
- "excitatory": The exposure INCREASES the outcome
- "inhibitory": The exposure DECREASES or REDUCES the outcome
- "no_change": No statistically significant effect observed
- "positive" significance: p < 0.05 or equivalent statistical threshold met
- "negative" significance: Effect not statistically significant"""


# ── Step 3: Concept Matching ──────────────────────────────────────────────────
# Temperature=0 for deterministic classification

CONCEPT_MATCHING_SYSTEM = """You are a biomedical terminologist. Determine whether \
the extracted term matches the target concept. Answer with only "yes" or "no"."""

CONCEPT_MATCHING_USER_TEMPLATE = """Does the extracted term "{extracted_term}" refer \
to the same concept as "{target_concept}"?

Consider synonyms, abbreviations, and closely related terms as matches.
Respond with only: yes or no"""


# ── Prompt builder functions ──────────────────────────────────────────────────

def build_entity_extraction_messages(
    abstract: str,
    exposure: str,
    outcome: str,
    include_few_shot: bool = True,
) -> list[dict[str, str]]:
    """Build the message list for Step 1 entity extraction.

    Args:
        abstract: The abstract text to extract entities from.
        exposure: Target exposure/intervention concept.
        outcome: Target outcome concept.
        include_few_shot: Whether to include few-shot examples.

    Returns:
        List of message dicts suitable for the OpenAI chat completions API.
    """
    messages: list[dict[str, str]] = [
        {"role": "system", "content": ENTITY_EXTRACTION_SYSTEM}
    ]

    if include_few_shot:
        for example in ENTITY_EXTRACTION_FEW_SHOT_EXAMPLES:
            user_msg = ENTITY_EXTRACTION_USER_TEMPLATE.format(
                exposure=example["exposure"],
                outcome=example["outcome"],
                abstract=example["abstract"],
            )
            messages.append({"role": "user", "content": user_msg})
            messages.append(
                {"role": "assistant", "content": _dict_to_json_str(example["output"])}
            )

    messages.append(
        {
            "role": "user",
            "content": ENTITY_EXTRACTION_USER_TEMPLATE.format(
                exposure=exposure,
                outcome=outcome,
                abstract=abstract,
            ),
        }
    )
    return messages


def build_relationship_extraction_messages(
    abstract: str,
    extracted_entities: dict[str, Any],
) -> list[dict[str, str]]:
    """Build messages for Step 2 relationship extraction.

    Args:
        abstract: The source abstract.
        extracted_entities: Output dict from Step 1 entity extraction.

    Returns:
        List of message dicts for the OpenAI chat completions API.
    """
    return [
        {"role": "system", "content": RELATIONSHIP_EXTRACTION_SYSTEM},
        {
            "role": "user",
            "content": RELATIONSHIP_EXTRACTION_USER_TEMPLATE.format(
                abstract=abstract,
                exposure_text=extracted_entities.get("exposure_text", ""),
                exposure_direction=extracted_entities.get("exposure_direction", ""),
                outcome_text=extracted_entities.get("outcome_text", ""),
                study_design=extracted_entities.get("study_design", "OTHER"),
            ),
        },
    ]


def build_concept_matching_messages(
    extracted_term: str,
    target_concept: str,
) -> list[dict[str, str]]:
    """Build messages for Step 3 concept matching (temperature=0).

    Args:
        extracted_term: The term extracted from the abstract.
        target_concept: The canonical concept to match against.

    Returns:
        List of message dicts for the OpenAI chat completions API.
    """
    return [
        {"role": "system", "content": CONCEPT_MATCHING_SYSTEM},
        {
            "role": "user",
            "content": CONCEPT_MATCHING_USER_TEMPLATE.format(
                extracted_term=extracted_term,
                target_concept=target_concept,
            ),
        },
    ]


def _dict_to_json_str(d: dict[str, Any]) -> str:
    """Convert a dict to a formatted JSON string for few-shot examples."""
    import json
    return json.dumps(d, indent=2)
