# Naming Update: Explanation Capacity Terminology

**Date:** 2026-04-29
**From:** universal-explanation-impossibility session
**For:** dash-impossibility-lean (NeurIPS attribution paper + monograph)

## The Change

The universal framework has adopted a consistent naming convention modelled on Shannon's information theory. The attribution paper and monograph should adopt the same names.

## Terminology Table

| Concept | Old Name | New Name | Shannon Parallel |
|---------|----------|----------|-----------------|
| dim(V^G) | "the invariant subspace dimension" | **Explanation capacity** (C) | Channel capacity |
| η = 1 − C/dim(V) | "instability rate" / "the η formula" | **Explanation loss rate** | — |
| The η prediction (R²=0.957) | "the η law" / "the universal η law" | **Explanation Capacity Law** | Shannon's theorem |
| unfaith₁ + unfaith₂ ≥ Δ−δ | "the approximate bilemma" | **Explanation uncertainty relation** | Heisenberg's relation |
| Orbit average / DASH / Reynolds | various | Also: **the explanation code** | Optimal channel code |
| Coverage conflict | "coverage conflict" | Also: **explanation conflict** | Noise |
| No neutral element → add one | "enrichment" | Keep, but also: **capacity expansion** | Alphabet extension |
| M models for ε-stability | "convergence prescription" | Also: **block length** | Block length |
| DASH | Diversified Aggregation for Stable Hypotheses | Keep (already renamed) | — |

## What to Update in This Repo

### NeurIPS paper (paper/main.tex)
1. Replace "approximate bilemma" with "explanation uncertainty relation" wherever it appears as a concept name (keep "bilemma" when referring to the theorem itself)
2. Add "explanation capacity" (C = dim V^G) where the η law is introduced
3. Add "the Explanation Capacity Law" as the name for the η prediction
4. Add "explanation code" as an alias for DASH in the Discussion

### Attribution monograph (paper/main_definitive.tex)
1. Same changes as NeurIPS paper
2. Add the terminology table from the universal monograph (adapted for attribution-specific content)
3. Rename the "approximate bilemma" section header to "Explanation Uncertainty Relation"

### References
The universal monograph defines these terms. Cite as:
"Caraker et al. (2026). The Limits of Explanation. arXiv preprint."

## Do NOT Rename
- **DASH** — already renamed to "Diversified Aggregation for Stable Hypotheses"
- **bilemma** — the theorem name stays. "Explanation uncertainty relation" is for the quantitative bound.
- **tightness** — precise, no better alternative
- **Rashomon** — Breiman's term, established
