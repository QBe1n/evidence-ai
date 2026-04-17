# Clinical Evidence Synthesizer: Architecture from Open-Source Components

## Executive Summary

Three open-source research groups have published MIT-licensed components that, combined, form the backbone of a Clinical Evidence Synthesizer — a tool that automates systematic reviews and evidence packages for biotech companies pursuing FDA submissions.

This report maps six repositories across three projects into a unified product architecture. The core pipeline: **extract PICO entities** (Columbia ebmlab) → **triangulate causal evidence across study designs** (Peking University) → **generate synthetic trial data for augmentation** (NeurIPS/Georgia Tech) → **summarize findings into regulatory-ready narratives** (Columbia ebmlab).

All components are MIT-licensed and academically published. None are production-ready — each requires significant engineering to serve as a product module.

---

## Source Repositories

| Repository | Lab | Published | License | Role |
|-----------|-----|-----------|---------|------|
| [ebmlab/PICOX](https://github.com/ebmlab/PICOX) | Columbia University | JAMIA 2024 | MIT | PICO entity extraction (overlapping spans) |
| [ebmlab/EvidenceOutcomes](https://github.com/ebmlab/EvidenceOutcomes) | Columbia University | Dataset release | MIT | Specialized clinical outcome extraction |
| [ebmlab/MedReview](https://github.com/ebmlab/MedReview) | Columbia University | npj Digital Medicine 2024 | MIT | Evidence summarization benchmark (8,575 pairs) |
| [xuanyshi/llm-evidence-triangulation](https://github.com/xuanyshi/llm-evidence-triangulation) | Peking University | medRxiv preprint | MIT | Causal evidence triangulation across study designs |
| [chufangao/TrialSynth](https://github.com/chufangao/TrialSynth) | Georgia Tech | NeurIPS 2024 Workshop | MIT | Synthetic sequential clinical trial data generation |
| [ebmlab/awesome-nlp-in-ebm](https://github.com/ebmlab/awesome-nlp-in-ebm) | Columbia University | Curated list | MIT | Reference: NLP papers in evidence-based medicine |

---

## Unified Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLINICAL EVIDENCE SYNTHESIZER                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  1. INGEST   │───▶│  2. EXTRACT  │───▶│ 3. TRIANGULATE│             │
│  │              │    │              │    │               │              │
│  │ PubMed API   │    │ PICOX (P/I)  │    │ LLM 2-step   │              │
│  │ ClinTrials   │    │ EvidOutcomes │    │ extraction    │              │
│  │ FDA databases│    │ (Outcomes)   │    │ CoE/LoE       │              │
│  │              │    │ BiomedBERT   │    │ scoring       │              │
│  └──────────────┘    └──────────────┘    └───────┬───────┘              │
│                                                   │                     │
│  ┌──────────────┐    ┌──────────────┐    ┌───────▼───────┐              │
│  │ 6. DELIVER   │◀───│ 5. SUMMARIZE │◀───│ 4. AUGMENT    │             │
│  │              │    │              │    │               │              │
│  │ FDA evidence │    │ MedReview    │    │ TrialSynth    │              │
│  │ packages     │    │ fine-tuned   │    │ VAE+Hawkes    │              │
│  │ Dashboards   │    │ LLM          │    │ synthetic     │              │
│  │ API          │    │              │    │ trial data    │              │
│  └──────────────┘    └──────────────┘    └───────────────┘              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Stage 1: Literature Ingestion

### Source: [llm-evidence-triangulation/pubmed_fetcher_function.py](https://github.com/xuanyshi/llm-evidence-triangulation)

The PubMed fetcher from the triangulation repo is the most complete ingestion module across all repos. It queries NCBI's eUtils efetch API, parses XML responses, and extracts:

- Publication dates, titles, structured abstract sections
- MeSH terms (all and major)
- Publication types and comment/correction counts

**Current limitations:**
- Rate limited with hardcoded `time.sleep(5)` between chunks
- Accepts only PMID lists (no search query support)
- Returns pandas DataFrames (no database persistence)

**Production requirements:**
- Add PubMed search API support (esearch) for dynamic literature discovery
- Add ClinicalTrials.gov API connector for trial registry data
- Add FDA database connectors (Drugs@FDA, clinical review documents)
- Implement result caching and incremental updates
- Add proper retry logic and exponential backoff

---

## Stage 2: PICO Entity Extraction

### Source: [ebmlab/PICOX](https://github.com/ebmlab/PICOX) + [ebmlab/EvidenceOutcomes](https://github.com/ebmlab/EvidenceOutcomes)

Two complementary models extract structured clinical entities from RCT abstracts.

### PICOX — Population, Intervention, Outcome Spans

A two-stage boundary-then-span architecture built on PubMedBERT-large:

1. **Boundary Detection**: Token-level classifier identifies span start/end positions (labels: OUT, START, END, BOTH, IN)
2. **Span Classification**: Multi-label sequence classifier determines entity type (P, I, O) with Non-Maximum Suppression for overlapping spans

**Performance**: 53.49% precision, 48.50% recall, 50.87% F1 on the EBM-NLP corpus (~5,000 abstracts)

**Data format**: BioC XML input → JSONL with PICO span annotations and confidence scores

### EvidenceOutcomes — Specialized Outcome Extraction

A focused BiomedBERT-base model trained on 640 expert-annotated abstracts (inter-rater agreement 0.76) specifically for clinical outcome detection using IOB2 tagging (B-Outcome, I-Outcome, O).

**Integration strategy**: Run PICOX for broad P/I/O extraction, then run EvidenceOutcomes as a refinement layer for higher-precision outcome identification. Merge results using confidence-weighted ensemble.

### Key Code Assets

| Module | Source | Function |
|--------|--------|----------|
| Boundary detector training | PICOX `step_1_1` notebook | PubMedBERT token classifier, boundary labels |
| Span classification | PICOX `step_2_1` notebook | Multi-label sigmoid classifier, NMS |
| Outcome model | EvidenceOutcomes `Pubmed_bert.py` | BiomedBERT token classifier, IOB2 scheme |
| Data preprocessing | PICOX `step_0` notebooks | BioC XML / BRAT → JSONL conversion |
| Annotation guidelines | EvidenceOutcomes PDF | Formal outcome entity definitions |

**Current state**: All code lives in Jupyter notebooks or standalone scripts. No packaging, no API, no tests. Different data formats across repos (JSONL vs CoNLL-TSV vs BioC XML).

---

## Stage 3: Evidence Triangulation

### Source: [xuanyshi/llm-evidence-triangulation](https://github.com/xuanyshi/llm-evidence-triangulation)

This is the core analytical engine. It implements automated evidence triangulation — synthesizing causal evidence across RCTs, observational studies, and Mendelian randomization studies using GPT-4o-mini.

### Three-Stage LLM Pipeline

**Step 1 — Entity Extraction**: Few-shot prompted GPT-4o-mini extracts exposures and outcomes from title+abstract text, returning structured JSON.

**Step 2 — Relationship Extraction**: Takes extracted entities as anchors and extracts:
- Effect direction (increase/decrease/no_change)
- Statistical significance
- Study design classification (RCT, OS, MR, META, REVIEW, SR)
- Participant counts and comparators

**Step 3 — Concept Matching**: Deterministic LLM classification (temperature=0) to match extracted concepts to the research question.

### Triangulation Algorithm (CoE/LoE)

The core IP — Convergency of Evidence scoring:

- Groups findings by study_design × exposure_direction × outcome_direction (6 cells)
- Weights by participant count within each design category
- Equal weighting across study designs (prevents observational studies from dominating)
- Computes three probabilities: \(p_{\text{excitatory}}\), \(p_{\text{no\_change}}\), \(p_{\text{inhibitory}}\)
- Level of Evidence: \(\text{LoE} = \frac{\max(p) - 1/3}{1 - 1/3}\), normalized against uniform prior

**Scale demonstrated**: 2,436 papers → 11,667 extracted relationships → 793 triangulation-eligible findings from 446 studies (salt/sodium → cardiovascular disease).

### Prompt Engineering Techniques

- Few-shot examples with real PubMed abstracts
- Two-step decomposition (entities first, then relationships)
- Structured JSON output enforcement
- Domain-specific classification rules for exposure direction
- Constrained vocabularies for study design and significance
- Temperature=0 for deterministic concept matching

**Critical limitation**: All prompts are hardcoded for salt/sodium-CVD only. Production use requires parameterized prompt templates that accept arbitrary exposure-outcome specifications.

---

## Stage 4: Synthetic Data Augmentation

### Source: [chufangao/TrialSynth](https://github.com/chufangao/TrialSynth)

A VAE with Transformer Hawkes Process encoder that generates synthetic sequential clinical trial data while preserving temporal event patterns.

### Architecture

```
Input (event_types, timestamps)
    → Transformer Encoder (sinusoidal temporal encoding + causal self-attention)
    → Latent space z ~ N(μ, σ² × var_multiplier)
    → Linear decoder → Hawkes process decoder
    → Synthetic event sequences
```

### Key Properties

- **Temporal fidelity**: Models irregular time intervals between clinical events using Hawkes process likelihood
- **Privacy knob**: `var_multiplier` parameter scales latent sampling variance (0.1 = high fidelity, 4.0 = high privacy)
- **Multi-component loss**: KL divergence + time MSE + Hawkes event likelihood + type cross-entropy + weighted END token loss
- **Evaluation**: Train on Synthetic, Test on Real (TSTR) using LSTM classifier

### Use Cases in the Synthesizer

1. **Data augmentation**: Expand small Phase I/II trial cohorts for analysis
2. **Privacy-preserving sharing**: Generate shareable synthetic datasets from proprietary trial data
3. **Pipeline testing**: Create realistic test fixtures for development without real patient data
4. **What-if simulation**: Model expected outcomes under different trial protocols

**Current state**: Self-described "very rough state." Values not synthesized (always 0), train=val split, duplicate class definitions, hardcoded CUDA device. NeurIPS workshop paper companion code, not production-ready.

---

## Stage 5: Evidence Summarization

### Source: [ebmlab/MedReview](https://github.com/ebmlab/MedReview)

MedReview provides 8,575 abstract-conclusion pairs from the Cochrane Library (systematic reviews across 37 medical topics, 1996–2023) for fine-tuning summarization models.

### Key Finding from the Paper

Fine-tuned open-source LLMs (PRIMERA, LongT5, Llama-2) **match or exceed GPT-4** on medical evidence summarization — critical for production deployment where cost, latency, and data privacy matter.

### Data Schema

```json
{
  "doi": "10.1002/14651858.CD007407.pub4",
  "abstract": "Background: Chronic suppurative otitis media ...",
  "conclusion": "Topical antibiotics may be more effective than ..."
}
```

**Splits**: 7,472 train / 394 val / 414 test (before cutoff) / 295 test (after cutoff)

**Integration**: Fine-tune an open-source LLM on this dataset to generate regulatory-ready evidence summaries from aggregated findings.

---

## Data Format Harmonization

A critical challenge: each repo uses a different data format.

| Repo | Format | Schema |
|------|--------|--------|
| PICOX | BioC XML → JSONL | `{pmid, tokens, pico_elements: {P: [...], I: [...], O: [...]}}` |
| EvidenceOutcomes | CoNLL TSV / BRAT | `token \t PMID \t start \t end \t label` |
| llm-evidence-triangulation | CSV → Excel → DataFrame | `pmid, exposure, direction, significance, study_design` |
| TrialSynth | DataFrame | `patient_id, event, value, time, label` |
| MedReview | JSONL | `{doi, abstract, conclusion}` |

### Proposed Unified Schema

```python
@dataclass
class ClinicalEvidence:
    # Source identification
    pmid: str
    doi: Optional[str]
    title: str
    abstract: str
    
    # PICO extraction (Stage 2)
    population: List[Span]       # From PICOX
    interventions: List[Span]    # From PICOX
    outcomes: List[Span]         # From PICOX + EvidenceOutcomes
    
    # Evidence extraction (Stage 3)
    relationships: List[Relationship]  # From triangulation
    study_design: StudyDesign
    participant_count: Optional[int]
    
    # Triangulation (Stage 3)
    coe_scores: Optional[CoEScores]    # p_excitatory, p_no_change, p_inhibitory
    loe: Optional[float]               # Level of Evidence
    
    # Summary (Stage 5)
    generated_summary: Optional[str]    # From fine-tuned LLM
    confidence: float
    
@dataclass
class Span:
    text: str
    start: int
    end: int
    label: str
    confidence: float

@dataclass
class Relationship:
    exposure: str
    exposure_direction: str  # increased/decreased
    outcome: str
    direction: str           # increase/decrease/no_change
    significance: str        # positive/negative
```

---

## Production Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                       │
│  POST /synthesize   POST /triangulate   GET /evidence/{query}     │
└────────────┬──────────────────┬────────────────────┬──────────────┘
             │                  │                    │
    ┌────────▼────────┐  ┌─────▼──────────┐  ┌─────▼──────────┐
    │ Literature       │  │ Extraction      │  │ Synthesis       │
    │ Discovery        │  │ Service         │  │ Service         │
    │                  │  │                 │  │                 │
    │ PubMed search    │  │ PICO extraction │  │ Triangulation   │
    │ ClinTrials.gov   │  │ (PICOX +        │  │ (CoE/LoE)       │
    │ FDA databases    │  │  EvidOutcomes)  │  │ Summarization   │
    │                  │  │ LLM extraction  │  │ (MedReview LLM) │
    └────────┬────────┘  └─────┬──────────┘  └─────┬──────────┘
             │                  │                    │
    ┌────────▼──────────────────▼────────────────────▼──────────┐
    │                     Data Layer                              │
    │  PostgreSQL (evidence store)  │  Redis (cache)              │
    │  S3 (documents, models)       │  Celery (async jobs)        │
    └───────────────────────────────────────────────────────────┘
```

### Tech Stack Recommendation

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| API | FastAPI (Python) | Native async, all repos are Python |
| Database | PostgreSQL | Structured evidence data, JSON support |
| Cache | Redis | PubMed result caching, rate limiting |
| Task Queue | Celery + Redis | Async LLM extraction jobs |
| ML Serving | Hugging Face Inference / vLLM | PICOX, EvidenceOutcomes, MedReview models |
| LLM | GPT-4o-mini / Claude | Triangulation extraction |
| Frontend | Next.js | Dashboard, evidence explorer |
| Deployment | Vercel (frontend) + AWS ECS (backend) | Scalable, familiar stack |

---

## Engineering Effort Estimate

| Component | Source Repo | Current State | Work Required |
|-----------|------------|---------------|---------------|
| PubMed fetcher | triangulation | Functional, single-domain | 1-2 weeks: add search API, caching, retry logic |
| PICO extraction | PICOX | Notebooks, no packaging | 2-3 weeks: extract to package, add API, test suite |
| Outcome extraction | EvidenceOutcomes | Script + data | 1-2 weeks: package model, integrate with PICO |
| LLM extraction | triangulation | Hardcoded salt/CVD | 2-3 weeks: parameterize prompts, add retry/validation |
| Triangulation | triangulation | 18x repeated code | 1 week: refactor, parameterize, add config |
| Summarization | MedReview | Data only, no code | 2-3 weeks: fine-tune LLM, build inference service |
| Synthetic data | TrialSynth | "Very rough" prototype | 3-4 weeks: fix issues, add value synthesis, API |
| Data layer | None | N/A | 2-3 weeks: schema, migrations, caching |
| API + frontend | None | N/A | 3-4 weeks: FastAPI backend, Next.js dashboard |
| **Total** | | | **~16-24 weeks for MVP** |

---

## Key Risks

1. **LLM extraction accuracy**: The triangulation pipeline was validated on one domain only (salt/CVD). Performance on arbitrary clinical topics is unproven and likely requires per-domain prompt tuning.

2. **PICO extraction F1 of ~51%**: While state-of-the-art for overlapping entity extraction, this means roughly half of entities are missed or incorrect. A human-in-the-loop review step is likely needed for regulatory submissions.

3. **No formal privacy guarantees**: TrialSynth's variance knob is not differentially private. FDA and HIPAA compliance would require additional privacy mechanisms.

4. **Regulatory classification**: A tool generating evidence packages for FDA submissions may itself be classified as clinical decision support software, triggering FDA 510(k) or De Novo requirements.

5. **Data access**: TrialSynth's training data (Project Data Sphere) requires a usage agreement. Real clinical trial data for any production deployment will have similar access constraints.

---

## Recommended MVP Scope

For a minimum viable product targeting biotech companies:

1. **Input**: User specifies a clinical question (exposure + outcome + optional study design filters)
2. **Literature search**: Automated PubMed search + PMID collection
3. **Extraction**: LLM-based two-step extraction (from triangulation repo) with parameterized prompts
4. **Analysis**: Triangulation scoring (CoE/LoE) with temporal trend visualization
5. **Output**: Evidence summary table + convergence plot + downloadable report

This skips PICO extraction (Stages 2) and synthetic data (Stage 4) for V1, focusing on the highest-value chain: search → extract → triangulate → summarize.
