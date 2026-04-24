# Handoff: Attribution Impossibility — From Universal Session

**Date:** 2026-04-24
**From:** universal-explanation-impossibility session
**For:** NeurIPS paper + attribution monograph session
**Deadline:** NeurIPS abstract May 4, paper May 6

---

## New Results from the Universal Session

### TinyStories Multi-Scale Circuit Stability (component-level attribution)

10 transformers trained from independent random seeds on TinyStories (real language) at two architectural scales, plus GPT-2 fine-tuned as boundary condition.

**Full results in:** `docs/tinystories-results-reference.json`
**Mean ablation comparison in:** `docs/mean-ablation-results-reference.json`

| Config | Arch | PPL (CV) | Full ρ | G-inv ρ | W-flip | B-flip | Pass |
|--------|------|----------|--------|---------|--------|--------|------|
| A | 4L/4H/d256 | 8.6 (0.7%) | 0.565 | **0.972** | 0.496 | 0.000 | 7/7 |
| B | 6L/8H/d512 | 10.0 (1.0%) | 0.540 | **0.982** | 0.489 | 0.000 | 7/7 |
| C | GPT-2 ft | 18.5 (0.1%) | 0.993 | 0.999 | 0.043 | 0.000 | 4/7 |

Key findings:
- 14/14 pre-registered predictions PASS for from-scratch configs
- Within-layer flip = 0.496 and 0.489 (predicted 0.500)
- Head-vs-MLP = 0.000 across ALL 30 models
- Split-half reliability (0.991, 0.960) >> between-model agreement (0.565, 0.540)
- Heads-only random projection: 100th percentile at both scales
- Permutation test: p < 0.001
- Cohen's d: 5.4 (Config A), 11.9 (Config B)
- All 4 heads in layer 0 appear as #1 across 10 seeds (full S₄)
- Config C (GPT-2 fine-tune): boundary condition confirmed — fine-tuning doesn't create Rashomon
- Config C split-half (0.878) < between-model (0.993) = no genuine diversity

Mean ablation robustness:
- Weight zeroing and mean ablation agree on G-invariant: ρ ≈ 0.97-0.99
- Cross-method per-model ρ ≈ 0.5-0.6 (methods disagree on heads, agree on V^G)
- The disagreement BETWEEN methods is itself an instance of the impossibility

### DASH Renamed

DASH = Diversified Aggregation for Stable Hypotheses (was "of SHAP"). Already updated in the universal repo. Update everywhere in this repo.

### Updated Theorem Counts

- Universal repo: 101 files, 501 theorems, 25 axioms, 0 sorry
- Attribution repo: 58 files, 357 theorems, 6 axioms, 0 sorry
- Ostrowski repo: 21 files, 298 theorems, 10 axioms, 0 sorry
- Total: 1,156 theorems, 0 sorry

### Prior Work Citations to Add

Fisher 2019 (MCR/Rashomon set ranges), D'Amour 2022 (underspecification), Chughtai 2023 (circuit diversity). The NeurIPS paper should cite and distinguish from all three.

---

## Scope Decisions

### Gene Expression (TSPAN8/CEACAM5)
Stays in Nature as Instance 1. NOT a primary result in NeurIPS. One sentence referencing the universal monograph is fine ("the instability extends to biomarker discovery — see [monograph]"). Do NOT include the GO enrichment analysis, 4-dataset table, or two-mode characterization.

### Component-Level Attribution = Attribution
Circuit importance via activation patching IS attribution — attributing importance to internal components. The NeurIPS paper covers attribution at two levels:
1. Input-level (SHAP) — which feature matters
2. Component-level (activation patching) — which circuit matters

These aren't separate results. They're one theorem operating at different granularities. Frame as: "attribution instability is structural at every level of a model."

### What Stays in Nature Only
- Universal theorem proof (cite monograph)
- Gene expression pathway divergence (Nature Instance 1)
- Neuroimaging NARPS reanalysis (Nature Instance 4)
- Causal inference CPDAG (Nature Instance 3)
- 20-impossibility classification by tightness
- Heisenberg uncertainty connection
- Galois analogy / recursive resolution / enrichment stack
- η law as cross-domain prediction
- Uncertainty from Symmetry theorem

### Dual Submission
Nature reports MI results in 15 lines (one of four instances). NeurIPS develops full ML-specific methodology, controls, and analysis over 2-3 pages. Different primary contribution (universal theorem vs ML toolkit), different experiments in depth, different audience, <10% shared content.

---

## NeurIPS Paper Structure (10 pages)

### 1. Introduction (1.5 pages)
Hook: "Train two identical models. Ask each which feature matters most. They disagree. Now look inside: ask which circuit computes the answer. They disagree there too. The instability isn't in the method — it's in the mathematics of attribution itself."

### 2. The Attribution Impossibility (2 pages)
- Theorem for any attribution system with Rashomon
- Input-level: GBDT ratio 1/(1-ρ²), Lasso ∞, neural net conditional
- Component-level: same theorem, S_k^L symmetry
- Tightness + bilemma

### 3. Diagnosis (1.5 pages)
- Coverage conflict diagnostic (7 lines, ρ=0.96)
- Noether counting for components
- SAGE algorithm
- Gaussian flip rate

### 4. Resolution (1 page)
- DASH for input-level (Pareto-optimal, O(M))
- G-invariant projection for component-level (same math)
- Both are orbit averaging / Reynolds operator

### 5. Experiments (3 pages)
Input-level: 77-dataset prevalence, clinical reversal (45%), bimodality, multi-model validation, model-class universality.
Component-level: TinyStories multi-scale (full analysis), controls, mean ablation robustness, GPT-2 boundary.

### 6. Discussion + Conclusion (1 page)

---

## Attribution Monograph Updates Needed

The monograph (`paper/main_definitive.tex`, ~66 pages) needs:

1. **Add TinyStories section** — Full component-level attribution results with all data from this handoff. Per-seed tables, all controls, all statistics.

2. **Add mean ablation comparison** — Method robustness section.

3. **Rename DASH** — "Diversified Aggregation for Stable Hypotheses" everywhere.

4. **Add component-level attribution framing** — Show that activation patching is attribution at a different granularity, governed by the same theorem.

5. **Update related work** — Add Fisher 2019, D'Amour 2022, Chughtai 2023.

6. **Add Code and Data Availability** — GitHub URLs, TinyStories dataset.

7. **Verify all numbers** — Every claim traces to a result file.

---

## Files Provided

| File | Content |
|------|---------|
| `docs/handoff-from-universal-apr24.md` | This file |
| `docs/tinystories-results-reference.json` | Full results (3 configs, all statistics, importance vectors) |
| `docs/mean-ablation-results-reference.json` | Mean ablation vs weight zeroing comparison |
