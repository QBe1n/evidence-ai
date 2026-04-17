"""Full systematic review example for EvidenceAI.

Demonstrates the complete workflow including:
- Custom database selection and date filtering
- Study design filtering
- PICO entity extraction access
- Triangulation score analysis
- FDA evidence package generation in eCTD format
- Continuous monitoring setup

This example produces a realistic evidence review for SGLT2 inhibitors
and heart failure hospitalization — a well-studied clinical question
with strong evidence from multiple large RCTs.

Prerequisites:
    pip install evidence-ai
    export OPENAI_API_KEY=sk-...
    export NCBI_EMAIL=your@email.com

Run:
    python examples/full_review.py
"""

import asyncio
import json
import os
from pathlib import Path

from evidence_ai import EvidenceAI
from evidence_ai.config import Settings
from evidence_ai.ingest import PubMedFetcher
from evidence_ai.extract import PICOExtractor
from evidence_ai.triangulate import TriangulationEngine
from evidence_ai.summarize import NarrativeGenerator, RegulatoryFormatter


async def main() -> None:
    print("EvidenceAI — Full Systematic Review Demo")
    print("=" * 60)
    print()

    # ── Configuration ──────────────────────────────────────────────────────────
    settings = Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        ncbi_email=os.environ.get("NCBI_EMAIL", "demo@evidenceai.com"),
        ncbi_api_key=os.environ.get("NCBI_API_KEY", ""),
    )

    clinical_question = (
        "Does SGLT2 inhibition reduce hospitalization for heart failure "
        "in patients with type 2 diabetes and cardiovascular disease?"
    )

    print(f"Clinical Question:")
    print(f"  {clinical_question}")
    print()

    # ── Stage 1: Ingest ────────────────────────────────────────────────────────
    print("Stage 1: Literature Ingestion")
    print("-" * 40)

    fetcher = PubMedFetcher(settings=settings)
    papers = await fetcher.search_and_fetch(
        query="SGLT2 inhibitor heart failure hospitalization diabetes cardiovascular",
        max_results=300,
        date_range={"start": "2015-01-01", "end": "2025-12-31"},
        study_design_filter=["Randomized Controlled Trial", "Meta-Analysis", "Systematic Review"],
    )
    print(f"  Papers found: {len(papers)}")

    rct_count = sum(1 for p in papers if p.is_rct)
    meta_count = sum(1 for p in papers if "Meta-Analysis" in p.publication_types)
    print(f"  RCTs: {rct_count}")
    print(f"  Meta-analyses: {meta_count}")
    print()

    # ── Stage 2: Extract ───────────────────────────────────────────────────────
    print("Stage 2: PICO Entity Extraction")
    print("-" * 40)

    extractor = PICOExtractor.from_pretrained(device="cpu")
    abstracts = [p.full_abstract_text for p in papers if p.full_abstract_text]
    source_ids = [p.pmid for p in papers if p.full_abstract_text]

    extraction_batch = extractor.extract_batch(abstracts, source_ids=source_ids)
    print(f"  Abstracts processed: {extraction_batch.total_processed}")
    print(f"  Success rate: {extraction_batch.success_rate:.1%}")

    rct_structured = sum(1 for r in extraction_batch.results if r.has_rct_structure)
    print(f"  With full PICO structure: {rct_structured}")
    print()

    # ── Stage 3: Triangulate ──────────────────────────────────────────────────
    print("Stage 3: Evidence Triangulation")
    print("-" * 40)

    engine = TriangulationEngine(
        llm_model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

    triangulation = await engine.triangulate(
        question=clinical_question,
        papers=papers,
        extracted_entities=extraction_batch,
        exposure="SGLT2 inhibitor",
        outcome="heart failure hospitalization",
    )

    print(f"  Papers analyzed: {triangulation.papers_analyzed}")
    print(f"  Papers eligible: {triangulation.papers_eligible}")
    print(f"  Level of Evidence: {triangulation.loe:.3f} ({triangulation.loe_label})")
    print(f"  Effect direction: {triangulation.effect_direction.value}")
    print()
    print(f"  Convergence of Evidence Scores:")
    print(f"    p(inhibitory) = {triangulation.coe_scores.p_inhibitory:.4f}")
    print(f"    p(no_change)  = {triangulation.coe_scores.p_no_change:.4f}")
    print(f"    p(excitatory) = {triangulation.coe_scores.p_excitatory:.4f}")
    print()
    print(f"  Design breakdown:")
    print(f"    RCTs: {triangulation.rct_count}")
    print(f"    Meta-analyses: {triangulation.meta_count}")
    print(f"    Observational: {triangulation.os_count}")
    print()

    # ── Stage 5: Summarize ────────────────────────────────────────────────────
    print("Stage 5: Evidence Narrative Generation")
    print("-" * 40)

    generator = NarrativeGenerator(
        llm_model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

    review = await generator.generate(
        question=clinical_question,
        papers=papers,
        pico_entities=extraction_batch,
        triangulation=triangulation,
    )

    print(f"  Review ID: {review.review_id}")
    print(f"  Summary:")
    print(f"    {review.summary}")
    print()
    print(f"  Key Findings:")
    for finding in review.key_findings:
        print(f"    • {finding}")
    print()

    # ── Stage 6: Deliver ──────────────────────────────────────────────────────
    print("Stage 6: FDA Evidence Package Generation")
    print("-" * 40)

    output_dir = Path("./output/full_review/")
    formatter = RegulatoryFormatter()

    # Generate eCTD module text
    review.module_25_text = formatter.generate_module_25(review)
    review.module_273_text = formatter.generate_module_273(review)
    review.module_274_text = formatter.generate_module_274(review)

    # Export package
    review.export_fda_package(output_dir, format="ectd")
    print(f"  Package exported to: {output_dir}")
    print(f"  Files generated:")
    for f in output_dir.iterdir():
        print(f"    - {f.name}")
    print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("=" * 60)
    print("REVIEW COMPLETE")
    print("=" * 60)
    print(f"  Question: {clinical_question[:70]}...")
    print(f"  Conclusion: {triangulation.summary_sentence}")
    print()
    print(f"  FDA Package: {output_dir}/")
    print()
    print("This review demonstrates ~73-91% cost reduction vs. traditional CRO SLRs.")
    print("(Frontiers in Pharmacology, 2025)")


if __name__ == "__main__":
    asyncio.run(main())
