# EvidenceAI + NeoVax AI: The Integrated Regulatory Intelligence Layer

## The Core Insight

NeoVax AI designs personalized cancer vaccines. EvidenceAI validates whether those designs can survive regulatory scrutiny. Together, they become an end-to-end platform: **design a vaccine → prove it works → get it approved.**

This isn't just two products sharing infrastructure. Personalized cancer vaccines have a unique regulatory problem that makes this combination essential.

---

## The Regulatory Problem Unique to Personalized Vaccines

Every personalized cancer vaccine is a **one-of-one product**. Each patient's vaccine encodes their unique tumor mutations. This breaks traditional drug approval:

- You can't run a standard Phase 3 trial because every patient gets a different drug
- [Moderna/Merck's mRNA-4157](https://www.merck.com/news/moderna-and-merck-announce-mrna-4157-v940-in-combination-with-keytruda-pembrolizumab-demonstrated-continued-improvement-in-recurrence-free-survival-and-distant-metastasis-free-survival-in-pa/) encodes up to 34 neoantigens per patient — no two vaccines are identical
- FDA's CBER regulates these as biologics (BLA pathway), but the [standard evidence frameworks don't fit](https://pmc.ncbi.nlm.nih.gov/articles/PMC12116195/)
- The [FDA's new Plausible Mechanism Framework](https://www.fda.gov/news-events/press-announcements/fda-launches-framework-accelerating-development-individualized-therapies-ultra-rare-diseases) (February 2026) explicitly acknowledges this gap — approval can now be based on mechanistic evidence rather than large randomized trials

This means the **evidence package** for a personalized vaccine must prove something different from traditional drugs:

1. The neoantigen selection algorithm reliably identifies immunogenic targets
2. The mRNA platform consistently produces functional vaccines
3. The manufacturing process is reproducible across patient-specific products
4. Clinical outcomes (tumor shrinkage, immune response, survival) correlate with algorithmically predicted targets
5. Safety signals are consistent across the platform even though each product is unique

**EvidenceAI is purpose-built to compile exactly this kind of cross-study, cross-platform evidence.**

---

## How EvidenceAI Serves NeoVax AI: Five Concrete Use Cases

### 1. Pre-Design Literature Validation

Before NeoVax designs a vaccine for a patient's tumor, EvidenceAI searches the evidence base:

```
INPUT: Patient's tumor mutations (e.g., BRAF V600E, KRAS G12D, TP53 R273H)

EvidenceAI DOES:
→ Search PubMed for every study targeting these specific mutations
→ Extract outcomes: immune response rates, tumor shrinkage, survival data
→ Triangulate evidence across RCTs, observational studies, case reports
→ Score each mutation target by Level of Evidence (LoE)
→ Flag mutations with poor immune response history
→ Find clinical trials currently recruiting for these mutations

OUTPUT: Evidence-ranked mutation list with confidence scores
"BRAF V600E → Strong evidence (LoE 0.87): targeted in 47 studies, 
 72% immune response rate, well-characterized"
"Novel mutation X123Y → No prior evidence: proceed with caution, 
 rely on computational prediction only"
```

This directly improves NeoVax's neoantigen selection. Instead of relying purely on computational prediction (MHCflurry, pVACseq), the AI also weighs real-world clinical evidence.

### 2. Clinical Trial Matching & Competitive Intelligence

For every vaccine NeoVax designs, EvidenceAI automatically:

- Searches [ClinicalTrials.gov](https://clinicaltrials.gov/) for active personalized vaccine trials with similar targets
- Identifies which mutations are being targeted by [Moderna/Merck (mRNA-4157)](https://trials.modernatx.com/study/?id=mRNA-4157-P201), [BioNTech (autogene cevumeran)](https://www.nature.com/articles/s41586-025-10004-2), and 120+ other mRNA vaccine programs
- Maps the competitive landscape: which cancer types, which mutations, which stages
- Flags where NeoVax's approach has differentiation or overlap

### 3. Regulatory Evidence Package Generation

When NeoVax is ready to seek approval (or support a partner's clinical trial), EvidenceAI generates the evidence dossier:

**For FDA BLA Submission (CBER pathway):**

| Evidence Component | EvidenceAI Generates |
|-------------------|---------------------|
| Clinical Overview (Module 2.5) | Systematic review of all neoantigen vaccine trials, outcomes synthesis |
| Summary of Clinical Efficacy (Module 2.7.3) | Cross-study efficacy data for the neoantigen platform |
| Summary of Clinical Safety (Module 2.7.4) | Integrated safety analysis across all patients treated on platform |
| Nonclinical Overview (Module 2.4) | Evidence synthesis for mechanism of action, immunological rationale |
| Literature Review | Comprehensive SLR per [FDA guidance for personalized neoantigen vaccines](https://www.casss.org/docs/default-source/cgtp/2019-cgtp-speaker-presentations/husain-syed-us-fda-2019.pdf) |

**For FDA's Plausible Mechanism Framework (new pathway):**

The [February 2026 FDA guidance](https://www.fda.gov/news-events/press-announcements/fda-launches-framework-accelerating-development-individualized-therapies-ultra-rare-diseases) requires demonstrating:

| Requirement | EvidenceAI Provides |
|------------|-------------------|
| "Identifying the disease-causing abnormality" | Evidence synthesis linking specific mutations to tumor pathology |
| "Therapy targets the root cause or proximate biological pathway" | Literature validation that selected neoantigens are immunologically relevant |
| "Well-characterized natural history data" | Systematic review of untreated outcomes for the specific cancer type |
| "Successful target drugging" | Cross-trial evidence that neoantigen vaccines induce measurable immune responses |
| "Improvement in clinical outcomes" | Triangulated evidence across all available personalized vaccine studies |

### 4. Companion Diagnostic Evidence Support

NeoVax's neoantigen prediction algorithm is essentially a **companion diagnostic** — it determines which patients get which treatment. [FDA is actively reclassifying oncology companion diagnostics](https://www.darkdaily.com/2025/12/29/fda-proposes-reclassifying-oncology-companion-diagnostics-potentially-easing-approval-path-and-expanding-patient-access/) from Class III (PMA) to Class II (510(k)), making this pathway more accessible.

EvidenceAI generates the evidence package for the CDx submission:

- Analytical validation data (sensitivity, specificity of neoantigen predictions)
- Clinical validation data (correlation between predicted neoantigens and immune response)
- Literature review supporting the biomarkers used in selection
- Concordance studies vs. existing prediction tools

### 5. Post-Market Surveillance & Evidence Updates

After any NeoVax-designed vaccine is administered, EvidenceAI continuously:

- Monitors PubMed, medRxiv, and ClinicalTrials.gov for new evidence on targeted mutations
- Flags new safety signals from related neoantigen vaccine trials
- Updates evidence scores as new data emerges ([BioNTech's 4-year follow-up](https://www.nature.com/articles/s41586-025-10004-2), Moderna/Merck's [5-year melanoma data](https://www.merck.com/news/moderna-and-merck-announce-mrna-4157-v940-in-combination-with-keytruda-pembrolizumab-demonstrated-continued-improvement-in-recurrence-free-survival-and-distant-metastasis-free-survival-in-pa/))
- Generates periodic evidence reports for regulatory authorities

---

## The Integrated Product Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    UNIFIED PLATFORM                                 │
│                                                                     │
│  ┌─────────────────────┐        ┌──────────────────────────┐       │
│  │     NeoVax AI        │        │      EvidenceAI           │      │
│  │  (Vaccine Design)    │◄──────►│  (Regulatory Evidence)    │      │
│  │                      │        │                           │      │
│  │ Tumor sequencing     │  API   │ Literature search         │      │
│  │ Mutation detection   │◄──────►│ Evidence triangulation    │      │
│  │ Neoantigen prediction│        │ Regulatory document gen   │      │
│  │ AlphaFold validation │        │ Clinical trial matching   │      │
│  │ mRNA design          │        │ Post-market monitoring    │      │
│  └─────────┬───────────┘        └────────────┬──────────────┘      │
│            │                                  │                     │
│  ┌─────────▼──────────────────────────────────▼──────────────┐     │
│  │                   SHARED INFRASTRUCTURE                    │     │
│  │                                                            │     │
│  │  LLM Layer (GPT-4 + Perplexity Sonar + Claude)            │     │
│  │  Audit Trail (every decision logged + traceable)           │     │
│  │  PostgreSQL + S3 (patient data + evidence store)           │     │
│  │  Next.js Dashboard (unified interface)                     │     │
│  │  FastAPI Backend (Python — bioinformatics + NLP)           │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │                  INTEGRATION LAYER                         │     │
│  │                                                            │     │
│  │  Sequencing Labs ─── RNA Synthesis Partners ─── Vet Clinics│     │
│  │  ClinicalTrials.gov ── PubMed ── FDA Databases ── medRxiv │     │
│  │  University RNA Labs ── Biotech Partners ── Hospitals      │     │
│  └───────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────┘
```

---

## The Data Flow: From Tumor to Approved Treatment

```
PATIENT JOURNEY:

1. TUMOR BIOPSY
   └──► Sequencing lab (WES/WGS)
        └──► VCF file (mutations)

2. NeoVax AI: DESIGN
   ├── Mutation detection
   ├── HLA typing
   ├── Neoantigen prediction (pVACseq + MHCflurry)
   ├── AlphaFold structure validation
   │
   │   ┌─── EvidenceAI: PRE-DESIGN VALIDATION ──┐
   │   │ "Is KRAS G12D a good target?"            │
   │   │ → 47 studies, 72% immune response        │
   │   │ → LoE: 0.87 (strong evidence)            │
   │   │ → 3 active Phase 3 trials targeting it   │
   │   └──────────────────────────────────────────┘
   │
   └──► Ranked neoantigens (evidence-weighted)
        └──► mRNA vaccine blueprint

3. MANUFACTURING
   └──► RNA synthesis lab produces vaccine

4. TREATMENT
   ├── Vaccine administered
   └── Outcomes tracked (tumor response, immune markers)

5. EvidenceAI: REGULATORY PACKAGE
   ├── Systematic literature review (automated)
   ├── Cross-patient efficacy synthesis
   ├── Integrated safety analysis
   ├── Plausible Mechanism evidence package
   └──► FDA BLA submission / Vet regulatory filing

6. EvidenceAI: POST-MARKET
   ├── Continuous literature monitoring
   ├── Safety signal detection
   └── Evidence score updates
```

---

## Why This Combination Is Defensible

### The Flywheel

```
More vaccines designed (NeoVax)
    → More outcome data collected
        → Better evidence packages (EvidenceAI)
            → Faster regulatory approvals
                → More clinics adopt the platform
                    → More vaccines designed
```

Each vaccine designed generates outcome data. Each outcome data point strengthens the evidence base. The stronger the evidence base, the easier the next approval. This is a compound advantage that accelerates over time.

### Competitive Moats

1. **No one else connects vaccine design to regulatory evidence.** Moderna/Merck, BioNTech, and all 120+ mRNA vaccine programs do these as separate workflows with separate teams. Integrating them into one platform is a genuine first.

2. **The audit trail spans from mutation to approval.** You can trace every decision — why this neoantigen was chosen, what evidence supported it, what the predicted binding affinity was, how the mRNA was optimized — in one system. Regulators love this.

3. **Cross-patient learning.** After 100 patients, you have a dataset that no single academic lab or pharma company has: neoantigen predictions + evidence scores + actual outcomes, all linked. This trains better prediction models and generates better evidence packages.

4. **Regulatory format expertise compounds.** The Plausible Mechanism Framework is brand new (February 2026). Whoever builds the first tools to generate evidence packages for this pathway defines how it gets used. That's you.

---

## Market Sizing: The Combined Opportunity

| Market Segment | TAM | NeoVax AI Revenue | EvidenceAI Revenue |
|---------------|-----|-------------------|-------------------|
| Veterinary oncology (6M dogs/yr with cancer in US) | $2-5B/yr | $500/analysis × 100K analyses = $50M | Bundled with analysis |
| Academic neoantigen vaccine trials (~400 active) | $1-2B/yr | Platform licenses $50K-$100K/yr | SLR packages $75K-$150K/trial |
| Biotech personalized vaccine programs (~120 mRNA) | $5-10B/yr | Enterprise platform $200K-$500K/yr | Regulatory evidence packages $150K-$500K/submission |
| Pharma partners (Moderna, BioNTech, etc.) | $10B+/yr | Neoantigen prediction API licensing | Full regulatory submission support |
| Hospital-based decentralized manufacturing | $20B+ (future) | Design software for RNA synthesis boxes | Continuous evidence monitoring |

**Combined platform ARR path:**

| Year | NeoVax AI | EvidenceAI | Combined | Valuation (25x) |
|------|-----------|-----------|----------|-----------------|
| Year 1 | $500K | $500K | $1M | $25M |
| Year 2 | $5M | $5M | $10M | $250M |
| Year 3 | $20M | $15M | $35M | $875M |
| Year 4 | $40M | $25M | $65M | $1.6B |

---

## The "Mass Market" Question

You asked specifically about mass market tests and approvals. Here's the reality:

### Personalized vaccines don't go through traditional "mass market" approval

They're approved as a **platform** under [FDA's Plausible Mechanism Framework](https://www.fda.gov/news-events/press-announcements/fda-launches-framework-accelerating-development-individualized-therapies-ultra-rare-diseases) or as a **BLA with platform-level evidence**, not as individual drugs. What gets approved is:

1. **The neoantigen selection algorithm** (the companion diagnostic)
2. **The mRNA manufacturing platform** (consistent quality across patient-specific products)
3. **The combined evidence** that the platform produces vaccines that work

This is exactly where EvidenceAI creates maximum value — it synthesizes evidence across all patients treated on the platform to prove the platform works, even though each vaccine is unique.

### The pathway to mass adoption

```
VETERINARY (now - no regulatory barrier)
  → Prove the platform works on animal cancers
  → Generate outcome data
  
ACADEMIC TRIALS (Year 1-2)
  → Support university clinical trials with evidence packages
  → Use FDA's Plausible Mechanism Framework
  → Build dataset of human outcomes
  
BREAKTHROUGH THERAPY DESIGNATION (Year 2-3)
  → Moderna/Merck already have BTD for melanoma
  → Compile cross-trial evidence for new indications
  
BLA SUBMISSION (Year 3-4)
  → Platform-level evidence package
  → CDx approval for the neoantigen prediction algorithm
  → EvidenceAI generates the entire regulatory dossier

HOSPITAL DECENTRALIZATION (Year 4+)
  → "RNA synthesis boxes" in hospitals
  → NeoVax = the design software every hospital uses
  → EvidenceAI = continuous regulatory compliance
```

### The real unlock: regulatory-grade neoantigen prediction

The biggest bottleneck isn't manufacturing — it's **proving that your algorithm picks the right targets**. [FDA's CBER specifically calls out](https://www.casss.org/docs/default-source/cgtp/2019-cgtp-speaker-presentations/husain-syed-us-fda-2019.pdf) the need to "justify the algorithms used to select neoantigen peptides." EvidenceAI generates that justification by synthesizing all available evidence on each predicted neoantigen.

---

## What to Build First

**Week 1-2:** Add a "literature validation" endpoint to the NeoVax pipeline that calls EvidenceAI's triangulation engine for every predicted neoantigen. This immediately makes NeoVax's predictions evidence-weighted, not just computationally predicted.

**Week 3-4:** Build the clinical trial matching feature — for every NeoVax design, automatically find and display relevant active trials from ClinicalTrials.gov.

**Month 2-3:** Build the regulatory document generator — take NeoVax's design + EvidenceAI's evidence synthesis and output a formatted evidence package (FDA Module 2.5/2.7 structure or Plausible Mechanism Framework).

This integration is the single biggest differentiator. No competing platform — not Moderna's, not BioNTech's, not any of the 400+ clinical trial programs — has automated evidence synthesis connected to vaccine design.
