/-
  Impossibility theorem (Theorem 1): no single sequential gradient-boosted
  model can simultaneously achieve stability and equity under collinearity.

  Part (i):  Equity violation — attribution ratio exceeds any bound as ρ → 1
  Part (ii): Stability bound — Spearman ≤ 1 - Ω((m/P)³)
-/
import DASHImpossibility.Ratio
import DASHImpossibility.General

set_option autoImplicit false

namespace DASHImpossibility

variable (fs : FeatureSpace)

/-! ### Part (i): Equity violation -/

/-- The attribution ratio 1/(1-ρ²) can be rewritten as 1 + ρ²/(1-ρ²),
    showing the equity violation is at least ρ²/(1-ρ²) above 1. -/
theorem attribution_ratio_ge (f : Model) (j₁ j₂ : Fin fs.P) (ℓ : Fin fs.L)
    (hj₁ : j₁ ∈ fs.group ℓ) (hj₂ : j₂ ∈ fs.group ℓ)
    (hfm : firstMover fs f = j₁) (hne : firstMover fs f ≠ j₂) :
    attribution fs j₁ f / attribution fs j₂ f ≥ 1 + fs.ρ ^ 2 / (1 - fs.ρ ^ 2) := by
  rw [attribution_ratio fs f j₁ j₂ ℓ hj₁ hj₂ hfm hne]
  suffices h : 1 / (1 - fs.ρ ^ 2) = 1 + fs.ρ ^ 2 / (1 - fs.ρ ^ 2) by linarith
  have h1 : (1 : ℝ) - fs.ρ ^ 2 ≠ 0 := ne_of_gt (one_minus_rho_sq_pos fs)
  field_simp
  ring

/-- Equity is violated: the ratio exceeds 1 + γ whenever γ < ρ²/(1-ρ²). -/
theorem not_equitable (f : Model) (j₁ j₂ : Fin fs.P) (ℓ : Fin fs.L)
    (hj₁ : j₁ ∈ fs.group ℓ) (hj₂ : j₂ ∈ fs.group ℓ)
    (hfm : firstMover fs f = j₁) (hne : firstMover fs f ≠ j₂)
    (γ : ℝ) (hγ : γ < fs.ρ ^ 2 / (1 - fs.ρ ^ 2)) :
    ¬ isEquitable γ (attribution fs j₁ f / attribution fs j₂ f) := by
  unfold isEquitable
  push Not
  have h := attribution_ratio_ge fs f j₁ j₂ ℓ hj₁ hj₂ hfm hne
  linarith

/-! ### Part (ii): Stability bound -/

/-- Stability is bounded: Spearman ≤ 1 - (m/P)³/6 when first-movers differ. -/
theorem not_stable (f f' : Model) (ℓ : Fin fs.L)
    (hfm_grp : firstMover fs f ∈ fs.group ℓ)
    (hfm'_grp : firstMover fs f' ∈ fs.group ℓ)
    (hdiff : firstMover fs f ≠ firstMover fs f')
    (δ : ℝ) (hδ : δ < (fs.groupSize ℓ : ℝ) ^ 3 / ((fs.P : ℝ) ^ 3 * 6)) :
    ¬ isStable δ (spearman fs (fun j => attribution fs j f)
                                (fun j => attribution fs j f')) := by
  unfold isStable
  push Not
  have h := spearman_bound fs f f' ℓ hfm_grp hfm'_grp hdiff
  linarith

/-! ### Combined impossibility -/

/-- The impossibility: equity and stability cannot both hold.
    For any model with a first-mover, equity is violated (ratio > 1).
    For any two models with different first-movers, stability is bounded. -/
theorem impossibility (f f' : Model) (j k : Fin fs.P) (ℓ : Fin fs.L)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ)
    (hfm : firstMover fs f = j) (hfm' : firstMover fs f' = k) (hjk : j ≠ k) :
    -- Equity is violated:
    attribution fs j f / attribution fs k f ≥ 1 + fs.ρ ^ 2 / (1 - fs.ρ ^ 2) ∧
    -- AND stability is bounded:
    spearman fs (fun i => attribution fs i f) (fun i => attribution fs i f') ≤
      1 - (fs.groupSize ℓ : ℝ) ^ 3 / ((fs.P : ℝ) ^ 3 * 6) := by
  refine ⟨?_, ?_⟩
  · exact attribution_ratio_ge fs f j k ℓ hj hk hfm (by rw [hfm]; exact hjk)
  · exact spearman_bound fs f f' ℓ (by rw [hfm]; exact hj) (by rw [hfm']; exact hk)
      (by rw [hfm, hfm']; exact hjk)

end DASHImpossibility
