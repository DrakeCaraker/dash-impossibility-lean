# The Attribution Impossibility

**No feature ranking can be simultaneously faithful, stable, and complete when features are correlated -- and we prove it in Lean 4.**

<!-- Badges are static. Update manually when counts change. -->
<!-- Verify with: grep -c '^theorem\|^lemma' DASHImpossibility/*.lean | awk -F: '{s+=$2}END{print s}' -->
<!-- Verify with: grep -c '^axiom' DASHImpossibility/*.lean | awk -F: '{s+=$2}END{print s}' -->
<!-- Verify with: grep -rn 'sorry' DASHImpossibility/*.lean (should be empty) -->
![Theorems](https://img.shields.io/badge/theorems-188-blue)
![Axioms](https://img.shields.io/badge/axioms-18-orange)
![Sorry](https://img.shields.io/badge/sorry-0-brightgreen)
![Lean 4](https://img.shields.io/badge/Lean-4-purple)

If you have ever retrained an XGBoost model and noticed the "most important feature" changed, this paper proves that is not a bug -- it is a mathematical inevitability. When features are correlated, no attribution method can simultaneously tell you what the model computed (faithfulness), give you the same answer across retrains (stability), and decide every pair of features (completeness). You must pick two of three. We prove it, quantify it, and give you a toolkit to handle it. The core impossibility theorem is machine-checked in Lean 4 with zero domain-specific axiom dependencies.

---

## Who Is This For?

**If you are a data scientist using SHAP:** Your feature rankings for correlated features are unreliable. The instability is not noise or a software bug -- it is a provable consequence of how gradient boosting interacts with collinearity. The fix is DASH: average SHAP values from multiple independently trained models to find what they agree on. See the [dash-shap](https://github.com/DrakeCaraker/dash-shap) companion package and the [stability API in PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255) for the F5 (single-model screen) to F1 (multi-model validation) to DASH (ensemble consensus) workflow.

**If you are a researcher in XAI or ML theory:** This is a formally verified impossibility theorem with 188 Lean proofs and 0 sorry. The Symmetric Bayes Dichotomy (supplement) is a general proof technique from invariant decision theory that you can reuse for any symmetric decision problem -- we demonstrate it on feature attribution, model selection, and causal discovery under Markov equivalence.

**If you are a regulator or model risk officer:** Single-model SHAP explanations are provably unreliable under collinearity. In a survey of 37 public datasets, approximately 60% exhibit attribution instability. This affects EU AI Act Art. 13(3)(b)(ii) requirements for disclosing "known and foreseeable circumstances" affecting accuracy, and SR 11-7 model risk management compliance.

**If you are from the Lean or Mathlib community:** 188 theorems across 36 files, 13 abstraction levels, using `MulAction` for the SBD orbit bounds, `ProbabilityTheory.cdf` for the Gaussian flip rate, and `Analysis.Calculus` for the FIM impossibility. The Gaussian CDF symmetry proofs (phi(0)=1/2, phi(-x)=1-phi(x)) via `NoAtoms` + `prob_compl_eq_one_sub` may be of independent interest.

---

## Quick Start

```bash
git clone https://github.com/DrakeCaraker/dash-impossibility-lean.git
cd dash-impossibility-lean

# Install Lean 4 via elan if needed
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Verify the formalization (188 theorems, 0 sorry)
lake build              # ~5 min with cached dependencies, ~20 min first build

# Verify axiom system consistency
python3 paper/scripts/axiom_consistency_model.py

# Run a key experiment (SHAP instability validation)
pip install xgboost lightgbm catboost shap scikit-learn numpy pandas
python3 paper/scripts/f1_f5_validation.py

# Build the paper (JMLR version)
cd paper && pdflatex main_jmlr.tex && bibtex main_jmlr && pdflatex main_jmlr.tex && pdflatex main_jmlr.tex
```

---

## What Exactly Did We Prove?

```
                    The Attribution Design Space

    Faithful ────── IMPOSSIBLE ────── Stable
        |              X                 |
        |         (Theorem 1)            |
        |                                |
    Family A                        Family B
    (single model)                  (DASH ensemble)
    + Faithful                      + Stable
    + Complete                      + Between-group faithful
    - Unstable (50% flips)          - Within-group ties
```

The design space of attribution methods under collinearity consists of exactly two families, and nothing else. Every method falls into one of these. DASH is Pareto-optimal on the ensemble branch.

### 1. The Impossibility

*Plain English:* You cannot rank correlated features faithfully, stably, and completely -- pick two.

*Lean:* `attribution_impossibility` in [`Trilemma.lean`](DASHImpossibility/Trilemma.lean) -- zero domain-axiom dependencies. The proof is a four-line contradiction from the Rashomon property (the observation that different training runs of the same model class can produce different near-optimal solutions).

### 2. The Design Space Theorem

*Plain English:* There are exactly two kinds of attribution methods under collinearity, and no method lives outside this dichotomy.

*Lean:* `design_space_theorem` + `family_a_or_family_b` in [`DesignSpace.lean`](DASHImpossibility/DesignSpace.lean) and [`DesignSpaceFull.lean`](DASHImpossibility/DesignSpaceFull.lean).

### 3. The Symmetric Bayes Dichotomy

*Plain English:* This impossibility pattern -- choose two of three desirable properties -- applies to any symmetric decision problem, not just SHAP. It is a recipe for proving impossibilities in settings with symmetry.

*Lean:* `symmetric_bayes_dichotomy` in [`SymmetricBayes.lean`](DASHImpossibility/SymmetricBayes.lean) -- general theorem with orbit bounds.

### 4. Quantitative Bounds

*Plain English:* The attribution ratio (how much the dominant feature is overweighted) diverges as 1/(1-rho^2) for gradient boosting, is infinite for Lasso, and converges at O(1/sqrt(T)) for random forests.

*Lean:* `ratio_tendsto_atTop` in [`Ratio.lean`](DASHImpossibility/Ratio.lean), `lasso_impossibility` in [`Lasso.lean`](DASHImpossibility/Lasso.lean).

### 5. DASH Resolution

*Plain English:* Average SHAP values from multiple independently trained models. This is provably the minimum-variance unbiased estimator with a tight ensemble size formula M_min = ceil(2.71 * sigma^2 / Delta^2).

*Lean:* `consensus_equity` in [`Corollary.lean`](DASHImpossibility/Corollary.lean), `sum_squares_ge_inv_M` in [`EnsembleBound.lean`](DASHImpossibility/EnsembleBound.lean).

### 6. Practical Diagnostics

*Plain English:* A Z-test workflow that tells you which feature pairs are unreliable, plus a single-model screening tool.

*Experiments:* F1 threshold |r| > 0.89 across 11 datasets. F5 screening achieves 94% precision. Validated at P=500 features in 2.5 minutes. See `paper/scripts/f1_f5_validation.py`.

---

## Architecture

### Repository Map

```
dash-impossibility-lean/
├── DASHImpossibility/             # 36 Lean 4 files, 188 theorems
│   ├── Defs.lean                  # Axiom system (6 type + 7 domain + 2 measure + 3 query)
│   ├── Trilemma.lean              # Core impossibility (0 axiom deps)
│   ├── SymmetricBayes.lean        # General SBD theorem
│   ├── DesignSpace.lean           # Design space characterization
│   ├── DesignSpaceFull.lean       # Design space exhaustiveness (Family A or B)
│   ├── FIMImpossibility.lean      # Independent proof via Fisher information
│   ├── GaussianFlipRate.lean      # Standard normal CDF + flip rate
│   ├── Consistency.lean           # Axiom system consistency (Fin 4 model)
│   ├── EnsembleBound.lean         # DASH variance optimality + ensemble size
│   └── ... (27 more files)        # See Basic.lean for all imports
├── paper/
│   ├── main_jmlr.tex              # JMLR submission (primary target)
│   ├── main_definitive.tex        # Complete reference (all content)
│   ├── main.tex                   # NeurIPS version (14 pages)
│   ├── supplement.tex             # NeurIPS supplement (77 pages)
│   ├── references.bib             # Citations
│   ├── scripts/                   # 32 experiment scripts
│   └── figures/                   # All figures (PDF)
├── docs/                          # Onboarding, verification, plans
│   ├── co-author-guide.md         # Plain English onboarding for collaborators
│   ├── verification-audit.md      # 32-item ranked human verification checklist
│   ├── self-verification-report.md # Machine-verified #print axioms results
│   └── ...
├── lakefile.toml                  # Lean build configuration
├── lean-toolchain                 # Lean version pin
└── CLAUDE.md                      # AI development instructions
```

### Lean Architecture: 13 Levels

The formalization is organized by abstraction level. Each level depends only on levels below it.

| Level | Files | What It Proves |
|-------|-------|---------------|
| 0 (pure logic) | `Trilemma.lean` | `attribution_impossibility` -- zero axiom deps |
| 1 (framework) | `Iterative.lean` | IterativeOptimizer abstraction connects to Rashomon |
| 2 (instantiation) | `General.lean`, `Lasso.lean`, `NeuralNet.lean` | Model-specific impossibilities |
| 3 (quantitative) | `SplitGap.lean`, `Ratio.lean` | 1/(1-rho^2) divergence (pure algebra) |
| 4 (Spearman) | `SpearmanDef.lean` | Spearman correlation from midranks, stability bounds |
| 5 (resolution) | `Corollary.lean`, `Impossibility.lean` | DASH equity, combined results |
| 6 (design space) | `DesignSpace.lean`, `DesignSpaceFull.lean` | Complete design space characterization |
| 7 (derivation) | `SymmetryDerive.lean` | `attribution_sum_symmetric` derived from axioms |
| 8 (generalization) | `SymmetricBayes.lean` | General SBD theorem |
| 9 (instances) | `ModelSelection.lean`, `CausalDiscovery.lean`, `SBDInstances.lean` | SBD applied to three domains |
| 10 (extensions) | `ConditionalImpossibility.lean`, `FairnessAudit.lean`, `FlipRate.lean` | Conditional SHAP, fairness, flip rates |
| 11 (bounds) | `EnsembleBound.lean`, `Efficiency.lean`, `AlphaFaithful.lean` | DASH optimality, efficiency, alpha-faithfulness |
| 12 (universality) | `RashomonUniversality.lean`, `RashomonInevitability.lean`, `LocalGlobal.lean` | Rashomon is inescapable, local >= global |
| Contrast | `RandomForest.lean` | Bounded violations (documentation, no formal proofs) |

### Axiom Inventory (18 total)

The core impossibility (Level 0) uses none of these -- only the Rashomon property as a hypothesis. The axioms support quantitative bounds and model-specific instantiations.

| Axiom | Lean Name | Category | Plain English |
|-------|-----------|----------|---------------|
| Abstract model type | `Model` | Type decl | "There exist trained models" |
| Boosting rounds | `numTrees`, `numTrees_pos` | Type decl | "Models have T > 0 boosting rounds" |
| Attribution function | `attribution` | Type decl | "Each feature has an importance score in each model" |
| Utilization count | `splitCount` | Type decl | "Each feature has a utilization count" |
| First-mover | `firstMover` | Type decl | "Each model has a first-mover feature" |
| Surjectivity | `firstMover_surjective` | Domain | "Every feature can be the first-mover in some model" |
| First-mover splits | `splitCount_firstMover` | Domain | "The first-mover gets T/(2-rho^2) splits" |
| Non-first-mover splits | `splitCount_nonFirstMover` | Domain | "Other features get (1-rho^2)T/(2-rho^2) splits" |
| Proportionality | `proportionality_global` | Domain | "Attribution = constant * split count" |
| Cross-group symmetry | `splitCount_crossGroup_symmetric` | Domain | "Features in different groups get equal splits" |
| Variance bound | `consensus_variance_bound` | Domain | "Consensus variance = single-model variance / M" |
| Spearman bound | `spearman_classical_bound` | Domain | "Spearman correlation <= 1 - m^3/P^3" |
| Measurable space | `modelMeasurableSpace` | Measure infra | "Models form a measurable space" |
| Probability measure | `modelMeasure` | Measure infra | "Models have a probability distribution" |
| Testing constant | `testing_constant` | Query complexity | "Le Cam testing constant exists" |
| Testing positivity | `testing_constant_pos` | Query complexity | "Testing constant > 0" |
| Le Cam bound | `le_cam_lower_bound` | Query complexity | "Query complexity >= sigma^2/Delta^2" |

The 3 query-complexity axioms axiomatize Le Cam's testing bound from Tsybakov (2009). They are textbook results, not domain-specific assumptions.

### Limitations

- **Equicorrelation assumption.** The axiom system assumes all features in a group share the same pairwise correlation. This simplifies the analysis. The diagnostics (F1, F5) do not require it.
- **Proportionality CV.** The proportionality axiom has CV = 0.66 at tree depth 6 in empirical validation. This affects the quantitative ratio but not the qualitative impossibility.
- **Query complexity axiomatized.** The Le Cam lower bound is axiomatized from the statistics literature rather than derived from Mathlib.
- **Balanced ensemble assumption.** The DASH O(1/M) convergence assumes a balanced ensemble (equal first-mover counts). The convergence is robust to approximate balance.

---

## Reproduce Everything

### Verify the Formalization

```bash
lake build
# Expected: compiles with 0 errors

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
```

### Build the Paper

```bash
cd paper

# JMLR version (primary)
pdflatex main_jmlr.tex && bibtex main_jmlr && pdflatex main_jmlr.tex && pdflatex main_jmlr.tex

# NeurIPS version
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

---

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
Yes -- but with provable optimality guarantees. DASH computes the mean |SHAP| across M independently trained models. The paper proves this is the minimum-variance unbiased estimator (via Cramer-Rao / Titu's lemma) and gives the tight ensemble size formula M_min = ceil(2.71 * sigma^2 / Delta^2).

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
Yes:
```bibtex
@article{caraker2026attribution,
  title={The Attribution Impossibility: Faithful, Stable, and Complete Feature
         Rankings Cannot Coexist Under Collinearity},
  author={Caraker, Drake and Arnold, Bryan and Rhoads, David},
  year={2026},
  note={Lean 4 formalization: \url{https://github.com/DrakeCaraker/dash-impossibility-lean}}
}
```

**How can I contribute?**
Open areas: (a) Derive the `spearman_classical_bound` axiom from first principles (gap documented in `SpearmanDef.lean`); (b) Contribute Gaussian CDF lemmas to Mathlib; (c) Run the diagnostic workflow on new datasets; (d) Extend the Symmetric Bayes Dichotomy to new domains (feature selection, hyperparameter tuning).

---

## Related Work

- **Bilodeau et al. (2024):** Proved completeness + linearity cannot coexist; we address stability instead and provide a constructive resolution.
- **Chouldechova (2017):** Proved calibration + balance + equal FPR cannot coexist when base rates differ; our trilemma is the explainability analogue.
- **Arrow (1951):** Proved IIA + Pareto + non-dictatorship cannot coexist; same structural template, different domain.
- **Nipkow (2009):** Formalized Arrow's theorem in Isabelle/HOL; we extend this tradition to explainable AI in Lean 4.
- **Zhang et al. (2026):** Formalized statistical learning theory in Lean 4; complementary Lean formalization work.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/co-author-guide.md](docs/co-author-guide.md) | Plain English onboarding for collaborators |
| [docs/verification-audit.md](docs/verification-audit.md) | 32-item ranked human verification checklist |
| [docs/self-verification-report.md](docs/self-verification-report.md) | Machine-verified `#print axioms` results |
| [docs/neurips-improvement-plan.md](docs/neurips-improvement-plan.md) | Improvement roadmap |
| [docs/full-formalization-plan.md](docs/full-formalization-plan.md) | Lean formalization roadmap |
| [CLAUDE.md](CLAUDE.md) | AI development instructions and conventions |

---

## Paper

- **Title:** The Attribution Impossibility: Faithful, Stable, and Complete Feature Rankings Cannot Coexist Under Collinearity
- **Authors:** Drake Caraker, Bryan Arnold, David Rhoads
- **Primary target:** JMLR (`paper/main_jmlr.tex`)
- **Backup target:** NeurIPS 2026 (`paper/main.tex` + `paper/supplement.tex`), abstract May 4, paper May 6
- **Companion code:** [dash-shap](https://github.com/DrakeCaraker/dash-shap) ([stability API in PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255))
- **arXiv:** Preprint forthcoming. Run `paper/scripts/prepare_arxiv.sh` to uncomment authors and fill URLs.

---

## Authors

**Drake Caraker** -- conceptualization, Lean formalization, experiments, software
**Bryan Arnold** -- [role]
**David Rhoads** -- [role]

Independent researchers. Contact: drakecaraker@gmail.com

---

## License

MIT License. See [`LICENSE`](LICENSE) for details.
