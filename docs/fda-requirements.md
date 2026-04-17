# FDA Regulatory Submission Evidence Requirements: Deep Dive
*Research compiled: 2025 | Sources: FDA, EMA, PMDA, TGA, peer-reviewed journals, market research firms*

---

## Table of Contents

1. [FDA Submission Types and Evidence Requirements](#1-fda-submission-types-and-evidence-requirements)
   - NDA
   - BLA
   - 510(k)
   - De Novo
   - Clinical Study Report (CSR)
   - ISS / ISE
2. [Volume and Economics](#2-volume-and-economics)
3. [Real-World Evidence (RWE) Trend](#3-real-world-evidence-rwe-trend)
4. [European and Global Angle](#4-european-and-global-angle)
5. [Key Decision Makers and Buyers](#5-key-decision-makers-and-buyers)

---

## 1. FDA Submission Types and Evidence Requirements

### Overview: The eCTD Format

All NDA and BLA submissions to FDA's CDER and CBER must be filed in **Electronic Common Technical Document (eCTD) format**, organized across five modules ([FDA eCTD page](https://www.fda.gov/drugs/electronic-regulatory-submission-and-review/electronic-common-technical-document-ectd)):

| Module | Content |
|--------|---------|
| **Module 1** | Regional/administrative (US-specific forms, cover letter, labeling) |
| **Module 2** | Cross-cutting summaries: quality overview, nonclinical overview and summary, clinical overview and clinical summary (includes ISE/ISS) |
| **Module 3** | Chemistry, Manufacturing & Controls (CMC) |
| **Module 4** | Nonclinical study reports (pharmacology, toxicology) |
| **Module 5** | Clinical study reports from all human trials |

As of September 2024, FDA accepts new submissions in eCTD v4.0 format; eCTD v3.2.2 remains supported ([FDA eCTD update, October 2024](https://www.fda.gov/drugs/electronic-regulatory-submission-and-review/electronic-common-technical-document-ectd)).

---

### 1.1 New Drug Application (NDA)

**Regulatory Authority:** FDA CDER  
**Legal Basis:** 21 CFR Part 314 (FD&C Act Section 505)  
**Standard for Approval:** "Safe and effective" — requires substantial evidence from adequate and well-controlled studies

**Evidence Package Requirements** ([FDA IND/NDA overview](https://www.fda.gov/drugs/types-applications/investigational-new-drug-ind-application)):

**Module 3 — Chemistry, Manufacturing & Controls:**
- Drug substance specifications and analytical methods
- Drug product formulation, manufacturing process
- Stability data (long-term, accelerated)
- Methods validation package
- Container closure system

**Module 4 — Nonclinical:**
- Pharmacology studies (primary and secondary pharmacodynamics)
- Pharmacokinetics (absorption, distribution, metabolism, excretion — ADME)
- Toxicology: single-dose, repeat-dose, genotoxicity, carcinogenicity, reproductive/developmental toxicity
- Safety pharmacology (cardiac, CNS, respiratory)

**Module 5 — Clinical:**
- Full Clinical Study Reports (CSRs) for all Phase I, II, III studies following ICH E3 format
- Tabulated clinical study data in CDISC/SDTM format (required since December 2016 for studies starting after that date)
- **Integrated Summary of Efficacy (ISE)** — pooled analysis of all efficacy data (21 CFR 314.50(d)(5)(v))
- **Integrated Summary of Safety (ISS)** — pooled analysis of all safety data across the development program (21 CFR 314.50(d)(5)(vi))
- Integrated Safety and Efficacy Summary at Module 2 level (Clinical Overview ~30 pages; Clinical Summary ~50–400 pages)

**Module 2 — Summaries:**
- Quality Overall Summary (QOS)
- Nonclinical Overview and Nonclinical Summary
- Clinical Overview (~30 pages): risk-benefit assessment
- Clinical Summary (~50–400 pages): Summary of Clinical Efficacy (SCE, Module 2.7.3) and Summary of Clinical Safety (SCS, Module 2.7.4)

**Administrative Requirements:**
- Form FDA 356h (application form)
- Patent certification (Hatch-Waxman)
- Labeling (proposed Prescribing Information, Medication Guide if applicable)
- Pediatric plans or waivers/deferrals (PREA)
- Risk Evaluation and Mitigation Strategy (REMS) if required
- Debarment certification, financial disclosure
- ClinicalTrials.gov compliance certification (FDA Form 3674)

**NDA Sub-types:**
- **505(b)(1):** Full NDA with company's own complete safety and efficacy data
- **505(b)(2):** Hybrid NDA — relies in part on literature or prior FDA findings; requires literature review to demonstrate the published evidence supports safety/efficacy
- **505(j):** Abbreviated NDA (ANDA) for generics — bioequivalence demonstration

**505(b)(2) and Literature Reviews:**  
The 505(b)(2) pathway is particularly evidence-synthesis intensive. Sponsors must conduct comprehensive literature searches, critically appraise published studies, and integrate findings into the Module 5 and 2 clinical sections. Systematic literature reviews (SLRs) are often used to identify all relevant published evidence on the active moiety, support safety bridging, and substantiate cross-reference to prior FDA findings ([Intertek, January 2026](https://www.intertek.com/blog/2026/01-16-literature-based-submissions-using-publicly-available-data-to-support-drug-development/)).

---

### 1.2 Biologics License Application (BLA)

**Regulatory Authority:** FDA CDER (monoclonal antibodies, most therapeutic biologics) or CBER (vaccines, blood, gene therapies, some cellular products)  
**Legal Basis:** 21 CFR Parts 600–680 (Public Health Service Act Section 351)  
**Standard for Approval:** "Safe, pure, and potent" — FDA interprets "potency" to include efficacy, requiring substantial evidence equivalent to NDA standards ([FDLI BLA Overview PDF](https://fdli.org/wp-content/uploads/2020/10/Hegreness-Matthew.pdf))

**How BLA Differs from NDA:**

| Dimension | NDA | BLA |
|-----------|-----|-----|
| Product type | Small molecule drugs | Biologics (antibodies, vaccines, gene therapies, cell therapies, blood products) |
| Legal standard | FD&C Act 505 | PHS Act 351 |
| CMC complexity | Lower | Much higher — living cell lines, complex manufacturing processes, biosimilarity considerations |
| Clinical data standard | "Substantial evidence" | "Substantial evidence" (harmonized with FDAMA 1997) |
| ISE/ISS requirement | Mandatory (21 CFR 314.50) | No explicit regulatory mandate, but strongly encouraged and near-universal |

**Unique BLA Evidence Requirements:**
- **Comparability protocols** for manufacturing changes (critical for biologics where manufacturing IS the product)
- **Immunogenicity assessment** — characterization of anti-drug antibody (ADA) responses, their clinical relevance
- **Product characterization** — structural characterization including primary/higher-order structure, post-translational modifications (glycosylation profiles, etc.)
- **Reference standard documentation**
- **Container closure and extractables/leachables** studies
- **Biological activity/potency assays** — in vitro, in vivo, or a combination

For **gene therapies and cell therapies**, additional requirements include:
- Biodistribution studies
- Integration site analysis (for integrating vectors)
- Long-term follow-up protocols (up to 15 years post-treatment for certain gene therapies)

**Review Timeline:**
- Standard review: 10 months from filing (PDUFA date)
- Priority review (designated): 6 months from filing
- Filing decision: 60 days from receipt ([FDA BLA process](https://www.fda.gov/vaccines-blood-biologics/development-approval-process-cber/biologics-license-applications-bla-process-cber))

Sources: [FDA BLA process (CBER)](https://www.fda.gov/vaccines-blood-biologics/development-approval-process-cber/biologics-license-applications-bla-process-cber); [The FDA Group BLA guide](https://www.thefdagroup.com/blog/2014/07/test-the-biologics-license-application-bla-process/)

---

### 1.3 510(k) — Premarket Notification

**Regulatory Authority:** FDA CDRH  
**Legal Basis:** FD&C Act Section 510(k)  
**Standard:** "Substantial equivalence" to a legally marketed predicate device  
**Applicable Device Classes:** Class I (some) and Class II devices; ~99% of devices entering market use this pathway

**Core Evidence Framework:**

A 510(k) submission must demonstrate substantial equivalence — that the new device has the **same intended use** and either the **same technological characteristics** as the predicate, or different technological characteristics that raise no new questions of safety and effectiveness ([FDA 510(k) Best Practices Guidance, September 2023](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/best-practices-selecting-predicate-device-support-premarket-notification-510k-submission)).

**Required Elements:**
1. **Device description** — materials, design principles, operating mechanisms
2. **Predicate device identification** — with justification of selection
3. **Substantial equivalence comparison** — intended use and technological characteristics side-by-side
4. **Performance/bench testing** data
5. **Risk analysis** (per ISO 14971)
6. **Labeling** (proposed Instructions for Use)
7. **Sterility/biocompatibility data** (if applicable, per ISO 10993)
8. **Software documentation** (if applicable, per FDA software guidance)
9. **Electromagnetic compatibility (EMC)** data (if applicable)

**Literature Review Role in 510(k):**
- Literature is used to establish predicate device history, safety/effectiveness baseline, and applicable performance standards
- If using clinical data from a *comparable device* (not the exact predicate), adequate justification for data applicability is required
- Published literature from scientific databases can serve as clinical evidence supporting substantial equivalence
- FDA's 2023 draft guidance on Best Practices for Selecting a Predicate Device emphasizes the predicate must be free of unmitigated use-related or design-related safety issues and must not have been subject to a design-related recall

**When Clinical Data Are Required in a 510(k):**
Clinical data may be required when: (1) intended use differs from predicate, (2) technological characteristics raise new safety questions, (3) substantial equivalence cannot be established through non-clinical testing, or (4) newly discovered risks are associated with the predicate device ([The FDA Group 510(k) guide](https://www.thefdagroup.com/blog/510k-explained)).

**Submission Statistics:**
- FDA authorized **3,107 510(k)s in FY2024** (3,326 in FY2023; 3,238 in FY2025) ([Emergo by UL, 2024 CDRH Annual Report](https://www.emergobyul.com/news/us-fda-cdrh-2024-annual-report-summary))
- All 510(k)s must now use the electronic Submission Template and Resource (**eSTAR**), mandatory since October 1, 2023
- Average review time: ~160–180 days; FDA clears ~15 510(k)s per workday ([IntuitionLabs 510(k) analysis](https://intuitionlabs.ai/articles/fda-510k-premarket-notification-process))

---

### 1.4 De Novo Classification

**Regulatory Authority:** FDA CDRH  
**Legal Basis:** FD&C Act Section 513(f)(2)  
**Standard:** "Reasonable assurance of safety and effectiveness" under general or special controls (Class I or II), without a legally marketed predicate device  
**Key Feature:** A granted De Novo creates a new device classification and can itself serve as a predicate for future 510(k) submissions ([FDA De Novo page](https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/de-novo-classification-request))

**Two Entry Points:**
1. **Option 1:** After receiving a "not substantially equivalent" (NSE) determination on a 510(k) submission
2. **Option 2:** Directly, when the requester determines no legally marketed predicate exists (avoiding the 510(k) step)

**Evidence Requirements:**
The De Novo data requirements more closely resemble a PMA than a 510(k) — sponsors must demonstrate that general or special controls can provide reasonable assurance of safety and effectiveness ([FDLI De Novo factors, 2017](https://www.fdli.org/2017/04/factors-consider-submitting-de-novo-request/)):

- **Safety and effectiveness data** — bench testing, animal studies, clinical data depending on risk profile
- **Risk analysis** — must demonstrate controls are sufficient for proposed Class I or II classification
- **Benefit-risk assessment** — probable benefits must outweigh probable risks
- **Clinical evidence (if applicable)** — retrospective real-world data can qualify (e.g., DEN170052 for mobile fertility app used ~15,000-user retrospective dataset as primary clinical evidence)
- **Proposed special controls** — new classification regulations that will govern this and future similar devices
- **Literature review** supporting safety claims

**Costs:**
- User fee (FY2025): $162,235 — approximately 7x the 510(k) fee of ~$21,760 ([Complizen De Novo guide, 2025](https://www.complizen.ai/post/de-novo-fda-pathway-complete-guide))

**Annual Volume:**
- FDA authorized **47 De Novos in FY2024** (47 in FY2023; 27 in FY2025) ([Emergo by UL](https://www.emergobyul.com/news/us-fda-cdrh-2024-annual-report-summary))

---

### 1.5 Clinical Study Report (CSR)

A **Clinical Study Report (CSR)** is a comprehensive scientific document describing the design, conduct, statistical analysis, and results of a single clinical trial. It is the foundational evidence unit for regulatory submissions — each individual clinical study is submitted as a CSR in Module 5 of the eCTD ([FDA ICH E3 guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e3-structure-and-content-clinical-study-reports)).

**Standard:** ICH Guideline E3 (Structure and Content of Clinical Study Reports), approved 1996, Q&A supplement 2013

**Full CSR Contents per ICH E3:**
1. **Title page and synopsis** (stand-alone summary, typically 3–10 pages)
2. **Introduction** — rationale, prior clinical experience, study objectives
3. **Study objectives** (primary, secondary, exploratory)
4. **Investigational plan** — study design, selection and exit criteria, dosing, blinding
5. **Study patients** — patient disposition, demographics, baseline characteristics, protocol deviations
6. **Efficacy evaluation** — statistical analysis plan, primary and secondary endpoints, results tables and figures
7. **Safety evaluation** — adverse events, deaths, laboratory data, vital signs, ECGs
8. **Discussion and overall conclusions**
9. **Reference list**
10. **Appendices** — protocol, amendments, sample CRF, investigator list, IRB approvals, statistical methodology, patient data listings

**Types of CSRs:**
- **Full CSR:** Required for pivotal trials and human pharmacology studies contributing to efficacy/safety evaluation
- **Abbreviated CSR:** Acceptable for supportive studies not designed to establish efficacy (per ICH E3 and FDA 1999 guidance)
- **Synopsis only:** Sometimes acceptable for very early-phase or non-contributing studies

**Regulatory Updates:**
- ICH E6(R3) Good Clinical Practice (2024–2025) updates emphasize data integrity, traceability, and risk-based monitoring — these cascade into CSR writing requirements
- eCTD v4.0 (effective September 2024) requires enhanced structured metadata and machine-readable formatting affecting CSR organization

Sources: [Clinion CSR guide](https://www.clinion.com/insight/clinical-study-reports-csr-complete-guide/); [ICH E3 Q&A FDA](https://www.fda.gov/media/84857/download)

---

### 1.6 Integrated Summary of Safety (ISS) and Integrated Summary of Efficacy (ISE)

While each CSR reports a single study, the **ISS and ISE synthesize data across the entire clinical program** to provide the FDA with a holistic view of the product's benefit-risk profile. These are required for NDA submissions under 21 CFR 314.50(d)(5)(v)–(vi) and strongly encouraged for BLAs ([FDA ISE guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/integrated-summary-effectiveness); [Quanticate ISS/ISE guide](https://www.quanticate.com/blog/integrated-summary-of-safety-efficacy-for-regulatory-submissions)).

**Regulatory Placement in CTD:**
- ISE → Module 5.3.5.3 (Reports of Analyses of Data from More Than One Study), cross-referenced to Module 2.7.3 (Summary of Clinical Efficacy)
- ISS → Module 5.3.5.3, cross-referenced to Module 2.7.4 (Summary of Clinical Safety)

**ISE — Integrated Summary of Efficacy**

Key components per FDA guidance ([FDA ISE guidance page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/integrated-summary-effectiveness)):
- Integrated summary demonstrating substantial evidence of effectiveness for each claimed indication
- Evidence supporting the dosage and administration section of labeling, including dose-response relationships
- Efficacy data analyzed by sex, age, racial, and other demographic subgroups
- Comparison of individual study results — consistency across studies and explanation of discrepancies
- Pooled analyses for insights across demographic subpopulations and dose-response
- Comparisons with alternative drugs (to contextualize clinical meaningfulness)
- Analysis of long-term effects and tolerance
- Review of relevant uncontrolled study data
- Justification for reliance on a single pivotal study (if applicable)

**ISS — Integrated Summary of Safety**

Key components per FDA guidance:
- Safety profiles integrated across all clinical studies (Phase I–III, including healthy volunteer data)
- Overall extent of exposure — number of patients by dose, duration, demographics
- Adverse events: overall analysis, serious adverse events, deaths, discontinuations
- Laboratory assessments: hematology, chemistry, urinalysis trends
- Dose-response analyses for adverse effects
- Drug-drug interaction data
- Drug-demographic interactions (PK/PD in special populations)
- Long-term adverse effects (≥6 months)
- Animal safety data relevant to human risk

**Key Technical Requirements:**
- All studies pooled in ISS/ISE must comply with CDISC data standards (SDTM for raw data; ADaM for analysis-ready datasets), mandatory for studies starting after December 17, 2016 ([Alira Health ISS/ISE requirements](https://alirahealth.com/education-hub/requirements-for-integrated-summaries-of-efficacy-and-safety-in-fda-submissions/))
- An **Integrated Statistical Analysis Plan (SAP)** must be in place before finalizing analyses
- Study pooling strategy must be prespecified and justified in a Study Data Standardization Plan (SDSP)
- FDA strongly recommends sharing the data integration and analysis strategy at the pre-NDA meeting

**ISS/ISE vs. Global Requirements:**

| Authority | ISE/ISS Requirement |
|-----------|---------------------|
| **FDA** | Mandatory for NDA (21 CFR 314.50); encouraged for BLA |
| **EMA** | Not separately mandated; integrated into Module 2.7.3 and 2.7.4 of the CTD |
| **PMDA (Japan)** | Not separately mandated; SDTM/CDISC required since 2017 |
| **Health Canada** | Not separately mandated; CTD format mandatory since January 2018 |

---

## 2. Volume and Economics

### 2.1 Annual Submission Volumes

**NDA and BLA (Pharmaceuticals/Biologics):**

| FY | NDAs Filed | BLAs Filed | Total Filed | Total Approved |
|----|-----------|-----------|-------------|----------------|
| 2023 | 123 | ~30 | ~153 | ~143 |
| 2024 | ~130 | ~30 | ~160 | ~143 |
| 2025 | 124 | 33 | 157 | 143 |

Sources: [FDA FY2025 Q4 Real Time Report](https://www.fda.gov/media/189426/download); [FDA FY2023 Q4 Real Time Report](https://www.fda.gov/media/173624/download)

Note: The above "filed" figures represent applications accepted for substantive review (after the 60-day filing decision). Novel drug approvals (NMEs + original BLAs) in 2024 totaled **50 novel approvals**, maintaining a 10-year rolling average of 46.5/year ([BLA Regulatory 2024 trends](https://bla-regulatory.com/fda-drug-approval-trends-2024-2025/)).

**Medical Devices (510(k), De Novo, PMA):**

| Submission Type | FY2022 | FY2023 | FY2024 | FY2025 |
|----------------|--------|--------|--------|--------|
| 510(k) clearances | 3,229 | 3,326 | 3,107 | 3,238 |
| De Novo | 23 | 47 | 47 | 27 |
| PMA (original) | 22 | 36 | 33 | 41 |
| PMA supplements | 2,126 | 2,180 | 2,217 | 2,210 |
| **Total FDA marketing authorizations** | **5,731** | **5,807** | **5,564** | **5,640** |

Source: [Emergo by UL CDRH 2024 Annual Report Summary](https://www.emergobyul.com/news/us-fda-cdrh-2024-annual-report-summary)

CDRH receives **~20,700 total submissions of all types per year** (including Q-submissions, IDEs, 513(g) requests). Only a fraction (~5,600) result in marketing authorizations.

### 2.2 What Percentage of Submissions Include Systematic Literature Reviews?

There are no published FDA statistics on the percentage of NDA/BLA submissions that include formal systematic literature reviews. However, based on regulatory context:

- **505(b)(2) NDAs:** By definition require literature-based evidence. These represent approximately **30–40% of all original NDA submissions** annually, based on FDA approval data patterns.
- **BLA submissions for biologics with extensive published literature** (e.g., repurposed proteins, well-characterized monoclonals) routinely include structured literature reviews.
- **510(k) submissions:** Literature is nearly universally included; the FDA and CFR explicitly require surveys of the literature for safety and known-use information ([Biotech Research Group](https://biotechresearchgroup.com/literature-reviews-are-valuable-in-regulatory-submissions/)).
- **De Novo submissions:** Literature reviews are required as part of the safety/effectiveness evidence package.
- A 2021–2022 FDA analysis found that **~92% of NME NDA/BLA submissions included RWE in some form** to support therapeutic context, and between 60–68% of all NDA/BLA approvals included some form of real-world or published data ([ScienceDirect RWE review](https://www.sciencedirect.com/science/article/abs/pii/S0149291824002716)).

### 2.3 Cost of Preparing Evidence Packages

**FDA Application Fees (FY2025):**
- NDA/BLA with clinical data: **$4.3 million** (up from $4.0M in FY2024; $3.2M in FY2023) ([Clinical Trials Arena, July 2024](https://www.clinicaltrialsarena.com/news/fda-cost-revealed-2025-application-drug/))
- NDA/BLA without clinical data: ~$2.2 million
- 510(k): ~$21,760 (FY2024)
- De Novo: $162,235 (FY2025)

**FDA's Internal Cost to Review an NDA/BLA (for context):**
- NDA NME with clinical data: ~$5.3–5.9 million in FY2014–2017 (FDA standard cost tables). Reflects FDA reviewer cost, not sponsor preparation cost.

**Sponsor Preparation Costs:**
Direct preparation costs for a full NDA/BLA submission package are not separately tracked as a line item, but drug development context indicates:
- Full drug development cost (preclinical through approval): **~$2.6 billion** (Tufts CSDD estimate, including cost of failures) ([GreenField Chemical analysis](https://greenfieldchemical.com/2023/08/10/the-staggering-cost-of-drug-development-a-look-at-the-numbers/))
- Phase III trials alone: **$350 million–$1 billion** per program
- Regulatory submission preparation (writing, publishing, filing): typically **$5–30 million** for a complex NDA/BLA, based on CRO project data and industry estimates; smaller programs or 505(b)(2) applications may be $1–10 million
- **Systematic literature review** alone: typically **$50,000–$500,000** depending on scope, therapeutic area, and number of databases searched
- Medical device clinical trial (supporting 510(k) to De Novo): **$1 million–$20 million** ([Complizen device trial cost guide](https://www.complizen.ai/post/how-much-do-medical-device-clinical-trials-actually-cost-complete-budget-breakdown))

### 2.4 Market Size: CROs and Consulting Firms

**Contract Research Organization (CRO) Market:**
- Global CRO services market: **$44.78 billion in 2024**, projected to reach **$80 billion by 2033** (CAGR 6.66%) ([Market Data Forecast](https://www.marketdataforecast.com/market-reports/contract-research-organization-services-market))
- Clinical segment dominates at 74–78% of market share
- Regulatory/medical affairs segment projected to grow significantly 2026–2035

**Pharmaceutical Regulatory Affairs Market (outsourcing + in-house):**
- Global pharmaceutical regulatory affairs market: **$9.47 billion in 2024**, projected to reach **$14.34 billion by 2030** (CAGR 7.17%) ([Grand View Research](https://www.grandviewresearch.com/industry-analysis/pharmaceutical-regulatory-affairs-market-report))
- US regulatory affairs market alone: **$5.19 billion in 2024**, projected to reach **$12.23 billion by 2034** ([BioSpace press release](https://www.biospace.com/press-releases/u-s-regulatory-affairs-market-size-to-surpass-usd-12-23-billion-by-2034))
- **Regulatory writing & publishing** is the dominant service segment (Grand View Research 2024)
- Outsourcing accounts for **59.07%** of the regulatory affairs market in 2024 (in-house: 40.93%)

**Regulatory Affairs Outsourcing Market:**
- $7.2 billion in 2024, projected to reach $15.43 billion by 2034 (CAGR 7.92%) ([Precedence Research](https://www.precedenceresearch.com/regulatory-affairs-outsourcing-market))
- Technavio projects growth of $4.71 billion at CAGR 12.3% through 2028 ([Technavio](https://www.technavio.com/report/regulatory-affairs-outsourcing-market-industry-analysis))

**Real-World Evidence Solutions Market (adjacent/growing):**
- US RWE solutions market: **$1.31 billion in 2025**, projected to reach **$3.52 billion by 2036** (CAGR 9.2%) ([Meticulous Research](https://www.meticulousresearch.com/product/us-rwe-solutions-market-5243))
- Global RWE solutions: **$20.03 billion in 2025**, projected to reach **$65.42 billion by 2034** (CAGR 14.4%) ([Fortune Business Insights](https://www.fortunebusinessinsights.com/real-world-evidence-solutions-market-107676))

**Major CROs and Regulatory Consulting Firms:**
Top firms serving this market include (not exhaustive):
- **Large CROs:** IQVIA, Parexel, PPD (Thermo Fisher Scientific), Syneos Health, PRA Health Sciences (ICON), Labcorp Drug Development, Charles River
- **Mid-size regulatory specialists:** Halloran Consulting, The FDA Group, Greenleaf Health, Armatus Regulatory, Rho Inc., Alira Health, Criterion Edge, Quanticate, Cytel, Certara
- **Academic/scientific CROs:** RTI Health Solutions, Evidera (PPD subsidiary), Mapi Group
- Thousands of small boutique firms (1–50 employees) serving biotech/medtech

---

## 3. Real-World Evidence (RWE) Trend

### 3.1 FDA's Framework for Real-World Evidence

**Definition:**
- **Real-World Data (RWD):** Data relating to patient health status and/or the delivery of health care routinely collected from a variety of sources (EHRs, insurance claims, patient registries, natural history databases, wearables, mobile apps)
- **Real-World Evidence (RWE):** Clinical evidence about the usage and potential benefits or risks of a medical product derived from analysis of RWD

**Legislative Mandate:**
The **21st Century Cures Act (December 2016)** directed FDA to evaluate the use of RWE to:
1. Support a new indication for a drug already approved under section 505(c) (FD&C Act)
2. Help satisfy post-approval study requirements

In response, FDA published the **"Framework for FDA's Real-World Evidence Program"** in December 2018 ([FDA RWE overview](https://www.fda.gov/science-research/science-and-research-special-topics/real-world-evidence)).

### 3.2 Key FDA Guidance Documents on RWE (as of 2024)

| Guidance | Status | Topic |
|----------|--------|-------|
| Framework for FDA's Real-World Evidence Program (2018) | Final | Overall framework |
| Real-World Data: Assessing EHRs and Claims Data | Final | Data source considerations |
| Registry data considerations | Final | Registry-based RWD |
| Data Standards for RWD Submissions | Final | Data submission requirements |
| Considerations for Use of RWD and RWE | Final (August 2023) | How to use RWD/RWE in submissions |
| Non-Interventional Studies for Drug and Biological Products | Final/Draft | Study design guidance |
| Externally Controlled Trials | Guidance | Single-arm trial design with RWD controls |
| Integrating RCTs into routine clinical practice | Guidance | Pragmatic trial design |

Source: [FDA RWE guidance page](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/considerations-use-real-world-data-and-real-world-evidence-support-regulatory-decision-making-drug)

### 3.3 Growing Acceptance of RWE in Regulatory Decisions

**Current State of Acceptance:**

- Since 2016, **35 drugs, biologics, or vaccines** have included RWE in their regulatory applications ([FDA press release, December 2025](https://www.fda.gov/news-events/press-announcements/fda-eliminates-major-barrier-using-real-world-evidence-drug-and-device-application-reviews))
- For **medical devices**, RWE has been more extensively used: **over 250 premarket authorizations** have included RWE since 2016
- From January 2019–June 2021, **116 drug/biologic approvals** included RWE; **65 of these studies** influenced FDA's final decision; 38 were incorporated into product labeling ([ScienceDirect, 2024](https://www.sciencedirect.com/article/abs/pii/S0149291824002716))
- 2021–2022 analysis: **92% of NME NDA/BLA submissions** included RWE to support therapeutic context; **16 of 88 NME applications** used RWE to support effectiveness or safety
- Labeling expansion (2022–May 2024): **25.2% of labeling expansion approvals** included or likely included RWE; 23–28% annually ([Therapeutic Innovation & Regulatory Science, June 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12446098/))

**December 2025 Policy Shift — Major Barrier Removed:**
FDA announced it will **no longer require identifiable individual patient data** when RWE is used in drug and device applications. Previously, FDA had required submission of private, individual-level patient data, making most large databases impractical for regulatory use. The new policy allows FDA reviewers to assess aggregate, de-identified data from sources like:
- National Cancer Institute's SEER database
- Hospital system EHR networks
- Insurance claims databases
- Electronic health record networks

This is expected to dramatically expand RWE use in submissions going forward ([FDA press release, December 15, 2025](https://www.fda.gov/news-events/press-announcements/fda-eliminates-major-barrier-using-real-world-evidence-drug-and-device-application-reviews)).

**Where RWE Is Most Used:**
- **Rare diseases (orphan drugs):** 20 of 243 non-oncology rare disease NDA/BLAs (2017–2022) used RWD to support efficacy; 45% received positive FDA feedback on the RWD quality ([Orphanet Journal of Rare Diseases, March 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10936002/))
- **Oncology:** Highest volume of RWE use; 43.6% of labeling expansion approvals with RWE were oncology products
- **Labeling expansion and supplemental applications:** RWE more commonly accepted for these vs. original approvals

### 3.4 Evidence Triangulation in FDA's Evolving Stance

FDA's approach now encourages "evidence triangulation" — combining:
1. **Randomized controlled trial (RCT) data** (gold standard for causality)
2. **Real-world observational data** (large population, real practice settings)
3. **Published literature** (historical controls, natural history studies)
4. **Patient registries** and **natural history studies** (especially for rare diseases)
5. **External control arms** using RWD (for single-arm trials)

FDA's PDUFA VII commitments (FY2023–2027) include:
- Reporting aggregate data on RWE submissions annually (by June 30, 2024)
- Public workshop on case studies to discuss what RWE meets regulatory requirements (by December 31, 2025)
- Updated or new RWE guidance documents (by December 31, 2026)
- The **Advancing RWE Program** established by December 2022 to identify approaches that meet regulatory requirements

Source: [Duke-Margolis slides, December 2024](https://healthpolicy.duke.edu/sites/default/files/2024-12/Slides%20-%20Optimizing%20the%20Use%20of%20RWE%20in%20Regulatory%20Decision%20Making%20for%20Drugs%20and%20Biological%20Products-Looking%20Forward.pdf)

---

## 4. European and Global Angle

### 4.1 European Medicines Agency (EMA)

**Regulatory Pathway:** Marketing Authorisation Application (MAA) — analogous to NDA/BLA

**Approval Pathways:**
| Pathway | Eligibility | Review Time |
|---------|-------------|-------------|
| **Centralized Procedure** | Mandatory for biotech, oncology, HIV/AIDS, neurodegenerative, rare diseases; optional for others | 210 active days (plus clock stops) |
| Decentralized Procedure | Non-mandatory products | Varies by member state |
| Mutual Recognition Procedure | Products already approved in ≥1 EU member state | Varies |
| National Procedure | Products marketed in single member state | Varies |

**Evidence Structure:** The CTD format (Modules 1–5) is mandatory, identical to FDA structure for Modules 2–5. Module 1 contains EU-specific administrative documents (EMA-specific application form, Summary of Product Characteristics, EU-specific labeling).

**Key Differences from FDA:**
- **ISE/ISS:** Not separately mandated as distinct documents; integrated data are captured within Module 2.7.3 (Summary of Clinical Efficacy) and Module 2.7.4 (Summary of Clinical Safety)
- **Benefit-risk assessment:** EMA requires an explicit benefit-risk evaluation by the Committee for Medicinal Products for Human Use (CHMP), which is typically more narrative and multidimensional than FDA's approach
- **Comparative effectiveness:** EMA guideline structure explicitly encourages comparison with established treatments; FDA is more conservative on requiring head-to-head data
- **PASS (Post-Authorization Safety Study):** EMA more routinely mandates post-approval safety studies as a condition of approval
- **Pediatric Investigation Plan (PIP):** Mandatory for all new medicines unless exempt; must be agreed before submission

**RWE at EMA:**
- Fewer than **1 in 10 EMA approvals (2020–2023)** incorporated RWE at first marketing authorization — significantly lower than FDA's ~30% rate ([JAMA Network Open, November 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12593103/))
- EMA lacks a dedicated RWE reporting template; inconsistent presentation across assessment reports
- EU Data Analysis and Real World Interrogation Network (DARWIN EU) initiative is building data infrastructure to accelerate RWE use
- Legislative changes in Germany and France (2023–2024) have expanded access to national health databases

**EMA Volume (2024):**
- EMA approved **34 new active substances (NASs) in 2024** ([CIRS R&D Briefing 101, 2025](https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf))
- Median submission gap vs. FDA: 49 days (products reach EMA 49 days after FDA submission, on median)

Sources: [EMA clinical guidelines page](https://www.ema.europa.eu/en/human-regulatory-overview/research-development/scientific-guidelines/clinical-efficacy-safety-guidelines); [Kivo MAA guide](https://kivo.io/news/marketing-authorisation-application-maa-submission-guide)

---

### 4.2 PMDA (Japan)

**Regulatory Authority:** Pharmaceuticals and Medical Devices Agency (PMDA), under MHLW  
**Legal Basis:** Pharmaceuticals and Medical Devices Act (PMD Act), significantly revised 2014, 2020, and 2025

**Evidence Requirements:**
- Full NDA in CTD/eCTD format (Japanese translations required for key sections, especially summaries and labeling)
- CDISC/SDTM data standards required since 2017
- Historically required Japan-specific Phase I data (Japanese subgroup studies); requirements have been relaxed for drugs already tested in diverse ethnic populations
- Strong emphasis on long-term safety data; typically requires 52-week controlled study data before approval for most chronic conditions

**Review Timelines:**
- Standard NDA: **12-month target** from acceptance
- Priority review (orphan, Sakigake): **6–9 months**
- Median actual review time has decreased from 600+ days (2005) to **333 days in 2023** (about 45% reduction over two decades)
- In 2024, median approval time was **290 days** from submission ([PMDA video, 2026](https://www.youtube.com/watch?v=vXMSvp7jVsc))

**2024 Volume:**
- PMDA approved **148 new drugs** in FY2024–25, including **66 new active ingredients** and 82 lifecycle updates — a record pace ([PharmaBoardroom, August 2025](https://pharmaboardroom.com/articles/japan-pmda-shoots-ahead-in-fy-2024%E2%80%9125-with-148-drug-approvals/))
- PMDA ranked **second globally** in 2024 NAS approvals (53), just behind FDA (56) ([CIRS R&D Briefing 101](https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf))

**Key Expedited Pathways:**
- **Sakigake Designation:** First-in-Japan innovative therapies; 6-month review target, dedicated PMDA concierge
- **Conditional Early Approval:** For serious rare diseases where confirmatory trial is impractical
- **Priority Review:** For significant improvements in efficacy or safety
- **Orphan Drug:** Diseases affecting <50,000 Japanese patients; 10-year reexamination period

**Drug Loss Challenge:**
Approximately **65% of new molecular entities approved in the US have not been approved in Japan** (as of ~2023) — the "Drug Loss" problem. PMDA has responded by relaxing Japan-only Phase I requirements and establishing a Consultation Center for Pediatric and Orphan Drug Development (CCPODD, launched July 2024).

**Submission Lag:** Median 727 days after FDA first submission — the longest lag among major regulators in 2024 ([CIRS R&D Briefing 101](https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf))

---

### 4.3 TGA (Australia)

**Regulatory Authority:** Therapeutic Goods Administration (TGA)  
**Register:** Australian Register of Therapeutic Goods (ARTG)

**Evidence Requirements for Drugs:**
- Full CTD format submission (parallels EMA/FDA structure)
- TGA undertakes ~**150 significant prescription medicine assessments per year** (new medicines or major variations) ([Australian Government inquiry, October 2023](https://www.health.gov.au/sites/default/files/2023-11/inquiry-into-approval-processes-for-new-drugs-and-novel-medical-technologies-in-australia.pdf))
- TGA approved **33 new active substances in 2024** ([CIRS R&D Briefing 101](https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf))
- **Abridged (reliance) pathway** available — TGA can rely on assessment reports from reference regulators (FDA, EMA, Health Canada, Swissmedic, etc.)
- Median submission gap after FDA: **219 days** (2024)

**Medical Devices:**
- TGA received **6,713 applications** for medical device inclusion in 2020–21
- Devices must demonstrate conformity with TGA Essential Principles (safety/performance)
- Higher-risk devices (Class III, Class IIb implantable): full conformity assessment required
- TGA accepts conformity assessment evidence from: EU Notified Bodies, FDA (PMA/510(k)), PMDA (Japan), Health Canada, Singapore HSA, MDSAP

**Project Orbis (Cross-Agency Collaboration):**
Between 2019–2021, Project Orbis facilitated simultaneous submissions and approvals across FDA, Health Canada (13 NASs), TGA (9), and others — reducing submission lags significantly ([Clarivate analysis, August 2022](https://clarivate.com/life-sciences-healthcare/blog/shorter-timelines-evolving-strategies-four-key-trends-in-regulatory-approvals-of-new-medicines/)).

---

### 4.4 Health Canada

**Regulatory Authority:** Health Canada's Health Products and Food Branch (HPFB)  
**Submission Type:** New Drug Submission (NDS) — analogous to NDA/BLA

**Key Features:**
- CTD format mandatory since **January 1, 2018**
- Standard review target: 300 calendar days for priority; 365 days for standard
- Literature-based submissions widely accepted, particularly for well-established use applications
- ISS/ISE not separately mandated; CTD structure applies

**Volume (2024):**
- Health Canada approved **24 NASs in 2024** ([CIRS R&D Briefing 101](https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf))
- Median submission gap after FDA: **262 days** (2024)
- Canada filed first for only **1% of new drugs** globally ([Health Affairs, February 2026](https://www.healthaffairs.org/doi/10.1377/hlthaff.2025.00595))

---

### 4.5 Global Opportunity — Scale vs. US-Only

**Comparative NAS Approvals by Agency (2024):**

| Agency | Country/Region | 2024 NAS Approvals | Median Submission Gap vs. FDA |
|--------|---------------|---------------------|-------------------------------|
| **FDA** | United States | **56** | 0 days (reference) |
| **PMDA** | Japan | **53** | 727 days |
| **Swissmedic** | Switzerland | 37 | 417 days |
| **EMA** | EU (27 countries) | **34** | 49 days |
| **TGA** | Australia | 33 | 219 days |
| **Health Canada** | Canada | 24 | 262 days |

Source: [CIRS R&D Briefing 101, 2025](https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf); [Health Affairs, February 2026](https://www.healthaffairs.org/doi/10.1377/hlthaff.2025.00595)

**Global Scale Multiplier:**
- For each product approved in the US, companies typically also pursue **EMA, PMDA, TGA, and Health Canada** — often requiring separate, tailored submission dossiers despite shared CTD framework
- 70% of new drugs are submitted to FDA first; 27% to EMA first; only 7% to PMDA and 1% to Health Canada first ([Health Affairs, February 2026](https://www.healthaffairs.org/doi/10.1377/hlthaff.2025.00595))
- **Global regulatory opportunity is 3–5x larger than US-only** for evidence preparation services, accounting for:
  - Parallel submissions to EMA, PMDA, TGA, Health Canada at comparable dossier complexity
  - Regional Module 1 adaptation for each jurisdiction
  - Country-specific labeling translations and bridging studies
  - Region-specific evidence requirements (e.g., Japanese ethnic sensitivity studies, EU comparative effectiveness data)

**Evidence Service Demand Multiplier by Pathway:**
| Submission | Evidence Synthesis Intensity | Typical SLR? |
|-----------|------------------------------|--------------|
| NDA (505(b)(1)) | Very high | Yes — background/known risk |
| NDA (505(b)(2)) | Extremely high | Yes — central to application |
| BLA | Very high | Yes — context/comparators |
| 510(k) | Moderate | Usually yes (informal) |
| De Novo | High | Yes |
| EMA MAA | Very high | Yes |
| PMDA NDA (Japan) | High (+ bridging) | Yes |
| TGA abridged | Moderate–High | Yes |
| Health Canada NDS | High | Yes |

---

## 5. Key Decision Makers and Buyers

### 5.1 Primary Buyer Personas for Evidence Synthesis Services

At biotech and pharmaceutical companies, the purchase of evidence synthesis services (systematic literature reviews, ISS/ISE preparation, meta-analyses, RWE studies, regulatory writing) involves several functional leaders. The decision typically sits at the intersection of **Regulatory Affairs, Medical Affairs, and Clinical Development**.

---

**A. Vice President / Senior Director of Regulatory Affairs**

*Most direct buyer for regulatory submission-specific evidence packages*

- **Role:** Owns the regulatory strategy, filing timelines, and submission quality
- **Pain points:** Meeting PDUFA dates, managing FDA interactions, preventing "Refuse to File" outcomes, demonstrating data completeness
- **Budget authority:** $5–30M+ department budgets at mid/large-size biotechs; at early-stage startups may rely on consultants for the entire function
- **What they buy:** Regulatory writing (CSRs, ISS, ISE, Module 2 summaries), 510(k)/De Novo preparation, literature-based submissions, regulatory consulting, eCTD publishing
- **Title variations:** VP Regulatory Affairs, SVP Regulatory Affairs, Chief Regulatory Officer (CRO), Head of Regulatory Affairs
- **Compensation range:** $200,000–$400,000+ ([RiteSite VP RA profile](http://www.ritesite.com/resume/Vice-President-Regulatory-Affairs-34463.htm))
- **Organizational reporting:** Typically reports to CMO or CSO; at small biotechs may report directly to CEO
- **Team size:** Ranges from 2–5 people at early-stage biotechs to 80–100+ at large pharma; one real-world example cites a **100-person regulatory team with a $20M budget** ([same RiteSite profile](http://www.ritesite.com/resume/Vice-President-Regulatory-Affairs-34463.htm))

---

**B. VP / Head of Medical Affairs**

*Buyer for evidence synthesis with broader lifecycle and medical communication applications*

- **Role:** Manages medical strategy, medical information, health economics/outcomes research (HEOR), MSL (Medical Science Liaison) programs, publication strategy
- **Pain points:** Scientific credibility with key opinion leaders, reimbursement dossiers, label expansion strategy, differentiation from competitors
- **Budget authority:** $5–50M+ depending on company size and stage
- **What they buy:** Systematic literature reviews (for publication, HTA submissions, and reimbursement), HEOR analyses, evidence gap assessments, publication plans, medical writing
- **Overlap with regulatory:** SLRs used for both regulatory submissions AND payer/HTA submissions (EMA CHMP, NICE, CADTH, ICER)
- **Key insight:** A well-designed SLR can serve both regulatory (FDA, EMA) and commercial (market access, HTA) goals simultaneously — creating leverage ([Criterion Edge, September 2025](https://criterionedge.com/designing-a-systematic-literature-review-slr-that-serves-both-regulatory-and-commercial-goals-for-pharmaceutical-companies/))

---

**C. VP / Head of Clinical Development / Chief Medical Officer**

*Sponsor of evidence synthesis for clinical strategy and development decisions*

- **Role:** Designs clinical trial programs, oversees clinical operations, owns overall benefit-risk profile
- **Pain points:** Development program efficiency, dose selection, go/no-go decisions, FDA interaction (pre-IND, End of Phase 2 meetings)
- **Budget authority:** Largest at pharma companies; often $50M–$500M+ for full development programs
- **What they buy:** Evidence gap analyses, natural history studies, comparator arm data via RWE, meta-analyses informing Phase III design, ISS/ISE preparation
- **Decision dynamics:** Clinical Development typically generates the data; Regulatory Affairs synthesizes it for submission; Medical Affairs uses it commercially

---

**D. Biostatistics and Data Sciences / Biometrics**

*Technical buyer and collaborator*

- **Role:** Manages statistical analysis plans, CDISC programming, ISS/ISE statistical analyses
- **Pain points:** CDISC compliance, pooling strategies, multiplicity adjustments, supporting FDA queries
- **What they buy:** CDISC programming services, statistical consulting, ISS/ISE analysis, meta-analysis methodology

---

### 5.2 Organizational Dynamics and Budget Authority

**At Early-Stage Biotech (Series A–C, pre-NDA):**
- Regulatory Affairs may be 1–3 people; most functions outsourced to CROs and regulatory consultants
- VP/Head of Regulatory Affairs is often the sole decision-maker and signs off on all evidence synthesis vendors
- Total regulatory outsourcing budget: **$500K–$5M/year**

**At Clinical-Stage Biotech (Phase II–III):**
- Dedicated Regulatory, Medical Affairs, and Biostats functions beginning to separate
- Evidence synthesis decisions may involve joint approval from VP RA + VP Clinical Development
- Total regulatory + evidence budget: **$5M–$50M/year**

**At Commercial-Stage Pharma/Biotech:**
- Mature procurement processes; vendor panels; preferred vendor agreements
- VP RA may control regulatory writing budget; VP Medical Affairs controls HEOR/SLR budget for non-submission purposes
- Multiple stakeholders must align: RA, Medical Affairs, CMO, and sometimes Legal

**McKinsey Insight on Submission Strategy:**
A McKinsey analysis found that pharmaceutical companies are increasingly treating regulatory submissions not just as compliance obligations but as "strategic capability building" exercises — with cross-functional orchestration across R&D and commercial functions beginning more than a year before submission ([McKinsey, September 2021](https://www.mckinsey.com/industries/life-sciences/our-insights/getting-strategic-about-new-product-submissions-in-the-pharma-industry)).

---

### 5.3 Typical Procurement Process

| Stage | Activity | Decision Maker |
|-------|----------|----------------|
| Evidence gap assessment | Identify what literature exists and what's missing | VP Clinical Development / VP RA |
| SLR scoping + vendor selection | Define scope, select search strategy, evaluate vendors | VP RA or Medical Affairs Director |
| SLR execution | Database searching, PRISMA screening, data extraction, synthesis | Outsourced to specialist CRO or academic center |
| Regulatory writing | ISS/ISE, Module 2 summaries, individual CSRs | RA team (in-house or outsourced) |
| Review and approval | QC, medical review, sign-off | CMO, VP RA, VP Biostats |
| Submission | eCTD publishing, ESG submission | Regulatory Operations |

**Average Cost of an Outsourced Systematic Literature Review:**
- Scope-dependent: $50,000 (narrow, single-indication, focused search) to $500,000+ (broad multi-indication, multiple databases, complex synthesis)
- Full HEOR-grade SLR with network meta-analysis: $200,000–$800,000
- Typical timeline: 3–9 months from kickoff to final report

---

## Appendix: Key Data Tables

### Submission Volume Summary (US FDA, FY2024)

| Type | Volume | Purpose |
|------|--------|---------|
| NDAs filed | ~130 | New drug marketing approvals |
| BLAs filed | ~30 | New biologic marketing approvals |
| 510(k)s authorized | 3,107 | Medical device clearances |
| De Novos authorized | 47 | Novel device classifications |
| PMA originals authorized | 33 | High-risk device approvals |
| PMA supplements authorized | 2,217 | Changes to approved devices |

### Global Regulatory Agency NAS Approvals (2024)

| Agency | Region | NAS Approvals 2024 |
|--------|--------|---------------------|
| FDA | United States | 56 |
| PMDA | Japan | 53 |
| Swissmedic | Switzerland | 37 |
| EMA | European Union | 34 |
| TGA | Australia | 33 |
| Health Canada | Canada | 24 |
| **Total (top 6)** | **Global** | **~237** |

### Market Size Summary

| Market | 2024 Value | 2030–2035 Projection | CAGR |
|--------|-----------|---------------------|------|
| Global CRO services | $44.78B | $80B (2033) | 6.66% |
| Global pharmaceutical regulatory affairs | $9.47B | $14.34B (2030) | 7.17% |
| US regulatory affairs | $5.19B | $12.23B (2034) | 9.1% |
| Global regulatory affairs outsourcing | $7.2B | $15.43B (2034) | 7.92% |
| US RWE solutions | $1.31B | $3.52B (2036) | 9.2% |
| Global RWE solutions | $20.03B | $65.42B (2034) | 14.4% |

---

## Key Source URLs

1. FDA eCTD requirements: https://www.fda.gov/drugs/electronic-regulatory-submission-and-review/electronic-common-technical-document-ectd
2. FDA BLA process (CBER): https://www.fda.gov/vaccines-blood-biologics/development-approval-process-cber/biologics-license-applications-bla-process-cber
3. FDA De Novo classification: https://www.fda.gov/medical-devices/premarket-submissions-selecting-and-preparing-correct-submission/de-novo-classification-request
4. FDA 510(k) predicate best practices (2023): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/best-practices-selecting-predicate-device-support-premarket-notification-510k-submission
5. FDA ICH E3 guidance (CSR): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/e3-structure-and-content-clinical-study-reports
6. FDA ICH E3 Q&A (PDF): https://www.fda.gov/media/84857/download
7. FDA ISE guidance: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/integrated-summary-effectiveness
8. FDA ISS/ISE location in CTD: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/integrated-summaries-effectiveness-and-safety-location-within-common-technical-document
9. FDA RWE framework overview: https://www.fda.gov/science-research/science-and-research-special-topics/real-world-evidence
10. FDA RWE barrier removal (Dec 2025): https://www.fda.gov/news-events/press-announcements/fda-eliminates-major-barrier-using-real-world-evidence-drug-and-device-application-reviews
11. FDA RWE guidance (August 2023): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/considerations-use-real-world-data-and-real-world-evidence-support-regulatory-decision-making-drug
12. FDA FY2025 Q4 Real Time Report: https://www.fda.gov/media/189426/download
13. FDA FY2023 Q4 Real Time Report: https://www.fda.gov/media/173624/download
14. CDRH 2024 Annual Report (Emergo): https://www.emergobyul.com/news/us-fda-cdrh-2024-annual-report-summary
15. FDA drug application fees FY2025: https://www.clinicaltrialsarena.com/news/fda-cost-revealed-2025-application-drug/
16. EMA clinical guidelines: https://www.ema.europa.eu/en/human-regulatory-overview/research-development/scientific-guidelines/clinical-efficacy-safety-guidelines
17. EMA MAA submission guide (Kivo): https://kivo.io/news/marketing-authorisation-application-maa-submission-guide
18. EMA RWE in approvals 2020–2023 (JAMA Network Open): https://pmc.ncbi.nlm.nih.gov/articles/PMC12593103/
19. PMDA approval stats (PharmaBoardroom): https://pharmaboardroom.com/articles/japan-pmda-shoots-ahead-in-fy-2024%E2%80%9125-with-148-drug-approvals/
20. PMDA regulatory pathways (IntuitionLabs): https://intuitionlabs.ai/articles/pmda-regulatory-pathways-japan
21. TGA performance 2023–24: https://www.tga.gov.au/resources/publication/corporate-reports/therapeutic-goods-administration-performance-report-2023-24
22. CIRS R&D Briefing 101 (global NAS approvals 2024): https://cirsci.org/wp-content/uploads/dlm_uploads/2025/08/CIRS-RD-Briefing-101-v1.1.pdf
23. Health Affairs submission gaps study: https://www.healthaffairs.org/doi/10.1377/hlthaff.2025.00595
24. RWE in NDA/BLA rare disease (Orphanet): https://pmc.ncbi.nlm.nih.gov/articles/PMC10936002/
25. RWE in labeling expansion (Therapeutic Innovation & Regulatory Science): https://pmc.ncbi.nlm.nih.gov/articles/PMC12446098/
26. Grand View pharmaceutical regulatory affairs market: https://www.grandviewresearch.com/industry-analysis/pharmaceutical-regulatory-affairs-market-report
27. US regulatory affairs market (BioSpace): https://www.biospace.com/press-releases/u-s-regulatory-affairs-market-size-to-surpass-usd-12-23-billion-by-2034
28. Global CRO market (Market Data Forecast): https://www.marketdataforecast.com/market-reports/contract-research-organization-services-market
29. Global RWE solutions market (Fortune Business Insights): https://www.fortunebusinessinsights.com/real-world-evidence-solutions-market-107676
30. Quanticate ISS/ISE guide: https://www.quanticate.com/blog/integrated-summary-of-safety-efficacy-for-regulatory-submissions
31. Alira Health ISS/ISE requirements: https://alirahealth.com/education-hub/requirements-for-integrated-summaries-of-efficacy-and-safety-in-fda-submissions/
32. Literature reviews in regulatory submissions (BRG): https://biotechresearchgroup.com/literature-reviews-are-valuable-in-regulatory-submissions/
33. Literature-based submissions (Intertek): https://www.intertek.com/blog/2026/01-16-literature-based-submissions-using-publicly-available-data-to-support-drug-development/
34. Systematic literature reviews in regulatory submissions (Criterion Edge): https://criterionedge.com/the-strategic-role-of-systematic-literature-reviews-slrs-in-pharmaceutical-and-combination-device-development/
35. McKinsey regulatory submission strategy: https://www.mckinsey.com/industries/life-sciences/our-insights/getting-strategic-about-new-product-submissions-in-the-pharma-industry
36. 2024 novel drug approvals trends (BLA Regulatory): https://bla-regulatory.com/fda-drug-approval-trends-2024-2025/
37. Drug development cost overview (GreenField): https://greenfieldchemical.com/2023/08/10/the-staggering-cost-of-drug-development-a-look-at-the-numbers/
38. De Novo complete guide (Complizen): https://www.complizen.ai/post/de-novo-fda-pathway-complete-guide
39. Duke-Margolis RWE slides December 2024: https://healthpolicy.duke.edu/sites/default/files/2024-12/Slides%20-%20Optimizing%20the%20Use%20of%20RWE%20in%20Regulatory%20Decision%20Making%20for%20Drugs%20and%20Biological%20Products-Looking%20Forward.pdf
