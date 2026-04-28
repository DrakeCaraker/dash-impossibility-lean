# The Attribution Impossibility: What It Is and Why It Matters

A plain-language guide to this project for someone with no prior context.

## The Problem in One Paragraph

When you train a machine learning model and ask "which feature was most important?", the answer changes depending on the random seed used during training. This is not a bug. It is not a tuning problem. It is a mathematical inevitability that affects every model class, every attribution method, and every dataset with correlated features. In a survey of 77 public datasets, 68% exhibit this instability. This project proves the impossibility, quantifies how bad it is, characterizes the complete space of possible solutions, proves the optimal fix, and machine-verifies everything in Lean 4.

## Origins

This project began as a practical observation: SHAP feature rankings for gradient-boosted models were flipping between retrains. The [dash-shap](https://github.com/DrakeCaraker/dash-shap) Python package was built to diagnose and fix this instability through ensemble averaging (DASH). The theoretical question was: *is this fixable in principle, or is it a fundamental limitation?*

The answer turned out to be a fundamental limitation — and a much deeper one than initially expected. The impossibility is not specific to SHAP, not specific to gradient boosting, and not specific to feature attribution. It applies to any attribution at any level of a model: input features (SHAP), internal circuits (activation patching), or any system with interchangeable components under the Rashomon property.

## What Is Proved

### The Core Impossibility (Theorem 1)

No feature ranking can be simultaneously:
- **Faithful** — reflecting what the model actually computed
- **Stable** — consistent across retrains with different random seeds
- **Complete** — deciding every pair of features

when features are correlated with similar true importance. This is analogous to Arrow's impossibility theorem for voting systems (IIA + Pareto + non-dictatorship cannot coexist) and Chouldechova's fairness impossibility (calibration + balance + equal false positive rates cannot coexist when base rates differ).

The proof is four lines long. The Rashomon property — that correlated features admit models ranking them in opposite orders — immediately yields a contradiction: a faithful ranking must agree with each model, but different models disagree.

### Quantitative Bounds

The impossibility is not a mild edge case. The attribution ratio (how much the dominant feature is overweighted) depends on the model class:

| Model Class | Attribution Ratio | Behavior |
|-------------|-------------------|----------|
| Gradient boosting (GBDT) | 1/(1-rho^2) | Diverges to infinity as correlation increases |
| Lasso | Infinity | One feature gets all credit, the other gets zero |
| Neural networks | Model-dependent | Conditional on initialization |
| Random forests | 1 + O(1/sqrt(T)) | Converges — the contrast case |

At correlation rho = 0.9, the dominant feature gets 5.3x its fair share. For binary collinear groups, the flip rate is exactly 1/2 — a literal coin flip.

### The Design Space Theorem

The achievable set of attribution methods consists of exactly two families:
- **Family A (single-model):** Faithful and complete, but rankings flip up to 50% of the time.
- **Family B (DASH ensemble):** Faithful and stable, but reports ties for indistinguishable features.

No third family exists. Both relaxation paths (drop completeness, drop stability) converge to the same solution: ensemble averaging. This convergence is itself proved.

### The Fix: DASH

**DASH** (Diversified Aggregation for Stable Hypotheses) averages feature importance across multiple independently trained models. This is provably the minimum-variance unbiased estimator (via Cauchy-Schwarz / Titu's lemma). The required ensemble size is M_min = ceil(2.71 * sigma^2 / Delta^2) for a 5% flip rate.

DASH is Pareto-optimal: no method achieves better stability without sacrificing more faithfulness. The tradeoff: within-group features that are genuinely interchangeable are reported as tied rather than arbitrarily ranked.

### The Symmetric Bayes Dichotomy

The impossibility generalizes beyond feature attribution. Any symmetric decision problem — where a population distribution is invariant under a symmetry group — admits exactly two strategy families. This is demonstrated across three structurally distinct instances:

1. **Feature attribution** (symmetry group S_2): cannot rank collinear features
2. **Model selection** (symmetry group S_2): cannot select among equivalent models
3. **Causal discovery** (CPDAG automorphisms): cannot orient edges in Markov equivalence classes

### The Bilemma

For binary explanation problems — "is this feature positive or negative?", "is this feature selected?" — the impossibility is strictly stronger. Faithful + stable alone is impossible (completeness is not needed to derive the contradiction). There is no fix because binary spaces have no neutral element (no "tie" to report).

## The Formalization

Everything is machine-verified in Lean 4 using Mathlib:
- **357 theorems**, 0 `sorry` (unproved claims), across 58 files
- **6 axioms** — the irreducible core (model type, first-mover function and surjectivity, cross-group baseline, proportionality constant, training distribution measure)
- **10 former axioms** are now definitions or derived theorems
- The core impossibility uses **zero axioms** — only the Rashomon property as a hypothesis

The formalization caught 2 logical inconsistencies and 1 type mismatch that survived informal review. This is the first formally verified impossibility result in explainable AI.

## Who Should Care

**Data scientists using SHAP.** If your dataset has correlated features with similar importance, your feature rankings are unreliable. The fix: average SHAP values across 25+ independently trained models (DASH). Use the [dash-shap](https://github.com/DrakeCaraker/dash-shap) Python package.

**ML researchers.** The Symmetric Bayes Dichotomy is a reusable proof technique for any symmetric decision problem. The Design Space Theorem provides a complete characterization template. The Lean formalization demonstrates AI-assisted formal methods at scale.

**Regulators and model risk officers.** Single-model SHAP audits for proxy discrimination are provably unreliable — the audit conclusion is a coin flip for collinear features. This affects EU AI Act Art. 13(3)(b)(ii) disclosure requirements and SR 11-7 model risk management. The paper provides diagnostic workflows and disclosure templates.

**The formal verification community.** 357 theorems across 58 files, 15 abstraction levels, using Mathlib's MulAction, ProbabilityTheory, and Analysis libraries. The axiom reduction from 16 to 6 demonstrates the "define rather than axiomatize" methodology.

## Ramifications

### For Practice
- **Feature importance reports for correlated features are unreliable.** Any study reporting a specific SHAP ranking from a single model on correlated features is reporting an artifact of the training seed.
- **Regulatory compliance requires ensemble explanations.** Single-model adverse action notices under ECOA can change based solely on the random seed.
- **The diagnostic workflow is actionable.** Screen (single model) → Z-test (5 models) → DASH (25+ models) provides a practical path from detection to resolution.

### For Theory
- **The Rashomon property is the root cause.** Collinearity creates a flat ridge in the loss landscape along which feature importance redistributes without changing model quality.
- **Explanation impossibilities parallel fairness impossibilities.** The structural analogy with Chouldechova/Kleinberg suggests a deeper connection between explainability and fairness constraints.
- **Binary explanation problems are strictly harder.** The bilemma shows that enriching the explanation space (from binary to graded) is necessary, not merely convenient.

### For AI Governance
- **Attribution instability is a "known and foreseeable circumstance"** under the EU AI Act.
- **Intersectional fairness compounds the problem.** For K protected attributes with unstable proxies, the probability of a correct audit is (1/2)^K.
- **The impossibility applies to mechanistic interpretability.** Circuit explanations of neural networks face the same trilemma.

## Future Directions

See [docs/future-research-directions.md](docs/future-research-directions.md) for the full list from the 9-reviewer panel. Key paths:

1. **Algorithmic identification impossibility.** Prove that "what algorithm does the model implement" is also unstable, not just "which component is most important." This would make the safety implications airtight.
2. **Frontier-scale from-scratch training.** Train multiple GPT-2+ models from scratch and verify the impossibility holds at scale.
3. **Deep invariant theory.** Isotypic decomposition of attribution variance, Molien's theorem for information budgets, V^G on non-trivial symmetry groups.
4. **General SBD theorem.** Prove the two-family decomposition for arbitrary G-invariant decision problems.
5. **SAE escape hatch.** Do independently trained SAEs on the same model produce the same features? If so, SAE-based attribution may escape the Rashomon property.
6. **Formalizing the Bayes-optimal half of the Design Space** in Lean (requires measure-theoretic decision theory from Mathlib).
7. **Building DASH into production ML pipelines.** The [dash-shap PR #255](https://github.com/DrakeCaraker/dash-shap/pull/255) stability API is the implementation target.

## How to Verify

```bash
git clone https://github.com/DrakeCaraker/dash-impossibility-lean
cd dash-impossibility-lean
make lean    # builds all 357 theorems (~5 min cached)
make verify  # checks counts match documentation
```

## Citation

```bibtex
@article{caraker2026attribution,
  title={The Attribution Impossibility: No Feature Ranking Is Faithful, Stable,
         and Complete Under Collinearity},
  author={Caraker, Drake and Arnold, Bryan and Rhoads, David},
  year={2026},
  doi={10.5281/zenodo.19468379}
}
```

## Paper

**NeurIPS 2026 submission:** `paper/main.tex` (10 pages, input-level + component-level) + `paper/supplement.tex` (81 pages). **Monograph:** `paper/main_definitive.tex` (82 pages, complete reference including TinyStories and mean ablation sections). **arXiv:** `paper/arxiv_monograph.tar.gz`. **JMLR:** `paper/main_jmlr.tex` (59 pages, to be submitted after NeurIPS decision).
