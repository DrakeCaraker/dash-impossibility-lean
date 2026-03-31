# Adversarial Full-Stack Audit: The Attribution Impossibility

> Audit date: 2026-03-31
> Goal: Find every error, overclaim, logical gap, and weakness that would
> prevent best paper at NeurIPS 2026 or acceptance at Nature Machine Intelligence.
> Agent results for Audits 1, 3, 5 pending — will be integrated when available.

---

## Audit 2: Mathematical Correctness

### Finding 2.1: F3 ε₀ algebra has intermediate error [MEDIUM]

**Location:** supplement.tex:672-675

**The claim:** "K₃/6 · (ε/λ₋)^{3/2} ≤ K₃/6 · λ₋^{9/2}/(K₃³ · λ₋^{3/2}) = λ₋³/(6K₃²)"

**The problem:** Substituting ε₀ = 2λ₋³/K₃² into (ε/λ₋)^{3/2} gives (2λ₋²/K₃²)^{3/2} = 2^{3/2} · λ₋³/K₃³. The paper drops the factor of 2^{3/2} ≈ 2.83 in the intermediate step. The final step claims λ₋³/(6K₃²) ≤ ε/2 = λ₋³/K₃², which requires 1/6 ≤ 1 (true). But the ACTUAL intermediate value is 2^{3/2}·λ₋³/(6K₃²), and the ACTUAL check is 2^{3/2}/6 ≈ 0.47 ≤ 1 (also true).

**Impact:** The conclusion is correct — ε₀ = 2λ₋³/K₃² does control the cubic remainder. But the algebra as written is wrong. A careful reviewer would flag this.

**Fix:** Replace the intermediate step with the correct calculation, or just note "a direct computation shows K₃/6 · (ε₀/λ₋)^{3/2} = 2^{3/2}λ₋³/(6K₃²) < λ₋³/K₃² = ε₀/2."

### Finding 2.2: Berry-Esseen applied to n=1 is non-standard [MEDIUM]

**Location:** supplement.tex:~940-975 (F1 proof Part I)

**The claim:** Berry-Esseen bound gives |ε_BE| ≤ C₀γ_{jk}/σ_{jk}³ for the flip rate approximation.

**The issue:** The Berry-Esseen theorem is about the CLT for sums of n i.i.d. variables. For n=1, there is no averaging — the bound is just the distance between the CDF of D = φ_j - φ_k and the Gaussian CDF. This bound can be vacuous (>1) if D is far from Gaussian.

**The paper acknowledges this** (line ~970: "for n=1, the bound is C₀γ/σ³ ... only informative when D is approximately Gaussian") and provides Shapiro-Wilk evidence. So it's not wrong, just unusual.

**Impact:** A pedantic reviewer could object to calling this "Berry-Esseen" when it's really just the trivial bound on CDF distance. The substance is correct.

**Fix:** Add a footnote: "For n=1, the Berry-Esseen bound reduces to a bound on the CDF distance between D and a Gaussian, which is informative only when D is well-approximated by a normal distribution."

### Finding 2.3: Design Space Theorem — S definition mismatch [CRITICAL]

**Location:** supplement.tex:1586-1587 (Definition) vs 1609 (Family A bound)

**The problem:** S is DEFINED as "between-group stability — the probability that the consensus preserves the true between-group ordering." But Family A's bound "S ≤ 1 - Ω(m³/P³)" comes from the **Spearman correlation** of the full ranking (main text Theorem 2), which includes within-group pair reshuffling. These are DIFFERENT metrics.

**Why this matters:** A majority-vote-of-M-models method is COMPLETE (ranks all pairs), has U = 1/2 for within-group pairs (by symmetry), and has high BETWEEN-GROUP stability (majority vote stabilizes with M). Its BETWEEN-GROUP S approaches 1, but its FULL-RANKING Spearman remains bounded by 1 - m³/P³ because within-group pairs are still randomly ordered.

If S means between-group stability (as defined), the Family A upper bound is WRONG — complete methods can achieve high between-group S with M>1 models while keeping U=1/2. If S means full-ranking Spearman (as needed for the bound), the definition is wrong.

**Impact:** This is the biggest mathematical issue in the paper. The Design Space Theorem's characterization of Family A is either wrong (if S = between-group) or misleadingly defined (if S = Spearman).

**Fix:** Either:
(a) Redefine S as full-ranking stability (expected Spearman) — then Family A's bound holds, but the theorem is about Spearman, not about between-group ordering preservation.
(b) Derive the Family A between-group S bound separately — show that even between-group stability is limited for complete methods (this is actually true: the within-group instability DOES propagate to between-group through rank correlations with nearby-ranked between-group features).
(c) State the theorem with S = full-ranking Spearman and note that between-group S is separately characterized.

### Finding 2.4: Design Space Theorem Step 3 — majority vote not covered [HIGH]

**Location:** supplement.tex:1675-1700 (Step 3 proof)

**The problem:** Step 3 considers 3 cases but doesn't cover the majority-vote method:
- Case 1: faithful to individual models → U = 1/2 ✓
- Case 2: not faithful to some model → optimal unfaithful assigns ties ✓
- Case 3: aggregates M>1 models, complete → U > 0 ✓

The majority vote IS covered by Case 3 (aggregates M>1, complete, U > 0). The claim "any tie-breaking rule disagrees with a fraction of models" is correct for the majority vote (U = 1/2 for symmetric within-group pairs). So the majority vote IS in Family A by its (S, U, C) values.

**BUT:** The Family A definition says S ≤ 1 - m³/P³. If S means between-group stability, the majority vote has S > 1 - m³/P³ for large M (see Finding 2.3). If S means Spearman, the majority vote HAS S ≤ 1 - m³/P³ because within-group randomness dominates.

**Impact:** This is a consequence of Finding 2.3. If Finding 2.3 is fixed (S = Spearman), this finding is resolved.

### Finding 2.5: F1 Proposition S3 first-stump bound — ε₀ arithmetic [LOW]

**Location:** supplement.tex:~160-170 (first-stump proposition)

**The claim:** α₁(n) = (2/π)(1 - (π-2)/n + O(n⁻²))

**Check:** The expansion is: α(δ) = 2/π · (1 - δ²(π-2)/σ² + O(δ⁴)). With E[δ²] = πσ²/(2n): E[α₁] = 2/π · (1 - (π-2)·π/(2n) + ...) = 2/π · (1 - π(π-2)/(2n)).

The paper writes "(1 - (π-2)/n)" but the correct expression is "(1 - π(π-2)/(2n))". Since π(π-2)/(2) ≈ 1.80, versus (π-2) ≈ 1.14, the paper understates the correction by a factor of ~1.6.

**Impact:** The conclusion ("negligible for n=2000") is unchanged — both give corrections of O(0.001). But the formula is wrong.

**Fix:** Replace (π-2)/n with π(π-2)/(2n).

---

## Audit 4: Overclaims

### Finding 4.1: "first formally verified impossibility in XAI" [MEDIUM]

**Location:** main.tex:57, 86

**The claim:** "constituting the first formally verified impossibility result in explainable AI"

**Evidence:** We have no evidence anyone else has done this. Line 86 says "to our knowledge" — the abstract line 57 does NOT have this qualifier.

**Fix:** Add "to our knowledge" to line 57, consistent with line 86.

### Finding 4.2: "33 substantive theorems" — classification needed [MEDIUM]

**Location:** CLAUDE.md, main text

**The claim:** "33 substantive theorems"

**The question:** Are all 33 genuinely substantive? Candidates for "trivial":
- `consensus_variance_rate`: directly applies an axiom (1 line: `exact consensus_variance_bound`)
- `consensus_variance_nonneg`: `div_nonneg` of nonneg axiom
- `infeasible_faithful_stable_complete`: direct call to `attribution_impossibility`
- `dash_variance_decreases`: direct call to `consensus_variance_rate`

At least 4 of the 33 are essentially wrapper theorems that call another theorem in 1 line. A reasonable count: ~29 substantive + 4 trivial wrappers.

**Fix:** Either say "29 substantive theorems" (excluding wrappers) or "33 theorems including convenience lemmas."

### Finding 4.3: "DASH is provably optimal" [MEDIUM]

**Location:** main.tex §7, supplement F2

**The claim:** "DASH(M) achieves this and is Pareto-optimal"

**What the evidence supports:** DASH is optimal among unbiased estimators of E[φ_j] for i.i.d. models with finite variance satisfying Cramér-Rao regularity. Not optimal among ALL methods (biased methods, nonlinear methods, methods that use side information).

**Impact:** The claim is correct within the stated scope but the main text §7 doesn't repeat the scope restriction.

**Fix:** Add "among unbiased aggregations" to the main text.

### Finding 4.4: "design space collapses to a single axis" [HIGH]

**Location:** main.tex:438, supplement Design Space Theorem

**The claim:** The design space collapses to ensemble size M.

**The problem:** This is true IF the only choice is between Family A and Family B. But there are intermediate methods (e.g., partial completion: rank some within-group pairs where the evidence is strong, tie the rest). The design space is actually 2D: (M, completion threshold). The "single axis" claim holds only when the practitioner has already chosen either "full completion" or "no within-group completion."

**Fix:** Acknowledge the completion threshold as a second dimension, or explicitly state the collapse is among methods that are either fully complete or produce full ties.

### Finding 4.5: The Arrow parallel [LOW]

**Location:** main.tex:200-205, 444-446

**The claim:** Structural parallel to Arrow's impossibility

**Assessment:** The parallel IS genuine: both are impossibility theorems for aggregating conflicting orderings, both have the same structure (3 desiderata, prove mutual incompatibility), both are resolved by relaxing completeness. The path convergence having no Arrow analogue is an honest distinction.

**However:** Arrow's theorem is about aggregating PREFERENCES of different agents. Our theorem is about the INSTABILITY of a single quantity (feature importance) across model instances. The "voters" in our case are not agents with preferences but random draws from a distribution. This is a weaker parallel than the paper suggests — Arrow's impossibility is about preference aggregation (a design problem), ours is about statistical estimation (a measurement problem).

**Fix:** Note the distinction: "The structural parallel holds at the formal level; the substantive interpretation differs: Arrow's is about aggregating heterogeneous preferences, ours about aggregating noisy measurements of the same underlying quantity."

---

## Audit 6: Nature Machine Intelligence Lens

### Finding 6.1: Accessibility [HIGH for NMI]

**The paper is written for ML researchers**, not for the broad NMI audience (biologists, physicists, policymakers). Specific issues:
- The abstract mentions "SHAP values," "Rashomon property," "collinearity" — jargon unfamiliar outside ML
- The Setup section (§2) assumes knowledge of gradient boosting, split counts, first-mover effects
- No motivating example in the introduction (e.g., "imagine a doctor using an AI that blames blood pressure for a prediction on Monday and cholesterol on Tuesday")

**Fix for NMI:** Rewrite the introduction with a concrete motivating scenario. Move technical setup to methods. Lead with the impossibility result and its implications, not the machinery.

### Finding 6.2: EU AI Act framing [MEDIUM]

**Location:** main.tex:461-464, supplement:~1360

**Assessment:** The EU AI Act reference (Art. 13(3)(b)(ii)) is CORRECT and SUBSTANTIVE. The paper correctly identifies attribution instability as a "known and foreseeable circumstance." The regulatory response template for ties (supplement) is excellent.

**For NMI:** The regulatory angle is the strongest hook for NMI. It should be expanded, not just a paragraph. A standalone "Implications for AI Regulation" section would strengthen an NMI submission.

### Finding 6.3: What a Nature editor would cut [MEDIUM]

The current 10+29 pages would need to become ~4000 words + methods + supplement for NMI. The editor would:
- Cut the entire Setup section (move to methods)
- Cut the formal axiom system
- Cut the Lean formalization details (mention in one sentence)
- Keep: impossibility theorem, the "two families" result, the F1 diagnostic, the financial case study, the regulatory implications
- Expand: motivating example, broader implications, practitioner guidance

---

## Audit 7: The "Foundational" Test

### Finding 7.1: What is our unique reusable technique? [CRITICAL for "foundational"]

Arrow introduced the ultrafilter lemma. Chouldechova introduced the calibration-balance quantitative tradeoff curve. What do WE introduce?

**Candidates:**
1. **The Rashomon-to-impossibility reduction**: If a model class has the Rashomon property, then faithfulness + stability + completeness is impossible. But the Rashomon property was articulated by Rudin (2024) and Fisher et al. (2019). Our contribution is connecting it to impossibility, but the connection is a 4-line proof.

2. **The IterativeOptimizer abstraction**: Dominance + surjectivity → Rashomon. This IS original and could be reused for other impossibility results. But it's a definition, not a technique.

3. **The Design Space Theorem**: Two families, Pareto frontier, M-axis collapse. This IS structural and could be reused for other aggregation problems. But it has the S-definition issue (Finding 2.3).

4. **The F1 diagnostic**: Z_jk test statistic for attribution instability. This IS practical and will be adopted. But it's a standard z-test, not a new technique.

**Honest assessment:** Our unique contribution is the FRAMEWORK — connecting Rashomon to impossibility to design space to optimal resolution. The individual pieces use standard techniques. The novelty is in the ASSEMBLY, not in any single component.

**Is this "foundational"?** It depends on the definition. If foundational means "introduces a technique others reuse" (Arrow, Nash), then NO — we don't introduce a new technique. If foundational means "establishes a structural understanding that changes how people think about a problem" (Chouldechova, our closest comparison), then POTENTIALLY YES — the Design Space Theorem, if correctly stated, does characterize what's achievable.

### Finding 7.2: Comparison to Arrow [HIGH]

| Dimension | Arrow | Us |
|-----------|-------|----|
| Proof technique | Ultrafilter (new) | Contradiction from Rashomon (standard) |
| Quantitative tradeoff | None (pure impossibility) | Yes (ratio, variance) |
| Resolution | Partial orders, Borda | DASH (ensemble averaging) |
| Formal verification | Nipkow (2009, Isabelle) | This paper (Lean) |
| Design space | 3 distinct relaxation paths | 2 converging paths |
| Practical impact | Changed voting theory | TBD |

**Arrow's advantage:** Novel proof technique, 75+ years of impact.
**Our advantage:** Quantitative bounds, constructive resolution, formal verification, practical diagnostic.

### Finding 7.3: Comparison to Chouldechova [MEDIUM]

| Dimension | Chouldechova | Us |
|-----------|-------------|----|
| Core result | Calibration + balance impossible | Faithfulness + stability + completeness impossible |
| Quantitative | Clean tradeoff curve (equation) | Ratio 1/(1-αρ²), variance O(1/M) |
| Resolution | Choose which to sacrifice | DASH (sacrifice completeness) |
| Audience | Fairness community (large) | XAI community (large) |
| Timing | 2017 (fairness debate peak) | 2026 (XAI regulation rising) |

**Chouldechova's advantage:** Single clean equation (calibration = f(base rate, FPR, FNR)). Immediate policy impact. Published in a medical informatics journal with broad audience.
**Our advantage:** Constructive resolution (DASH), formal verification, design space characterization, practical diagnostic.

**Is our result on the same level?** In mathematical depth: comparable (both are applications of pigeonhole/symmetry arguments). In immediate impact: Chouldechova had better timing and a cleaner one-equation result. In long-term potential: our design space characterization is structurally richer.

---

## Vet Round 1: Factual

- Finding 2.1 (ε₀ algebra): Verified computationally. The factor of 2^{3/2} IS dropped. Confirmed.
- Finding 2.3 (S definition): Verified by reading the supplement. S IS defined as "between-group stability" and the bound IS from the Spearman correlation. These ARE different metrics.
- Finding 2.5 (α₁ formula): Need to verify. The expansion step needs careful checking.
- Finding 4.2 (33 vs 29): Need agent results to confirm which theorems are trivial wrappers.

## Vet Round 2: Am I overclaiming about problems?

- Finding 2.3 (S definition mismatch): Am I making this bigger than it is? Let me reconsider. For the MAIN TEXT §7, S is described as "stability S" without specifying between-group or full-ranking. In the supplement, S is defined as between-group. The Spearman bound (main text Theorem 2) IS about full-ranking. So there IS a mismatch, but it could be fixed by clarifying the definition. **Not overclaiming — this is a real issue.**

- Finding 4.4 (single axis overclaim): Am I inventing intermediate methods that don't exist in practice? The "partial completion" method (rank some within-group pairs, tie others) IS a real possibility. Practitioners DO report partial rankings (e.g., "top 5 features" without fully ordering features 6-20). **Not overclaiming — this is a real gap.**

- Finding 7.1 (no unique technique): Am I being too harsh? Arrow's ultrafilter lemma is elegant but Arrow himself didn't use it — it was discovered later by others analyzing his proof. Arrow's ORIGINAL proof used a step-by-step construction. Maybe the right comparison is to Arrow's original proof style, which was also "straightforward." **Possibly underclaiming — our IterativeOptimizer abstraction IS a reusable conceptual tool, even if it's not a "technique" in the narrow sense.**

## Vet Round 3: Omissions

- I didn't check whether the information loss formula is correct (Audit 2 should cover the math in the info loss section).
- I didn't verify the first-stump proposition's expansion formula against a CAS.
- Missing: whether the supplement's Proposition numbers are consistent (do theorem environments reset across sections?).

---

## Ranked Action List for Best Paper

### CRITICAL (must fix)

1. **Fix Design Space Theorem S definition** (Finding 2.3): Redefine S as full-ranking expected Spearman, or derive the Family A bound for between-group S separately. This is a mathematical error in the centerpiece theorem.

### HIGH (should fix)

2. **Fix F3 ε₀ algebra** (Finding 2.1): Correct the intermediate step or add explicit computation.
3. **Acknowledge design space is 2D** (Finding 4.4): M + completion threshold. Or restrict the "single axis" claim to the extremes.
4. **Classify theorems honestly** (Finding 4.2): Say "29 substantive theorems + 4 convenience lemmas" or similar.
5. **Add "among unbiased aggregations" to DASH optimality** in main text (Finding 4.3).
6. **Fix first-stump formula** (Finding 2.5): π(π-2)/(2n) not (π-2)/n.

### MEDIUM (nice to fix)

7. **Add "to our knowledge" to abstract line 57** (Finding 4.1).
8. **Add Berry-Esseen footnote** (Finding 2.2).
9. **Sharpen the Arrow parallel** (Finding 4.5): Note the preference-aggregation vs measurement-estimation distinction.
10. **For NMI: rewrite intro with motivating scenario** (Finding 6.1).

### LOW (cosmetic)

11. Expand NMI regulatory section if submitting there (Finding 6.2).

---

## Phased Implementation Plan

### Phase I: Critical Fix (1-2 hours)

**Task 1: Fix Design Space Theorem S definition.**
- Option A (recommended): Redefine S as expected Spearman correlation between independent evaluations of the method. This makes Family A's bound S ≤ 1 - m³/P³ correct by construction.
- Update: supplement.tex Definition (line 1586), main.tex §7 (line 433), and all references to "between-group stability" in the Design Space context.
- Verify the proof still holds under the new definition.

### Phase II: High Priority Fixes (1-2 hours)

**Task 2: Fix F3 ε₀ algebra.**
- Replace the intermediate step in supplement.tex:672-675 with the correct computation.

**Task 3: Fix first-stump formula.**
- Replace (π-2)/n with π(π-2)/(2n) in supplement.tex.

**Task 4: Honest theorem count.**
- Classify each of the 33 theorems. Update paper to say "29 substantive theorems and 4 convenience lemmas, with 0 sorry."

**Task 5: DASH optimality scope.**
- Add "among unbiased aggregations" to main.tex §7.

**Task 6: Design space dimensionality.**
- Add a sentence acknowledging the completion threshold as a second dimension, with the "single axis" holding at the extremes.

### Phase III: Medium Priority (30 min)

**Task 7: Abstract qualifier** — add "to our knowledge" to line 57.
**Task 8: Berry-Esseen footnote** — add clarification.
**Task 9: Arrow parallel nuance** — add distinction sentence.

### /vet of this plan

The plan prioritizes correctly: Finding 2.3 (S definition) is the only mathematical ERROR — everything else is sloppiness or overclaiming. If Finding 2.3 is not fixed, a strong reviewer WILL reject the Design Space Theorem as incorrectly stated.

The plan is conservative — it fixes issues without major restructuring. For NMI submission, a more substantial rewrite would be needed (Phase IV, not included here because the user said to focus on NeurIPS/NMI best paper, and the NeurIPS format is already set).

**Confidence: HIGH that these are the real issues. The S definition mismatch is the most important finding of this entire audit.**
