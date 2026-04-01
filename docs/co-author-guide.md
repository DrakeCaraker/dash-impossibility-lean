# Co-Author Onboarding Guide

**The Attribution Impossibility: Faithful, Stable, and Complete Feature Rankings Cannot Coexist Under Collinearity**

Welcome, Bryan and David. This document is your entry point into the project. It assumes you are smart researchers who have not been in the development conversation — you can read code if needed, but you should not need to. Everything you need is here.

---

## 1. What This Paper Proves

When you train a machine learning model on correlated features and ask "which feature matters most?", the answer depends on which version of the model you happen to train — not on any fundamental truth about the data. We prove this is not a limitation of any particular attribution method; it is a mathematical impossibility. Specifically: no feature ranking can simultaneously be *faithful* (reflect what the model actually computed), *stable* (give the same answer regardless of which equivalent model you explain), and *complete* (decide every pair of features) when features are correlated. This is the attribution analogue of Arrow's impossibility theorem in social choice theory. We also characterize the full design space of attribution methods under this constraint, and show that DASH (ensemble averaging over independently trained models) is the provably optimal relaxation: it achieves zero unfaithfulness and stability approaching 1 as the ensemble grows. The core impossibility theorem carries a machine-checked proof in Lean 4 with zero domain-specific axioms — it depends only on the Rashomon property, which holds for any model class with multiple near-optimal solutions.

---

## 2. The 60-Second Summary

- **Impossibility.** No single-model attribution method can be faithful, stable, and complete under collinearity. Proved in Lean 4. The proof depends on zero domain-specific axioms — only propext, Classical.choice, and Quot.sound (the standard foundations of Lean).
- **Design space.** Every attribution method falls into one of two families: faithful-and-complete methods (with unfaithfulness rate 1/2 for within-group pairs) or ensemble methods (DASH, with ties). The boundary is sharp and proved.
- **DASH.** Ensemble averaging over balanced sets of independently trained models achieves exact ties (zero unfaithfulness) for collinear feature pairs, with variance decreasing as 1/M. This is the provably optimal resolution.
- **Lean formalization.** 15 Lean files, 49 declarations (40 theorems + 9 lemmas), 15 axioms (6 type infrastructure + 2 measure infrastructure + 7 domain), 0 `sorry`. The three key theorems — `attribution_impossibility`, `attribution_impossibility_weak`, `strongly_faithful_impossible` — all have zero domain-axiom dependencies verified by `#print axioms`.
- **Experiments.** Validated across XGBoost, LightGBM, and CatBoost on 11 datasets, 2 attribution methods (TreeSHAP and permutation importance), with 26 experiment scripts and 26 results files. CV of 0.35–0.66 for within-group feature rankings confirms the instability.
- **Extensions.** Fairness audit impossibility (protected attributes as collinear features), causal discovery extension, LLM attention extension. These are in the supplement and empirically validated.

---

## 3. How to Read This Paper

**Read first (30 minutes):**
- Abstract and Introduction (Section 1): the main claim and its motivation
- Theorem 1 (Section 3): the core impossibility statement — this is the center of gravity for the whole paper
- Corollary 1 and the Design Space Theorem (Section 4): DASH as the resolution
- The "Proof status transparency" paragraph (end of Section 3 or beginning of Section 4): this distinguishes what is *proved*, *derived*, *argued*, and *empirical* — read this carefully, it is load-bearing for the paper's intellectual honesty claims

**Read carefully (1 hour):**
- Section 2 (Definitions): the three properties and what they mean precisely
- Section 5 (Experiments): what was measured, how, and what the results show
- The Lean architecture overview (wherever it appears in the paper or supplement)

**Skim:**
- Section 6 (Extensions): fairness, causal, LLM — these are real contributions but secondary
- The full supplement proof sections for GBDT, Lasso, neural nets — the proofs are correct but you do not need to verify them in detail

**Skip unless assigned:**
- The SymPy verification scripts (`paper/scripts/verify_lemma6_algebra.py` and relatives)
- The figure generation scripts
- The Lean source files (unless you want to verify specific theorems)

---

## 4. What We Need From You

**Critical review tasks:**

1. **Mathematical correctness of the main theorem statement.** Read Theorem 1 and its proof sketch. Does the informal description match the formal statement? Are the three properties (faithfulness, stability, completeness) defined in a way that corresponds to what practitioners actually want? Flag any gap between the informal claim and the formal proof.

2. **Axiom system review.** Read the axiom inventory in CLAUDE.md (reproduced below). The 7 domain axioms are mathematical idealizations of GBDT behavior. Do they accurately describe gradient boosting under Gaussian data? The most important are `proportionality_global` (uniform proportionality constant across models) and `splitCount_firstMover`/`splitCount_nonFirstMover` (the Gaussian conditioning argument). Flag any axiom you think is empirically implausible or formally too strong.

3. **Experiment interpretation.** Read the experimental results section. Does the claim that "CV = 0.35–0.66 confirms instability" hold up? Is the comparison between single-model and DASH attributions fair? Is the baseline selection appropriate?

4. **Related work coverage.** Read the related work section. Are there important papers we are missing? Specifically: Bilodeau 2024 (limits of post-hoc explanations), Laberge 2023 (perturbation stability), Rudin 2024 (interpretable models), Huang 2024 (collinear SHAP). These should be compared. Flag any claim about prior work that seems overreaching.

5. **Proof status transparency.** Verify that every claim in the paper is correctly labeled as proved, derived, argued, or empirical. A "proved" claim should trace to a Lean theorem with zero domain-axiom dependencies. A "derived" claim traces to Lean theorems that use domain axioms. An "argued" claim has a supplement proof. An "empirical" claim has an experiment. Flag anything mislabeled.

**What to flag:**
- Any claim that does not follow from the stated axioms
- Any axiom you consider empirically implausible
- Any place where "proved" language is used for something that is only argued or empirical
- Any missing citation for a closely related result
- Any inconsistency between the paper's stated theorem counts and what is in the code

---

## 5. Key Decisions Needing Your Input

**Venue choice:**
- Primary: NeurIPS 2026 (abstract May 4, paper May 6). This is a tight timeline.
- Secondary: JMLR (no deadline). This would allow a more thorough treatment but delay publication by 12–18 months.
- Question for co-authors: Do you think NeurIPS is the right venue, or should we target a venue more receptive to formal methods + ML theory? ICML and ICLR are also possibilities for a May submission if there are late-breaking calls.

**Supplement scope:**
- The supplement is currently 65 pages. This is long. We need to decide what belongs in the main text versus supplement.
- Proposal: move the full Lean architecture description and axiom justifications to the supplement, keeping the main text focused on the mathematical results and experiments.
- Question: what level of Lean detail is appropriate for the main text at NeurIPS?

**Author contributions:**
- A "CRediT" statement is needed. Draft: Drake Caraker — conceptualization, formal methods, Lean formalization, software; Bryan Arnold — [your contribution]; David Rhoads — [your contribution].
- Please fill in your contributions and flag any concern about the ordering.

**The "zero axiom" claim:**
- The paper's headline claim is that `attribution_impossibility` uses zero domain axioms. This is verified by `#print axioms` in Lean. However, it still uses standard logical axioms (propext, Classical.choice, Quot.sound). Make sure you are comfortable with how this is described in the paper — it should say "zero domain-specific axioms" not "zero axioms".

---

## 6. Verification Checklist

These are the 10 most important things a human should verify before submission. Detailed instructions for each are in `docs/verification-audit.md`.

**[V1] Axiom empirical plausibility (2 hours, Bryan)**
Read the 7 domain axioms in `DASHImpossibility/Defs.lean`. For each, verify that the mathematical property it encodes is a reasonable idealization of the described behavior. The most important are `proportionality_global` and the two `splitCount` axioms. Red flag: an axiom that is false for any standard GBDT implementation.

**[V2] Theorem 1 informal-formal match (1 hour, Bryan or David)**
Read the informal statement of Theorem 1 in the paper, then read the formal Lean statement of `attribution_impossibility` in `DASHImpossibility/Trilemma.lean`. Do they match? Is the paper's informal description a faithful summary of the formal statement? Red flag: the informal statement is stronger than what the formal proof establishes.

**[V3] Experiment reproducibility (3 hours, David)**
Pick 2–3 of the 26 experiment scripts in `paper/scripts/` and run them. Do they reproduce the reported results? Red flag: results differ materially from what the paper reports.

**[V4] Related work completeness (1 hour, Bryan)**
Search Google Scholar for: "feature attribution stability", "SHAP collinearity", "explanation instability". Are there papers published in 2024–2026 that we are missing that make similar claims? Red flag: a concurrent paper that proves a closely related theorem.

**[V5] Proof status transparency (30 min, David)**
Read the "Proof status transparency" paragraph in the paper. Then pick 5 claims from the body of the paper labeled "proved" and verify they trace to Lean theorems without `sorry`. Run: `grep -r "sorry" DASHImpossibility/*.lean`. Red flag: any `sorry` found.

**[V6] Axiom count consistency (10 min, anyone)**
Run: `grep -c "^axiom" DASHImpossibility/*.lean` and compare to what the paper claims (15 total). Run: `grep -c "^theorem\|^lemma" DASHImpossibility/*.lean` and compare to the paper's claimed 49. Red flag: any discrepancy.

**[V7] DASH experiment validity (1 hour, David)**
Verify that the DASH experiment (ensemble averaging) is implemented correctly. Is the ensemble truly balanced (equal first-mover counts)? Is the Spearman correlation computed correctly? Red flag: systematic bias in the ensemble construction.

**[V8] Extensions validity (1 hour, Bryan)**
Read Section 6 (extensions). Are the claims about fairness audits, causal discovery, and LLM attention correctly described? Are the limitations clearly stated? Red flag: extension claims that are not actually supported by the theoretical framework.

**[V9] Bibliography completeness (30 min, anyone)**
Read the 23 references. Are the citations accurate? Are important work on SHAP, feature attribution, and impossibility results included? Check: Lundberg & Lee 2017, Shapley 1953, Arrow 1951. Red flag: a citation that does not support the claim it is attached to.

**[V10] NeurIPS format compliance (30 min, Drake)**
Before submission: replace `neurips_2026.sty` placeholder with the official style file. Verify page count (main text ≤ 9 pages plus references and checklist). Verify all author information is complete. Red flag: page limit exceeded or author fields blank.

---

## 7. Timeline

| Date | Milestone |
|------|-----------|
| April 1–7 | Co-authors read paper, flag issues |
| April 8–14 | Address flagged issues, finalize theorem counts |
| April 15–21 | Co-author verification items V1–V5 |
| April 22–28 | Final pass, author contributions, bibliography |
| April 30 | arXiv preprint posted |
| May 4 | NeurIPS 2026 abstract deadline |
| May 6 | NeurIPS 2026 paper deadline |
| May–June | JMLR submission (expanded version) |

**Critical path:** V1 (axiom plausibility) and V2 (informal-formal match) are the most important items. If either reveals a problem, we need to know by April 14 to have time to fix it.

---

## Appendix: Axiom Inventory (for reference)

| Axiom | Type | What it says |
|-------|------|--------------|
| `Model` | Type decl | Abstract trained model type |
| `numTrees`, `numTrees_pos` | Type decl | Number of boosting rounds |
| `attribution` | Type decl | Attribution function φ_j(f) |
| `splitCount`, `firstMover` | Type decl | Split counts and first-mover |
| `firstMover_surjective` | Domain | Every feature can be first-mover |
| `splitCount_firstMover` | Domain | First-mover split count = T/(2-ρ²) |
| `splitCount_nonFirstMover` | Domain | Non-first-mover split count = (1-ρ²)T/(2-ρ²) |
| `proportionality_global` | Domain | φ_j(f) = c·n_j(f) with uniform c |
| `splitCount_crossGroup_symmetric` | Domain | Cross-group split counts equal |
| `modelMeasurableSpace`, `modelMeasure` | Measure infra | Probability space on Model |
| `consensus_variance_bound` | Domain | Var(consensus) = Var(φ)/M |
| `spearman_classical_bound` | Domain | Spearman ≤ 1 - m³/P³ |
