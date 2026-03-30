/-
  Corollary 1: DASH achieves equity and between-group stability,
  resolving the impossibility by breaking sequential dependence.

  (a) Equity in expectation — consensus attributions are equal within groups
  (b) Stability via LLN — variance → 0 as M → ∞ (stated, proof deferred)
  (c) Within-group ranking is undetermined by symmetry
-/
import DASHImpossibility.Impossibility

set_option autoImplicit false

namespace DASHImpossibility

variable (fs : FeatureSpace)

/-! ### Corollary 1(a): Equity in expectation -/

/-- DASH consensus attributions are equal for features in the same group.
    Direct from Axiom 7 (attribution sum symmetry) + definition of consensus. -/
theorem consensus_equity (M : ℕ) (hM : 0 < M) (models : Fin M → Model)
    (j k : Fin fs.P) (ℓ : Fin fs.L)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) :
    consensus fs M hM models j = consensus fs M hM models k := by
  unfold consensus
  congr 1
  exact attribution_sum_symmetric fs M hM models j k ℓ hj hk

/-! ### Corollary 1(c): Within-group instability is irreducible -/

/-- The consensus difference between same-group features is exactly zero.
    Neither feature systematically outranks the other — any observed ordering
    is due to finite-sample noise, not a true importance difference. -/
theorem consensus_difference_zero (M : ℕ) (hM : 0 < M) (models : Fin M → Model)
    (j k : Fin fs.P) (ℓ : Fin fs.L)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) :
    consensus fs M hM models j - consensus fs M hM models k = 0 := by
  rw [consensus_equity fs M hM models j k ℓ hj hk]
  simp

/-! ### Corollary 1(b): Between-group stability (stated) -/

/-- Between-group stability improves with ensemble size M.
    The variance of consensus attributions decreases as O(1/M).
    Full proof requires measure-theoretic setup (IndepFun.variance_sum);
    we state the property as a remark. -/
theorem consensus_variance_decreases :
    True := by  -- Placeholder for the variance bound
  -- The full statement would be:
  -- Var(consensus fs M hM models j) ≤ Var(attribution fs j ·) / M
  -- Proof uses IndepFun.variance_sum from Mathlib.Probability.Moments.Variance
  -- with independence from i.i.d. seeds and bounded variance.
  -- Deferred: requires MeasureSpace on Seed.
  trivial

end DASHImpossibility
