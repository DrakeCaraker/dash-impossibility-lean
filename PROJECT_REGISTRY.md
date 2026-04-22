# Project Registry

**Auto-verified:** Run `make registry-check` or `python3 paper/scripts/verify_registry.py` to validate all machine-checkable claims below.

**Last verified:** 2026-04-22 | **Lean:** 357 theorems, 6 axioms, 0 sorry, 58 files

---

## 1. Lean Formalization State

```
Theorems+lemmas: 357
Axioms:          6
Sorry:           0
Files:           58
Toolchain:       leanprover/lean4:v4.29.0-rc8
Mathlib:         yes (Analysis, Probability, Data.Finset)
```

### 1.1 Axiom Inventory (6 total, all in Defs.lean)

| # | Name | Type | Justification | Derivable? |
|---|------|------|---------------|------------|
| 1 | `Model` | Type declaration | Abstract trained model | No (structural) |
| 2 | `firstMover` | Function | Dominant feature per model | No (requires implementing XGBoost) |
| 3 | `firstMover_surjective` | Behavioral | DGP symmetry: every feature can be first-mover | Yes (formalize stochastic training) |
| 4 | `crossGroupBaselineCore` | Structural | Cross-group split counts depend only on group indices | Yes (formalize Gaussian conditioning) |
| 5 | `proportionalityConstant` | Empirical | φ_j = c · n_j with c > 0 | No (empirical approximation, CV ≈ 0.35-0.66) |
| 6 | `modelMeasure` | External | Training distribution over models | No (input data) |

### 1.2 Axiom Reduction History

- v1: 16 axioms (splitCount axiomatized with 5 property axioms)
- v2: 10 axioms (splitCount DEFINED, crossGroupBaseline refactored)
- v3: 6 axioms (numTrees bundled, attribution DEFINED, modelMeasurableSpace = ⊤, testing_constant = 1/8)

### 1.3 Proof Chain (5 levels)

#### Level 0 — Zero axioms (pure logic)
| Theorem | File | What it proves |
|---------|------|---------------|
| `explanation_impossibility` | ExplanationSystem.lean | Abstract trilemma: F+S+D → ⊥ under Rashomon |
| `attribution_impossibility` | Trilemma.lean | Feature ranking trilemma (4-line proof) |
| `attribution_impossibility_weak` | Trilemma.lean | Implication-only faithfulness version |
| `bilemma_of_compatible_eq` | Bilemma.lean | Binary H: F+S → ⊥ (no completeness needed) |
| `rashomon_unfaithfulness` | Bilemma.lean | ≥1 unfaithful per Rashomon pair |
| `all_or_nothing` | Bilemma.lean | No approximate faithfulness for binary H |
| `tightness_dichotomy` | BeyondBinary.lean | Neutral ↔ F+S achievable |
| `neutral_implies_FS_achievable` | BeyondBinary.lean | Direction theorem |
| `coverageConflict_implies_no_neutral` | BeyondBinary.lean | Coverage conflict → bilemma applies |
| `shap_sign_bilemma` | Bilemma.lean | SHAPSign constructive instance |
| `feature_selection_bilemma` | Bilemma.lean | FeatureStatus constructive instance |
| `counterfactual_bilemma` | Bilemma.lean | CounterfactualDir constructive instance |

#### Level 1 — 2 axioms (Model, firstMover)
| Theorem | File | What it proves |
|---------|------|---------------|
| `iterative_impossibility` | Iterative.lean | IterativeOptimizer → Rashomon |

#### Level 2 — 3 axioms (+firstMover_surjective)
| Theorem | File | What it proves |
|---------|------|---------------|
| `gbdt_impossibility_local` | ProportionalityLocal.lean | GBDT impossibility without proportionality |
| `rashomon_from_symmetry` | RashomonUniversality.lean | Permutation closure → Rashomon |
| `rashomon_inevitability` | RashomonInevitability.lean | Stochastic symmetric training → Rashomon |

#### Level 3 — 4 axioms (+crossGroupBaselineCore)
| Theorem | File | What it proves |
|---------|------|---------------|
| `splitCount` (def) | Defs.lean | DEFINED: if-then-else on firstMover group |
| `splitCount_firstMover` | Defs.lean | DERIVED: first-mover gets T/(2-ρ²) |
| `splitCount_nonFirstMover` | Defs.lean | DERIVED: others get (1-ρ²)T/(2-ρ²) |
| `split_gap_exact` | SplitGap.lean | Pure algebra: gap = ρ²T/(2-ρ²) |
| `ratio_tendsto_atTop` | Ratio.lean | 1/(1-ρ²) → ∞ as ρ → 1 |

#### Level 4 — 5 axioms (+proportionalityConstant)
| Theorem | File | What it proves |
|---------|------|---------------|
| `attribution` (def) | Defs.lean | DEFINED: c * splitCount |
| `proportionality_global` | Defs.lean | DERIVED from definition |
| `attribution_sum_symmetric` | SymmetryDerive.lean | ∑φ_j = ∑φ_k for balanced ensembles (35 lines) |
| `consensus_equity` | Corollary.lean | DASH equity |
| `design_space_theorem` | DesignSpace.lean | Exactly two families |
| `family_a_or_family_b` | DesignSpaceFull.lean | Exhaustiveness |
| `sum_squares_ge_inv_M` | EnsembleBound.lean | Cauchy-Schwarz / Titu's lemma |

#### Level 5 — 6 axioms (+modelMeasure, full system)
| Theorem | File | What it proves |
|---------|------|---------------|
| `attribution_variance` (def) | Defs.lean | From Mathlib ProbabilityTheory.variance |
| `attribution_prob_half` | UnfaithfulQuantitative.lean | Unfaithfulness = exactly 1/2 |
| `tie_dominates_commitment` | BayesOptimalTie.lean | Bayes-optimal ties |
| `dash_unique_pareto_optimal` | ParetoOptimality.lean | DASH Pareto dominance |

---

## 2. Experimental Results

### 2.1 Validated (survived all controls)

| Result | Key number | Source | Status |
|--------|-----------|--------|--------|
| Ranking lottery (Breast Cancer) | 24 distinct top-3 (50 seeds), 35 (100 seeds) | ranking_replication_study.py | **VALIDATED** |
| Cross-implementation lottery | XGB 24, LGB 29, RF 40 | ranking_replication_study.py | **VALIDATED** |
| Subsample sensitivity | 17 distinct at 0.95, 1 at 1.0 | ranking_replication_study.py | **VALIDATED** |
| Gene expression (TSPAN8 vs CEA) | 80/20 alternation, ρ=0.858 | inline (AP_Colon_Kidney) | **VALIDATED** |
| Gene expression positive control | AP_Breast_Lung top-3 stable (92%) | inline | **VALIDATED** |
| Clinical reversal (German Credit) | 45% XGB, 46% LGB, 35% RF | results_clinical_decision_reversal_v2.json (universal repo) | **VALIDATED** |
| Coverage conflict diagnostic | Spearman 0.59-0.98, 4 model classes | validate_predictions.py (ostrowski repo) | **VALIDATED** |
| Minority fraction vs Gaussian | 0.96 vs 0.46 on California Housing | validate_predictions.py (ostrowski repo) | **VALIDATED** |
| Var[SHAP] = min MSE | 0/800 violations at machine precision | test_variance_bound.py (ostrowski repo) | **VALIDATED** |
| Bimodality (synthetic ρ ≥ 0.5) | Dip p < 0.002, permutation-validated | validate_predictions.py (ostrowski repo) | **VALIDATED** |
| Model-class universality | CC works for XGB/RF/Ridge/LASSO | model_class_rigorous.py (dash-shap repo) | **VALIDATED** |
| NN attribution instability | 87% unstable, 8:1 model vs SHAP noise | paper experiments | **VALIDATED** |
| MI circuit multiplicity | 36% Jaccard@3, 10 grokked transformers | results_mech_interp_definitive_v2.json (universal repo) | **VALIDATED** (weak control) |
| Published ranking replication | 4 pairs reported stable, 28-48% flip | paper experiments | **VALIDATED** |
| Prevalence survey | 68% of 77 datasets | paper experiments | **VALIDATED** |
| SNR calibration | R²=0.94 across 1,325 pairs | paper experiments | **VALIDATED** |

### 2.2 Retracted (DO NOT USE)

| Result | Why retracted | Session |
|--------|---------------|---------|
| Entropy bimodality | 100% permutation artifact | Ostrowski |
| Pairwise "audit pairs" | Marginal rates suffice, no pair-specific signal | Ostrowski |
| p/2 unfaithfulness bound | Correct: p · mean_minority_fraction (≈14-19%) | Ostrowski |
| Data-only instability prediction | Max Spearman 0.26 — no data-only formula exists | Ostrowski |
| η from correlation thresholds | Inverts reality for XGBoost+SHAP | Ostrowski |
| Phase transition in stability | Gradual, not sharp | Ostrowski |

### 2.3 Nuanced (use with caveats)

| Result | Caveat |
|--------|--------|
| Bimodality on real data | NOT confirmed on California Housing (p=0.575) |
| MI v2 controls | Pre-grok 0.300 vs post-grok 0.518 gap is moderate |
| Gene expression pathway claim | Both TSPAN8 and CEA are cell adhesion; distinction is cancer-biology-specific |
| 68% prevalence | From benchmark datasets; may not generalize to production with decorrelated features |

---

## 3. Paper State

| Paper | File | Pages | Status | Key counts |
|-------|------|-------|--------|------------|
| NeurIPS main | paper/main.tex | 9 | **Submission-ready** | 357/6/0 |
| Supplement | paper/supplement.tex | 81 | **Submission-ready** | 357/6/0 |
| JMLR | paper/main_jmlr.tex | 59 | Ready (after NeurIPS) | 357/6/0 |
| Monograph | paper/main_definitive.tex | 77 | Exhaustive | 357/6/0 |

### 3.1 Distinctive Content Per Paper

**NeurIPS only:** Ranking lottery table + figures, subsample sensitivity figure, gene expression figure, 7-line code snippet, clinical reversal ablation table, model-class universality paragraph

**JMLR only:** SBD (3 instances), conditional SHAP, fairness audit, FIM bridge, query complexity, 11 additional datasets, depth×ρ tables, Spearman algebra, DASH information loss, compressed sensing

**Monograph only:** All of the above + MI circuit multiplicity full paragraph, topological analysis, regulatory mapping, SymPy verification details

---

## 4. Claims Registry

Each claim in the NeurIPS paper with its evidence source:

| Claim | Source type | Source |
|-------|-----------|--------|
| No ranking is F+S+C under Rashomon | PROVED | attribution_impossibility (0 axioms) |
| For binary H, F+S alone impossible | PROVED | bilemma_of_compatible_eq (0 axioms) |
| Design space has exactly two families | PROVED | family_a_or_family_b (5 axioms) |
| DASH is Pareto-optimal | PROVED | dash_unique_pareto_optimal (6 axioms) |
| DASH binary optimality (uniquely optimal) | PROVED (theorem) | Ostrowski session |
| Var[SHAP] = min MSE | PROVED (identity) | 0/800 violations empirical confirmation |
| Attribution ratio = 1/(1-ρ²) | DERIVED | ratio_tendsto_atTop (4 axioms) |
| Bilemma holds at every ε | PROVED | ApproximateBilemma.lean (Ostrowski repo) |
| Quantitative bilemma Δ-δ | PROVED | ApproximateBilemma.lean (Ostrowski repo) |
| Collapsed tightness (harder than fairness) | PROVED | UnifiedMetaTheorem.lean (Ostrowski repo) |
| 24 distinct top-3 on Breast Cancer | EMPIRICAL | ranking_replication_study.py |
| 35 at 100 seeds | EMPIRICAL | ranking_replication_study.py |
| 45% clinical reversal | EMPIRICAL | results_clinical_decision_reversal_v2.json |
| TSPAN8 vs CEA 80/20 | EMPIRICAL | AP_Colon_Kidney experiment |
| Minority fraction Spearman 0.92-0.98 | EMPIRICAL | validate_predictions.py |
| Gaussian formula 0.46 on California | EMPIRICAL | validate_predictions.py |
| Bimodality dip p < 0.002 | TESTED | validate_predictions.py |
| 68% of 77 datasets unstable | EMPIRICAL | prevalence_survey.py |
| NN 87% unstable | EMPIRICAL | paper experiments |
| MI 36% Jaccard | EMPIRICAL | results_mech_interp_definitive_v2.json |
| Model-class universality | EMPIRICAL | model_class_rigorous.py |

---

## 5. Cross-Repo Pointers

| Repo | Path | What it contains |
|------|------|-----------------|
| dash-impossibility-lean | (this repo) | Lean formalization + all papers |
| ostrowski-impossibility | ../ostrowski-impossibility | FoP paper, Arrow proof, ML constructive instances, empirical validation scripts, approximate bilemma, unified meta-theorem |
| universal-explanation-impossibility | ../universal-explanation-impossibility | Nature paper draft, MI v2 results, clinical reversal data, gene expression data, brain imaging experiments |
| dash-shap | ../dash-shap | Python DASH implementation, stability API, model-class comparison scripts |

---

## 6. Publication Plan

| Paper | Venue | Deadline | Status |
|-------|-------|----------|--------|
| Attribution Impossibility | NeurIPS 2026 | Abstract May 4, Paper May 6 | **Submission-ready** |
| Ostrowski Impossibility | Foundations of Physics | No deadline | Submission-ready |
| Universal Impossibility | Nature | ~October 2026 | Draft (needs rewrite) |
| Attribution Impossibility (expanded) | JMLR | After NeurIPS decision | Ready |
| Monograph | arXiv | Anytime | Exhaustive |

Dual submission rules: NeurIPS + Nature never simultaneous. JMLR after NeurIPS decision only. FoP has zero overlap. See docs/publication-plan.md for full analysis.
