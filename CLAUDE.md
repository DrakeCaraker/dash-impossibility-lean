# The Attribution Impossibility — Lean 4 Formalization

Lean 4 formalization of the impossibility theorem for attribution under symmetry. Target venue: NeurIPS 2026 (abstract May 4, paper May 6). Paper 3 in the 5-paper research program housed in [dash-shap](https://github.com/DrakeCaraker/dash-shap). The F5→F1→DASH stability API is in [dash-shap PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255).

## What This Proves

No importance ranking — of input features or internal components — can simultaneously be faithful (reflect the model's attributions), stable (consistent across equivalent models), and complete (rank all pairs) when interchangeable components exist under the Rashomon property. The core theorem requires **zero domain axioms**.

The impossibility operates at two levels: input-level (SHAP on collinear features) and component-level (activation patching on architecturally symmetric heads). The resolution at both levels is the stable projection (orbit averaging): DASH for features, G-invariant projection for circuits. Model-specific instantiations show GBDT has ratio 1/(1-ρ²) → ∞, Lasso has ratio ∞, neural nets have conditional violations, and random forests have bounded O(1/√T) violations.

**Naming conventions:** See `docs/naming-conventions.md`. Canonical terms from the universal framework apply here. Key: "the stable projection" (not "the explanation code"), "explanation uncertainty bound" (not "tradeoff bound" or "uncertainty relation"), "Explanation Capacity Theorem" (not "Capacity Law"), "over-explanation penalty" (not "beyond-capacity penalty").

## Architecture

```
Level 0 (pure logic):     Trilemma.lean — attribution_impossibility + _weak (zero axiom deps)
Level 1 (framework):      Iterative.lean — IterativeOptimizer → Rashomon → impossibility
Level 2 (instantiation):  General.lean (GBDT), Lasso.lean, NeuralNet.lean
Level 3 (quantitative):   SplitGap.lean, Ratio.lean (1/(1-ρ²) divergence)
Level 4 (Spearman):       SpearmanDef.lean (defined from scratch, qualitative bound derived)
Level 5 (resolution):     Corollary.lean (DASH equity), Impossibility.lean (combined)
Level 6 (design space):   DesignSpace.lean + DesignSpaceFull.lean (all 4 steps complete)
Level 7 (derivation):     SymmetryDerive.lean (attribution_sum_symmetric, DERIVED)
Level 8 (generalization):  SymmetricBayes.lean (general SBD theorem)
Level 9 (instances):      ModelSelection.lean, CausalDiscovery.lean, SBDInstances.lean
Level 10 (extensions):    ConditionalImpossibility.lean, FairnessAudit.lean, FlipRate.lean, MechInterp.lean
Level 11 (bounds):        EnsembleBound.lean, Efficiency.lean, AlphaFaithful.lean
Level 12 (universality):  RashomonUniversality.lean, RashomonInevitability.lean, LocalGlobal.lean
Level 13 (abstract):      ExplanationSystem.lean (abstract ExplanationSystem, explanation_impossibility)
Level 14 (bilemma):       Bilemma.lean (bilemma, unfaithfulness bound, all-or-nothing, SHAPSign, FeatureStatus)
Strengthening:            ProportionalityLocal.lean (impossibility from per-model c only)
                          Qualitative.lean (impossibility from 2 axioms: dominance + surjectivity)
                          ApproximateEquity.lean (Rashomon from bounded proportionality)
                          Setup.lean (GBDTSetup structure bundling all axioms)
Contrast:                 RandomForest.lean (bounded violations, no formal proofs)
```

## File Structure

```
DASHImpossibility/
  Defs.lean              — FeatureSpace, 6 axioms, stability/equity defs, consensus, variance from Mathlib
  Trilemma.lean          — RashimonProperty, attribution_impossibility, attribution_impossibility_weak
  Iterative.lean         — IterativeOptimizer abstraction
  General.lean           — GBDT instance, gbdt_impossibility, gbdtOptimizer
  SplitGap.lean          — split_gap_exact, split_gap_ge_half (pure algebra)
  Ratio.lean             — attribution_ratio = 1/(1-ρ²), ratio_tendsto_atTop
  SpearmanDef.lean       — Spearman defined from midranks, qualitative + quantitative bounds
  Lasso.lean             — lasso_impossibility (ratio = ∞)
  NeuralNet.lean         — nn_impossibility (conditional on captured feature)
  RandomForest.lean      — Contrast case (documentation, no formal proofs)
  Impossibility.lean     — Combined: equity violation + stability bound
  Corollary.lean         — DASH consensus equity, variance convergence
  DesignSpace.lean       — Design Space Theorem (composite), DASH ties
  DesignSpaceFull.lean   — Design Space exhaustiveness (Step 3: Family A or B)
  SymmetryDerive.lean    — attribution_sum_symmetric (DERIVED from axioms)
  ModelSelection.lean    — Model selection impossibility (S45-S47)
  ModelSelectionDesignSpace.lean — Model selection design space (S48)
  AlphaFaithful.lean     — α-faithfulness bound (S66-S67)
  UnfaithfulBound.lean   — Unfaithfulness ≥ 1/2, ties optimal (S9-S11)
  PathConvergence.lean   — Relaxation path convergence (S38, S40)
  RashomonUniversality.lean — Rashomon from symmetry via feature swap (S3-S4)
  RashomonInevitability.lean — Impossibility is inescapable (S5-S6)
  ConditionalImpossibility.lean — Conditional SHAP impossibility + escape (S44)
  FlipRate.lean          — Exact GBDT flip rate, binary group = coin flip (S8)
  Efficiency.lean        — SHAP efficiency amplification m/(m-1) (S12-S14)
  LocalGlobal.lean       — Local ≥ global instability (S35)
  SymmetricBayes.lean    — General SBD: orbit bounds, trichotomy, exhaustiveness (S49-S50)
  GaussianFlipRate.lean  — Standard normal CDF Φ, flip rate formula (S31 Gaussian)
  FIMImpossibility.lean  — Gaussian FIM impossibility, Rashomon ellipsoid (S16-S17)
  QueryComplexity.lean   — Query complexity Ω(σ²/Δ²), Le Cam structural (S28)
  CausalDiscovery.lean   — Causal discovery impossibility (S53-S55)
  SBDInstances.lean      — SBD instances + abstract aggregation (S51-S52, S58)
  FairnessAudit.lean     — Fairness audit impossibility (S56)
  MechInterp.lean        — Mechanistic interpretability impossibility bounds
  EnsembleBound.lean     — DASH variance optimality + ensemble size (S22, S26)
  ExplanationSystem.lean — Abstract ExplanationSystem, faithful/stable/decisive, explanation_impossibility
  Bilemma.lean           — Bilemma (F+S impossible for binary H), unfaithfulness bound, all-or-nothing, SHAPSign, FeatureStatus
  Basic.lean             — Import hub
paper/
  main.tex           — NeurIPS 2026 paper (10 pages)
  supplement.tex     — Supplementary (79 pages)
  references.bib     — 49 references
  scripts/           — 51 scripts (figure generation, validation, diagnostics)
  figures/           — PDF figures (ratio, instability, DASH, design space, SNR calibration, conditional threshold, etc.)
```

## Lean State: 58 files, 6 axioms, 357 theorems+lemmas, 0 sorry

## Axiom Inventory (6 total)

| Category | Axioms | Used by |
|----------|--------|---------|
| Type declarations | Model, numTrees, numTrees_pos, attribution, firstMover | Infrastructure (bundled in Setup.lean) |
| Core properties | firstMover_surjective, crossGroupBaselineCore, proportionality_global | GBDT bounds |
| Measure infrastructure | modelMeasurableSpace, modelMeasure | Variance (Mathlib connection) |

**Axiom stratification (verified by `#print axioms`):**
- **Core impossibility** (`attribution_impossibility`): ZERO behavioral axioms (only Model + attribution types)
- **Qualitative impossibility** (`impossibility_qualitative`): ZERO behavioral axioms (dominance + surjectivity as hypotheses)
- **GBDT impossibility** (`gbdt_impossibility_local`): 4 axioms (surj, fm, nfm — NO proportionality_global)
- **Quantitative impossibility** (`impossibility`): 5 axioms (+ proportionality_global for ratio)
- **DASH resolution** (`consensus_equity`): 6 axioms (+ cross-group symmetric)
- **Bundled impossibility** (`attribution_impossibility_bundled`): ZERO axioms (fully parametric via GBDTSetup)

**Formerly axiomatized, now defined/derived:**
- `splitCount` — now a `def` from firstMover, ρ, T, and crossGroupBaselineCore
- `splitCount_firstMover`, `splitCount_nonFirstMover` — derived from splitCount def
- `splitCount_crossGroup_symmetric` — derived from splitCount def (same crossGroupBaselineCore for same-group features)
- `splitCount_crossGroup_stable` — derived from crossGroupBaseline_stable (crossGroupBaselineCore depends only on group indices)
- `testing_constant` — now `def testing_constant := 1/8` (Le Cam's value from Tsybakov 2009)
- `testing_constant_pos` — derived by `norm_num`
- `spearman_classical_bound` → `spearman_instability_bound` in SpearmanDef.lean
- `le_cam_lower_bound` — theorem in QueryComplexity.lean (provable by `not_lt.mp`)
- `consensus_variance_bound` — theorem in Defs.lean (from attribution_variance_nonneg + Nat.cast_nonneg)
- `attribution_sum_symmetric` — theorem in SymmetryDerive.lean (from proportionality + split-count + cross-group + balance)
- `attribution_variance` — noncomputable def from ProbabilityTheory.variance (Mathlib)
- `attribution_variance_nonneg` — theorem from Mathlib's variance_nonneg
- `attribution_proportional` — backward-compatible theorem wrapper from proportionality_global

The core impossibility theorem (Levels 0-1) uses **none** of these — only the Rashomon property as hypothesis.

## Building

```bash
make help          # show all targets
make lean          # compile Lean (~5 min)
make paper         # compile all paper versions
make verify        # build + count consistency check
make validate      # run 3 key experiments (~5 min)
make setup         # full setup for new contributors
```

## Submission

- **NeurIPS 2026** (primary): `paper/main.tex` (10 pages) + `paper/supplement.tex` (81 pages). Abstract May 4, Paper May 6. Official `neurips_2026.sty`.
- **JMLR** (after NeurIPS decision): `paper/main_jmlr.tex` (59 pages, `jmlr.cls` from TeX Live).
- **Monograph** (source of truth): `paper/main_definitive.tex` (82 pages). arXiv tarball: `paper/arxiv_monograph.tar.gz`.
- **arXiv**: Run `paper/scripts/prepare_arxiv.sh` to uncomment authors and fill URLs.
- Title: "The Attribution Impossibility: No Importance Ranking Is Faithful, Stable, and Complete Under Symmetry"
- Authors: Drake Caraker, Bryan Arnold, David Rhoads
- Companion code: [dash-shap PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255)

## Output Preferences

- When asked to run commands or show output, display the raw output directly. Do not summarize or post-process command output unless explicitly asked to summarize.
- When editing shell scripts or running shell commands, account for macOS/zsh compatibility. Avoid bash-specific syntax. Escape `!` properly in strings.

## Do NOT

- Summarize, filter, or curate lists of findings. Present ALL items in prioritized order. For audits, assessments, and analysis tasks, default to thorough and detailed. Only go brief when the user explicitly asks for a summary.
- Skip or defer items in an execution plan. Execute everything identified. If an item is genuinely blocked, flag it as blocked with a specific unblocking condition — don't silently skip it.
- Commit paper changes without verifying paper-code consistency. Run this verification block and confirm all numbers match the paper text before committing:
  ```bash
  grep -c "^theorem\|^lemma" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "theorems+lemmas:", s}'
  grep -c "^axiom" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "axioms:", s}'
  grep -rc "sorry" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "sorry:", s}'
  ls DASHImpossibility/*.lean | wc -l | awk '{print "files:", $1}'
  ```
- Push reverts or force-pushes without explicit approval. Confirm intent before any destructive git operation.
- Use `sorry` without a `-- TODO:` comment explaining what's needed
- Change axioms without re-running the SymPy verification (in companion repo: `dash-shap/paper/proofs/verify_lemma6_algebra.py`)
- Add `autoImplicit true` — all variables must be explicit
- Claim "N theorems" without verifying — count with `grep -c "^theorem\|^lemma" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print s}'` (currently 357)
- Run parallel subagents that both modify the same file (causes build cache corruption)
- Axiomatize quantities that can be defined — prefer definitions with axiomatized bounds (see SpearmanDef.lean pattern)
- Claim empirical results as "proved" or "Lean-verified" — distinguish: **proved** (zero axiom deps), **derived** (from axioms), **argued** (supplement proof only), **empirical** (experiments). The paper's "Proof status transparency" paragraph is the reference.

## Complete Inventory of Proofs, Experiments, and Results

> **Full reference with explanations, methodology, and provenance:** See [`docs/complete-reference.md`](docs/complete-reference.md). The tables below are a quick-lookup index; the reference doc explains WHY each result matters, HOW it was validated, and WHAT it depends on.

### Lean Formalization (58 files, 357 theorems, 6 axioms, 0 sorry)

#### Core Impossibility (Level 0 — zero domain axioms)
| Theorem | File | What it proves |
|---------|------|---------------|
| `explanation_impossibility` | ExplanationSystem.lean | Abstract trilemma: F+S+D → ⊥ under Rashomon. ZERO axioms of any kind. |
| `attribution_impossibility` | Trilemma.lean | Feature ranking trilemma (4-line proof). Depends only on Model type. |
| `attribution_impossibility_weak` | Trilemma.lean | Implication-only faithfulness version (weaker assumption). |
| `bilemma_of_compatible_eq` | Bilemma.lean | Binary H: F+S → ⊥ without completeness. Zero axioms. |
| `rashomon_unfaithfulness` | Bilemma.lean | ≥1 unfaithful per Rashomon pair. |
| `all_or_nothing` | Bilemma.lean | No approximate faithfulness for binary H. |
| `tightness_dichotomy` | BeyondBinary.lean | Neutral element ↔ F+S achievable. |
| `shap_sign_bilemma` | Bilemma.lean | SHAPSign constructive instance (zero axioms). |
| `feature_selection_bilemma` | Bilemma.lean | FeatureStatus constructive instance. |
| `counterfactual_bilemma` | Bilemma.lean | CounterfactualDir constructive instance. |
| `mech_interp_bilemma` | MechInterp.lean | Circuit decomposition impossibility (derived Rashomon, zero custom axioms). |
| `impossibility_qualitative` | Qualitative.lean | Impossibility from just dominance + surjectivity (2 axioms as hypotheses). |
| `attribution_impossibility_bundled` | Setup.lean | Fully parametric via GBDTSetup (zero global axioms). |

#### Model-Specific Bounds (Levels 2-3 — 3-5 axioms)
| Theorem | File | What it proves |
|---------|------|---------------|
| `gbdt_impossibility_local` | ProportionalityLocal.lean | GBDT impossibility without proportionality_global (3 axioms). |
| `split_gap_exact` | SplitGap.lean | Exact split gap = ρ²T/(2-ρ²) (pure algebra). |
| `ratio_tendsto_atTop` | Ratio.lean | Attribution ratio 1/(1-ρ²) → ∞ as ρ → 1. |
| `lasso_impossibility` | Lasso.lean | Lasso ratio = ∞ at any ρ > 0. |
| `nn_impossibility` | NeuralNet.lean | NN impossibility conditional on captured feature. |
| `binary_group_flip_rate` | FlipRate.lean | Binary group flip rate = exactly 1/2. |

#### Additional Key Results
| Theorem | File | What it proves |
|---------|------|---------------|
| `attribution_prob_half` | UnfaithfulQuantitative.lean | Unfaithfulness probability = exactly 1/2 under DGP symmetry. |
| `attribution_sum_symmetric` | SymmetryDerive.lean | DASH equity derivation (35-line proof from axioms). |
| `conditional_escape` | ConditionalImpossibility.lean | Conditional SHAP DOES escape when Δβ is large enough. |
| `ensemble_bound_formula` | EnsembleBound.lean | M_min = ⌈2.71σ²/Δ²⌉ for 5% flip rate. |
| `mech_interp_impossibility` | MechInterp.lean | Circuit trilemma (F+S+D) for neural network components. |

#### Resolution + Optimality (Levels 5-6 — 5-6 axioms)
| Theorem | File | What it proves |
|---------|------|---------------|
| `consensus_equity` | Corollary.lean | DASH produces equal attributions for symmetric features. |
| `design_space_theorem` | DesignSpace.lean | Design space has exactly two families. |
| `family_a_or_family_b` | DesignSpaceFull.lean | Exhaustiveness: no third family among deterministic methods. |
| `sum_squares_ge_inv_M` | EnsembleBound.lean | Cauchy-Schwarz / Titu's lemma variance bound. |
| `dash_unique_pareto_optimal` | ParetoOptimality.lean | DASH Pareto-dominates all other stable methods. |
| `tie_dominates_commitment` | BayesOptimalTie.lean | Bayes-optimal ties for symmetric features. |
| `relaxation_paths_converge` | PathConvergence.lean | Both relaxation paths converge to DASH. |

#### Generalizations (Levels 8-12)
| Theorem | File | What it proves |
|---------|------|---------------|
| `symmetric_bayes_dichotomy` | SymmetricBayes.lean | General SBD: any symmetric decision → two families. |
| `rashomon_from_symmetry` | RashomonUniversality.lean | Permutation closure → Rashomon. |
| `rashomon_inevitability` | RashomonInevitability.lean | Stochastic symmetric training → Rashomon. |
| `local_attribution_impossibility` | LocalGlobal.lean | Local instability ≥ global instability. |
| `conditional_attribution_impossibility` | ConditionalImpossibility.lean | Conditional SHAP impossibility when β_j = β_k. |
| `fairness_audit_impossibility` | FairnessAudit.lean | SHAP proxy audit = coin flip. |
| `intersectional_audit_impossibility` | IntersectionalFairness.lean | K-attribute audit: (1/2)^K. |
| `gaussian_fim_impossibility` | FIMImpossibility.lean | FIM → Rashomon ellipsoid. |
| `model_selection_impossibility` | ModelSelection.lean | Cannot select among equivalent models. |
| `causal_discovery_impossibility` | CausalDiscovery.lean | Cannot orient edges in Markov equivalence. |
| `mi_is_exact_boundary` | MutualInformation.lean | MI > 0 ↔ Rashomon (exact boundary). |

#### Cross-Repo (universal-explanation-impossibility)
| Theorem | File | What it proves |
|---------|------|---------------|
| `reynolds_best_approximation` | UncertaintyFromSymmetry.lean | Orbit average = closest stable approximation (L² optimality). |
| `mi_quantitative_unfaithfulness` | MIQuantitativeBridge.lean | MI > 0 → any stable explanation has error ≥ Δ/2. |
| `mi_implies_positive_gap` | MIQuantitativeBridge.lean | MI > 0 → Rashomon witnesses have opposite orderings. |

### Empirical Results (53 scripts, 35 JSON result files, 14 figures)

#### Input-Level Attribution
| Experiment | Key Finding | Script | Result |
|-----------|-------------|--------|--------|
| Ranking lottery (Breast Cancer) | 24 distinct top-3 from 50 seeds (4.2% agreement) | ranking_replication_study.py | VALIDATED |
| Cross-implementation lottery | XGB 24, LGB 29, RF 40 distinct rankings | ranking_replication_study.py | VALIDATED |
| Subsample sensitivity | 17 distinct at subsample=0.95, 1 at 1.0 | ranking_replication_study.py | VALIDATED |
| Explanation reversal (German Credit) | 45% XGB, 46% LGB, 35% RF | financial_case_study.py | VALIDATED |
| Gene expression (TSPAN8 vs CEA) | 80/20 alternation, ρ=0.858 | inline | VALIDATED |
| Prevalence survey | 68% of 77 datasets (>10% flip rate) | prevalence_survey.py | VALIDATED |
| Coverage conflict diagnostic | Spearman 0.59-0.98, 4 model classes | comprehensive_validation.py | VALIDATED |
| Minority fraction vs Gaussian | 0.96 vs 0.46 on California Housing | comprehensive_validation.py | VALIDATED |
| Variance = min MSE | 0/800 violations at machine precision | (ostrowski repo) | VALIDATED |
| Bimodality (dip test) | p < 0.002 for ρ ≥ 0.5, control p=0.373 | comprehensive_validation.py | VALIDATED |
| Model-class universality | XGB/RF/Ridge/LASSO all show instability | (dash-shap repo) | VALIDATED |
| NN attribution instability | 87% unstable pairs, 8:1 model vs SHAP noise | nn_shap_validation.py | VALIDATED |
| SNR calibration | Φ(-SNR) R²=0.94 across 1,325 pairs | snr_calibration.py | VALIDATED |
| Drug discovery (BBBP) | Pearson: 0%, MI: 19.4%, actual: 23.1% | (universal repo) | VALIDATED |

#### Component-Level Attribution
| Experiment | Key Finding | Source | Result |
|-----------|-------------|--------|--------|
| TinyStories Config A (4L/4H) | ρ=0.565→0.972, W-flip=0.496, d=5.4, 7/7 PASS | docs/tinystories-results-reference.json | VALIDATED |
| TinyStories Config B (6L/8H) | ρ=0.540→0.982, W-flip=0.489, d=11.9, 7/7 PASS | docs/tinystories-results-reference.json | VALIDATED |
| GPT-2 boundary condition | ρ=0.993, W-flip=0.043, 4/7 PASS (expected) | docs/tinystories-results-reference.json | VALIDATED |
| Mean ablation robustness | G-inv ρ≈0.97-0.99; cross-method ρ≈0.5-0.6 | docs/mean-ablation-results-reference.json | VALIDATED |
| Full S₄ realization (Config A) | All 4 L0 heads appear as #1 across 10 seeds | docs/tinystories-results-reference.json | VALIDATED |
| Split-half reliability | 0.991 (A), 0.960 (B) >> between-model 0.565, 0.540 | docs/tinystories-results-reference.json | VALIDATED |
| Random projection control | G-inv at 100th percentile, perm p<0.001 | docs/tinystories-results-reference.json | VALIDATED |

#### Running Experiments (SageMaker ml.g5.12xlarge)
| Experiment | Status | Script | Expected |
|-----------|--------|--------|----------|
| GPT-2-small from scratch (10 seeds) | IN PROGRESS (SageMaker ml.g5.12xlarge, 4x A10G) | experiments/gpt2_train.py | 7/7 predictions PASS |
| GPT-2 activation patching | QUEUED (after training) | experiments/gpt2_evaluate.py | rho < 0.70 raw, > 0.80 G-inv |
| IOI circuit analysis (10 seeds) | QUEUED (after patching) | experiments/ioi_analysis.py | Within-layer flip ≈ 0.50 |
| SAE stability (10 SAEs) | QUEUED (after patching) | experiments/sae_experiment.py | Feature cosine > 0.80 (escape hatch?) |

### Paper Versions
| Paper | File | Pages | Status |
|-------|------|-------|--------|
| NeurIPS 2026 | paper/main.tex | 9+refs+checklist | SUBMISSION-READY (needs 1-page cut) |
| NeurIPS supplement | paper/supplement.tex | 81 | READY |
| Monograph | paper/main_definitive.tex | 83 | EXHAUSTIVE |
| JMLR | paper/main_jmlr.tex | 59 | READY (after NeurIPS) |
| arXiv preprint | paper/main_preprint.tex | 10 | READY |
| OpenReview abstract | paper/abstract_openreview.txt | 200 words | READY |

### Key Numbers (all verified against source)
| Claim | Value | Source |
|-------|-------|--------|
| Lean theorems+lemmas | 357 | grep verification |
| Lean axioms | 6 | grep verification |
| Lean sorry | 0 | grep verification |
| Lean files | 58 | ls count |
| Prevalence | 68% of 77 datasets | prevalence_survey.py |
| Ranking lottery | 24 distinct top-3 (50 seeds, Breast Cancer) | ranking_replication_study.py |
| Explanation reversal | 45% (German Credit, XGB, subsample=0.8) | financial_case_study.py |
| TinyStories A full ρ | 0.565 [0.527, 0.603] | tinystories-results-reference.json |
| TinyStories A G-inv ρ | 0.972 [0.966, 0.979] | tinystories-results-reference.json |
| TinyStories B full ρ | 0.540 [0.516, 0.565] | tinystories-results-reference.json |
| TinyStories B G-inv ρ | 0.982 [0.977, 0.986] | tinystories-results-reference.json |
| GPT-2 ft ρ | 0.993 | tinystories-results-reference.json |
| Within-layer flip A | 0.496 [0.467, 0.526] | tinystories-results-reference.json |
| Within-layer flip B | 0.489 [0.478, 0.500] | tinystories-results-reference.json |
| Cohen's d A / B | 5.4 / 11.9 | tinystories-results-reference.json |
| Drug discovery (BBBP) | Pearson 0%, MI 19.4%, actual 23.1% | handoff-mi-bridge-session.md |
| MI permutation threshold | τ₉₅ = 0.027 (BBBP) | handoff-mi-bridge-session.md |

### Diagnostic Tools
| Tool | Lines | Performance | Script |
|------|-------|-------------|--------|
| Minority fraction (coverage conflict) | 7 | Spearman 0.92-0.98 vs flip rate | paper/main.tex (verbatim block) |
| Single-model screen | ~20 | 94% precision (tree-based) | f1_f5_validation.py |
| Z-test (multi-model) | ~10 | r = -0.89 on Breast Cancer | f1_f5_validation.py |
| G-invariant projection (V^G) | ~5 | 100th percentile vs random | experiments/gpt2_evaluate.py |
| MI screening | ~15 | Catches 67-93% hidden dependencies | (universal repo) |

### Cross-Repo Dependencies
| Repo | What it provides | Used by |
|------|-----------------|---------|
| dash-shap (PR #255) | DASH implementation, stability API, model-class comparison | Referenced in paper |
| universal-explanation-impossibility | reynolds_best_approximation, MI bridge theorems, TinyStories data | Lean theorems cited in paper |
| ostrowski-impossibility | Fairness tightness experiment, approximate bilemma (ostrowski version) | Referenced in supplement |
