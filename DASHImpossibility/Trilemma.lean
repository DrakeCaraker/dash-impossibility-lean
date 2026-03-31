/-
  The Attribution Trilemma: no single-model feature ranking can simultaneously
  be faithful (reflect the model's attributions), stable (model-independent),
  and complete (decide all pairs).

  This is the model-agnostic layer. The GBDT-specific axioms instantiate
  the Rashomon property, but the trilemma holds for ANY attribution method
  satisfying it.

  Analogue of Arrow's impossibility theorem for social choice:
    Arrow:      IIA + Pareto + non-dictatorship → impossible
    Attribution: Faithfulness + Stability + Completeness → impossible

  Resolution (same as Arrow): relax completeness → partial orders.
  DASH achieves this by averaging attributions, making symmetric features
  equivalent rather than arbitrarily ranked.
-/
import DASHImpossibility.Defs

set_option autoImplicit false

namespace DASHImpossibility

variable (fs : FeatureSpace)

/-! ### The Rashomon Property -/

/-- The Rashomon property for feature attributions: for any two symmetric
    features (same group, same true coefficient), there exist models that
    rank them in opposite orders. This holds whenever the model class
    contains models with different feature utilization patterns —
    a consequence of collinearity creating an equivalence class of
    near-optimal models. -/
def RashimonProperty : Prop :=
  ∀ (ℓ : Fin fs.L) (j k : Fin fs.P),
    j ∈ fs.group ℓ → k ∈ fs.group ℓ → j ≠ k →
    ∃ f f' : Model,
      attribution fs j f > attribution fs k f ∧
      attribution fs k f' > attribution fs j f'

/-! ### The Attribution Trilemma -/

/-- **The Attribution Trilemma.** No model-independent ranking can faithfully
    represent all models' feature attributions when symmetric features exist.

    A ranking that is:
    • **Faithful** — reflects each model's attribution ordering
    • **Stable** — the same relation regardless of which model is explained
    necessarily FAILS to be:
    • **Complete** — some feature pairs cannot be decided

    This is a formal impossibility: assuming faithfulness for all models
    and a fixed (stable) ranking derives `False`.

    The resolution is to relax completeness: use partial orders where
    symmetric features are incomparable, or use population-level
    attributions (DASH) where symmetric features are tied.

    Note: this impossibility applies to SINGLE-MODEL explanations.
    Population-level explanations (expected attributions over an ensemble)
    are not subject to it, because E[φ_j] = E[φ_k] under DGP symmetry —
    the ranking is correctly undetermined. -/
theorem attribution_trilemma
    (hrash : RashimonProperty fs)
    (ℓ : Fin fs.L) (j k : Fin fs.P)
    (hj : j ∈ fs.group ℓ) (hk : k ∈ fs.group ℓ) (hjk : j ≠ k)
    (ranking : Fin fs.P → Fin fs.P → Prop)
    (h_faithful : ∀ f : Model,
      ranking j k ↔ attribution fs j f > attribution fs k f) :
    False := by
  obtain ⟨f, f', h1, h2⟩ := hrash ℓ j k hj hk hjk
  have hrank : ranking j k := (h_faithful f).mpr h1
  have hcontra : attribution fs j f' > attribution fs k f' := (h_faithful f').mp hrank
  linarith

end DASHImpossibility
