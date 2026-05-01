# The Attribution Impossibility — Complete Reference

**Last verified:** 2026-04-30 | **Lean:** 357 theorems, 6 axioms, 0 sorry, 58 files

This document is the authoritative reference for everything proved, validated, and available in this repository. It is designed so that any session — human or AI — can read this single file and know exactly what exists, where it lives, what it means, and how confident we are in each claim.

---

## 1. The Core Result

**What we prove:** No importance ranking — of input features or internal circuit components — can simultaneously be faithful (reflect the model's attributions), stable (consistent across equivalent models), and complete (rank all pairs) when interchangeable components exist under the Rashomon property.

**Why it matters:** Every practitioner who has ever retrained an XGBoost model and noticed the SHAP rankings changed is experiencing a mathematical inevitability, not a software bug. The impossibility applies to SHAP, LIME, permutation importance, activation patching, and any method that assigns importance scores to interchangeable components. 68% of 77 public datasets are affected.

**The exact boundary:** MI(X_j, X_k) > 0 — mutual information, not Pearson correlation. This captures nonlinear dependencies that VIF and Pearson miss entirely. On drug discovery data (BBBP), Pearson predicts 0% instability for a nonlinearly dependent pair; actual instability is 23%.

**The quantitative floor:** Any stable explanation has unfaithfulness ≥ Δ/2 on at least one Rashomon witness. No algorithm, no amount of computation, no clever method can beat this bound.

**The resolution:** Orbit averaging (DASH for features, G-invariant projection for circuits) is the provably unique optimal stable method. It achieves the explanation capacity bound with equality — minimum information loss among all stable approximations.

**Proof status:** The core impossibility (`explanation_impossibility`) has ZERO domain axioms — it follows from pure logic plus the Rashomon hypothesis. Machine-verified in Lean 4 with 0 sorry.

---

## 2. Lean Formalization

### 2.1 Scale and Organization

58 Lean 4 files, 357 theorems and lemmas, 6 axioms, 0 sorry. Organized in 15 abstraction levels from pure logic (Level 0) to optimality proofs (Level 14). The formalization caught 2 logical inconsistencies and 1 type mismatch that survived informal review.

**Toolchain:** leanprover/lean4:v4.29.0-rc8 with Mathlib (Analysis, Probability, Data.Finset).

**Build:** `lake build` or `make lean` (~5 min cached, ~20 min first build). Expected: 2890 jobs, 0 errors.

### 2.2 Axiom System (6 axioms — the irreducible core)

These 6 axioms are the only unproved assumptions in the entire formalization. Every theorem's axiom dependencies are tracked via `#print axioms`.

| # | Lean Name | Plain English | Why it can't be proved | Used by |
|---|-----------|--------------|----------------------|---------|
| 1 | `Model` | "There exist trained models" | Abstract type — can't be derived | Everything |
| 2 | `firstMover` | "Each model has a dominant feature" | Requires implementing XGBoost internals | GBDT bounds |
| 3 | `firstMover_surjective` | "Every feature can be dominant in some model" | Requires formalizing stochastic training | GBDT bounds, Rashomon |
| 4 | `crossGroupBaselineCore` | "Cross-group split counts depend on group indices only" | Requires formalizing Gaussian conditioning | Cross-group stability |
| 5 | `proportionalityConstant` | "Attribution = c × split count, with c > 0 uniform" | Empirical approximation (CV ≈ 0.35-0.66) | DASH equity, quantitative bounds |
| 6 | `modelMeasure` | "Models have a probability distribution" | Input data — the training distribution | Variance, ensemble bounds |

**Axiom stratification — what depends on what:**
- Core impossibility (`explanation_impossibility`): **0 axioms** — pure logic
- GBDT impossibility (`gbdt_impossibility_local`): **3 axioms** (1-3)
- DASH equity (`consensus_equity`): **5 axioms** (1-5)
- Full system (variance + query complexity): **6 axioms** (all)

**10 former axioms eliminated** by defining them as computable definitions: splitCount (if-then-else on firstMover group), attribution (c × splitCount), numTrees (field of FeatureSpace), modelMeasurableSpace (discrete σ-algebra), testing_constant (1/8 from Tsybakov 2009), and 5 derived properties of splitCount.

**Consistency:** The axiom system is non-vacuous — `Consistency.lean` constructs a concrete `Fin 4` model satisfying all 6 axioms simultaneously.

### 2.3 Key Theorems — Grouped by What They Prove

#### The Impossibility Itself

| Theorem | File | Axioms | What it proves | Why it matters |
|---------|------|--------|---------------|---------------|
| `explanation_impossibility` | ExplanationSystem.lean | 0 | F+S+D → ⊥ under Rashomon (abstract) | The most general version — applies to ANY explanation system |
| `attribution_impossibility` | Trilemma.lean | 0 behavioral | F+S+C → ⊥ for feature rankings | The ML-specific version, 4-line proof |
| `attribution_impossibility_weak` | Trilemma.lean | 0 behavioral | Same with implication-only faithfulness | Matches the paper's Definition 1 exactly |
| `impossibility_qualitative` | Qualitative.lean | 0 (hypotheses) | Impossibility from dominance + surjectivity only | Shows only 2 properties needed as hypotheses |
| `attribution_impossibility_bundled` | Setup.lean | 0 global | Fully parametric via GBDTSetup structure | Demonstrates axioms are convenience, not necessity |

**Methodology:** Each version uses strictly weaker assumptions. The progression from `explanation_impossibility` (abstract, zero axioms) through `attribution_impossibility` (ML-specific) to `gbdt_impossibility_local` (GBDT-specific, 3 axioms) demonstrates the impossibility holds at every level of specificity.

#### The Bilemma (Strengthening for Binary Questions)

| Theorem | File | Axioms | What it proves |
|---------|------|--------|---------------|
| `bilemma_of_compatible_eq` | Bilemma.lean | 0 | For binary H, F+S alone is impossible (no completeness needed) |
| `rashomon_unfaithfulness` | Bilemma.lean | 0 | ≥1 of every 2 Rashomon witnesses is unfaithful |
| `all_or_nothing` | Bilemma.lean | 0 | No "approximately faithful" middle ground for binary H |
| `shap_sign_bilemma` | Bilemma.lean | 0 | Constructive instance: SHAPSign (positive/negative) |
| `feature_selection_bilemma` | Bilemma.lean | 0 | Constructive instance: FeatureStatus (selected/not) |
| `counterfactual_bilemma` | Bilemma.lean | 0 | Constructive instance: CounterfactualDir (increase/decrease) |
| `mech_interp_bilemma` | MechInterp.lean | 0 | Circuit decomposition impossibility (derived Rashomon) |

**Why binary is harder:** Rankings have ties (a neutral element). Binary questions don't — every answer contradicts the other. This means the "drop completeness" resolution (DASH ties) doesn't work for binary questions. The only resolution is enrichment — adding a neutral element (e.g., "uncertain" as a third option). This is the "collapsed tightness" concept.

**Constructive instances:** All three ML instances (SHAPSign, FeatureStatus, CounterfactualDir) use inductive types with `decide`-closed proofs — zero axioms, fully constructive.

#### The Tightness Classification

| Theorem | File | What it proves |
|---------|------|---------------|
| `tightness_dichotomy` | BeyondBinary.lean | F+S achievable ↔ H has a neutral element |
| `coverageConflict_implies_no_neutral` | BeyondBinary.lean | Coverage conflict → no neutral → bilemma applies |
| `neutral_implies_FS_achievable` | BeyondBinary.lean | Neutral element → F+S is achievable (DASH provides the tie) |
| `neutral_destroys_coverageConflict` | BeyondBinary.lean | Enrichment eliminates coverage conflict |

**What this means in practice:** Before trying to build a stable explanation method, check whether your explanation space H has a neutral element. If yes (rankings have ties), DASH works. If no (binary questions like SHAP sign), you must either enrich H (add "uncertain") or accept unfaithfulness ≥ 1/2.

#### Model-Specific Quantitative Bounds

| Theorem | File | What it proves | Practical meaning |
|---------|------|---------------|-------------------|
| `split_gap_exact` | SplitGap.lean | Gap = ρ²T/(2-ρ²) | The first-mover advantage in split counts (pure algebra) |
| `ratio_tendsto_atTop` | Ratio.lean | 1/(1-ρ²) → ∞ | Attribution ratio diverges for GBDT as correlation → 1 |
| `lasso_impossibility` | Lasso.lean | Ratio = ∞ | Lasso gives all credit to one feature, zero to the other |
| `nn_impossibility` | NeuralNet.lean | Conditional | NN impossibility depends on which feature the network "captures" |
| `binary_group_flip_rate` | FlipRate.lean | Flip rate = exactly 1/2 | For m=2 collinear features, the ranking is literally a coin flip |

**The architecture discrimination:** Different model classes have quantitatively different impossibility profiles. GBDTs diverge as 1/(1-ρ²). Lasso is infinitely unfaithful (all-or-nothing selection). Neural nets are conditional on initialization. Random forests converge at O(1/√T) — the contrast case where the impossibility weakens with ensemble size.

**Empirical validation:** The corrected ratio 1/(1-αρ²) with α ≈ 2/π fits empirical GBDT data at R² = 0.89. The correction α accounts for finite-depth trees (the Lean-verified 1/(1-ρ²) assumes infinite depth / full signal capture).

#### The Design Space (Complete Characterization)

| Theorem | File | What it proves |
|---------|------|---------------|
| `design_space_theorem` | DesignSpace.lean | Exactly two families of attribution methods exist |
| `family_a_or_family_b` | DesignSpaceFull.lean | Exhaustiveness: no third family among deterministic methods |
| `dash_unique_pareto_optimal` | ParetoOptimality.lean | DASH Pareto-dominates all other stable methods |
| `tie_dominates_commitment` | BayesOptimalTie.lean | Bayes-optimal to report ties for symmetric features |
| `relaxation_paths_converge` | PathConvergence.lean | Both relaxation paths (drop S, drop C) converge to DASH |
| `consensus_equity` | Corollary.lean | DASH produces equal attributions for symmetric features |

**Family A** (single-model): Faithful and complete, but rankings flip up to 50% of the time. Every single-model method (TreeSHAP, KernelSHAP, permutation importance) is in this family.

**Family B** (orbit averaging / DASH): Faithful and stable, but reports ties for interchangeable features. DASH is Pareto-optimal within this family. Stability increases as 1 - O(1/M) with ensemble size M.

**No third family exists** among deterministic aggregation methods. The ideal point (S=1, U=0, C=complete) is infeasible. This is proved by contradiction: any method that is complete + faithful must track per-model attributions (Family A), and any method that is stable must produce ties for interchangeable components (Family B).

**Scope restriction:** The exhaustiveness proof applies to deterministic methods that compute rankings from per-model attributions. It explicitly excludes probabilistic rankings, confidence intervals, set-valued outputs, and methods that pool training data.

#### DASH Optimality (Multiple Independent Proofs)

| Theorem | File | Optimality claim |
|---------|------|-----------------|
| `sum_squares_ge_inv_M` | EnsembleBound.lean | Cauchy-Schwarz / Titu's lemma: Var ≥ σ²/M (DASH achieves equality) |
| `dash_unique_pareto_optimal` | ParetoOptimality.lean | Pareto-dominates all other stable methods |
| `tie_dominates_commitment` | BayesOptimalTie.lean | Bayes-optimal ties for symmetric features |
| `reynolds_best_approximation` | (universal repo) | Closest stable approximation in L² norm — minimum information loss |

**Why four proofs matter:** Each proof uses a different mathematical framework (Cauchy-Schwarz, Pareto ordering, Bayesian decision theory, projection geometry) and establishes a different kind of optimality. Together they show DASH is optimal from every angle — not just "a good method" but provably the unique best one.

#### The MI Boundary and Quantitative Bridge

| Theorem | File | What it proves |
|---------|------|---------------|
| `mi_is_exact_boundary` | MutualInformation.lean | MI > 0 ↔ Rashomon property holds (exact, not just sufficient) |
| `mi_quantitative_unfaithfulness` | (universal repo) | MI > 0 → any stable explanation has error ≥ Δ/2 |
| `mi_implies_positive_gap` | (universal repo) | MI > 0 → Rashomon witnesses have strictly opposite orderings |

**Why MI matters more than Pearson:** Pearson correlation captures only linear dependence. MI captures all statistical dependence including nonlinear. Example: X₂ = X₁² has |ρ| = 0.08 (Pearson says independent) but MI = 1.91 (strongly dependent). VIF = 1.008 (says no multicollinearity). The impossibility applies but ALL standard diagnostics miss it.

**Drug discovery validation:** On BBBP (blood-brain barrier permeability, binary molecular fingerprints), Pearson predicts 0% instability for a nonlinearly dependent pair; MI predicts 19.4%; actual is 23.1%. MI reduces prediction error from 23 to 3.6 percentage points.

#### Generalizations (Symmetric Bayes Dichotomy)

| Theorem | File | Domain |
|---------|------|--------|
| `symmetric_bayes_dichotomy` | SymmetricBayes.lean | General: any symmetric decision problem → two families |
| `model_selection_impossibility` | ModelSelection.lean | Cannot select among Rashomon-equivalent models |
| `causal_discovery_impossibility` | CausalDiscovery.lean | Cannot orient edges in Markov equivalence class |
| `conditional_attribution_impossibility` | ConditionalImpossibility.lean | Conditional SHAP doesn't escape when β_j = β_k |
| `fairness_audit_impossibility` | FairnessAudit.lean | SHAP proxy audit = coin flip for collinear features |
| `intersectional_audit_impossibility` | IntersectionalFairness.lean | K attributes: joint audit correctness = (1/2)^K |
| `gaussian_fim_impossibility` | FIMImpossibility.lean | FIM → Rashomon ellipsoid (independent proof path) |
| `rashomon_from_symmetry` | RashomonUniversality.lean | Permutation closure → Rashomon |
| `rashomon_inevitability` | RashomonInevitability.lean | Stochastic symmetric training → Rashomon is inevitable |
| `local_attribution_impossibility` | LocalGlobal.lean | Local instability ≥ global instability |

**The SBD pattern:** Any symmetric decision problem (where the population is invariant under a symmetry group G) admits exactly two strategy families: the faithful-but-unstable individual strategy and the stable-but-tied orbit average. This is not specific to attribution — it's a general theorem in invariant decision theory. Attribution, model selection, and causal discovery are three verified instances.

---

## 3. Empirical Results

### 3.1 Input-Level Attribution

#### The Ranking Lottery
- **What:** Train 50 XGBoost models (seeds 0-49, subsample=0.8) on Breast Cancer Wisconsin. Count distinct top-3 SHAP rankings.
- **Result:** 24 distinct top-3 rankings. The most common ranking appears in only 12% of runs. At 100 seeds: 35 distinct. Top-5: 46 distinct (0.4% agreement).
- **Control:** Deterministic training (subsample=1.0): 1 ranking for all seeds.
- **Cross-implementation:** LightGBM: 29 distinct. Random Forest: 40 distinct. The instability is implementation-independent.
- **Source:** `paper/scripts/ranking_replication_study.py`
- **Why it matters:** Any study reporting a specific SHAP ranking from a single model on Breast Cancer is reporting one of dozens of equally valid options.

#### Explanation Reversal (German Credit)
- **What:** Train 30 models per condition on German Credit (1,000 applicants, 24 features). Measure how often the top explanation category changes.
- **Result:** 45% of applicants (XGB, subsample=0.8) receive a different "most important feature" category. Applicant #91 gets 6 different top-feature labels across 30 seeds.
- **Control:** Deterministic (seed only, no subsampling): 0% reversal for boosted models, 35% for RF (due to bootstrap).
- **DASH resolution:** M=25 reduces disagreement to 8%.
- **Source:** `paper/scripts/financial_case_study.py`, `results_clinical_decision_reversal_v2.json`
- **Why it matters:** Under ECOA, the adverse action notice changes based on the training seed — a regulatory concern.

#### Prevalence Survey
- **What:** Test 77 public datasets for attribution instability (>10% within-group flip rate, 20 models per dataset).
- **Result:** 68% exhibit instability (Wilson CI: [56%, 77%]). For P ≥ 20 features: 93% ([81%, 98%]).
- **Power:** 32% at the 10% threshold — the 68% is a conservative lower bound.
- **Source:** `paper/scripts/prevalence_survey.py`

#### Diagnostics Performance
- **Minority fraction:** Spearman 0.92-0.98 with empirical flip rates across all datasets. Outperforms Gaussian Φ(-SNR) by 2× on real data (0.955 vs 0.463 on California Housing). 7 lines of code.
- **Model-class universality:** Tested on XGBoost, Random Forest, Ridge, LASSO across 3 datasets. Within-family ρ = 0.79-0.94. Cross-family agreement non-significant.
- **Bimodality:** Hartigan dip test: p < 0.002 for ρ ≥ 0.5, control p = 0.373 at ρ = 0.
- **Source:** `paper/scripts/comprehensive_validation.py`, `paper/scripts/snr_calibration.py`

#### Drug Discovery (MI Bridge Validation)
- **What:** Test MI as a dependence boundary on BBBP (binary molecular fingerprints).
- **Result:** Pearson predicts 0% instability. MI predicts 19.4%. Actual: 23.1%. MI reduces error by 23 → 3.6 percentage points.
- **Permutation threshold:** τ₉₅ = 0.027 (no post-hoc threshold selection).
- **Source:** `handoff-mi-bridge-session.md` (universal repo experiments)
- **Why it matters:** Standard multicollinearity diagnostics (VIF = 1.008, |ρ| = 0.08) are completely blind to nonlinear dependence.

### 3.2 Component-Level Attribution (TinyStories)

#### Setup
10 transformers trained from independent random seeds on TinyStories at two scales + GPT-2 fine-tuned as boundary condition. Component importance by activation patching (weight zeroing). 7 theory-derived predictions per configuration evaluated before any post-hoc analysis.

#### Results

| Config | Arch | PPL (CV%) | Full ρ | G-inv ρ | W-flip | B-flip | d | Split-half | Pass |
|--------|------|-----------|--------|---------|--------|--------|---|-----------|------|
| A | 4L/4H/d256 | 8.6 (0.7%) | 0.565 | **0.972** | 0.496 | 0.000 | 5.4 | 0.991 | 7/7 |
| B | 6L/8H/d512 | 10.0 (1.0%) | 0.540 | **0.982** | 0.489 | 0.000 | 11.9 | 0.960 | 7/7 |
| C (GPT-2 ft) | 12L/12H/d768 | 18.5 (0.1%) | 0.993 | 0.999 | 0.043 | 0.000 | — | 0.878 | 4/7 |

- **14/14 theory-derived predictions PASS** for from-scratch configs.
- **Within-layer flip ≈ 0.50:** Indistinguishable from the theoretical coin-flip prediction. Which head is "most important" is determined by the training seed.
- **Head-vs-MLP flip = 0.000:** The stable between-orbit structure is perfectly preserved across all 30 models.
- **Full S₄ realization:** All 4 heads in layer 0 of Config A appear as #1 across 10 seeds.
- **GPT-2 boundary:** Fine-tuning doesn't create Rashomon diversity. ρ = 0.993, flip = 4.3%. Theory correctly predicts: less Rashomon → less instability.

#### Controls
- **Split-half reliability:** Within-model measurements are highly precise (0.991, 0.960) — far exceeding between-model agreement (0.565, 0.540). The instability is structural, not measurement noise.
- **Random projection null:** G-invariant projection at 100th percentile of 1,000 random projections to the same dimensionality (permutation p < 0.001).
- **Mean ablation robustness:** G-inv ρ ≈ 0.97-0.99 under both weight zeroing and mean ablation. Cross-method per-model ρ ≈ 0.5-0.6 — methods disagree on raw heads but agree on V^G.

**Source:** `docs/tinystories-results-reference.json`, `docs/mean-ablation-results-reference.json`

### 3.3 Running Experiments (SageMaker ml.g5.12xlarge, 4x A10G)

| Experiment | What it tests | Status | Scripts |
|-----------|---------------|--------|---------|
| **GPT-2-small from scratch** | 7 predictions at the MI community's benchmark scale | IN PROGRESS | `experiments/gpt2_train.py`, `gpt2_evaluate.py` |
| **IOI circuit analysis** | Does IOI importance permute across seeds? | QUEUED | `experiments/ioi_analysis.py` |
| **SAE stability** | Do independently trained SAEs find the same features? | QUEUED | `experiments/sae_experiment.py` |

**Why GPT-2 matters:** All foundational MI papers (Wang et al. 2022, Olsson et al. 2022, Conmy et al. 2023) used GPT-2-small. Confirming the impossibility at this scale means every published head-level circuit finding is seed-dependent.

**Why SAE matters:** If SAE features are stable across SAE training seeds (expected, since the model is frozen), SAE-based interpretability escapes the Rashomon property — an important escape hatch. If unstable, the impossibility extends to the dominant MI paradigm.

**Crash recovery:** All experiments use atomic DONE markers and checkpoint resume. Safe to restart after instance interruption.

---

## 4. Papers

| Paper | File | Pages | Content | Status |
|-------|------|-------|---------|--------|
| **NeurIPS 2026** | `paper/main.tex` | 9+refs+checklist | Core impossibility + MI boundary + two-level validation + drug discovery | Needs 1-page cut (limit is 9) |
| **NeurIPS supplement** | `paper/supplement.tex` | 81 | Complete axiom system, all proofs, extended experiments, fairness tightness, Reynolds | READY |
| **Monograph** | `paper/main_definitive.tex` | 83 | Everything — the exhaustive reference | EXHAUSTIVE |
| **JMLR** | `paper/main_jmlr.tex` | 59 | Expanded NeurIPS with SBD, conditional, fairness, FIM | READY (after NeurIPS) |
| **arXiv preprint** | `paper/main_preprint.tex` | 10 | NeurIPS with authors visible | READY |
| **OpenReview abstract** | `paper/abstract_openreview.txt` | 200 words | Submission abstract | READY |
| **arXiv monograph** | `paper/arxiv_monograph.tar.gz` | 83 | Self-contained arXiv package | READY |

**Deadlines:** Abstract May 4, Paper May 6 (NeurIPS 2026, AOE).

---

## 5. Naming Conventions

See `docs/naming-conventions.md` for the full table. Key terms:

| Concept | Canonical name | Do NOT use |
|---------|---------------|------------|
| Orbit average / DASH / V^G | **The stable projection** | "explanation code" |
| unfaith₁ + unfaith₂ ≥ Δ−δ | **Explanation uncertainty bound** | "uncertainty relation" |
| dim(V^G) | **Explanation capacity** (C) | "invariant subspace dimension" |
| The η prediction | **Explanation Capacity Theorem** | "Capacity Law" |
| η = 1 − C/dim(V) | **Explanation loss rate** | "instability rate" |

---

## 6. Cross-Repo Map

| Repo | Path | What it provides | This repo uses |
|------|------|-----------------|---------------|
| **dash-shap** | ../dash-shap | DASH Python implementation, stability API (PR #255), model-class comparison scripts | Referenced in paper, not imported |
| **universal-explanation-impossibility** | ../universal-explanation-impossibility | `reynolds_best_approximation`, MI bridge theorems, TinyStories training data, drug discovery experiments | 3 Lean theorems cited in NeurIPS paper |
| **ostrowski-impossibility** | ../ostrowski-impossibility | Fairness tightness experiment (`scripts/fairness_tightness_v3.py`), approximate bilemma (ostrowski version), Langlands connection | Fairness tightness referenced in supplement |

---

## 7. Verification Commands

```bash
# Lean counts (must match: 357/6/0/58)
grep -c "^theorem\|^lemma" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "theorems+lemmas:", s}'
grep -c "^axiom" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "axioms:", s}'
grep -rc "sorry" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "sorry:", s}'
ls DASHImpossibility/*.lean | wc -l | awk '{print "files:", $1}'

# Build Lean
make lean  # or: lake build

# Compile all papers
make paper

# Full verification
make verify
```
