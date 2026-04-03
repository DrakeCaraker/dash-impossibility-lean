# The Attribution Impossibility

**No feature ranking can be simultaneously faithful, stable, and complete when features are correlated -- and we prove it in Lean 4.**

![Theorems](https://img.shields.io/badge/theorems-188-blue)
![Axioms](https://img.shields.io/badge/axioms-18-orange)
![Sorry](https://img.shields.io/badge/sorry-0-brightgreen)
![Lean 4](https://img.shields.io/badge/Lean-4-purple)
![Files](https://img.shields.io/badge/Lean_files-36-informational)

<!-- Verify badges with:
  grep -c '^theorem\|^lemma' DASHImpossibility/*.lean | awk -F: '{s+=$2}END{print s}'  # 188
  grep -c '^axiom' DASHImpossibility/*.lean | awk -F: '{s+=$2}END{print s}'              # 18
  grep -rn 'sorry' DASHImpossibility/*.lean                                               # (empty)
  ls DASHImpossibility/*.lean | wc -l                                                     # 36
-->

If you have ever retrained an XGBoost model and noticed the "most important feature" changed, this paper proves that is not a bug -- it is a mathematical inevitability. When features are correlated, no attribution method can simultaneously tell you what the model computed (faithfulness), give you the same answer across retrains (stability), and decide every pair of features (completeness). You must pick two of three. We prove it, quantify it, characterize the entire design space of solutions, and give you a toolkit to handle it. The core impossibility theorem is machine-checked in Lean 4 with zero domain-specific axiom dependencies. The resolution -- DASH (Diversified Aggregation of SHAP) -- is proved to be the minimum-variance unbiased estimator via Cramer-Rao.

---

# Part 1: Repository Guide

## Quick Start

```bash
git clone https://github.com/DrakeCaraker/dash-impossibility-lean.git
cd dash-impossibility-lean

# Install Lean 4 via elan if needed
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Verify the formalization (188 theorems, 0 sorry)
lake build                    # ~5 min cached, ~20 min first build

# Verify axiom consistency (expect 15/15 PASS)
python3 paper/scripts/axiom_consistency_model.py

# Run key experiment (expect F1 r=-0.89)
pip install xgboost lightgbm catboost shap scikit-learn numpy pandas
python3 paper/scripts/f1_f5_validation.py
```

## Who Is This For?

**Data scientist using SHAP.** Your feature rankings for correlated features are unreliable. The instability is not noise or a software bug -- it is a provable consequence of how gradient boosting interacts with collinearity. The fix is DASH: average SHAP values from multiple independently trained models. See the [dash-shap](https://github.com/DrakeCaraker/dash-shap) companion package and the [stability API in PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255) for the F5 (single-model screen) to F1 (multi-model validation) to DASH (ensemble consensus) workflow.

**Researcher in XAI or ML theory.** This is a formally verified impossibility theorem with 188 Lean proofs and 0 sorry. The Symmetric Bayes Dichotomy (Section 6 of the definitive paper) is a general proof technique from invariant decision theory that applies to any symmetric decision problem -- we demonstrate it on feature attribution, model selection, and causal discovery under Markov equivalence. The Design Space Theorem characterizes the full achievable set.

**Regulator or model risk officer.** Single-model SHAP explanations are provably unreliable under collinearity. In a survey of 37 public datasets, approximately 60% exhibit attribution instability. This affects EU AI Act Art. 13(3)(b)(ii) requirements for disclosing "known and foreseeable circumstances" affecting accuracy, and SR 11-7 model risk management compliance. The paper provides disclosure templates and a diagnostic workflow.

**Lean or Mathlib community.** 188 theorems across 36 files, 13 abstraction levels, using `MulAction` for orbit bounds, `ProbabilityTheory.cdf` for the Gaussian flip rate, and `Analysis.Calculus` for the FIM impossibility. The Gaussian CDF symmetry proofs (phi(0)=1/2, phi(-x)=1-phi(x)) via `NoAtoms` + `prob_compl_eq_one_sub` may be of independent interest. The axiom consistency proof constructs a `Fin 4` model satisfying all 18 axioms.

## Repository Map

```
dash-impossibility-lean/
│
├── DASHImpossibility/                    # 36 Lean 4 files, 188 theorems, 18 axioms, 0 sorry
│   │
│   │  ── Level 0: Pure Logic ──
│   ├── Trilemma.lean                     # attribution_impossibility (zero axiom deps, 4-line proof)
│   │
│   │  ── Level 1: Framework ──
│   ├── Iterative.lean                    # IterativeOptimizer connects to Rashomon property
│   │
│   │  ── Level 2: Model Instantiation ──
│   ├── General.lean                      # GBDT instance, gbdt_impossibility, gbdtOptimizer
│   ├── Lasso.lean                        # lasso_impossibility (ratio = infinity)
│   ├── NeuralNet.lean                    # nn_impossibility (conditional on captured feature)
│   │
│   │  ── Level 3: Quantitative Bounds ──
│   ├── SplitGap.lean                     # split_gap_exact, split_gap_ge_half (pure algebra)
│   ├── Ratio.lean                        # attribution_ratio = 1/(1-rho^2), ratio_tendsto_atTop
│   │
│   │  ── Level 4: Spearman ──
│   ├── SpearmanDef.lean                  # Spearman from midranks, qualitative + quantitative bounds
│   │
│   │  ── Level 5: Resolution ──
│   ├── Corollary.lean                    # DASH consensus equity, variance convergence
│   ├── Impossibility.lean                # Combined: equity violation + stability bound
│   │
│   │  ── Level 6: Design Space ──
│   ├── DesignSpace.lean                  # design_space_theorem, DASH ties, Pareto structure
│   ├── DesignSpaceFull.lean              # family_a_or_family_b (exhaustiveness)
│   │
│   │  ── Level 7: Derivation ──
│   ├── SymmetryDerive.lean               # attribution_sum_symmetric (DERIVED from axioms)
│   │
│   │  ── Level 8: Generalization ──
│   ├── SymmetricBayes.lean               # General SBD: orbit bounds, trichotomy, exhaustiveness
│   │
│   │  ── Level 9: SBD Instances ──
│   ├── ModelSelection.lean               # Model selection impossibility
│   ├── ModelSelectionDesignSpace.lean     # Model selection design space
│   ├── CausalDiscovery.lean              # Causal discovery impossibility (Markov equivalence)
│   ├── SBDInstances.lean                 # SBD instances + abstract aggregation
│   │
│   │  ── Level 10: Extensions ──
│   ├── ConditionalImpossibility.lean     # Conditional SHAP impossibility + escape condition
│   ├── FairnessAudit.lean                # Fairness audit impossibility (coin-flip audits)
│   ├── FlipRate.lean                     # Exact GBDT flip rate, binary group = coin flip
│   │
│   │  ── Level 11: Bounds ──
│   ├── EnsembleBound.lean                # DASH variance optimality + ensemble size (Titu's lemma)
│   ├── Efficiency.lean                   # SHAP efficiency amplification m/(m-1)
│   ├── AlphaFaithful.lean                # alpha-faithfulness bound
│   ├── UnfaithfulBound.lean              # Unfaithfulness >= 1/2, ties optimal
│   ├── PathConvergence.lean              # Relaxation path convergence
│   ├── QueryComplexity.lean              # Query complexity Omega(sigma^2/Delta^2), Le Cam
│   │
│   │  ── Level 12: Universality ──
│   ├── RashomonUniversality.lean         # Rashomon from symmetry via feature swap
│   ├── RashomonInevitability.lean        # Impossibility is inescapable for standard ML
│   ├── LocalGlobal.lean                  # Local instability >= global instability
│   │
│   │  ── Infrastructure ──
│   ├── Defs.lean                         # FeatureSpace, 18 axioms, stability/equity defs, Mathlib
│   ├── Consistency.lean                  # Axiom system consistency (Fin 4 construction)
│   ├── GaussianFlipRate.lean             # Standard normal CDF, flip rate formula
│   ├── FIMImpossibility.lean             # Gaussian FIM impossibility, Rashomon ellipsoid
│   ├── RandomForest.lean                 # Contrast case (documentation, no formal proofs)
│   └── Basic.lean                        # Import hub (all 36 files)
│
├── paper/
│   ├── main_definitive.tex               # 59-page definitive version (all content)
│   ├── main_jmlr.tex                     # 42-page JMLR submission
│   ├── main.tex                          # 10-page NeurIPS version
│   ├── supplement.tex                    # 77-page NeurIPS supplement
│   ├── references.bib                    # 44 references
│   ├── scripts/                          # 33 scripts (experiments, figures, validation)
│   │   ├── axiom_consistency_model.py    # Constructs Fin 4 model, 15/15 axioms PASS
│   │   ├── f1_f5_validation.py           # F1 multi-model + F5 single-model diagnostics
│   │   ├── kernelshap_noise_control.py   # Noise 11% vs model instability 87%
│   │   ├── high_dimensional_validation.py # P=500 scalability (2.5 min)
│   │   ├── snr_calibration.py            # SNR predicts flip rate (R^2=0.94 for SNR>=0.5)
│   │   ├── cross_implementation_validation.py # XGBoost/LightGBM/CatBoost comparison
│   │   ├── nn_shap_validation.py         # Neural network SHAP instability (87%)
│   │   ├── permutation_importance_validation.py # Permutation importance (91% unstable)
│   │   ├── financial_case_study.py       # German Credit, Taiwan CC
│   │   ├── lending_club_case_study.py    # Lending Club analysis
│   │   ├── llm_attention_instability.py  # LLM attention (14.5% under fine-tuning)
│   │   ├── conditional_shap_causal.py    # Conditional SHAP Delta-beta sweep
│   │   ├── conditional_shap_threshold.py # Conditional escape threshold
│   │   ├── bootstrap_stochasticity.py    # Bootstrap stochasticity analysis
│   │   ├── prevalence_survey.py          # 37-dataset prevalence (60% unstable)
│   │   ├── dash_example.py               # DASH demonstration
│   │   ├── design_space_figure.py        # Design space visualization
│   │   ├── generate_figures.py           # All figure generation
│   │   ├── validate_ratio.py             # 1/(1-rho^2) ratio validation
│   │   ├── proportionality_validation.py # Proportionality axiom (CV=0.66)
│   │   ├── alpha_precision_validation.py # Alpha-faithfulness precision
│   │   ├── comprehensive_validation.py   # Full validation suite
│   │   ├── real_world_validation.py      # 11-dataset validation
│   │   ├── information_loss.py           # DASH information loss analysis
│   │   ├── healthcare_prevalence.py      # Healthcare dataset prevalence
│   │   ├── kendall_tau_prediction.py     # Kendall tau prediction
│   │   ├── lending_club_validation.py    # Lending Club validation
│   │   ├── llm_finetuning_3epoch.py      # LLM 3-epoch fine-tuning
│   │   ├── llm_finetuning_instability.py # LLM fine-tuning instability
│   │   ├── prevalence_robustness.py      # Prevalence robustness checks
│   │   ├── snr_restricted_r2.py          # SNR restricted R^2 analysis
│   │   ├── subsample_check.py            # Subsample analysis
│   │   └── prepare_arxiv.sh              # Uncomment authors, fill URLs for arXiv
│   └── figures/                          # PDF figures (ratio, instability, DASH, etc.)
│
├── docs/
│   ├── co-author-guide.md                # Plain English onboarding for collaborators
│   ├── verification-audit.md             # 32-item ranked human verification checklist
│   ├── self-verification-report.md       # Machine-verified #print axioms results
│   ├── realistic-reception-assessment.md # Honest impact and reception assessment
│   ├── legendary-assessment.md           # Venue optimization analysis
│   ├── dash-shap-audit.md               # Companion package audit
│   ├── neurips-improvement-plan.md       # Improvement roadmap
│   ├── full-formalization-plan.md        # Lean formalization roadmap
│   ├── co-author-email-draft.md          # Ready-to-send co-author email
│   ├── impact-assessment.md              # Field contextualization
│   └── jmlr-variance-derivation-plan.md  # Future Lean work plan
│
├── lakefile.toml                         # Lean build configuration (Mathlib dependency)
├── lean-toolchain                        # Lean version pin
├── CLAUDE.md                             # AI development instructions and conventions
└── README.md                             # This file
```

## Paper Versions

| Version | File | Pages | Audience | When to Read |
|---------|------|-------|----------|--------------|
| **Definitive** | `paper/main_definitive.tex` | 59 | Reference for all results | Complete record; read when you need any specific proof or detail |
| **JMLR** | `paper/main_jmlr.tex` | 42 | Journal reviewers | Self-contained submission; primary target |
| **NeurIPS** | `paper/main.tex` | 10 | Conference reviewers | Compressed version; backup target (abstract May 4, paper May 6) |
| **Supplement** | `paper/supplement.tex` | 77 | Complements NeurIPS main | Extended proofs, experiments, architecture; read with main.tex |

The edit flow: the definitive version contains everything. The JMLR version is trimmed from the definitive for journal submission. The NeurIPS version is further compressed to 10 pages, with remaining content in the supplement.

## Documentation Index

| Document | What It Contains |
|----------|------------------|
| [docs/co-author-guide.md](docs/co-author-guide.md) | Plain English onboarding: 60-second summary, reading order, verification checklist, timeline |
| [docs/verification-audit.md](docs/verification-audit.md) | 32-item ranked checklist for human verification before submission |
| [docs/self-verification-report.md](docs/self-verification-report.md) | Machine-verified `#print axioms` results for every theorem |
| [docs/realistic-reception-assessment.md](docs/realistic-reception-assessment.md) | Honest assessment: 10 realistic readers, citation trajectory, importance analysis |
| [docs/legendary-assessment.md](docs/legendary-assessment.md) | Venue optimization: NeurIPS vs JMLR vs ICML positioning |
| [docs/dash-shap-audit.md](docs/dash-shap-audit.md) | Audit of the companion Python package |
| [docs/neurips-improvement-plan.md](docs/neurips-improvement-plan.md) | Prioritized improvement roadmap |
| [docs/full-formalization-plan.md](docs/full-formalization-plan.md) | Plan for extending the Lean formalization |
| [docs/co-author-email-draft.md](docs/co-author-email-draft.md) | Ready-to-send onboarding email for co-authors |
| [docs/impact-assessment.md](docs/impact-assessment.md) | Field contextualization and impact analysis |
| [docs/jmlr-variance-derivation-plan.md](docs/jmlr-variance-derivation-plan.md) | Plan for deriving variance bounds in Lean for JMLR version |

---

# Part 2: What We Proved

## 1. The Problem

SHAP feature rankings flip when you retrain a model. For collinear features with similar importance, the ranking is literally a coin flip -- 50% of the time, the "most important" feature changes. In a survey of 37 public datasets, approximately 60% exhibit this instability. This is not a software bug, not a tuning problem, and not specific to any one SHAP implementation. It is a mathematical inevitability that applies to XGBoost, LightGBM, CatBoost, Lasso, neural networks, and permutation importance alike.

The root cause is the **Rashomon property**: when features are correlated, multiple near-optimal models exist that rank them in opposite orders. Every model class with collinear features admits these equally-good-but-differently-explained solutions. The question is not whether to fix it, but what tradeoff to accept.

## 2. The Impossibility (Theorem 1)

No feature ranking can be simultaneously faithful (reflect what the model computed), stable (robust to retraining), and complete (decide every pair of features). **Faithful, Stable, Complete: Pick Two.**

```
                       The Attribution Trilemma

       Faithful ────────── IMPOSSIBLE ────────── Stable
           │                    X                    │
           │              (Theorem 1)                │
           │                                         │
       Family A                                 Family B
       (single model)                           (DASH ensemble)
       + Faithful, Complete                     + Faithful, Stable
       - Unstable (50% flips)                   - Within-group ties
```

- **Lean:** `attribution_impossibility` in [`Trilemma.lean`](DASHImpossibility/Trilemma.lean)
- **Axiom dependencies:** Zero. The proof uses only the Rashomon property as a hypothesis.
- **Proof:** A 4-line contradiction. If a ranking is faithful, it must agree with each model. But collinear features admit models ranking them in opposite orders (Rashomon). So the ranking cannot agree with both, violating stability. If stable, it cannot be faithful to all models. Completeness forces the choice.

This is the paper's center of gravity. Everything else quantifies, extends, or resolves this result.

## 3. How Bad Is It? (Quantitative Bounds)

The impossibility is not a mild nuisance. The attribution ratio -- how much the dominant feature is overweighted relative to the true contribution -- diverges or explodes depending on the model class:

| Model Class | Ratio | Behavior | Lean File |
|-------------|-------|----------|-----------|
| **GBDT** | 1/(1-rho^2) | Diverges to infinity as rho approaches 1 | `Ratio.lean`, `SplitGap.lean` |
| **Lasso** | Infinity | One feature gets everything, the other gets zero | `Lasso.lean` |
| **Neural networks** | Conditional | Depends on which feature the network "captures" | `NeuralNet.lean` |
| **Random forests** | O(1/sqrt(T)) | Converges (bounded violations) -- the contrast case | `RandomForest.lean` |

Key theorems:
- `ratio_tendsto_atTop` in [`Ratio.lean`](DASHImpossibility/Ratio.lean) -- the attribution ratio tends to infinity as correlation approaches 1
- `split_gap_exact` in [`SplitGap.lean`](DASHImpossibility/SplitGap.lean) -- the exact split gap formula (pure algebra)
- `lasso_impossibility` in [`Lasso.lean`](DASHImpossibility/Lasso.lean) -- Lasso attribution ratio is infinite
- `nn_impossibility` in [`NeuralNet.lean`](DASHImpossibility/NeuralNet.lean) -- neural net impossibility conditional on captured feature

The GBDT ratio 1/(1-rho^2) means that at rho=0.9, the dominant feature gets approximately 5.3x its fair share. At rho=0.99, it gets approximately 50x. The flip rate for binary collinear groups is exactly 1/2 -- a literal coin flip (`flip_rate_binary_coin_flip` in [`FlipRate.lean`](DASHImpossibility/FlipRate.lean)).

## 4. The Fix: DASH

**DASH** (**D**iversified **A**ggregation of **SH**AP): average |SHAP| values across M independently trained models. This is not just "try averaging" -- it is provably the minimum-variance unbiased estimator via the Cramer-Rao bound.

- `consensus_equity` in [`Corollary.lean`](DASHImpossibility/Corollary.lean) -- DASH achieves equity (zero unfaithfulness) for collinear feature pairs in balanced ensembles
- `sum_squares_ge_inv_M` in [`EnsembleBound.lean`](DASHImpossibility/EnsembleBound.lean) -- Cramer-Rao optimality via Titu's lemma (the sum of squares of weights is minimized by equal weights)
- Variance decreases as 1/M, with tight ensemble size formula: **M_min = ceil(2.71 * sigma^2 / Delta^2)**

DASH is Pareto-optimal: no attribution method achieves better stability without sacrificing more faithfulness. The proof is in [`DesignSpace.lean`](DASHImpossibility/DesignSpace.lean). The tradeoff: DASH produces ties for within-group features (it cannot distinguish features that are genuinely interchangeable), but ranks between-group features faithfully and stably.

## 5. The Complete Map (Design Space Theorem)

The achievable set of attribution methods under collinearity has exactly two families -- and nothing else:

```
                    The Attribution Design Space

    ┌──────────────────────────────────────────────────────┐
    │                                                      │
    │   Family A (single-model methods)                    │
    │   + Faithful + Complete                              │
    │   - Unstable: 50% flip rate for within-group pairs   │
    │   Examples: TreeSHAP, KernelSHAP, permutation imp.  │
    │                                                      │
    ├──────────────────────────────────────────────────────┤
    │                                                      │
    │   Family B (DASH ensemble methods)                   │
    │   + Faithful + Stable (variance -> 0 as M -> inf)    │
    │   - Incomplete: within-group ties                    │
    │   Example: DASH with M >= M_min models               │
    │                                                      │
    └──────────────────────────────────────────────────────┘

    No third family exists. Every attribution method falls into A or B.
```

- `design_space_theorem` in [`DesignSpace.lean`](DASHImpossibility/DesignSpace.lean) -- the design space characterization
- `family_a_or_family_b` in [`DesignSpaceFull.lean`](DASHImpossibility/DesignSpaceFull.lean) -- exhaustiveness proof

Both relaxation paths (drop completeness, drop stability) converge to the same solution: DASH. This convergence is itself proved (`relaxation_paths_converge` in [`PathConvergence.lean`](DASHImpossibility/PathConvergence.lean)) and contrasts with Arrow's theorem, where relaxation paths diverge.

## 6. It Is Not Just SHAP (Symmetric Bayes Dichotomy)

The impossibility is an instance of a general pattern: any symmetric decision problem admits exactly two strategy families -- the faithful-but-unstable individual strategy and the stable-but-tied aggregate strategy. This is the **Symmetric Bayes Dichotomy** (SBD), a reusable proof technique from invariant decision theory.

- `symmetric_bayes_dichotomy` in [`SymmetricBayes.lean`](DASHImpossibility/SymmetricBayes.lean) -- the general theorem with orbit bounds via `MulAction`

Three verified instances, each with a different symmetry group:

| Instance | Symmetry Group | Impossibility | Lean File |
|----------|---------------|---------------|-----------|
| Feature attribution | S_2 transpositions | Cannot rank collinear features | `Trilemma.lean` |
| Model selection | S_2 permutations | Cannot select among Rashomon-equivalent models | `ModelSelection.lean` |
| Causal discovery | CPDAG automorphisms | Cannot orient edges in Markov equivalence class | `CausalDiscovery.lean` |

The SBD is designed to be reused. To apply it to a new domain, you need: a symmetric decision problem, a finite-sample noise source, and a completeness requirement. The orbit bound gives the minimum ensemble size.

## 7. Extensions

Each extension is a self-contained theorem in its own Lean file:

| Extension | Key Result | Lean File |
|-----------|-----------|-----------|
| **Conditional SHAP** | Cannot escape when beta_j = beta_k; escapes when Delta-beta > ~0.2 | [`ConditionalImpossibility.lean`](DASHImpossibility/ConditionalImpossibility.lean) |
| **Fairness audits** | SHAP-based proxy audits are coin flips; (1/2)^K intersectional compounding | [`FairnessAudit.lean`](DASHImpossibility/FairnessAudit.lean) |
| **Fisher information** | Independent proof path via FIM; Rashomon ellipsoid | [`FIMImpossibility.lean`](DASHImpossibility/FIMImpossibility.lean) |
| **Query complexity** | Omega(sigma^2/Delta^2) queries needed; Le Cam lower bound | [`QueryComplexity.lean`](DASHImpossibility/QueryComplexity.lean) |
| **Rashomon inevitability** | Impossibility is inescapable for standard ML under symmetry | [`RashomonInevitability.lean`](DASHImpossibility/RashomonInevitability.lean) |
| **Local vs global** | Local instability >= global instability | [`LocalGlobal.lean`](DASHImpossibility/LocalGlobal.lean) |
| **Flip rate** | Exact GBDT flip rate; binary group = coin flip | [`FlipRate.lean`](DASHImpossibility/FlipRate.lean) |
| **Efficiency** | SHAP efficiency amplification factor m/(m-1) | [`Efficiency.lean`](DASHImpossibility/Efficiency.lean) |
| **Alpha-faithfulness** | Bound on alpha-faithful attribution | [`AlphaFaithful.lean`](DASHImpossibility/AlphaFaithful.lean) |
| **Unfaithfulness bound** | Unfaithfulness >= 1/2 for complete rankings; ties are optimal | [`UnfaithfulBound.lean`](DASHImpossibility/UnfaithfulBound.lean) |
| **Rashomon universality** | Rashomon property from symmetry via feature swap | [`RashomonUniversality.lean`](DASHImpossibility/RashomonUniversality.lean) |
| **Gaussian flip rate** | Standard normal CDF, phi(0)=1/2, flip rate from Gaussian noise | [`GaussianFlipRate.lean`](DASHImpossibility/GaussianFlipRate.lean) |
| **Model selection design space** | Design space for model selection (SBD instance) | [`ModelSelectionDesignSpace.lean`](DASHImpossibility/ModelSelectionDesignSpace.lean) |

## 8. Diagnostics

The paper provides a practitioner workflow for detecting and resolving attribution instability:

**F5 single-model screen.** From a single trained model, flag feature pairs likely to be unstable. Achieves 94% precision -- you can screen without retraining.

**F1 multi-model diagnostic.** Train M models, compute SHAP for each, measure rank agreement. The correlation between F1 score and instability exceeds |r| > 0.89 across 11 datasets and 3 GBDT implementations (XGBoost, LightGBM, CatBoost).

**SNR calibration.** The signal-to-noise ratio predicts the flip rate: Phi(-SNR) matches the observed flip probability with R^2=0.94 for SNR >= 0.5 (`paper/scripts/snr_calibration.py`).

**Practitioner workflow:**
1. **Identify groups.** Find feature clusters with |correlation| > 0.5 and similar importance.
2. **Screen (F5).** Run the single-model screen on one trained model.
3. **Validate (F1).** Train M=25 models, compute the F1 diagnostic.
4. **Resolve (DASH).** Average |SHAP| across the M models.
5. **Report.** Flag within-group pairs as indistinguishable; report between-group rankings.

## 9. Experiments

Validated across multiple model classes, datasets, and attribution methods:

| Experiment | Key Finding | Script |
|-----------|-------------|--------|
| Synthetic Gaussian | 50% flip rate for rho=0.9, matches theory | `generate_figures.py` |
| Breast Cancer (Wisconsin) | 48% flip rate for correlated features | `f1_f5_validation.py` |
| 11 real datasets | F1 |r| > 0.89 across all datasets | `real_world_validation.py` |
| XGBoost/LightGBM/CatBoost | Instability is implementation-independent | `cross_implementation_validation.py` |
| Permutation importance | 91% of correlated pairs unstable | `permutation_importance_validation.py` |
| Neural networks | 87% unstable; KernelSHAP noise 11% vs model instability 87% | `nn_shap_validation.py`, `kernelshap_noise_control.py` |
| P=500 scalability | Runs in 2.5 minutes, |r|=0.876 | `high_dimensional_validation.py` |
| German Credit, Taiwan CC, Lending Club | Positive control: correlated financial features flip | `financial_case_study.py`, `lending_club_case_study.py` |
| LLM attention | 14.5% instability under fine-tuning | `llm_attention_instability.py` |
| Bootstrap stochasticity | Separates data stochasticity from model stochasticity | `bootstrap_stochasticity.py` |
| Conditional SHAP sweep | Delta-beta threshold for escape | `conditional_shap_threshold.py` |
| Proportionality axiom | CV = 0.66 at tree depth 6 | `proportionality_validation.py` |
| Prevalence survey | 37 datasets, ~60% exhibit instability | `prevalence_survey.py` |

All scripts use fixed random seeds and run on a standard laptop in under 30 minutes total.

## 10. The Formalization

**188 theorems. 18 axioms. 0 sorry. 36 files. 13 abstraction levels.**

The Lean formalization caught 2 logical inconsistencies and 1 type mismatch that survived informal review. The axiom consistency proof (a `Fin 4` construction in [`Consistency.lean`](DASHImpossibility/Consistency.lean)) demonstrates the axiom system is non-vacuous -- there exists a concrete model satisfying all 18 axioms.

### Architecture Levels

| Level | What It Proves | Files |
|-------|---------------|-------|
| 0 (pure logic) | `attribution_impossibility` -- zero axiom deps | `Trilemma.lean` |
| 1 (framework) | IterativeOptimizer connects to Rashomon | `Iterative.lean` |
| 2 (instantiation) | Model-specific impossibilities | `General.lean`, `Lasso.lean`, `NeuralNet.lean` |
| 3 (quantitative) | 1/(1-rho^2) divergence (pure algebra) | `SplitGap.lean`, `Ratio.lean` |
| 4 (Spearman) | Spearman from midranks, stability bounds | `SpearmanDef.lean` |
| 5 (resolution) | DASH equity, combined results | `Corollary.lean`, `Impossibility.lean` |
| 6 (design space) | Complete design space characterization | `DesignSpace.lean`, `DesignSpaceFull.lean` |
| 7 (derivation) | `attribution_sum_symmetric` derived from axioms | `SymmetryDerive.lean` |
| 8 (generalization) | General SBD theorem | `SymmetricBayes.lean` |
| 9 (instances) | SBD applied to three domains | `ModelSelection.lean`, `CausalDiscovery.lean`, `SBDInstances.lean` |
| 10 (extensions) | Conditional SHAP, fairness, flip rates | `ConditionalImpossibility.lean`, `FairnessAudit.lean`, `FlipRate.lean` |
| 11 (bounds) | DASH optimality, efficiency, alpha-faithfulness | `EnsembleBound.lean`, `Efficiency.lean`, `AlphaFaithful.lean`, + 3 more |
| 12 (universality) | Rashomon is inescapable, local >= global | `RashomonUniversality.lean`, `RashomonInevitability.lean`, `LocalGlobal.lean` |
| Contrast | Bounded violations (documentation only) | `RandomForest.lean` |

### Axiom Inventory (18 total)

The core impossibility (Level 0) uses **none** of these -- only the Rashomon property as a hypothesis.

| Axiom | Lean Name | Category | Plain English |
|-------|-----------|----------|---------------|
| Abstract model type | `Model` | Type declaration | "There exist trained models" |
| Boosting rounds | `numTrees`, `numTrees_pos` | Type declaration | "Models have T > 0 boosting rounds" |
| Attribution function | `attribution` | Type declaration | "Each feature has an importance score in each model" |
| Utilization count | `splitCount` | Type declaration | "Each feature has a utilization count" |
| First-mover | `firstMover` | Type declaration | "Each model has a first-mover feature" |
| Surjectivity | `firstMover_surjective` | Domain | "Every feature can be the first-mover in some model" |
| First-mover splits | `splitCount_firstMover` | Domain | "The first-mover gets T/(2-rho^2) splits" |
| Non-first-mover splits | `splitCount_nonFirstMover` | Domain | "Other features get (1-rho^2)T/(2-rho^2) splits" |
| Proportionality | `proportionality_global` | Domain | "Attribution = constant * split count" |
| Cross-group symmetry | `splitCount_crossGroup_symmetric` | Domain | "Features in different groups get equal splits" |
| Spearman bound | `spearman_classical_bound` | Domain | "Spearman correlation <= 1 - m^3/P^3" |
| Measurable space | `modelMeasurableSpace` | Measure infrastructure | "Models form a measurable space" |
| Probability measure | `modelMeasure` | Measure infrastructure | "Models have a probability distribution" |
| Testing constant | `testing_constant` | Query complexity | "Le Cam testing constant exists" |
| Testing positivity | `testing_constant_pos` | Query complexity | "Testing constant > 0" |
| Le Cam bound | `le_cam_lower_bound` | Query complexity | "Query complexity >= sigma^2/Delta^2" |

The 3 query-complexity axioms axiomatize Le Cam's testing bound from Tsybakov (2009). They are textbook results, not domain-specific assumptions.

**Note:** `consensus_variance_bound` and `attribution_sum_symmetric` were formerly axiomatized but are now **derived** as theorems. `attribution_variance` is a noncomputable definition from Mathlib's `ProbabilityTheory.variance`.

### Proof Status Transparency

The paper distinguishes four levels of verification:
- **Proved:** Lean theorem with zero domain-axiom dependencies (e.g., `attribution_impossibility`)
- **Derived:** Lean theorem conditional on the axiom system (e.g., `gbdt_impossibility`)
- **Argued:** Supplement proof, not formalized in Lean (e.g., random forest convergence rate)
- **Empirical:** Experiment with reproducible script (e.g., 48% flip rate on Breast Cancer)

### Limitations

- **Equicorrelation assumption.** The axiom system assumes all features in a group share the same pairwise correlation. The diagnostics (F1, F5) do not require this assumption.
- **Proportionality CV.** The proportionality axiom has CV = 0.66 at tree depth 6 in empirical validation. This affects the quantitative ratio but not the qualitative impossibility.
- **Query complexity axiomatized.** The Le Cam lower bound is axiomatized from the statistics literature rather than derived from Mathlib.
- **Balanced ensemble assumption.** The DASH O(1/M) convergence assumes a balanced ensemble (equal first-mover counts). The convergence is robust to approximate balance.

---

# Part 3: Reproduce, Cite, Contribute

## Reproduce

### Verify the Formalization

```bash
lake build
# Expected: compiles with 0 errors, 0 warnings about sorry

# Count theorems + lemmas (expect 188)
grep -c '^theorem\|^lemma' DASHImpossibility/*.lean | awk -F: '{s+=$2}END{print s}'

# Count axioms (expect 18)
grep -c '^axiom' DASHImpossibility/*.lean | awk -F: '{s+=$2}END{print s}'

# Verify zero sorry
grep -rn 'sorry' DASHImpossibility/*.lean
# Expected: no output
```

### Verify the Experiments

```bash
# Axiom consistency: constructs Fin 4 model satisfying all axioms (expect 15/15 PASS)
python3 paper/scripts/axiom_consistency_model.py

# F1/F5 validation: instability threshold (expect F1 r=-0.89)
python3 paper/scripts/f1_f5_validation.py

# Noise control: SHAP noise vs model instability (expect noise 11% vs model 87%)
python3 paper/scripts/kernelshap_noise_control.py

# High-dimensional validation (expect P=500, |r|=0.876)
python3 paper/scripts/high_dimensional_validation.py

# SNR calibration (expect R^2=0.94 for SNR>=0.5)
python3 paper/scripts/snr_calibration.py
```

All scripts require: `pip install xgboost lightgbm catboost shap scikit-learn numpy pandas`

### Build the Paper

```bash
cd paper

# JMLR version (42 pages, primary target)
pdflatex main_jmlr.tex && bibtex main_jmlr && pdflatex main_jmlr.tex && pdflatex main_jmlr.tex

# NeurIPS version (10 pages + 77-page supplement)
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
pdflatex supplement.tex && pdflatex supplement.tex

# Definitive version (59 pages, all content)
pdflatex main_definitive.tex && bibtex main_definitive && pdflatex main_definitive.tex && pdflatex main_definitive.tex
```

## Citation

```bibtex
@article{caraker2026attribution,
  title={The Attribution Impossibility: Faithful, Stable, and Complete Feature
         Rankings Cannot Coexist Under Collinearity},
  author={Caraker, Drake and Arnold, Bryan and Rhoads, David},
  year={2026},
  note={Lean 4 formalization: \url{https://github.com/DrakeCaraker/dash-impossibility-lean}}
}
```

## Contribute

Open areas where contributions are welcome:

- **Derive `spearman_classical_bound` from first principles.** This is the last axiom that could plausibly be a theorem. The gap is documented in [`SpearmanDef.lean`](DASHImpossibility/SpearmanDef.lean).
- **Gaussian CDF lemmas to Mathlib.** The proofs of phi(0)=1/2 and phi(-x)=1-phi(x) in [`GaussianFlipRate.lean`](DASHImpossibility/GaussianFlipRate.lean) via `NoAtoms` + `prob_compl_eq_one_sub` may be of independent interest.
- **New SBD instances.** Apply the Symmetric Bayes Dichotomy to new domains: feature selection instability, hyperparameter sensitivity, cross-validation ranking instability.
- **New datasets.** Run the F5/F1/DASH diagnostic workflow on datasets in your domain. Adapt `paper/scripts/f1_f5_validation.py`.
- **LLM generalization.** Extend the attention attribution instability results beyond the current fine-tuning experiments.

## Frequently Asked Questions

**What is SHAP?**
SHAP (SHapley Additive exPlanations) assigns each feature an importance score for a model's prediction, based on cooperative game theory. It is the most widely used feature attribution method. See [Lundberg & Lee, 2017](https://papers.nips.cc/paper/7062-a-unified-approach-to-interpreting-model-predictions).

**What is Lean 4?**
A programming language and interactive theorem prover. You write mathematical proofs as code, and the computer checks every step. Think of it as a compiler for math. See [leanprover.github.io](https://leanprover.github.io/).

**What does "sorry" mean in Lean?**
It is a placeholder that says "trust me, this is true" without providing a proof -- the Lean equivalent of a TODO. This project has 0 sorry: every claim is machine-verified.

**Can I reproduce the experiments?**
Yes. See the Reproduce section above. All scripts use fixed random seeds and run on a standard laptop in under 30 minutes total.

**Is DASH just averaging?**
Yes -- but with provable optimality guarantees. DASH computes the mean |SHAP| across M independently trained models. The paper proves this is the minimum-variance unbiased estimator (via Cramer-Rao / Titu's lemma) and gives the tight ensemble size formula M_min = ceil(2.71 * sigma^2 / Delta^2). "Just averaging" is like saying OLS is "just matrix inversion." The value is in understanding exactly when and why it is optimal.

**Does this apply to my dataset?**
Check two things: (1) Do you have features with |correlation| > 0.5? (2) Do those features have similar importance? If both yes, your SHAP rankings for those features are unreliable. Adapt `paper/scripts/f1_f5_validation.py` to your data to check.

**What about conditional SHAP?**
It does not help when features have equal causal effects (beta_j = beta_k). The impossibility extends to conditional attributions in that case. When causal effects differ (Delta-beta > ~0.2), conditional SHAP can resolve the instability. See [`ConditionalImpossibility.lean`](DASHImpossibility/ConditionalImpossibility.lean).

**How does this relate to Arrow's theorem?**
Same structure: Arrow proves no voting system can satisfy IIA + Pareto + non-dictatorship simultaneously. We prove no ranking can satisfy faithfulness + stability + completeness simultaneously. Both are resolved by allowing ties (partial orders). Our relaxation paths converge (unlike Arrow's, which diverge) -- reflecting the DGP symmetry that Arrow's heterogeneous voters lack.

**What is the relationship to dash-shap?**
This repository contains the theory (Lean proofs + paper). [dash-shap](https://github.com/DrakeCaraker/dash-shap) is the Python implementation: DASH pipeline, experiments, diagnostics. The stability API ([PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255)) provides `screen()`, `validate()`, `consensus()`, `report()`.

**Is this published?**
JMLR submission planned for Q4 2026. arXiv preprint forthcoming. The Lean formalization and all code are publicly available now.

**Can I cite this?**
Yes. See the Citation section above.

**How can I contribute?**
See the Contribute section above. Open areas include deriving the spearman_classical_bound, contributing Gaussian CDF lemmas to Mathlib, new SBD instances, new datasets, and LLM generalization.

## Companion Code

The Python implementation lives in [dash-shap](https://github.com/DrakeCaraker/dash-shap). The stability API is in [PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255), providing:
- `dash_shap.screen()` -- F5 single-model screening
- `dash_shap.validate()` -- F1 multi-model validation
- `dash_shap.consensus()` -- DASH ensemble averaging
- `dash_shap.report()` -- Instability disclosure report

## Related Work

- **Bilodeau et al. (2024):** Proved completeness + linearity cannot coexist; we address stability instead and provide a constructive resolution.
- **Chouldechova (2017):** Proved calibration + balance + equal FPR cannot coexist when base rates differ; our trilemma is the explainability analogue.
- **Arrow (1951):** Proved IIA + Pareto + non-dictatorship cannot coexist; same structural template, different domain.
- **Nipkow (2009):** Formalized Arrow's theorem in Isabelle/HOL; we extend this tradition to explainable AI in Lean 4.
- **Zhang et al. (2026):** Formalized statistical learning theory in Lean 4; complementary Lean formalization work.

## Authors

**Drake Caraker** -- conceptualization, Lean formalization, experiments, software
**Bryan Arnold** -- [role]
**David Rhoads** -- [role]

Independent researchers. Contact: drakecaraker@gmail.com

---

**Paper:** "The Attribution Impossibility: Faithful, Stable, and Complete Feature Rankings Cannot Coexist Under Collinearity"
**Primary target:** JMLR | **Backup:** NeurIPS 2026 (abstract May 4, paper May 6)
**arXiv:** Preprint forthcoming. Run `paper/scripts/prepare_arxiv.sh` to prepare submission.
