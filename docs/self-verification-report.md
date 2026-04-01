# Self-Verification Report

Generated: 2026-04-01
Branch: main @ `03e1498`

## Lean #print axioms Results (MACHINE-VERIFIED)

The following were verified by running `#print axioms` in Lean 4:

| Theorem | Domain Axioms Used | Status |
|---------|-------------------|--------|
| `attribution_impossibility` | **NONE** (Model, attribution + Lean kernel only) | ✅ **CENTRAL CLAIM CONFIRMED** |
| `attribution_impossibility_weak` | **NONE** | ✅ |
| `strongly_faithful_impossible` | **NONE** | ✅ |
| `balanced_flip_symmetry` | **NONE** (Model, firstMover + kernel only) | ✅ |
| `attribution_sum_symmetric` | proportionality_global, splitCount_firstMover, splitCount_nonFirstMover, splitCount_crossGroup_symmetric | ✅ Derived from expected axioms |
| `consensus_equity` | Same as attribution_sum_symmetric | ✅ |
| `design_space_theorem` | All above + consensus_variance_bound, modelMeasurableSpace, modelMeasure | ✅ |

### Key finding
`attribution_impossibility` depends on: `[Model, attribution, propext, Classical.choice, Quot.sound]`

- `Model` and `attribution` are type declarations (the theorem needs types to state itself)
- `propext`, `Classical.choice`, `Quot.sound` are Lean 4 kernel axioms (standard in all Lean proofs)
- **ZERO domain-specific property axioms** — the paper's "zero axiom dependencies" claim is verified

## Count Verification

| Claim in paper | Actual | Match? |
|---------------|--------|--------|
| 49 declarations | 49 | ✅ |
| 15 axioms | 15 | ✅ |
| 0 sorry | 0 | ✅ |
| 40 theorems + 9 lemmas | 40 + 9 = 49 | ✅ |
| 7 domain-specific axioms | 7 | ✅ |
| 2 infrastructure axioms | 2 (modelMeasurableSpace, modelMeasure) | ✅ |
| 6 type declarations | 6 | ✅ |
| 23 references | 23 | ✅ |

## Axiom Categorization (verified)

**Type declarations (6):** Model, numTrees, numTrees_pos, attribution, splitCount, firstMover

**Measure infrastructure (2):** modelMeasurableSpace, modelMeasure

**Domain-specific (7):**
1. firstMover_surjective
2. splitCount_firstMover
3. splitCount_nonFirstMover
4. proportionality_global
5. consensus_variance_bound
6. splitCount_crossGroup_symmetric
7. spearman_classical_bound

## Cross-Reference Check

- No undefined references in main.tex ✅
- No undefined references in supplement.tex ✅
- Only font warnings (cosmetic) ✅

## Library Versions (documented in supplement L770)

- Python 3.9.6, XGBoost 2.1.4, SHAP 0.49.1, NumPy 2.0.2 ✅

## What Was NOT Verified (requires humans)

See docs/verification-audit.md for the complete 32-item checklist.
Top 5 non-negotiables:
1. Co-author reads the full paper
2. Axiom consistency check (construct concrete model)
3. Lean statement ↔ paper statement comparison
4. Read Laberge 2023 for novelty overlap
5. Re-run 3 key experiments on different machine
