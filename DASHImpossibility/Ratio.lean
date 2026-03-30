/-
  Attribution ratio lemma: the split-count ratio between first-mover
  and non-first-mover in the same group equals 1/(1-ρ²), and this
  diverges as ρ → 1.

  Algebraic consequence of Axioms 2 and 3; the limit is real analysis.
-/
import DASHImpossibility.SplitGap

set_option autoImplicit false

namespace DASHImpossibility

variable (fs : FeatureSpace)

/-! ### Split-count ratio -/

/-- Split-count ratio between first-mover and non-first-mover = 1/(1-ρ²).
    This is the within-group inequity created by sequential boosting. -/
theorem splitCount_ratio (f : Model) (j₁ j₂ : Fin fs.P) (ℓ : Fin fs.L)
    (hj₁ : j₁ ∈ fs.group ℓ) (hj₂ : j₂ ∈ fs.group ℓ)
    (hfm : firstMover fs f = j₁) (hne : firstMover fs f ≠ j₂) :
    (splitCount fs j₁ f : ℝ) / (splitCount fs j₂ f : ℝ) =
      1 / (1 - fs.ρ ^ 2) := by
  have hfm_grp : firstMover fs f ∈ fs.group ℓ := by rw [hfm]; exact hj₁
  rw [splitCount_firstMover fs f j₁ hfm,
      splitCount_nonFirstMover fs f j₂ ℓ hj₂ hne hfm_grp]
  have h1 := denom_ne_zero fs
  have h2 : (1 : ℝ) - fs.ρ ^ 2 ≠ 0 := ne_of_gt (one_minus_rho_sq_pos fs)
  have h3 : (↑numTrees : ℝ) ≠ 0 := ne_of_gt (Nat.cast_pos.mpr numTrees_pos)
  field_simp

/-- Attribution ratio between first-mover and non-first-mover = 1/(1-ρ²).
    Follows from splitCount_ratio + strengthened Axiom 4 (model-wide c). -/
theorem attribution_ratio (f : Model) (j₁ j₂ : Fin fs.P) (ℓ : Fin fs.L)
    (hj₁ : j₁ ∈ fs.group ℓ) (hj₂ : j₂ ∈ fs.group ℓ)
    (hfm : firstMover fs f = j₁) (hne : firstMover fs f ≠ j₂) :
    attribution fs j₁ f / attribution fs j₂ f = 1 / (1 - fs.ρ ^ 2) := by
  obtain ⟨c, hc_pos, hc_eq⟩ := attribution_proportional fs f
  rw [hc_eq j₁, hc_eq j₂]
  rw [mul_div_mul_left _ _ (ne_of_gt hc_pos)]
  exact splitCount_ratio fs f j₁ j₂ ℓ hj₁ hj₂ hfm hne

/-! ### Ratio divergence -/

/-- As ρ → 1⁻, the ratio 1/(1-ρ²) → +∞ (Theorem 10(i)).
    Factor as 1/((1-ρ)(1+ρ)); as ρ → 1, (1+ρ) → 2 and 1/(1-ρ) → ∞. -/
theorem ratio_tendsto_atTop :
    Filter.Tendsto (fun ρ : ℝ => 1 / (1 - ρ ^ 2))
      (nhdsWithin 1 (Set.Iio 1)) Filter.atTop := by
  -- TODO: Factor 1-ρ² = (1-ρ)(1+ρ), use Tendsto.div and
  -- tendsto_inv_zero_atTop on the (1-ρ) factor.
  -- Mathlib has the primitives in Mathlib.Topology.Algebra.Order.LiminfLimsup
  -- and Mathlib.Analysis.SpecificLimits.Basic.
  sorry

end DASHImpossibility
