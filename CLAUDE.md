# DASH Impossibility — Lean 4 Formalization

Lean 4 formalization of the impossibility theorem from `paper/impossibility.tex` in the [dash-shap](https://github.com/DrakeCaraker/dash-shap) repo. Target venue: NeurIPS or AISTATS (Paper 3 in the 5-paper research program).

## What This Proves

No single sequential gradient-boosted model can simultaneously achieve stable AND equitable feature attributions under feature collinearity. DASH (ensemble averaging) circumvents this by breaking the sequential dependency.

## Proof Structure

```
Axiom 1: First-mover ∈ group        (DGP symmetry)
Axiom 2: n_{j1} = T/(2-ρ²)          (Gaussian conditioning)
Axiom 3: n_{jq} = (1-ρ²)T/(2-ρ²)   (residual signal)
Axiom 4: φ_j ∝ n_j                  (Assumption 7: uniform contribution)
    ↓
Lemma: split gap ≥ ½ρ²T             (algebra — SymPy verified)
    ↓
Lemma: attribution ratio = 1/(1-ρ²) (algebra — SymPy verified)
    ↓
Theorem 10(i): ratio → ∞ as ρ → 1   (real analysis limit)
Theorem 10(ii): Spearman ≤ 1-Ω(1/L³) (rank permutation argument)
    ↓
Corollary 11(a): E[φ̄_j] = E[φ̄_k]   (linearity + symmetry)
Corollary 11(b): Var(Φ̄_ℓ) = O(1/M)  (LLN — mathlib has this)
Corollary 11(c): Pr[same order] = ½  (normal symmetry)
```

## Approach: Axiomatic

We axiomatize gradient boosting and TreeSHAP at the level of their mathematical properties, not their algorithmic implementation. The axioms are justified by:
1. The Gaussian conditioning argument in the paper
2. SymPy verification of all algebra (`dash-shap/paper/proofs/verify_lemma6_algebra.py`)
3. Symmetry of the DGP

This means we prove: **IF gradient boosting has these properties (axioms), THEN the impossibility holds.** The axioms themselves are justified by the paper's classical proofs.

## Mathlib Availability

| Primitive | Available? |
|---|---|
| Strong LLN | YES — `Mathlib.Probability.StrongLaw` |
| Variance, Expectation | YES — `Mathlib.Probability.Variance` |
| Independence | YES — `Mathlib.Probability.Independence` |
| Real analysis (limits) | YES — `Mathlib.Analysis.*` |
| Finsets, partitions | YES — `Mathlib.Data.Finset` |
| Central Limit Theorem | **NO** — not in mathlib yet |
| Multivariate Gaussian | **NO** — only univariate |
| Spearman correlation | **NO** — must define |
| Gradient boosting | **NO** — axiomatized |
| TreeSHAP | **NO** — axiomatized |

## File Structure

```
DASHImpossibility/
  Defs.lean       — Feature space, axioms, stability/equity defs, consensus
  Basic.lean      — Imports (will hold lemmas)
  SplitGap.lean   — TODO: Lemma: gap ≥ ½ρ²T
  Ratio.lean      — TODO: Lemma: ratio = 1/(1-ρ²), limit → ∞
  Impossibility.lean — TODO: Theorem 10
  Corollary.lean  — TODO: Corollary 11 (a,b,c)
```

## Building

```bash
lake update    # fetch mathlib cache (~8000 files, first time only)
lake build     # compile everything
```

## Key Decision: Roadmap Discrepancy

The dash-shap ROADMAP describes Paper 3 as proving stability + accuracy + **completeness** can't coexist (Arrow-type). The current `impossibility.tex` proves stability + **equity** tradeoff. The current formalization matches `impossibility.tex`. If Paper 3 evolves, the axioms and definitions may need updating, but the proof techniques transfer.

## Related Files in dash-shap

- `paper/impossibility.tex` — the LaTeX proof being formalized
- `paper/proofs/verify_lemma6_algebra.py` — SymPy verification (all pass)
- `paper/proofs/impossibility.lean` — UlamAI probe output (shell only)
- `paper/proofs/artifacts/segments.json` — parsed proof structure
- `docs/private/roadmap.md` — 5-paper research program

## Do NOT

- Use `sorry` without a `-- TODO:` comment explaining what's needed
- Change axioms without re-running the SymPy verification
- Add `autoImplicit true` — all variables must be explicit
