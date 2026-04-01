# The Attribution Impossibility — Lean 4 Formalization

Lean 4 formalization of the impossibility theorem for feature attribution under collinearity. Target venue: NeurIPS 2026 (abstract May 4, paper May 6). Paper 3 in the 5-paper research program housed in [dash-shap](https://github.com/DrakeCaraker/dash-shap).

## What This Proves

No single-model feature ranking can simultaneously be faithful (reflect the model's attributions), stable (consistent across equivalent models), and complete (rank all feature pairs) when features are collinear. The core theorem requires **zero model-specific axioms** — only the Rashomon property.

Model-specific instantiations show GBDT has ratio 1/(1-ρ²) → ∞, Lasso has ratio ∞, neural nets have conditional violations, and random forests have bounded O(1/√T) violations. DASH (ensemble averaging) resolves the impossibility for balanced ensembles.

## Architecture

```
Level 0 (pure logic):     Trilemma.lean — attribution_impossibility (zero axiom deps)
Level 1 (framework):      Iterative.lean — IterativeOptimizer → Rashomon → impossibility
Level 2 (instantiation):  General.lean (GBDT), Lasso.lean, NeuralNet.lean
Level 3 (quantitative):   SplitGap.lean, Ratio.lean (1/(1-ρ²) divergence)
Level 4 (Spearman):       SpearmanDef.lean (defined from scratch, qualitative bound derived)
Level 5 (resolution):     Corollary.lean (DASH equity), Impossibility.lean (combined)
Level 6 (design space):   DesignSpace.lean (design_space_theorem, Pareto structure)
Contrast:                 RandomForest.lean (bounded violations, no formal proofs)
```

## File Structure

```
DASHImpossibility/
  Defs.lean          — FeatureSpace, 14 axioms, stability/equity defs, consensus
  Trilemma.lean      — RashimonProperty, attribution_impossibility (model-agnostic)
  Iterative.lean     — IterativeOptimizer abstraction
  General.lean       — GBDT instance, gbdt_impossibility, gbdtOptimizer
  SplitGap.lean      — split_gap_exact, split_gap_ge_half (pure algebra)
  Ratio.lean         — attribution_ratio = 1/(1-ρ²), ratio_tendsto_atTop
  SpearmanDef.lean   — Spearman defined from midranks, qualitative + quantitative bounds
  Lasso.lean         — lasso_impossibility (ratio = ∞)
  NeuralNet.lean     — nn_impossibility (conditional on captured feature)
  RandomForest.lean  — Contrast case (documentation, no formal proofs)
  Impossibility.lean — Combined: equity violation + stability bound
  Corollary.lean     — DASH consensus equity, variance convergence
  DesignSpace.lean   — Design Space Theorem (composite), DASH ties, exhaustiveness
  Basic.lean         — Import hub
paper/
  main.tex           — NeurIPS 2026 paper (13 pages incl. refs+checklist)
  supplement.tex     — Supplementary (52 pages)
  references.bib     — 22 citations
  scripts/           — 21 scripts (figure generation, validation, diagnostics)
  figures/           — PDF figures (ratio, instability, DASH, F1/F5, design space, SNR calibration, conditional threshold, etc.)
```

## Lean State: 14 files, 15 axioms, 44 declarations (35 theorems + 9 lemmas), 0 sorry

## Axiom Inventory (15 total)

| Category | Axioms | Used by |
|----------|--------|---------|
| Type declarations | Model, numTrees, numTrees_pos, attribution, splitCount, firstMover | Infrastructure |
| Core properties | firstMover_surjective, splitCount_firstMover, splitCount_nonFirstMover, attribution_proportional | GBDT bounds |
| DASH | attribution_sum_symmetric | Corollary equity |
| Variance | attribution_variance, attribution_variance_nonneg, consensus_variance_bound | Corollary stability |
| Spearman | spearman_classical_bound (about defined quantity) | Quantitative stability |

The core impossibility theorem (Levels 0-1) uses **none** of these — only the Rashomon property as hypothesis.

## Building

```bash
lake build     # compile everything (~1988 jobs)
```

## NeurIPS 2026 Submission

- Paper: `paper/main.tex` (9 pages + supplement)
- Title: "The Attribution Impossibility: Faithful, Stable, and Complete Feature Rankings Cannot Coexist Under Collinearity"
- Abstract deadline: May 4, Paper deadline: May 6
- Placeholder `neurips_2026.sty` — replace with official style before submission
- TODO: Add co-author information

## Do NOT

- Commit paper changes without verifying paper-code consistency: theorem count (`grep -c "^theorem\|^lemma" DASHImpossibility/*.lean`), axiom count (`grep -c "^axiom" DASHImpossibility/*.lean`), page counts (`pdfinfo paper/main.pdf`, `pdfinfo paper/supplement.pdf`), and sorry count all match what the paper text claims
- Use `sorry` without a `-- TODO:` comment explaining what's needed
- Change axioms without re-running the SymPy verification (`dash-shap/paper/proofs/verify_lemma6_algebra.py`)
- Add `autoImplicit true` — all variables must be explicit
- Claim "N theorems" without verifying — count with `grep -c "^theorem\|^lemma"` (currently 42)
- Run parallel subagents that both modify the same file (causes build cache corruption)
- Axiomatize quantities that can be defined — prefer definitions with axiomatized bounds (see SpearmanDef.lean pattern)
- Claim empirical results as "proved" or "Lean-verified" — distinguish: **proved** (zero axiom deps), **derived** (from axioms), **argued** (supplement proof only), **empirical** (experiments). The paper's "Proof status transparency" paragraph is the reference.
