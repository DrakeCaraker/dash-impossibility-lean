# The Attribution Impossibility — Lean 4 Formalization

Lean 4 formalization of the impossibility theorem for feature attribution under collinearity. Target venue: NeurIPS 2026 (abstract May 4, paper May 6). Paper 3 in the 5-paper research program housed in [dash-shap](https://github.com/DrakeCaraker/dash-shap).

## What This Proves

No single-model feature ranking can simultaneously be faithful (reflect the model's attributions), stable (consistent across equivalent models), and complete (rank all feature pairs) when features are collinear. The core theorem requires **zero model-specific axioms** — only the Rashomon property.

Model-specific instantiations show GBDT has ratio 1/(1-ρ²) → ∞, Lasso has ratio ∞, neural nets have conditional violations, and random forests have bounded O(1/√T) violations. DASH (ensemble averaging) resolves the impossibility for balanced ensembles.

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
Level 10 (extensions):    ConditionalImpossibility.lean, FairnessAudit.lean, FlipRate.lean
Level 11 (bounds):        EnsembleBound.lean, Efficiency.lean, AlphaFaithful.lean
Level 12 (universality):  RashomonUniversality.lean, RashomonInevitability.lean, LocalGlobal.lean
Contrast:                 RandomForest.lean (bounded violations, no formal proofs)
```

## File Structure

```
DASHImpossibility/
  Defs.lean              — FeatureSpace, 13 axioms, stability/equity defs, consensus, variance from Mathlib
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
  QueryComplexity.lean   — Query complexity Ω(σ²/Δ²), Le Cam axiomatized (S28)
  CausalDiscovery.lean   — Causal discovery impossibility (S53-S55)
  SBDInstances.lean      — SBD instances + abstract aggregation (S51-S52, S58)
  FairnessAudit.lean     — Fairness audit impossibility (S56)
  EnsembleBound.lean     — DASH variance optimality + ensemble size (S22, S26)
  Basic.lean             — Import hub
paper/
  main.tex           — NeurIPS 2026 paper (14 pages pre-restructure)
  supplement.tex     — Supplementary (70 pages)
  references.bib     — 23 citations
  scripts/           — 30 scripts (figure generation, validation, diagnostics)
  figures/           — PDF figures (ratio, instability, DASH, F1/F5, design space, SNR calibration, conditional threshold, etc.)
```

## Lean State: 36 files, 17 axioms, 180 theorems+lemmas, 2 sorry (Gaussian CDF symmetry — Mathlib gap)

## Axiom Inventory (17 total)

| Category | Axioms | Used by |
|----------|--------|---------|
| Type declarations | Model, numTrees, numTrees_pos, attribution, splitCount, firstMover | Infrastructure |
| Core properties | firstMover_surjective, splitCount_firstMover, splitCount_nonFirstMover, proportionality_global, splitCount_crossGroup_symmetric | GBDT bounds |
| Measure infrastructure | modelMeasurableSpace, modelMeasure | Variance (Mathlib connection) |
| Spearman | spearman_classical_bound (about defined quantity) | Quantitative stability |
| Query complexity | testing_constant, testing_constant_pos, le_cam_lower_bound | Query complexity (Le Cam) |

**Formerly axiomatized, now derived:**
- `consensus_variance_bound` — theorem in Defs.lean (from attribution_variance_nonneg + Nat.cast_nonneg; existential witness is trivial)
- `attribution_sum_symmetric` — theorem in SymmetryDerive.lean (from proportionality + split-count + cross-group + balance)
- `attribution_variance` — noncomputable def from ProbabilityTheory.variance (Mathlib)
- `attribution_variance_nonneg` — theorem from Mathlib's variance_nonneg
- `attribution_proportional` — backward-compatible theorem wrapper from proportionality_global

The core impossibility theorem (Levels 0-1) uses **none** of these — only the Rashomon property as hypothesis.

## Building

```bash
lake build     # compile everything (~2500 jobs)
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
- Claim "N theorems" without verifying — count with `grep -c "^theorem\|^lemma"` (currently 180)
- Run parallel subagents that both modify the same file (causes build cache corruption)
- Axiomatize quantities that can be defined — prefer definitions with axiomatized bounds (see SpearmanDef.lean pattern)
- Claim empirical results as "proved" or "Lean-verified" — distinguish: **proved** (zero axiom deps), **derived** (from axioms), **argued** (supplement proof only), **empirical** (experiments). The paper's "Proof status transparency" paragraph is the reference.
