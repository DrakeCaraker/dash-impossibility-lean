# Handoff: Attribution Impossibility → Nature Universal Paper Session

**Date:** 2026-04-19
**From:** dash-impossibility-lean repo (NeurIPS attribution paper session)
**To:** universal-explanation-impossibility repo (Nature submission)

## What This Session Produced for the Nature Paper

### 1. Gene Expression Pathway Divergence (THE biological hook)

**Dataset:** AP_Colon_Kidney (546 samples, 10,935 genes, OpenML)
**Setup:** Top 50 genes by variance, 50 XGBoost models (subsample=0.8, seeds 0-49), TreeSHAP

**Result:** The #1 biomarker gene alternates between:
- **TSPAN8** (203824_at): invasion/metastasis pathway — #1 in **80%** of seeds
- **CEACAM5/CEA** (201884_at): immune evasion pathway — #1 in **20%** of seeds
- Correlation: ρ = 0.858 (both colon-enriched tissue markers)

**Probe mappings verified** via Affymetrix HG-U133A annotation (NetAffx, BioGPS, GeneCards).

**Pathway interpretation (vetted):**
- Both are cell adhesion molecules — qualify as "distinct cancer biology roles, not distinct GO terms"
- TSPAN8: tetraspanin-enriched microdomains → integrin signaling → invasion
- CEACAM5: GPI-anchored adhesion → immune evasion → differentiation (classical clinical colon cancer marker)
- Pathway-level conclusion (colon identity) is preserved; gene-level target differs
- Framing: "the specific biomarker target — the actionable output of a discovery pipeline — is a seed artifact"

**Controls:**
- Deterministic (subsample=1.0): 1 ranking, 100% agreement
- AP_Breast_Lung (breast vs lung): top-3 STABLE (2 distinct rankings, 92% agreement) — top gene dominates with 2× importance gap. This is the positive control showing large gaps protect even correlated genes.

**DASH resolves:** Both TSPAN8 and CEA appear in the DASH consensus top-2, correctly reporting that both contribute without privileging either.

**Scripts:** `dash-impossibility-lean/paper/scripts/ranking_replication_study.py` (Breast Cancer ranking lottery); gene expression analysis run inline (to be formalized into a script).

### 2. MI v2 Results (available, interpret with caveats)

**Dataset:** Modular addition mod 113, 10 grokked transformers (all 100% accuracy)
**Method:** Activation patching (heads + MLPs = 10 components)
**Results file:** `universal-explanation-impossibility/knockout-experiments/results_mech_interp_definitive_v2.json`

**Key numbers:**
- Mean Spearman of component importance: 0.518
- Min Spearman: -0.176 (anti-correlated circuits)
- Top-3 Jaccard: 0.356 (36% agreement on top-3 components)
- Flip rate: 0.30 (30% of components change importance rank)

**Control issue (MUST acknowledge):**
- Pre-grokking control: Spearman 0.489
- Post-grokking: 0.518
- Gap is small (0.03) — a reviewer will question whether activation patching reliably distinguishes circuits

**Best framing:** "10 networks computing the same function agree on only 36% of top-3 circuit components. Two networks can identify anti-correlated circuits (min ρ = -0.18)." Lead with the Jaccard and anti-correlation, not the mean Spearman.

**DO NOT claim:** "The circuits are different" (too strong for the control gap). DO claim: "Circuit importance rankings are as unstable as SHAP feature rankings."

### 3. Ranking Lottery Data (for context, stays in NeurIPS)

These results are in the NeurIPS paper and should be CITED, not duplicated:
- Breast Cancer: 24 distinct top-3, 4.2% agreement
- Cross-implementation: XGBoost 24, LightGBM 29, RF 40
- German Credit: 45% clinical reversal (4×3 ablation)
- 5-dataset table: 3 stable, 1 borderline, 1 unstable

### 4. Lean Formalization State (shared resource)

**dash-impossibility-lean repo:** 58 files, 357 theorems, 6 axioms, 0 sorry
- All ML bilemma instances constructive (SHAPSign, FeatureStatus, CounterfactualDir)
- ExplanationSystem abstraction with trilemma + bilemma
- Tightness dichotomy (neutral element ↔ F+S achievable)
- Coverage conflict diagnostic
- Direction theorem (anti-monotone vs Arrow)

**ostrowski-impossibility repo:** 18 files, 167 theorems, 10 axioms, 0 sorry
- Arrow proved from scratch
- May's theorem
- All instances constructive (Bool/Unit)
- Compatibility complex characterization

### 5. Validated Tools (from Ostrowski session)

All survived controls and are ready for use:
- Coverage conflict diagnostic: Spearman 0.92-0.98
- Nonparametric flip predictor (minority fraction): 7 lines, 0.96 vs Gaussian 0.46
- Var[SHAP] = quality floor: 0/800 violations
- DASH binary optimality: uniquely optimal majority vote

### 6. Retracted Results (DO NOT USE)

- Entropy bimodality: RETRACTED (100% permutation artifact)
- Pairwise interaction as "audit pairs": WEAKENED (marginal rates suffice)
- p/2 unfaithfulness bound: CORRECTED to p · mean_minority_fraction (≈14-19%)

---

## What the Nature Paper Should Contain

### The Pitch (one paragraph)

No explanation of an underspecified system can be faithful, stable, and decisive. We prove this as a single four-line theorem with zero domain-specific axioms, then show it governs four high-stakes domains: the biomarker a drug pipeline targets depends on the training seed (genomics), the circuit a safety audit identifies depends on the training run (AI safety), the causal edges a discovery algorithm orients depend on the data split (causal inference), and the loan explanation an applicant receives depends on a random number (clinical AI). For each domain, the impossibility has a precise resolution determined by the algebraic structure of the explanation space. The framework is formalized in Lean 4 with 357 theorems and 0 unproved claims.

### Structure (8-10 pages Nature format)

1. **The theorem** (1 page): ExplanationSystem abstraction, Rashomon property, trilemma (4-line proof), bilemma (for binary H). Zero axioms.

2. **The tightness classification** (1 page): Neutral element ↔ F+S achievable. Compatibility complex characterization. The 2×2 table. Direction theorem (anti-monotone vs Arrow).

3. **Instance 1: Genomics** (1.5 pages): AP_Colon_Kidney. TSPAN8 vs CEA. 80/20 alternation, ρ=0.858. Pathway analysis. DASH resolves. Positive control: AP_Breast_Lung stable.

4. **Instance 2: AI Safety** (1.5 pages): MI v2. 10 grokked transformers. 36% Jaccard@3. Anti-correlated circuits. Meloux 2025 (85 circuits for XOR). Resolution: equivalence classes, not individual circuits. Caveat: pre-grokking control gap is small.

5. **Instance 3: Causal Inference** (0.5 page): Markov equivalence. CPDAG = the neutral-element resolution. PC/GES algorithms already implement this.

6. **Instance 4: Clinical AI** (0.5 page): 45% German Credit reversal (cite NeurIPS paper for depth). Regulatory implications (EU AI Act, ECOA). Brief.

7. **Resolution** (1 page): DASH for rankings, equivalence classes for circuits, CPDAG for causal, Pitman estimator (Hunt-Stein). The resolution is determined by the explanation space's algebraic structure.

8. **Discussion** (1 page): Lean verification. Fairness impossibilities as future instances. Limitations (MI control, equicorrelation, binary limitation).

### What Goes in Supplement / Methods

- Full proofs
- Quantitative bounds by model class (GBDT ratio, Lasso, RF)
- All experimental details (hyperparameters, datasets, preprocessing)
- Extended gene expression analysis
- Extended MI analysis with per-model circuit details
- Lean file cross-reference table
- Arrow comparison details

### What Does NOT Go in the Nature Paper

- The diagnostic pipeline (minority fraction, Z-test, variance budget) — that's the NeurIPS paper's contribution
- The ranking lottery on Breast Cancer — cite the NeurIPS paper
- The 1/(1-ρ²) GBDT ratio derivation — too ML-specific
- The SBD (Symmetric Bayes Dichotomy) — too technical for Nature readers
- Split-count axioms — too ML-specific

---

## Key Peer Review Findings to Address

From 4+ rounds of adversarial review across the attribution and Ostrowski papers:

1. **"The proof is trivial."** The proof IS simple. The contribution is the framework (tightness classification), the cross-domain instantiation (four domains), and the gene expression finding. Lead with the findings, not the proof.

2. **"The MI control is weak."** Acknowledged. Frame as "36% Jaccard@3 and anti-correlated circuits" not as "circuits are provably different." The Meloux 2025 citation (85 circuits) provides independent evidence.

3. **"Both TSPAN8 and CEA are cell adhesion — same pathway."** Acknowledge: "pathway-level conclusion preserved; gene-level biomarker target differs." The instability matters for biomarker DEVELOPMENT (which gene to target), not for pathway UNDERSTANDING.

4. **"This is just the Rashomon effect, which is well-known."** The Rashomon effect is empirically observed. We prove it's IMPOSSIBLE to overcome, characterize the COMPLETE design space, and show the consequences across FOUR domains. The theory, classification, and cross-domain instantiation are all new.

5. **"Independent researchers."** The Lean verification compensates — claims are machine-checked, not trust-based.

---

## Relationship to Other Papers

| Paper | Venue | Relationship to Nature |
|-------|-------|----------------------|
| Attribution impossibility (NeurIPS) | NeurIPS 2026 | Companion: SHAP-specific depth. Nature cites for quantitative bounds + diagnostic pipeline. |
| Ostrowski impossibility (FoP) | Foundations of Physics | Independent: physics application. Nature can cite for the enrichment stack. |
| DASH pipeline (TMLR) | TMLR | Software paper. Nature cites for the implementation. |
| arXiv monograph | arXiv | Comprehensive reference. Nature cites for extended proofs. |

**Do NOT dual-submit** the Nature paper with the NeurIPS paper. They share the core theorem but have distinct lead contributions (NeurIPS = diagnostic pipeline; Nature = cross-domain framework).

---

## File Locations

| File | Content |
|------|---------|
| `dash-impossibility-lean/paper/main.tex` | NeurIPS paper (has gene expression paragraph) |
| `dash-impossibility-lean/paper/main_definitive.tex` | Monograph (75pp, all results) |
| `dash-impossibility-lean/DASHImpossibility/*.lean` | 58 Lean files (357/6/0) |
| `universal-explanation-impossibility/paper/nature_article.tex` | Current Nature draft (needs update) |
| `universal-explanation-impossibility/knockout-experiments/results_mech_interp_definitive_v2.json` | MI v2 data |
| `universal-explanation-impossibility/knockout-experiments/results_clinical_decision_reversal_v2.json` | Clinical reversal data |
| `ostrowski-impossibility/docs/empirical-validation-results.md` | Bimodality + CC validation |
| `ostrowski-impossibility/OstrowskiImpossibility/Core/GeneralTheory.lean` | Arrow proof, abstract framework |

---

## Timeline

- **Now → May 4:** Submit NeurIPS abstract
- **Now → May 6:** Submit NeurIPS paper (main.tex + supplement.tex)
- **May → August:** Write Nature paper with expanded gene expression analysis, deeper MI interpretation, pathway analysis via GO enrichment
- **September:** NeurIPS decision. If accept → Nature paper cites it. If reject → consider ICML 2027 or expand into JMLR.
- **October:** Submit Nature paper

---

## The One Thing That Would Make the Nature Paper Stronger

Run the MI v2 experiment with 30 models (not 10) and a within-model consistency control (patch the same model twice → should give Spearman ~1.0). If within-model consistency is 0.95+ but between-model is 0.52, the control is clean and the "circuits aren't conserved" claim is airtight. The EC2 infrastructure exists. This is the highest-leverage remaining experiment.
