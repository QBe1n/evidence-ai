"""Quick start example for EvidenceAI.

Demonstrates the minimal 5-line usage to run a systematic review.

Prerequisites:
    pip install evidence-ai
    export OPENAI_API_KEY=sk-...
    export NCBI_EMAIL=your@email.com

Run:
    python examples/quick_start.py
"""

import asyncio
import os

from evidence_ai import EvidenceAI


async def main() -> None:
    # Initialize the client
    client = EvidenceAI(openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # Run a systematic review — just 5 lines
    review = await client.synthesize(
        question="Does semaglutide reduce cardiovascular mortality in type 2 diabetes?",
        max_papers=100,  # Keep small for this demo
    )

    # Print the results
    print(f"\nEvidence Synthesis Complete")
    print(f"{'='*50}")
    print(f"Question:           {review.question}")
    print(f"Papers screened:    {review.papers_screened}")
    print(f"Papers included:    {review.papers_included}")
    print(f"Level of Evidence:  {review.level_of_evidence:.2f} ({review.loe_label})")
    print(f"Effect direction:   {review.effect_direction.value}")
    print()
    print(f"CoE Scores:")
    print(f"  p(inhibitory): {review.coe_scores.p_inhibitory:.3f}")
    print(f"  p(no_change):  {review.coe_scores.p_no_change:.3f}")
    print(f"  p(excitatory): {review.coe_scores.p_excitatory:.3f}")
    print()
    print(f"Summary:")
    print(f"  {review.summary}")
    print()
    print(f"Key Findings:")
    for finding in review.key_findings:
        print(f"  • {finding}")
    print()

    # Export to FDA package
    output_dir = "./output/quick_start/"
    review.export_fda_package(output_dir, format="json")
    print(f"Evidence package exported to: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
