# Publication Plan

**Last updated:** 2026-04-20
**Status:** NeurIPS submission-ready. All other papers staged.

## Timeline

| Date | Action | Paper | Venue |
|------|--------|-------|-------|
| **May 4** | Submit abstract | Attribution Impossibility | NeurIPS 2026 |
| **May 6** | Submit paper + supplement | Attribution Impossibility | NeurIPS 2026 |
| May–June | Submit | Ostrowski Impossibility | Foundations of Physics |
| May–June | Post updated preprint | Monograph | arXiv |
| **September** | NeurIPS decision | — | — |
| **October+** | Submit (if NeurIPS decision known) | Universal Impossibility | Nature |
| **After NeurIPS** | Submit (if accepted, cite NeurIPS; if rejected, standalone) | Attribution Impossibility | JMLR |

## Dual Submission Rules

### Hard constraints
- **NeurIPS + Nature:** Safe. Different venues, different timelines, different lead contributions. Nature submitted AFTER NeurIPS decision (September). No simultaneous review.
- **NeurIPS + JMLR:** NEVER simultaneously. JMLR is the expanded NeurIPS paper. Submit JMLR only after NeurIPS decision.
- **NeurIPS + FoP:** Safe. Zero content overlap (different theorem, different domain).
- **NeurIPS + arXiv:** Safe. NeurIPS explicitly allows preprints.

### The gene expression overlap
Both NeurIPS and Nature present the TSPAN8/CEA finding. Risk: **LOW**.
- NeurIPS: 1 paragraph + 1 figure (ranking lottery extension)
- Nature: 1.5 pages with full pathway analysis (Instance 1)
- Different titles, abstracts, lead contributions, framing
- Never under review simultaneously
- Standard practice for conference → journal expansion

### Deanonymization risk
The Lean repo (github.com/DrakeCaraker/dash-impossibility-lean) is public. The Zenodo DOI links to it with author names. If a NeurIPS reviewer searches for the theorem title, they may find the repo and preprint. This is:
- **Allowed** by NeurIPS policy (preprints permitted)
- **Common** (most NeurIPS papers have arXiv preprints)
- **Unavoidable** (the repo must be public for the Zenodo DOI)

## What's in Each Paper (Non-Overlapping Contributions)

### NeurIPS (9pp + 81pp supplement) — Attribution Impossibility
**Distinctive:** Diagnostic pipeline (coverage conflict, minority fraction, variance budget), ranking lottery (24/35 distinct on Breast Cancer), GBDT ratio 1/(1-ρ²), 77-dataset prevalence, DASH binary/continuous optimality, clinical reversal (45% German Credit, 4×3 ablation), subsample sensitivity, cross-implementation (XGBoost/LightGBM/RF), SNR calibration, Z-test diagnostic, gene expression (condensed), MI (one sentence)

### Nature (~10pp) — Universal Explanation Impossibility
**Distinctive:** Abstract ExplanationSystem framework, tightness classification (2×2 table), compatibility complex, direction theorem, 4 domain instances (genomics with full pathway analysis, AI safety with MI v2 + controls, causal discovery with CPDAG, clinical), η law, enrichment resolution via Hunt-Stein

### FoP (27pp) — Ostrowski Impossibility
**Distinctive:** Ostrowski bridge to Mathlib, Freund-Witten three-fold zeta symmetry, enrichment stack (recursive, unbounded depth), adelic resolution uniqueness, physics Levels 0-3

### JMLR (59pp) — Attribution Impossibility (expanded)
**Distinctive relative to NeurIPS:** SBD (3 instances), conditional SHAP impossibility, fairness audit impossibility, FIM-to-Rashomon bridge, query complexity bounds, 11 additional datasets, depth×ρ tables, Spearman algebra, DASH information loss, compressed sensing connection, topological analysis, regulatory mapping

### arXiv Monograph (77pp) — Definitive Reference
Everything. Cited by all other papers for extended proofs and full experimental details.

## Contingency Plans

### If NeurIPS rejects
- Submit JMLR (59pp) standalone — no dependency on NeurIPS
- Alternatively: submit to ICML 2027 (different version, with mech interp experiment if completed)
- The monograph on arXiv establishes priority regardless

### If NeurIPS accepts
- JMLR cites the NeurIPS paper and expands with 50 pages of additional content
- Nature cites the NeurIPS paper in Instance 2 (Feature Attribution)
- All papers benefit from the NeurIPS imprimatur

### If Nature rejects
- Submit to PNAS or Science Advances (the universal framework fits both)
- Alternatively: expand into a Proceedings of the IEEE survey

### If arXiv preprint stays on hold
- Submit a new version (with 6 axioms, 357 theorems) to replace the on-hold version
- Or email moderation@arxiv.org with the submission ID

## Current Paper State

| Paper | File | Pages | Status | Counts verified |
|-------|------|-------|--------|----------------|
| NeurIPS main | paper/main.tex | 9 | **Submission-ready** | 357/6/0 ✓ |
| NeurIPS supplement | paper/supplement.tex | 81 | **Submission-ready** | Counter fixed ✓ |
| JMLR | paper/main_jmlr.tex | 59 | Ready (submit after NeurIPS) | 357/6/0 ✓ |
| Monograph | paper/main_definitive.tex | 77 | Exhaustive | 357/6/0 ✓ |
| FoP | ostrowski repo | 27 | Submission-ready | 167/10/0 ✓ |
| Nature | universal repo | Draft | Needs rewrite with new results | — |

## Verification Checklist (Run Before Any Submission)

```bash
cd /Users/drake.caraker/ds_projects/dash-impossibility-lean
grep -c "^theorem\|^lemma" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "theorems+lemmas:", s}'
grep -c "^axiom" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "axioms:", s}'
grep -rc "sorry" DASHImpossibility/*.lean | awk -F: '{s+=$2} END {print "sorry:", s}'
ls DASHImpossibility/*.lean | wc -l | awk '{print "files:", $1}'
```

Expected: 357 theorems, 6 axioms, 0 sorry, 58 files.
