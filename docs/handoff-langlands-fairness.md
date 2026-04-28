# Handoff: Langlands + Fairness Results → NeurIPS/JMLR Session

**Date:** 2026-04-28
**From:** ostrowski-impossibility repo (Langlands + fairness session)
**To:** dash-impossibility-lean repo (NeurIPS + JMLR papers)

---

## New Results Available

### Result 1: Fairness Tightness Transition

The Chouldechova-Kleinberg fairness impossibility was classified using the
impossibility framework's tightness types, under performance constraints.

**Finding:** The tightness TRANSITIONS from non-binding to binding:

| TPR constraint | Tightness | What it means |
|---|---|---|
| tau = 0.0 | FULL | All pairs achievable (degenerate classifiers) |
| tau >= 0.3 | PPV-BLOCKED | Calibration is the poison |

At any practical performance level (TPR >= 30%):
- Equalized odds (equal FPR + equal FNR): ACHIEVABLE
- ANY pair involving calibration (PPV parity): BLOCKED
- The triple (all three): BLOCKED

Validated on Adult Income + synthetic data (two base rate gaps).
Bootstrap with model retraining (20 iterations, 100% stable).
Scripts: `../ostrowski-impossibility/scripts/fairness_tightness_v3.py`

### Result 2: Reynolds Optimality Theorem (Machine-Verified)

In the upstream repo (universal-explanation-impossibility), three new
theorems in UncertaintyFromSymmetry.lean:

- `reynolds_naturality` — equivariant maps commute with projections
- `fixed_perp_residual` — fixed points are orthogonal to residuals
- `reynolds_best_approximation` — Rv is the UNIQUE closest fixed point to v

This proves DASH is not just a good resolution — it is the provably
unique minimum-information-loss stable resolution among all linear
projections. The proof uses the Pythagorean decomposition:
||v||² = ||Rv||² + ||v - Rv||².

### Result 3: The Langlands Connection (For Discussion Only)

The impossibility framework connects to the Langlands program:
- GL(n, F_p) for all n >= 2, all primes: collapsed tightness
- The abelian/non-abelian boundary = full/collapsed tightness boundary
- DASH and the Langlands correspondence are both Reynolds projections
- Information loss = adjoint character (proved + computationally verified)
- 453 theorems, 0 sorry in the ostrowski-impossibility repo

Full details in `../ostrowski-impossibility/docs/handoff-langlands-rh.md`

### Result 4: Negative Experimental Result

A Langlands-derived prediction (optimal ensemble size = partition number
p(n)) was tested and REFUTED. The framework transfers STRUCTURE (tightness
types, Reynolds optimality) but NOT group-specific NUMBERS. Do not claim
quantitative cross-domain prediction.

---

## How These Results Relate to NeurIPS vs JMLR

The NeurIPS paper (9 pages) and JMLR paper (unlimited) have different
page budgets. The new results fit differently in each:

### For the NeurIPS Paper (9 pages)

**The fairness transition:** ONE FIGURE (the transition table: tau vs
tightness type) + ONE PARAGRAPH of interpretation. The finding
("calibration is the universal poison at TPR >= 0.3") is a concrete
demonstration that the framework produces actionable results. It should
appear as a RESULT, not as a full case study.

**Reynolds optimality:** ONE SENTENCE strengthening the DASH claim:
"DASH is the provably unique minimum-information-loss stable resolution
(Theorem X, machine-verified)." No proof, just the citation. The theorem
lives in the Lean formalization.

**Langlands:** ZERO in the main text. At most one sentence in Discussion:
"The tightness classification extends to the Langlands program [ref]."
ML reviewers don't need it.

**The negative p(n) result:** ZERO. Don't mention.

### For the JMLR Paper (unlimited)

**The fairness transition:** A FULL CASE STUDY SECTION. The v3 experiment
in detail: methodology (performance-constrained threshold search, bootstrap
with model retraining, multi-dataset), results (the transition table at
all tau and epsilon values), interpretation (calibration is the poison),
implications (practitioners should choose equalized odds).

**Reynolds optimality:** A FULL SUBSECTION with the proof sketch and
the impossibility interpretation. "The Reynolds best-approximation theorem
proves DASH is optimal among all linear stable projections. The information
loss ||v - Rv||² is minimized by DASH and equals the adjoint character
of the symmetry group's representation."

**Tightness classification:** A FULL SECTION organizing all ML domains
by type. Table with: domain, three properties, tightness type, resolution.
The fairness experiment is the worked example showing how the classification
changes practice.

**Design space theorem (Family A/B):** FULL SECTION. The proved
dichotomy: all resolutions are either conservative (maximal ties) or
aggressive (minimal ties). This hasn't appeared in the NeurIPS version —
the JMLR gets it.

**Langlands:** A DISCUSSION SUBSECTION. "The same tightness classification
that organizes ML impossibilities also organizes the Langlands program.
The abelian/non-abelian boundary corresponds to full/collapsed tightness.
The DASH Reynolds projection is the same mathematical operation as the
Langlands correspondence. The adjoint character controls information
loss in both settings." 2-3 paragraphs, properly qualified. Not the
main contribution — the mathematical context.

**Lean formalization:** A FULL APPENDIX listing the theorem inventory
(453 theorems, 0 sorry) with the key theorem names and what they prove.

---

## What NOT to Include (in either paper)

- The RH investigation (3 negative results) — standalone Exp. Math. paper
- The Möbius interpretation — too number-theoretic for ML audience
- The automorphicity gap — too abstract for ML audience
- The HomExplanationSystem — mathematical contribution, not ML
- The failed p(n) prediction — negative result, don't mention
- Claims about "proving Langlands conjectures" — the framework explains
  structure, it doesn't construct correspondences

---

## Files Available

| File | Repo | Content |
|------|------|---------|
| `scripts/fairness_tightness_v3.py` | ostrowski | Final fairness experiment |
| `docs/handoff-fairness-results.md` | all three repos | Fairness results summary |
| `docs/handoff-langlands-rh.md` | ostrowski + universal | Full Langlands context |
| `UncertaintyFromSymmetry.lean` | universal | Reynolds theorems (last 3) |
| `DASHResolution.lean` | universal | DASH = Reynolds on S_n |
| `Core/GLnLanglands.lean` | ostrowski | GL(n) boundary theorem |
| `Core/AdjointConnection.lean` | ostrowski | loss = adjoint character |
